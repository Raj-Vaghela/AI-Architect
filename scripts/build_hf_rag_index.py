#!/usr/bin/env python3
"""
Hugging Face RAG Index Builder

Builds a deterministic, versioned RAG index from hf.models + hf.model_cards.
Performs exclusion, deduplication, chunking, and OpenAI embedding generation.

All writes go through direct Postgres connection (NOT MCP).
"""

import argparse
import hashlib
import logging
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import psycopg2
import psycopg2.extras
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('hf_rag_index.log')
    ]
)
logger = logging.getLogger(__name__)


class RAGIndexBuilder:
    """Builds deterministic RAG index with deduplication and embeddings"""
    
    def __init__(self, config: Dict):
        """Initialize with configuration"""
        self.config = config
        self.conn = None
        self.openai_client = None
        self.encoder = None
        self.stats = defaultdict(int)
        self.failures = []
        
        # Initialize tiktoken
        try:
            self.encoder = tiktoken.get_encoding("cl100k_base")
            logger.info("Initialized tiktoken encoder: cl100k_base")
        except Exception as e:
            logger.error(f"Failed to initialize tiktoken: {e}")
            raise
    
    def connect_db(self):
        """Connect to Postgres"""
        try:
            self.conn = psycopg2.connect(self.config['db_url'])
            self.conn.autocommit = False
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def init_openai(self):
        """Initialize OpenAI client"""
        try:
            self.openai_client = OpenAI(api_key=self.config['openai_api_key'])
            logger.info(f"OpenAI client initialized with model: {self.config['embed_model']}")
        except Exception as e:
            logger.error(f"OpenAI initialization failed: {e}")
            raise
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken"""
        try:
            return len(self.encoder.encode(text))
        except Exception as e:
            logger.warning(f"Token counting failed, using fallback: {e}")
            return len(text.split())
    
    def compute_hash(self, text: str) -> str:
        """Compute SHA256 hash"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def normalize_text(self, text: str) -> str:
        """Normalize text deterministically"""
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Trim trailing spaces from each line
        lines = [line.rstrip() for line in text.split('\n')]
        
        # Collapse >3 blank lines to 2
        normalized_lines = []
        blank_count = 0
        for line in lines:
            if line == '':
                blank_count += 1
                if blank_count <= 2:
                    normalized_lines.append(line)
            else:
                blank_count = 0
                normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)
    
    # ========== STEP A: EXCLUSION RULES ==========
    
    def apply_exclusion_rules(self):
        """Mark cards for exclusion based on Tier 1 rules"""
        logger.info("=" * 60)
        logger.info("STEP A: Applying exclusion rules")
        logger.info("=" * 60)
        
        cursor = self.conn.cursor()
        
        # Rule 1: "No model card found."
        cursor.execute("""
            UPDATE hf.model_cards
            SET excluded_from_rag = TRUE,
                exclusion_reason = 'No content'
            WHERE card_text = 'No model card found.'
            AND excluded_from_rag = FALSE
        """)
        rule1_count = cursor.rowcount
        logger.info(f"Rule 1 (No content): {rule1_count} cards excluded")
        
        # Rule 2: token_count < 50
        cursor.execute("""
            UPDATE hf.model_cards
            SET excluded_from_rag = TRUE,
                exclusion_reason = 'Too short (<50 tokens)'
            WHERE token_count < 50
            AND excluded_from_rag = FALSE
        """)
        rule2_count = cursor.rowcount
        logger.info(f"Rule 2 (Too short): {rule2_count} cards excluded")
        
        # Rule 3: token_count > 100000
        cursor.execute("""
            UPDATE hf.model_cards
            SET excluded_from_rag = TRUE,
                exclusion_reason = 'Too long (>100k tokens, likely non-textual)'
            WHERE token_count > 100000
            AND excluded_from_rag = FALSE
        """)
        rule3_count = cursor.rowcount
        logger.info(f"Rule 3 (Too long): {rule3_count} cards excluded")
        
        self.conn.commit()
        
        self.stats['excluded_no_content'] = rule1_count
        self.stats['excluded_too_short'] = rule2_count
        self.stats['excluded_too_long'] = rule3_count
        self.stats['total_excluded'] = rule1_count + rule2_count + rule3_count
        
        logger.info(f"Total excluded: {self.stats['total_excluded']}")
    
    # ========== STEP B: CANONICAL MAPPING ==========
    
    def build_canonical_mapping(self):
        """Build canonical card mapping with deduplication"""
        logger.info("=" * 60)
        logger.info("STEP B: Building canonical mapping (deduplication)")
        logger.info("=" * 60)
        
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Get all non-excluded cards grouped by card_hash
        logger.info("Fetching non-excluded cards...")
        cursor.execute("""
            SELECT 
                mc.card_hash,
                mc.model_id,
                COALESCE(m.downloads, 0) as downloads,
                COALESCE(m.likes, 0) as likes,
                mc.model_id as model_id_tie
            FROM hf.model_cards mc
            LEFT JOIN hf.models m ON mc.model_id = m.model_id
            WHERE mc.excluded_from_rag = FALSE
            ORDER BY mc.card_hash, 
                     downloads DESC, 
                     likes DESC, 
                     model_id_tie ASC
        """)
        
        cards = cursor.fetchall()
        logger.info(f"Found {len(cards)} non-excluded cards")
        
        # Group by card_hash and pick canonical
        hash_groups = defaultdict(list)
        for card in cards:
            hash_groups[card['card_hash']].append(card)
        
        logger.info(f"Found {len(hash_groups)} unique card_hash values")
        
        # Prepare canon data
        canon_data = []
        model_to_card_data = []
        
        for card_hash, group in hash_groups.items():
            # First model in sorted group is canonical (deterministic)
            canonical = group[0]
            duplicate_count = len(group)
            
            canon_data.append((
                card_hash,
                canonical['model_id'],
                duplicate_count
            ))
            
            # Map all models to this card_hash
            for card in group:
                model_to_card_data.append((
                    card['model_id'],
                    card_hash
                ))
        
        # Upsert into card_canon
        logger.info(f"Upserting {len(canon_data)} canonical cards...")
        cursor.executemany("""
            INSERT INTO hf.card_canon (card_hash, canonical_model_id, duplicate_count)
            VALUES (%s, %s, %s)
            ON CONFLICT (card_hash) DO UPDATE SET
                canonical_model_id = EXCLUDED.canonical_model_id,
                duplicate_count = EXCLUDED.duplicate_count
        """, canon_data)
        
        # Upsert into model_to_card
        logger.info(f"Upserting {len(model_to_card_data)} model-to-card mappings...")
        cursor.executemany("""
            INSERT INTO hf.model_to_card (model_id, card_hash)
            VALUES (%s, %s)
            ON CONFLICT (model_id) DO UPDATE SET
                card_hash = EXCLUDED.card_hash
        """, model_to_card_data)
        
        self.conn.commit()
        
        self.stats['unique_card_hashes'] = len(hash_groups)
        self.stats['total_model_mappings'] = len(model_to_card_data)
        self.stats['total_duplicates'] = len(model_to_card_data) - len(hash_groups)
        
        logger.info(f"Canonical mapping complete:")
        logger.info(f"  - Unique cards: {self.stats['unique_card_hashes']}")
        logger.info(f"  - Total models mapped: {self.stats['total_model_mappings']}")
        logger.info(f"  - Duplicate models: {self.stats['total_duplicates']}")
    
    # ========== STEP C: DETERMINISTIC CHUNKING ==========
    
    def extract_key_sections(self, text: str, max_tokens: int = 12000) -> str:
        """Extract key sections from large cards with robust error handling"""
        try:
            # Safety check: ensure text is valid
            if not text or not isinstance(text, str):
                logger.warning("Invalid text input to extract_key_sections, returning empty string")
                return ""
            
            # Keywords for important sections (case-insensitive)
            keywords = [
                'description', 'overview', 'intended use', 'how to use',
                'usage', 'limitations', 'license'
            ]
            
            # Split by headings
            sections = []
            current_section = []
            current_heading = None
            
            try:
                lines = text.split('\n')
            except Exception as e:
                logger.error(f"Failed to split text into lines: {e}, using raw text")
                lines = [text]
            
            for line in lines:
                try:
                    # Check if line is a heading
                    heading_match = re.match(r'^(#{1,4})\s+(.+)$', line)
                    if heading_match:
                        # Save previous section
                        if current_section:
                            sections.append({
                                'heading': current_heading,
                                'content': '\n'.join(current_section),
                                'is_key': any(kw in (current_heading or '').lower() for kw in keywords)
                            })
                        current_section = [line]
                        current_heading = heading_match.group(2)
                    else:
                        current_section.append(line)
                except Exception as e:
                    logger.debug(f"Error processing line in extract_key_sections: {e}")
                    # Continue processing other lines
                    current_section.append(line)
            
            # Save last section
            if current_section:
                try:
                    sections.append({
                        'heading': current_heading,
                        'content': '\n'.join(current_section),
                        'is_key': any(kw in (current_heading or '').lower() for kw in keywords) if current_heading else False
                    })
                except Exception as e:
                    logger.debug(f"Error saving last section: {e}")
            
            # Prioritize key sections
            key_sections = [s for s in sections if s.get('is_key', False)]
            other_sections = [s for s in sections if not s.get('is_key', False)]
            
            # Build extracted text
            extracted = []
            total_tokens = 0
            
            # Add key sections first
            for section in key_sections:
                try:
                    section_content = section.get('content', '')
                    section_tokens = self.count_tokens(section_content)
                    if total_tokens + section_tokens <= max_tokens:
                        extracted.append(section_content)
                        total_tokens += section_tokens
                    else:
                        break
                except Exception as e:
                    logger.debug(f"Error processing key section: {e}")
                    continue
            
            # Add other sections if space remains
            for section in other_sections:
                try:
                    section_content = section.get('content', '')
                    section_tokens = self.count_tokens(section_content)
                    if total_tokens + section_tokens <= max_tokens:
                        extracted.append(section_content)
                        total_tokens += section_tokens
                    else:
                        break
                except Exception as e:
                    logger.debug(f"Error processing other section: {e}")
                    continue
            
            result = '\n\n'.join(extracted)
            
            # Fallback: if extraction resulted in empty text, return truncated original
            if not result or result.strip() == '':
                logger.warning(f"Section extraction resulted in empty text, falling back to truncation")
                # Truncate to max_tokens using simple token-based truncation
                tokens = self.encoder.encode(text)
                if len(tokens) > max_tokens:
                    tokens = tokens[:max_tokens]
                result = self.encoder.decode(tokens)
            
            return result
            
        except Exception as e:
            logger.error(f"extract_key_sections failed with error: {e}, falling back to truncation")
            # Final fallback: truncate the original text
            try:
                tokens = self.encoder.encode(text)
                if len(tokens) > max_tokens:
                    tokens = tokens[:max_tokens]
                return self.encoder.decode(tokens)
            except Exception as e2:
                logger.error(f"Fallback truncation also failed: {e2}, returning original text prefix")
                # Last resort: return first N characters
                return text[:50000] if text else ""
    
    def chunk_text(self, text: str, card_hash: str, token_count: int) -> List[Dict]:
        """Chunk text deterministically with robust error handling"""
        # Normalize text first
        normalized_text = self.normalize_text(text)
        
        # Handle large cards (10k-100k tokens)
        if 10000 <= token_count <= 100000:
            logger.info(f"Large card ({card_hash[:8]}...): {token_count} tokens, extracting key sections...")
            try:
                extracted_text = self.extract_key_sections(normalized_text, max_tokens=12000)
                
                # Validate extraction result
                if not extracted_text or extracted_text.strip() == '':
                    logger.warning(f"Large card ({card_hash[:8]}...): extraction returned empty, using truncation fallback")
                    # Fallback to simple truncation
                    tokens = self.encoder.encode(normalized_text)
                    tokens = tokens[:12000]
                    normalized_text = self.encoder.decode(tokens)
                else:
                    normalized_text = extracted_text
                
                new_token_count = self.count_tokens(normalized_text)
                logger.info(f"Large card ({card_hash[:8]}...): after extraction: {new_token_count} tokens (reduced from {token_count})")
                token_count = new_token_count
                
            except Exception as e:
                logger.error(f"Large card ({card_hash[:8]}...): extraction failed: {e}, using truncation fallback")
                # Fallback to truncation
                tokens = self.encoder.encode(normalized_text)
                tokens = tokens[:12000]
                normalized_text = self.encoder.decode(tokens)
                token_count = self.count_tokens(normalized_text)
        
        chunks = []
        
        # Single chunk for small cards
        if token_count <= self.config['chunk_target']:
            chunk_text = normalized_text
            chunks.append({
                'chunk_hash': self.compute_hash(chunk_text),
                'card_hash': card_hash,
                'chunk_index': 0,
                'chunk_text': chunk_text,
                'token_count': token_count
            })
            return chunks
        
        # Multi-chunk: split by headings
        sections = []
        current_section = []
        
        for line in normalized_text.split('\n'):
            # Check for H2 or H3 heading
            if re.match(r'^#{2,3}\s+', line):
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)
        
        if current_section:
            sections.append('\n'.join(current_section))
        
        # If no headings found, fall back to sliding window
        if len(sections) <= 1:
            sections = self._sliding_window_split(normalized_text)
        
        # Process sections into chunks
        chunk_index = 0
        for i, section in enumerate(sections):
            section_tokens = self.count_tokens(section)
            
            # If section is small enough, use as-is
            if section_tokens <= self.config['chunk_target']:
                chunk_text = section
                chunks.append({
                    'chunk_hash': self.compute_hash(chunk_text),
                    'card_hash': card_hash,
                    'chunk_index': chunk_index,
                    'chunk_text': chunk_text,
                    'token_count': section_tokens
                })
                chunk_index += 1
            else:
                # Section too large, split with sliding window
                sub_chunks = self._sliding_window_split(section)
                for sub_chunk in sub_chunks:
                    sub_tokens = self.count_tokens(sub_chunk)
                    chunks.append({
                        'chunk_hash': self.compute_hash(sub_chunk),
                        'card_hash': card_hash,
                        'chunk_index': chunk_index,
                        'chunk_text': sub_chunk,
                        'token_count': sub_tokens
                    })
                    chunk_index += 1
        
        return chunks
    
    def _sliding_window_split(self, text: str) -> List[str]:
        """Split text using sliding window with overlap"""
        tokens = self.encoder.encode(text)
        chunks = []
        
        target = self.config['chunk_target']
        overlap = self.config['chunk_overlap']
        
        start = 0
        while start < len(tokens):
            end = min(start + target, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoder.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            if end >= len(tokens):
                break
            
            start = end - overlap
        
        return chunks
    
    def chunk_all_canonical_cards(self):
        """Chunk all canonical cards"""
        logger.info("=" * 60)
        logger.info("STEP C: Chunking canonical cards")
        logger.info("=" * 60)
        
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Get canonical cards
        limit_clause = ""
        if self.config['max_canon_models'] > 0:
            limit_clause = f"LIMIT {self.config['max_canon_models']}"
        
        query = f"""
            SELECT 
                cc.card_hash,
                cc.canonical_model_id,
                mc.card_text,
                mc.token_count
            FROM hf.card_canon cc
            JOIN hf.model_cards mc ON cc.canonical_model_id = mc.model_id
            ORDER BY cc.card_hash
            {limit_clause}
        """
        
        cursor.execute(query)
        canonical_cards = cursor.fetchall()
        
        logger.info(f"Chunking {len(canonical_cards)} canonical cards...")
        
        all_chunks = []
        chunk_stats = []
        
        for idx, card in enumerate(canonical_cards, 1):
            if idx % 100 == 0:
                logger.info(f"Chunked {idx}/{len(canonical_cards)} cards...")
            
            try:
                chunks = self.chunk_text(
                    card['card_text'],
                    card['card_hash'],
                    card['token_count']
                )
                
                all_chunks.extend(chunks)
                chunk_stats.append(len(chunks))
                
            except Exception as e:
                logger.error(f"Failed to chunk card {card['card_hash']}: {e}")
                self.failures.append({
                    'card_hash': card['card_hash'],
                    'model_id': card['canonical_model_id'],
                    'error': str(e),
                    'step': 'chunking'
                })
        
        logger.info(f"Generated {len(all_chunks)} total chunks")
        
        # Insert chunks (upsert)
        logger.info("Inserting chunks into database...")
        cursor = self.conn.cursor()
        
        insert_query = """
            INSERT INTO hf.card_chunks (
                chunk_hash, card_hash, chunk_index, chunk_text, 
                token_count, embedding_model_name, chunker_version
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (chunker_version, embedding_model_name, chunk_hash) 
            DO NOTHING
        """
        
        chunk_data = [
            (
                chunk['chunk_hash'],
                chunk['card_hash'],
                chunk['chunk_index'],
                chunk['chunk_text'],
                chunk['token_count'],
                self.config['embed_model'],
                self.config['chunker_version']
            )
            for chunk in all_chunks
        ]
        
        cursor.executemany(insert_query, chunk_data)
        inserted_count = cursor.rowcount
        self.conn.commit()
        
        self.stats['total_chunks_generated'] = len(all_chunks)
        self.stats['chunks_inserted'] = inserted_count
        self.stats['chunks_per_card_min'] = min(chunk_stats) if chunk_stats else 0
        self.stats['chunks_per_card_max'] = max(chunk_stats) if chunk_stats else 0
        self.stats['chunks_per_card_median'] = sorted(chunk_stats)[len(chunk_stats)//2] if chunk_stats else 0
        
        logger.info(f"Chunks inserted: {inserted_count}")
        logger.info(f"Chunks per card: min={self.stats['chunks_per_card_min']}, "
                   f"median={self.stats['chunks_per_card_median']}, "
                   f"max={self.stats['chunks_per_card_max']}")
    
    # ========== STEP D: EMBEDDINGS ==========
    
    @retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5),
        reraise=True
    )
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding with retry logic"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.config['embed_model'],
                input=text
            )
            return response.data[0].embedding
        except RateLimitError as e:
            logger.warning(f"Rate limit hit, retrying...")
            raise
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    def embed_chunks(self):
        """Generate embeddings for chunks"""
        logger.info("=" * 60)
        logger.info("STEP D: Generating embeddings")
        logger.info("=" * 60)
        
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Get chunks without embeddings
        cursor.execute("""
            SELECT id, chunk_text, token_count
            FROM hf.card_chunks
            WHERE embedding IS NULL
            AND chunker_version = %s
            AND embedding_model_name = %s
            ORDER BY id
        """, (self.config['chunker_version'], self.config['embed_model']))
        
        chunks_to_embed = cursor.fetchall()
        total_chunks = len(chunks_to_embed)
        
        logger.info(f"Found {total_chunks} chunks needing embeddings")
        
        if total_chunks == 0:
            logger.info("No chunks to embed, skipping")
            self.stats['chunks_embedded'] = 0
            return
        
        # Process in batches with rate limiting
        batch_size = self.config['batch_size']
        embedded_count = 0
        
        for i in range(0, total_chunks, batch_size):
            batch = chunks_to_embed[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(total_chunks + batch_size - 1)//batch_size}...")
            
            for chunk in batch:
                try:
                    # Generate embedding
                    embedding = self.generate_embedding(chunk['chunk_text'])
                    
                    # Update database
                    update_cursor = self.conn.cursor()
                    update_cursor.execute("""
                        UPDATE hf.card_chunks
                        SET embedding = %s
                        WHERE id = %s
                    """, (embedding, chunk['id']))
                    
                    embedded_count += 1
                    
                    if embedded_count % 10 == 0:
                        logger.info(f"Embedded {embedded_count}/{total_chunks} chunks")
                    
                    # Small delay to respect rate limits
                    time.sleep(0.05)
                    
                except Exception as e:
                    logger.error(f"Failed to embed chunk {chunk['id']}: {e}")
                    self.failures.append({
                        'chunk_id': chunk['id'],
                        'error': str(e),
                        'step': 'embedding'
                    })
            
            # Commit after each batch
            self.conn.commit()
            logger.info(f"Batch committed, total embedded: {embedded_count}")
        
        self.stats['chunks_embedded'] = embedded_count
        logger.info(f"Embedding complete: {embedded_count}/{total_chunks} chunks embedded")
    
    # ========== REPORTING ==========
    
    def generate_report(self):
        """Generate final report"""
        logger.info("=" * 60)
        logger.info("Generating report")
        logger.info("=" * 60)
        
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Get additional stats
        cursor.execute("SELECT COUNT(*) as count FROM hf.models")
        self.stats['total_models'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM hf.model_cards")
        self.stats['total_model_cards'] = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM hf.card_chunks
            WHERE embedding IS NOT NULL
        """)
        self.stats['chunks_with_embeddings'] = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM hf.card_chunks
            WHERE embedding IS NULL
        """)
        self.stats['chunks_pending_embeddings'] = cursor.fetchone()['count']
        
        # Chunk token stats
        cursor.execute("""
            SELECT 
                MIN(token_count) as min_tokens,
                MAX(token_count) as max_tokens,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY token_count) as median_tokens,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY token_count) as p95_tokens
            FROM hf.card_chunks
        """)
        token_stats = cursor.fetchone()
        
        # Top 20 largest cards
        cursor.execute("""
            SELECT 
                mc.model_id,
                mc.token_count,
                mc.excluded_from_rag,
                mc.exclusion_reason
            FROM hf.model_cards mc
            ORDER BY mc.token_count DESC
            LIMIT 20
        """)
        largest_cards = cursor.fetchall()
        
        # Generate markdown report
        report = f"""# HF RAG Index Build Report

**Generated:** {datetime.now().isoformat()}  
**Chunker Version:** {self.config['chunker_version']}  
**Embedding Model:** {self.config['embed_model']}  
**Tokenizer:** tiktoken cl100k_base  

## Configuration

| Parameter | Value |
|-----------|-------|
| Chunk Target Tokens | {self.config['chunk_target']} |
| Chunk Overlap Tokens | {self.config['chunk_overlap']} |
| Max Canon Models | {self.config['max_canon_models']} (0 = no limit) |
| Batch Size | {self.config['batch_size']} |

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Total Models** | {self.stats['total_models']:,} |
| **Total Model Cards** | {self.stats['total_model_cards']:,} |
| **Excluded Cards** | {self.stats['total_excluded']:,} |
| - No content | {self.stats['excluded_no_content']:,} |
| - Too short (<50 tokens) | {self.stats['excluded_too_short']:,} |
| - Too long (>100k tokens) | {self.stats['excluded_too_long']:,} |
| **Unique Card Hashes (Canon)** | {self.stats['unique_card_hashes']:,} |
| **Total Model Mappings** | {self.stats['total_model_mappings']:,} |
| **Duplicate Models** | {self.stats['total_duplicates']:,} |
| **Total Chunks Generated** | {self.stats['total_chunks_generated']:,} |
| **Chunks Inserted** | {self.stats['chunks_inserted']:,} |
| **Chunks with Embeddings** | {self.stats['chunks_with_embeddings']:,} |
| **Chunks Pending Embeddings** | {self.stats['chunks_pending_embeddings']:,} |

## Chunk Statistics

### Chunks per Card

| Metric | Value |
|--------|-------|
| Minimum | {self.stats['chunks_per_card_min']} |
| Median | {self.stats['chunks_per_card_median']} |
| Maximum | {self.stats['chunks_per_card_max']} |

### Chunk Token Distribution

| Metric | Tokens |
|--------|--------|
| Minimum | {int(token_stats['min_tokens']) if token_stats['min_tokens'] else 0} |
| Median | {int(token_stats['median_tokens']) if token_stats['median_tokens'] else 0} |
| p95 | {int(token_stats['p95_tokens']) if token_stats['p95_tokens'] else 0} |
| Maximum | {int(token_stats['max_tokens']) if token_stats['max_tokens'] else 0} |

## Top 20 Largest Cards

| Model ID | Token Count | Excluded | Reason |
|----------|-------------|----------|--------|
"""
        
        for card in largest_cards:
            excluded = "✅" if card['excluded_from_rag'] else "❌"
            reason = card['exclusion_reason'] or "N/A"
            report += f"| {card['model_id']} | {card['token_count']:,} | {excluded} | {reason} |\n"
        
        report += f"""
## Failures

Total failures: {len(self.failures)}

"""
        
        if self.failures:
            report += "| Type | ID | Error |\n"
            report += "|------|-----|-------|\n"
            for failure in self.failures[:20]:  # Show first 20
                step = failure.get('step', 'unknown')
                id_val = failure.get('card_hash') or failure.get('chunk_id') or 'N/A'
                error = failure.get('error', 'Unknown error')[:100]
                report += f"| {step} | {id_val} | {error} |\n"
        else:
            report += "No failures ✅\n"
        
        report += """
## Next Steps

1. Verify chunk uniqueness constraint
2. Confirm excluded cards have no chunks
3. Test vector similarity search
4. Run sample RAG queries

---

**Report End**
"""
        
        # Write report
        with open('docs/hf_rag_index_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info("Report written to docs/hf_rag_index_report.md")
    
    # ========== MAIN EXECUTION ==========
    
    def run(self):
        """Execute full pipeline"""
        start_time = time.time()
        
        try:
            logger.info("=" * 60)
            logger.info("HF RAG INDEX BUILDER - START")
            logger.info("=" * 60)
            
            self.connect_db()
            self.init_openai()
            
            # Step A: Exclusions
            self.apply_exclusion_rules()
            
            # Step B: Canonical mapping
            self.build_canonical_mapping()
            
            # Step C: Chunking
            self.chunk_all_canonical_cards()
            
            # Step D: Embeddings
            self.embed_chunks()
            
            # Generate report
            self.generate_report()
            
            elapsed = time.time() - start_time
            logger.info("=" * 60)
            logger.info(f"PIPELINE COMPLETE - Elapsed: {elapsed:.2f}s")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
        finally:
            self.close_db()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Build HF RAG Index',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--env-file',
        default='.env.local',
        help='Environment file to load (default: .env.local)'
    )
    
    args = parser.parse_args()
    
    # Load environment
    load_dotenv(args.env_file)
    
    # Build config
    config = {
        'db_url': os.getenv('SUPABASE_DB_URL'),
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'embed_model': os.getenv('OPENAI_EMBED_MODEL', 'text-embedding-3-small'),
        'chunker_version': os.getenv('CHUNKER_VERSION', 'hf_chunker_v1'),
        'chunk_target': int(os.getenv('CHUNK_TARGET_TOKENS', '900')),
        'chunk_overlap': int(os.getenv('CHUNK_OVERLAP_TOKENS', '120')),
        'max_canon_models': int(os.getenv('MAX_CANON_MODELS', '0')),
        'batch_size': int(os.getenv('BATCH_SIZE', '100')),
    }
    
    # Validate config
    if not config['db_url']:
        logger.error("SUPABASE_DB_URL not set")
        sys.exit(1)
    
    if not config['openai_api_key']:
        logger.error("OPENAI_API_KEY not set")
        sys.exit(1)
    
    # Run pipeline
    builder = RAGIndexBuilder(config)
    builder.run()


if __name__ == '__main__':
    main()

