#!/usr/bin/env python3
"""
Load dry run data into Supabase database
This script generates SQL statements from the dry_run_data.json file
"""

import json
import sys

def escape_sql_string(s):
    """Escape string for SQL"""
    if s is None:
        return 'NULL'
    return "'" + str(s).replace("'", "''") + "'"

def main():
    # Load dry run data
    with open('dry_run_data.json', 'r') as f:
        data = json.load(f)
    
    tasks = data['tasks']
    models = data['models']
    
    print("-- Insert tasks")
    for task in tasks:
        task_id = escape_sql_string(task['task_id'])
        task_label = escape_sql_string(task['task_label'])
        print(f"INSERT INTO hf.tasks (task_id, task_label) VALUES ({task_id}, {task_label}) ON CONFLICT (task_id) DO NOTHING;")
    
    print("\n-- Insert models")
    for model in models:
        model_id = escape_sql_string(model['model_id'])
        license_val = escape_sql_string(model['license'])
        likes = model['likes'] if model['likes'] else 'NULL'
        downloads = model['downloads'] if model['downloads'] else 'NULL'
        last_modified = 'NULL' if model['last_modified'] == 'None' else escape_sql_string(model['last_modified'])
        tags = escape_sql_string(json.dumps(model['tags'])) if model['tags'] else 'NULL'
        pipeline_tag = escape_sql_string(model['pipeline_tag'])
        
        print(f"INSERT INTO hf.models (model_id, license, likes, downloads, last_modified, tags, pipeline_tag) VALUES ({model_id}, {license_val}, {likes}, {downloads}, {last_modified}, {tags}::jsonb, {pipeline_tag}) ON CONFLICT (model_id) DO UPDATE SET likes = EXCLUDED.likes, downloads = EXCLUDED.downloads, updated_at = NOW();")
    
    print("\n-- Insert model-task mappings")
    for model in models:
        model_id = escape_sql_string(model['model_id'])
        task_id = escape_sql_string(model['task_id'])
        rank = model['rank_in_task']
        print(f"INSERT INTO hf.model_tasks (model_id, task_id, rank_in_task) VALUES ({model_id}, {task_id}, {rank}) ON CONFLICT (model_id, task_id) DO UPDATE SET rank_in_task = EXCLUDED.rank_in_task;")

if __name__ == '__main__':
    main()

