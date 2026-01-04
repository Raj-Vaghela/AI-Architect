#!/usr/bin/env python3
"""
Hugging Face Model Ingestion Script

This script fetches the top N models for each Hugging Face task and ingests them
into the Supabase database under the 'hf' schema.

Features:
- Idempotent: Safe to rerun multiple times
- Rate limit handling: Exponential backoff with retries
- Conservative concurrency: Controlled request rate
- Deduplication: Models appearing in multiple tasks are stored once
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

import psycopg2
import psycopg2.extras
import requests
from dotenv import load_dotenv
from huggingface_hub import HfApi, list_models
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
        logging.FileHandler('hf_ingestion.log')
    ]
)
logger = logging.getLogger(__name__)


class HFIngestionError(Exception):
    """Base exception for ingestion errors"""
    pass


class RateLimitError(Exception):
    """Exception for rate limit errors"""
    pass


class HFModelIngester:
    """Handles ingestion of Hugging Face models into Supabase"""
    
    def __init__(self, db_url: str, hf_token: Optional[str] = None):
        """
        Initialize the ingester
        
        Args:
            db_url: PostgreSQL connection string
            hf_token: Hugging Face API token (optional but recommended)
        """
        self.db_url = db_url
        self.hf_token = hf_token
        self.hf_api = HfApi(token=hf_token)
        self.conn = None
        self.session = requests.Session()
        
        # Rate limiting
        self.request_delay = 0.5  # 500ms between requests (conservative)
        self.last_request_time = 0
        
    def connect_db(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.db_url)
            self.conn.autocommit = False
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise HFIngestionError(f"Database connection failed: {e}")
    
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
    
    @retry(
        retry=retry_if_exception_type((RateLimitError, requests.exceptions.RequestException)),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5),
        reraise=True
    )
    def _fetch_with_retry(self, url: str) -> Dict:
        """
        Fetch data from URL with retry logic
        
        Args:
            url: URL to fetch
            
        Returns:
            JSON response as dict
        """
        self._rate_limit_wait()
        
        headers = {}
        if self.hf_token:
            headers['Authorization'] = f'Bearer {self.hf_token}'
        
        response = self.session.get(url, headers=headers, timeout=30)
        
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            raise RateLimitError("Rate limit exceeded")
        
        response.raise_for_status()
        return response.json()
    
    def fetch_tasks(self) -> List[Dict]:
        """
        Fetch all available tasks from Hugging Face
        
        Returns:
            List of task dictionaries
        """
        logger.info("Fetching tasks from Hugging Face API...")
        try:
            tasks_data = self._fetch_with_retry("https://huggingface.co/api/tasks")
            
            # Parse tasks - the API returns a dict with task IDs as keys
            tasks = []
            if isinstance(tasks_data, dict):
                for task_id, task_info in tasks_data.items():
                    task_label = task_info.get('label', task_info.get('name', task_id))
                    tasks.append({
                        'task_id': task_id,
                        'task_label': task_label
                    })
            
            logger.info(f"Found {len(tasks)} tasks")
            return tasks
        except Exception as e:
            logger.error(f"Failed to fetch tasks: {e}")
            raise HFIngestionError(f"Task fetch failed: {e}")
    
    def upsert_tasks(self, tasks: List[Dict]) -> int:
        """
        Upsert tasks into hf.tasks table
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            Number of tasks upserted
        """
        if not tasks:
            return 0
        
        logger.info(f"Upserting {len(tasks)} tasks...")
        
        try:
            cursor = self.conn.cursor()
            
            # Use ON CONFLICT to make it idempotent
            upsert_query = """
                INSERT INTO hf.tasks (task_id, task_label, created_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (task_id) 
                DO UPDATE SET 
                    task_label = EXCLUDED.task_label
            """
            
            for task in tasks:
                cursor.execute(upsert_query, (
                    task['task_id'],
                    task['task_label']
                ))
            
            self.conn.commit()
            logger.info(f"Successfully upserted {len(tasks)} tasks")
            return len(tasks)
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to upsert tasks: {e}")
            raise HFIngestionError(f"Task upsert failed: {e}")
    
    @retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5),
        reraise=True
    )
    def fetch_models_for_task(
        self, 
        task_id: str, 
        limit: int = 1000
    ) -> List[Dict]:
        """
        Fetch top models for a specific task
        
        Args:
            task_id: Task identifier
            limit: Maximum number of models to fetch
            
        Returns:
            List of model dictionaries
        """
        logger.info(f"Fetching top {limit} models for task: {task_id}")
        
        try:
            self._rate_limit_wait()
            
            # Use huggingface_hub to list models
            # Sort by downloads (primary), then likes (secondary)
            models = list(list_models(
                filter=task_id,
                sort="downloads",
                direction=-1,
                limit=limit,
                token=self.hf_token
            ))
            
            model_data = []
            for idx, model in enumerate(models, 1):
                try:
                    # Extract model information
                    model_info = {
                        'model_id': model.id,
                        'license': getattr(model, 'license', None),
                        'likes': getattr(model, 'likes', 0),
                        'downloads': getattr(model, 'downloads', 0),
                        'last_modified': getattr(model, 'last_modified', None),
                        'tags': list(getattr(model, 'tags', [])),
                        'pipeline_tag': getattr(model, 'pipeline_tag', None),
                        'task_id': task_id,
                        'rank_in_task': idx
                    }
                    model_data.append(model_info)
                    
                except Exception as e:
                    logger.warning(f"Error processing model {model.id}: {e}")
                    continue
            
            logger.info(f"Fetched {len(model_data)} models for task {task_id}")
            return model_data
            
        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                logger.warning(f"Rate limit hit for task {task_id}")
                raise RateLimitError(f"Rate limit for task {task_id}")
            logger.error(f"Failed to fetch models for task {task_id}: {e}")
            return []  # Return empty list on non-rate-limit errors
    
    def upsert_models(self, models: List[Dict]) -> Tuple[int, int]:
        """
        Upsert models into hf.models table
        
        Args:
            models: List of model dictionaries
            
        Returns:
            Tuple of (inserted_count, updated_count)
        """
        if not models:
            return 0, 0
        
        # Deduplicate by model_id (keep first occurrence)
        seen = set()
        unique_models = []
        for model in models:
            if model['model_id'] not in seen:
                seen.add(model['model_id'])
                unique_models.append(model)
        
        logger.info(f"Upserting {len(unique_models)} unique models (deduplicated from {len(models)})...")
        
        try:
            cursor = self.conn.cursor()
            
            # Upsert query - update if model exists
            upsert_query = """
                INSERT INTO hf.models (
                    model_id, license, likes, downloads, 
                    last_modified, tags, pipeline_tag, 
                    created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (model_id) 
                DO UPDATE SET 
                    license = COALESCE(EXCLUDED.license, hf.models.license),
                    likes = COALESCE(EXCLUDED.likes, hf.models.likes),
                    downloads = COALESCE(EXCLUDED.downloads, hf.models.downloads),
                    last_modified = COALESCE(EXCLUDED.last_modified, hf.models.last_modified),
                    tags = COALESCE(EXCLUDED.tags, hf.models.tags),
                    pipeline_tag = COALESCE(EXCLUDED.pipeline_tag, hf.models.pipeline_tag),
                    updated_at = NOW()
            """
            
            for model in unique_models:
                cursor.execute(upsert_query, (
                    model['model_id'],
                    model['license'],
                    model['likes'],
                    model['downloads'],
                    model['last_modified'],
                    json.dumps(model['tags']) if model['tags'] else None,
                    model['pipeline_tag']
                ))
            
            self.conn.commit()
            logger.info(f"Successfully upserted {len(unique_models)} models")
            return len(unique_models), 0
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to upsert models: {e}")
            raise HFIngestionError(f"Model upsert failed: {e}")
    
    def upsert_model_tasks(self, models: List[Dict]) -> int:
        """
        Upsert model-task mappings into hf.model_tasks table
        
        Args:
            models: List of model dictionaries with task_id and rank_in_task
            
        Returns:
            Number of mappings upserted
        """
        if not models:
            return 0
        
        logger.info(f"Upserting {len(models)} model-task mappings...")
        
        try:
            cursor = self.conn.cursor()
            
            # Upsert query for mappings
            upsert_query = """
                INSERT INTO hf.model_tasks (
                    model_id, task_id, rank_in_task, created_at
                )
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (model_id, task_id) 
                DO UPDATE SET 
                    rank_in_task = EXCLUDED.rank_in_task
            """
            
            for model in models:
                cursor.execute(upsert_query, (
                    model['model_id'],
                    model['task_id'],
                    model['rank_in_task']
                ))
            
            self.conn.commit()
            logger.info(f"Successfully upserted {len(models)} model-task mappings")
            return len(models)
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to upsert model-task mappings: {e}")
            raise HFIngestionError(f"Model-task mapping upsert failed: {e}")
    
    def ingest_all(
        self, 
        limit_per_task: int = 1000, 
        max_tasks: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Main ingestion workflow
        
        Args:
            limit_per_task: Number of models to fetch per task
            max_tasks: Maximum number of tasks to process (for testing)
            
        Returns:
            Dictionary with ingestion statistics
        """
        stats = {
            'tasks_fetched': 0,
            'tasks_processed': 0,
            'models_fetched': 0,
            'models_upserted': 0,
            'mappings_upserted': 0,
            'errors': 0
        }
        
        start_time = time.time()
        
        try:
            # Connect to database
            self.connect_db()
            
            # Fetch and upsert tasks
            tasks = self.fetch_tasks()
            stats['tasks_fetched'] = len(tasks)
            self.upsert_tasks(tasks)
            
            # Limit tasks for testing
            if max_tasks:
                tasks = tasks[:max_tasks]
                logger.info(f"Limited to {max_tasks} tasks for testing")
            
            # Process each task
            all_models = []
            for idx, task in enumerate(tasks, 1):
                task_id = task['task_id']
                logger.info(f"Processing task {idx}/{len(tasks)}: {task_id}")
                
                try:
                    # Fetch models for this task
                    models = self.fetch_models_for_task(task_id, limit_per_task)
                    
                    if models:
                        stats['models_fetched'] += len(models)
                        all_models.extend(models)
                        stats['tasks_processed'] += 1
                    else:
                        logger.warning(f"No models found for task {task_id}")
                    
                    # Small delay between tasks
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing task {task_id}: {e}")
                    stats['errors'] += 1
                    continue
            
            # Upsert all models (with deduplication)
            if all_models:
                models_count, _ = self.upsert_models(all_models)
                stats['models_upserted'] = models_count
                
                # Upsert model-task mappings
                mappings_count = self.upsert_model_tasks(all_models)
                stats['mappings_upserted'] = mappings_count
            
            elapsed_time = time.time() - start_time
            logger.info(f"Ingestion completed in {elapsed_time:.2f} seconds")
            logger.info(f"Statistics: {json.dumps(stats, indent=2)}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            raise
        finally:
            self.close_db()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Ingest Hugging Face models into Supabase',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--limit-per-task',
        type=int,
        default=1000,
        help='Number of models to fetch per task (default: 1000)'
    )
    
    parser.add_argument(
        '--max-tasks',
        type=int,
        default=None,
        help='Maximum number of tasks to process (for testing)'
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
    
    # Run ingestion
    try:
        ingester = HFModelIngester(db_url, hf_token)
        stats = ingester.ingest_all(
            limit_per_task=args.limit_per_task,
            max_tasks=args.max_tasks
        )
        
        logger.info("=" * 60)
        logger.info("INGESTION COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"Tasks fetched: {stats['tasks_fetched']}")
        logger.info(f"Tasks processed: {stats['tasks_processed']}")
        logger.info(f"Models fetched: {stats['models_fetched']}")
        logger.info(f"Unique models upserted: {stats['models_upserted']}")
        logger.info(f"Model-task mappings: {stats['mappings_upserted']}")
        logger.info(f"Errors: {stats['errors']}")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

