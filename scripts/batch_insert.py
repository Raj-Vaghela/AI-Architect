#!/usr/bin/env python3
"""
Batch the SQL inserts into smaller chunks for execution
"""

import sys

def main():
    with open('dry_run_insert.sql', 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    # Separate by section
    tasks = []
    models = []
    mappings = []
    
    current_section = None
    for line in lines:
        line = line.strip()
        if not line or line.startswith('--'):
            if 'Insert tasks' in line:
                current_section = 'tasks'
            elif 'Insert models' in line:
                current_section = 'models'
            elif 'Insert model-task' in line:
                current_section = 'mappings'
            continue
        
        if current_section == 'tasks':
            tasks.append(line)
        elif current_section == 'models':
            models.append(line)
        elif current_section == 'mappings':
            mappings.append(line)
    
    print(f"Tasks: {len(tasks)}")
    print(f"Models: {len(models)}")
    print(f"Mappings: {len(mappings)}")
    
    # Write batches
    batch_size = 20
    
    # Write models in batches
    for i in range(0, len(models), batch_size):
        batch = models[i:i+batch_size]
        with open(f'batch_models_{i//batch_size + 1}.sql', 'w', encoding='utf-8') as f:
            f.write('\n'.join(batch))
    
    # Write mappings in batches
    for i in range(0, len(mappings), batch_size):
        batch = mappings[i:i+batch_size]
        with open(f'batch_mappings_{i//batch_size + 1}.sql', 'w', encoding='utf-8') as f:
            f.write('\n'.join(batch))
    
    print(f"\nCreated {(len(models) + batch_size - 1) // batch_size} model batch files")
    print(f"Created {(len(mappings) + batch_size - 1) // batch_size} mapping batch files")

if __name__ == '__main__':
    main()

