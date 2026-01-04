#!/usr/bin/env python3
"""
Generate simplified SQL inserts for dry run data
"""

import json

def main():
    with open('dry_run_data.json', 'r') as f:
        data = json.load(f)
    
    models = data['models']
    
    print("-- Insert all models from dry run")
    print("INSERT INTO hf.models (model_id, likes, downloads, pipeline_tag) VALUES")
    
    values = []
    for m in models:
        model_id = m['model_id'].replace("'", "''")
        likes = m['likes'] if m['likes'] else 'NULL'
        downloads = m['downloads'] if m['downloads'] else 'NULL'
        pipeline_tag = f"'{m['pipeline_tag']}'" if m['pipeline_tag'] else 'NULL'
        values.append(f"('{model_id}', {likes}, {downloads}, {pipeline_tag})")
    
    print(',\n'.join(values))
    print("ON CONFLICT (model_id) DO UPDATE SET likes = EXCLUDED.likes, downloads = EXCLUDED.downloads, updated_at = NOW();")
    
    print("\n\n-- Insert all model-task mappings")
    print("INSERT INTO hf.model_tasks (model_id, task_id, rank_in_task) VALUES")
    
    values = []
    for m in models:
        model_id = m['model_id'].replace("'", "''")
        task_id = m['task_id'].replace("'", "''")
        rank = m['rank_in_task']
        values.append(f"('{model_id}', '{task_id}', {rank})")
    
    print(',\n'.join(values))
    print("ON CONFLICT (model_id, task_id) DO UPDATE SET rank_in_task = EXCLUDED.rank_in_task;")

if __name__ == '__main__':
    main()

