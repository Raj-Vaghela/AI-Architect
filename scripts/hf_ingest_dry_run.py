#!/usr/bin/env python3
"""
Hugging Face Model Ingestion - Dry Run Test Script

This is a simplified version for testing that outputs SQL statements
instead of executing them directly. Use this to verify the logic before
running the full ingestion.
"""

import json
import logging
import sys
import time
from typing import Dict, List

import requests
from huggingface_hub import HfApi, list_models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_tasks() -> List[Dict]:
    """Fetch all available tasks from Hugging Face"""
    logger.info("Fetching tasks from Hugging Face API...")
    
    response = requests.get("https://huggingface.co/api/tasks", timeout=30)
    response.raise_for_status()
    tasks_data = response.json()
    
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


def fetch_models_for_task(task_id: str, limit: int = 50) -> List[Dict]:
    """Fetch top models for a specific task"""
    logger.info(f"Fetching top {limit} models for task: {task_id}")
    
    try:
        time.sleep(0.5)  # Rate limiting
        
        models = list(list_models(
            filter=task_id,
            sort="downloads",
            direction=-1,
            limit=limit
        ))
        
        model_data = []
        for idx, model in enumerate(models, 1):
            try:
                model_info = {
                    'model_id': model.id,
                    'license': getattr(model, 'license', None),
                    'likes': getattr(model, 'likes', 0),
                    'downloads': getattr(model, 'downloads', 0),
                    'last_modified': str(getattr(model, 'last_modified', None)),
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
        logger.error(f"Failed to fetch models for task {task_id}: {e}")
        return []


def main():
    """Run dry run test"""
    logger.info("=" * 60)
    logger.info("STARTING DRY RUN TEST")
    logger.info("=" * 60)
    
    max_tasks = 2
    limit_per_task = 50
    
    try:
        # Fetch tasks
        tasks = fetch_tasks()
        logger.info(f"Will process {max_tasks} tasks (limited for testing)")
        
        # Process limited tasks
        all_models = []
        for idx, task in enumerate(tasks[:max_tasks], 1):
            task_id = task['task_id']
            logger.info(f"\nProcessing task {idx}/{max_tasks}: {task_id}")
            
            models = fetch_models_for_task(task_id, limit_per_task)
            if models:
                all_models.extend(models)
                logger.info(f"✓ Fetched {len(models)} models for {task_id}")
            else:
                logger.warning(f"✗ No models found for {task_id}")
            
            time.sleep(1)  # Delay between tasks
        
        # Statistics
        unique_models = len(set(m['model_id'] for m in all_models))
        
        logger.info("\n" + "=" * 60)
        logger.info("DRY RUN STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Tasks processed: {max_tasks}")
        logger.info(f"Total models fetched: {len(all_models)}")
        logger.info(f"Unique models: {unique_models}")
        logger.info(f"Model-task mappings: {len(all_models)}")
        
        # Show sample data
        logger.info("\n" + "=" * 60)
        logger.info("SAMPLE DATA (first 3 models)")
        logger.info("=" * 60)
        for model in all_models[:3]:
            logger.info(f"\nModel: {model['model_id']}")
            logger.info(f"  Task: {model['task_id']}")
            logger.info(f"  Rank: {model['rank_in_task']}")
            logger.info(f"  Downloads: {model['downloads']}")
            logger.info(f"  Likes: {model['likes']}")
        
        # Export data for manual inspection
        output_file = 'dry_run_data.json'
        with open(output_file, 'w') as f:
            json.dump({
                'tasks': tasks[:max_tasks],
                'models': all_models,
                'stats': {
                    'tasks_processed': max_tasks,
                    'total_models': len(all_models),
                    'unique_models': unique_models
                }
            }, f, indent=2)
        
        logger.info(f"\n✓ Data exported to {output_file}")
        logger.info("\n" + "=" * 60)
        logger.info("DRY RUN COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Dry run failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

