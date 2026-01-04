#!/usr/bin/env python3
"""
Process Missing HF Cards - Targeted Reprocessing Script

This script processes ONLY the canonical cards that have no chunks in hf.card_chunks.
It reuses the improved chunking logic from build_hf_rag_index.py with the fixed
extract_key_sections() function.

Usage:
    python scripts/process_missing_cards.py --env-file .env.local
"""

import argparse
import hashlib
import logging
import os
import re
import sys
import time
from typing import Dict, List

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
        logging.FileHandler('process_missing_cards.log')
    ]
)
logger = logging.getLogger(__name__)


class MissingCardsProcessor:
    """Process canonical cards that have no chunks"""
    
    def __init__(self, config: Dict):
        """Initialize with configuration"""
        self.config = config
        self.conn = None
        self.openai_client = None
        self.encoder = None
        
        # Statistics
        self.stats = {
            'missing_cards_found': 0,
            'cards_processed': 0,
            'chunks_generated': 0,
            'chunks_inserted': 0,
            'chunks_embedded': 0,
            'failures': 0
        }
        self.failures = []
    
    def connect_db(self):
        """Establish database connection"""
        logger.info("Connecting to database...")
        self.conn = psycopg2.connect(self.config['db_url'])
        self.encoder = tiktoken.get_encoding(self.config['tokenizer'])
        logger.info("Database connected")
    
    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def init_openai(self):
        """Initialize OpenAI client"""
        logger.info("Initializing OpenAI client...")
        self.openai_client = OpenAI(api_key=self.config['openai_key'])
        logger.info("OpenAI client initialized")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            return len(self.encoder.encode(text, disallowed_special=()))
        except Exception as e:
            logger.warning(f"Token counting failed: {e}, estimating...")
            return len(text) // 4
    
    def compute_hash(self, text: str) -> str:
        """Compute SHA256 hash of text"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for consistent chunking"""
        # Consistent line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        # Collapse multiple blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    
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
            chunks.append({
                'chunk_hash': self.compute_hash(normalized_text),
                'card_hash': card_hash,
                'chunk_index': 0,
                'chunk_text': normalized_text,
                'token_count': token_count
            })
            return chunks
        
        # Chunk by markdown headings (## and ###)
        heading_pattern = r'^(#{2,3})\s+(.+)$'
        lines = normalized_text.split('\n')
        
        sections = []
        current_section = []
        
        for line in lines:
            if re.match(heading_pattern, line):
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)
        
        if current_section:
            sections.append('\n'.join(current_section))
        
        # If we got sections, chunk them
        if len(sections) > 1:
            chunk_index = 0
            for section in sections:
                section_tokens = self.count_tokens(section)
                
                # Section fits in one chunk
                if section_tokens <= self.config['chunk_target']:
                    chunks.append({
                        'chunk_hash': self.compute_hash(section),
                        'card_hash': card_hash,
                        'chunk_index': chunk_index,
                        'chunk_text': section,
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
        else:
            # No headings found, use sliding window
            sub_chunks = self._sliding_window_split(normalized_text)
            for idx, sub_chunk in enumerate(sub_chunks):
                sub_tokens = self.count_tokens(sub_chunk)
                chunks.append({
                    'chunk_hash': self.compute_hash(sub_chunk),
                    'card_hash': card_hash,
                    'chunk_index': idx,
                    'chunk_text': sub_chunk,
                    'token_count': sub_tokens
                })
        
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
                input=text,
                model=self.config['embed_model']
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    def process_missing_cards(self):
        """Find and process cards with no chunks"""
        logger.info("=" * 60)
        logger.info("FINDING MISSING CARDS")
        logger.info("=" * 60)
        
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Find canonical cards with no chunks
        query = """
            SELECT 
                cc.card_hash,
                cc.canonical_model_id,
                mc.card_text,
                mc.token_count
            FROM hf.card_canon cc
            LEFT JOIN hf.model_cards mc ON cc.canonical_model_id = mc.model_id
            WHERE NOT EXISTS (
                SELECT 1 FROM hf.card_chunks ch WHERE ch.card_hash = cc.card_hash
            )
            AND NOT COALESCE(mc.excluded_from_rag, false)
            ORDER BY mc.token_count DESC
        """
        
        cursor.execute(query)
        missing_cards = cursor.fetchall()
        
        self.stats['missing_cards_found'] = len(missing_cards)
        logger.info(f"Found {len(missing_cards)} cards without chunks")
        
        if len(missing_cards) == 0:
            logger.info("No missing cards to process!")
            return
        
        # Process each missing card
        logger.info("=" * 60)
        logger.info("CHUNKING MISSING CARDS")
        logger.info("=" * 60)
        
        all_chunks = []
        
        for idx, card in enumerate(missing_cards, 1):
            logger.info(f"Processing {idx}/{len(missing_cards)}: {card['canonical_model_id']} ({card['token_count']} tokens)")
            
            try:
                chunks = self.chunk_text(
                    card['card_text'],
                    card['card_hash'],
                    card['token_count']
                )
                
                logger.info(f"  → Generated {len(chunks)} chunks")
                all_chunks.extend(chunks)
                self.stats['cards_processed'] += 1
                self.stats['chunks_generated'] += len(chunks)
                
            except Exception as e:
                logger.error(f"  → Failed to chunk: {e}")
                self.failures.append({
                    'card_hash': card['card_hash'],
                    'model_id': card['canonical_model_id'],
                    'error': str(e),
                    'step': 'chunking'
                })
                self.stats['failures'] += 1
        
        logger.info(f"Generated {len(all_chunks)} total chunks from {self.stats['cards_processed']} cards")
        
        # Insert chunks
        logger.info("=" * 60)
        logger.info("INSERTING CHUNKS")
        logger.info("=" * 60)
        
        cursor = self.conn.cursor()
        
        insert_query = """
            INSERT INTO hf.card_chunks (
                chunk_hash, card_hash, chunk_index, chunk_text, 
                token_count, embedding_model_name, chunker_version
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (chunker_version, embedding_model_name, chunk_hash) 
            DO NOTHING
        """
        
        inserted = 0
        for chunk in all_chunks:
            try:
                cursor.execute(insert_query, (
                    chunk['chunk_hash'],
                    chunk['card_hash'],
                    chunk['chunk_index'],
                    chunk['chunk_text'],
                    chunk['token_count'],
                    self.config['embed_model'],
                    self.config['chunker_version']
                ))
                if cursor.rowcount > 0:
                    inserted += 1
            except Exception as e:
                logger.error(f"Failed to insert chunk: {e}")
        
        self.conn.commit()
        self.stats['chunks_inserted'] = inserted
        logger.info(f"Inserted {inserted} new chunks (duplicates automatically skipped)")
        
        # Embed new chunks
        self.embed_new_chunks()
    
    def embed_new_chunks(self):
        """Generate embeddings for chunks without embeddings"""
        logger.info("=" * 60)
        logger.info("EMBEDDING NEW CHUNKS")
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
            logger.info("No chunks to embed!")
            return
        
        embedded_count = 0
        
        for chunk in chunks_to_embed:
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
                    self.conn.commit()
                
                # Small delay to respect rate limits
                time.sleep(0.05)
                
            except Exception as e:
                logger.error(f"Failed to embed chunk {chunk['id']}: {e}")
                self.failures.append({
                    'chunk_id': chunk['id'],
                    'error': str(e),
                    'step': 'embedding'
                })
        
        self.conn.commit()
        self.stats['chunks_embedded'] = embedded_count
        logger.info(f"Embedding complete: {embedded_count}/{total_chunks} chunks embedded")
    
    def generate_report(self):
        """Generate summary report"""
        logger.info("=" * 60)
        logger.info("SUMMARY REPORT")
        logger.info("=" * 60)
        
        logger.info(f"Missing cards found:    {self.stats['missing_cards_found']}")
        logger.info(f"Cards processed:        {self.stats['cards_processed']}")
        logger.info(f"Chunks generated:       {self.stats['chunks_generated']}")
        logger.info(f"Chunks inserted:        {self.stats['chunks_inserted']}")
        logger.info(f"Chunks embedded:        {self.stats['chunks_embedded']}")
        logger.info(f"Failures:               {self.stats['failures']}")
        
        if self.failures:
            logger.info("\nFailures:")
            for failure in self.failures[:10]:
                logger.info(f"  - {failure}")
    
    def run(self):
        """Execute the missing cards processing"""
        start_time = time.time()
        
        try:
            logger.info("=" * 60)
            logger.info("MISSING CARDS PROCESSOR - START")
            logger.info("=" * 60)
            
            self.connect_db()
            self.init_openai()
            
            self.process_missing_cards()
            self.generate_report()
            
            elapsed = time.time() - start_time
            logger.info("=" * 60)
            logger.info(f"PROCESSING COMPLETE - Elapsed: {elapsed:.2f}s")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise
        finally:
            self.close_db()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Process missing HF canonical cards')
    parser.add_argument('--env-file', default='.env.local', help='Path to environment file')
    args = parser.parse_args()
    
    # Load environment
    if not os.path.exists(args.env_file):
        logger.error(f"Environment file not found: {args.env_file}")
        sys.exit(1)
    
    load_dotenv(args.env_file)
    
    # Build config
    config = {
        'db_url': os.getenv('SUPABASE_DB_URL'),
        'openai_key': os.getenv('OPENAI_API_KEY'),
        'embed_model': os.getenv('OPENAI_EMBED_MODEL', 'text-embedding-3-small'),
        'chunker_version': os.getenv('CHUNKER_VERSION', 'hf_chunker_v1'),
        'chunk_target': int(os.getenv('CHUNK_TARGET_TOKENS', '900')),
        'chunk_overlap': int(os.getenv('CHUNK_OVERLAP_TOKENS', '120')),
        'tokenizer': 'cl100k_base'
    }
    
    # Validate required config
    if not config['db_url']:
        logger.error("SUPABASE_DB_URL not set in environment")
        sys.exit(1)
    
    if not config['openai_key']:
        logger.error("OPENAI_API_KEY not set in environment")
        sys.exit(1)
    
    # Run processor
    processor = MissingCardsProcessor(config)
    processor.run()


if __name__ == '__main__':
    main()


