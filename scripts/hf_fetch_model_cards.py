#!/usr/bin/env python3
"""
Hugging Face Model Card Fetcher

Fetches README/model card text for models in hf.models and stores them
in hf.model_cards for later RAG applications.

Features:
- Idempotent: Uses PRIMARY KEY constraint to prevent duplicates
- Resume support: Can continue from a specific model_id
- Rate limiting: Conservative delays and exponential backoff
- Token counting: Uses tiktoken for accurate token counts
"""

import argparse
import hashlib
import logging
import os
import sys
import time
from typing import Dict, List, Optional, Tuple

import psycopg2
import psycopg2.extras
import tiktoken
from dotenv import load_dotenv
from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.utils import RepositoryNotFoundError, EntryNotFoundError
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
        logging.FileHandler('hf_model_cards.log')
    ]
)
logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Exception for rate limit errors"""
    pass


class ModelCardFetcher:
    """Handles fetching and storing Hugging Face model cards"""
    
    def __init__(self, db_url: str, hf_token: Optional[str] = None):
        """
        Initialize the fetcher
        
        Args:
            db_url: PostgreSQL connection string
            hf_token: Hugging Face API token (optional but recommended)
        """
        self.db_url = db_url
        self.hf_token = hf_token
        self.hf_api = HfApi(token=hf_token)
        self.conn = None
        
        # Initialize tiktoken encoder
        self.tokenizer_name = "tiktoken:cl100k_base"
        try:
            self.encoder = tiktoken.get_encoding("cl100k_base")
            logger.info(f"Initialized tokenizer: {self.tokenizer_name}")
        except Exception as e:
            logger.error(f"Failed to initialize tiktoken: {e}")
            raise
        
        # Rate limiting
        self.request_delay = 0.5  # 500ms between requests
        self.last_request_time = 0
        
        # Track failures
        self.failures = []
        
    def connect_db(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.db_url)
            self.conn.autocommit = False
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def _rate_limit_wait(self):
        """Implement conservative rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()
    
    def get_models_without_cards(
        self, 
        batch_size: int = 100,
        start_after: Optional[str] = None,
        max_models: Optional[int] = None
    ) -> List[str]:
        """
        Get list of model IDs that don't have model cards yet
        
        Args:
            batch_size: Number of models to fetch
            start_after: Resume after this model_id
            max_models: Maximum number of models to process
            
        Returns:
            List of model IDs
        """
        try:
            cursor = self.conn.cursor()
            
            # Query for models without cards
            if start_after:
                query = """
                    SELECT m.model_id
                    FROM hf.models m
                    LEFT JOIN hf.model_cards mc ON m.model_id = mc.model_id
                    WHERE mc.model_id IS NULL
                    AND m.model_id > %s
                    ORDER BY m.model_id
                    LIMIT %s
                """
                cursor.execute(query, (start_after, batch_size))
            else:
                query = """
                    SELECT m.model_id
                    FROM hf.models m
                    LEFT JOIN hf.model_cards mc ON m.model_id = mc.model_id
                    WHERE mc.model_id IS NULL
                    ORDER BY m.model_id
                    LIMIT %s
                """
                cursor.execute(query, (batch_size,))
            
            models = [row[0] for row in cursor.fetchall()]
            
            # Apply max_models limit if specified
            if max_models and len(models) > max_models:
                models = models[:max_models]
            
            logger.info(f"Found {len(models)} models without cards")
            return models
            
        except Exception as e:
            logger.error(f"Failed to query models: {e}")
            raise
    
    @retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5),
        reraise=True
    )
    def fetch_model_card(self, model_id: str) -> str:
        """
        Fetch model card/README text from Hugging Face
        
        Args:
            model_id: Model identifier
            
        Returns:
            Model card text (or fallback message)
        """
        self._rate_limit_wait()
        
        logger.info(f"Fetching model card for: {model_id}")
        
        try:
            # Try to fetch README.md using file resolver
            readme_path = hf_hub_download(
                repo_id=model_id,
                filename="README.md",
                repo_type="model",
                token=self.hf_token
            )
            
            # Read the file
            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                card_text = f.read()
            
            if not card_text or len(card_text.strip()) == 0:
                logger.warning(f"Empty README for {model_id}")
                return "No model card found."
            
            logger.info(f"Successfully fetched card for {model_id} ({len(card_text)} chars)")
            return card_text
            
        except EntryNotFoundError:
            logger.warning(f"No README.md found for {model_id}")
            return "No model card found."
            
        except RepositoryNotFoundError:
            logger.warning(f"Repository not found: {model_id}")
            return "No model card found."
            
        except Exception as e:
            # Check if it's a rate limit error
            if "429" in str(e) or "rate limit" in str(e).lower():
                logger.warning(f"Rate limit hit for {model_id}")
                raise RateLimitError(f"Rate limit for {model_id}")
            
            logger.error(f"Error fetching card for {model_id}: {e}")
            return "No model card found."
    
    def compute_hash(self, text: str) -> str:
        """
        Compute SHA256 hash of text
        
        Args:
            text: Text to hash
            
        Returns:
            Hex digest of SHA256 hash
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken
        
        Args:
            text: Text to tokenize
            
        Returns:
            Number of tokens
        """
        try:
            tokens = self.encoder.encode(text)
            return len(tokens)
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Fallback: approximate by splitting on whitespace
            return len(text.split())
    
    def store_model_card(
        self,
        model_id: str,
        card_text: str,
        card_hash: str,
        token_count: int
    ) -> bool:
        """
        Store model card in database
        
        Args:
            model_id: Model identifier
            card_text: Model card text
            card_hash: SHA256 hash of card text
            token_count: Number of tokens
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            
            # Insert model card (PK constraint prevents duplicates)
            insert_query = """
                INSERT INTO hf.model_cards (
                    model_id, card_text, card_hash, token_count, 
                    tokenizer_name, fetched_at
                )
                VALUES (%s, %s, %s, %s, %s, NOW())
                ON CONFLICT (model_id) DO NOTHING
            """
            
            cursor.execute(insert_query, (
                model_id,
                card_text,
                card_hash,
                token_count,
                self.tokenizer_name
            ))
            
            self.conn.commit()
            logger.info(f"Stored model card for {model_id} ({token_count} tokens)")
            return True
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to store card for {model_id}: {e}")
            self.failures.append({
                'model_id': model_id,
                'reason': str(e),
                'type': 'database_error'
            })
            return False
    
    def process_model(self, model_id: str) -> bool:
        """
        Process a single model: fetch card, compute stats, store
        
        Args:
            model_id: Model identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Fetch model card
            card_text = self.fetch_model_card(model_id)
            
            # Compute hash
            card_hash = self.compute_hash(card_text)
            
            # Count tokens
            token_count = self.count_tokens(card_text)
            
            # Store in database
            success = self.store_model_card(
                model_id, card_text, card_hash, token_count
            )
            
            return success
            
        except RateLimitError:
            # Re-raise rate limit errors for retry
            raise
        except Exception as e:
            logger.error(f"Error processing {model_id}: {e}")
            self.failures.append({
                'model_id': model_id,
                'reason': str(e),
                'type': 'processing_error'
            })
            return False
    
    def fetch_batch(
        self,
        batch_size: int = 100,
        max_models: Optional[int] = None,
        start_after: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Fetch model cards for a batch of models
        
        Args:
            batch_size: Number of models to fetch per batch
            max_models: Maximum total models to process
            start_after: Resume after this model_id
            
        Returns:
            Statistics dictionary
        """
        stats = {
            'total_attempted': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }
        
        start_time = time.time()
        
        try:
            # Connect to database
            self.connect_db()
            
            # Get models without cards
            models = self.get_models_without_cards(
                batch_size=batch_size if not max_models else max_models,
                start_after=start_after,
                max_models=max_models
            )
            
            if not models:
                logger.info("No models to process")
                return stats
            
            # Process each model
            for idx, model_id in enumerate(models, 1):
                logger.info(f"Processing {idx}/{len(models)}: {model_id}")
                
                try:
                    success = self.process_model(model_id)
                    stats['total_attempted'] += 1
                    
                    if success:
                        stats['successful'] += 1
                    else:
                        stats['failed'] += 1
                    
                    # Small delay between models
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error processing {model_id}: {e}")
                    stats['failed'] += 1
                    stats['total_attempted'] += 1
                    continue
            
            elapsed_time = time.time() - start_time
            logger.info(f"Batch completed in {elapsed_time:.2f} seconds")
            logger.info(f"Statistics: {stats}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Batch fetch failed: {e}")
            raise
        finally:
            self.close_db()
    
    def get_failures(self) -> List[Dict]:
        """Get list of failures"""
        return self.failures


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Fetch Hugging Face model cards',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Number of models to fetch per batch (default: 100)'
    )
    
    parser.add_argument(
        '--max-models',
        type=int,
        default=None,
        help='Maximum number of models to process (for testing)'
    )
    
    parser.add_argument(
        '--start-after',
        type=str,
        default=None,
        help='Resume after this model_id'
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    db_url = os.getenv('SUPABASE_DB_URL')
    hf_token = os.getenv('HF_TOKEN')
    
    if not db_url:
        logger.error("SUPABASE_DB_URL environment variable not set")
        sys.exit(1)
    
    if not hf_token:
        logger.warning("HF_TOKEN not set - rate limits may be more restrictive")
    
    # Run fetcher
    try:
        fetcher = ModelCardFetcher(db_url, hf_token)
        
        # Continuous processing mode (unless max_models is specified for testing)
        if args.max_models:
            # Test mode - single batch
            stats = fetcher.fetch_batch(
                batch_size=args.batch_size,
                max_models=args.max_models,
                start_after=args.start_after
            )
            
            logger.info("=" * 60)
            logger.info("FETCH COMPLETED (TEST MODE)")
            logger.info("=" * 60)
            logger.info(f"Total attempted: {stats['total_attempted']}")
            logger.info(f"Successful: {stats['successful']}")
            logger.info(f"Failed: {stats['failed']}")
        else:
            # Production mode - continuous batching until all models processed
            logger.info("=" * 60)
            logger.info("STARTING CONTINUOUS FETCH MODE")
            logger.info("=" * 60)
            
            total_stats = {
                'total_attempted': 0,
                'successful': 0,
                'failed': 0,
                'batches': 0
            }
            
            batch_num = 0
            while True:
                batch_num += 1
                logger.info(f"\n{'='*60}")
                logger.info(f"BATCH {batch_num}")
                logger.info(f"{'='*60}")
                
                stats = fetcher.fetch_batch(
                    batch_size=args.batch_size,
                    max_models=None,
                    start_after=args.start_after
                )
                
                # If no models were processed, we're done
                if stats['total_attempted'] == 0:
                    logger.info("No more models to process - all done!")
                    break
                
                # Update totals
                total_stats['total_attempted'] += stats['total_attempted']
                total_stats['successful'] += stats['successful']
                total_stats['failed'] += stats['failed']
                total_stats['batches'] += 1
                
                logger.info(f"Batch {batch_num} complete: {stats['successful']} successful, {stats['failed']} failed")
                logger.info(f"Overall progress: {total_stats['total_attempted']:,} models processed")
                
                # Small delay between batches to avoid hammering the API
                time.sleep(2)
            
            logger.info("\n" + "=" * 60)
            logger.info("ALL BATCHES COMPLETED")
            logger.info("=" * 60)
            logger.info(f"Total batches: {total_stats['batches']}")
            logger.info(f"Total attempted: {total_stats['total_attempted']:,}")
            logger.info(f"Successful: {total_stats['successful']:,}")
            logger.info(f"Failed: {total_stats['failed']:,}")
        
        # Show failures
        failures = fetcher.get_failures()
        if failures:
            logger.warning(f"\n{len(failures)} failures:")
            for fail in failures[:20]:  # Show first 20
                logger.warning(f"  - {fail['model_id']}: {fail['reason'][:100]}")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

