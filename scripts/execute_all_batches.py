#!/usr/bin/env python3
"""
Execute all batch SQL files
This outputs the SQL in a format ready for MCP execution
"""

import glob

def main():
    # Get all batch files
    model_files = sorted(glob.glob('batch_models_*.sql'))
    mapping_files = sorted(glob.glob('batch_mappings_*.sql'))
    
    print("-- Execute all model batches")
    for f in model_files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            print(f"\n-- Batch: {f}")
            print(content)
    
    print("\n\n-- Execute all mapping batches")
    for f in mapping_files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            print(f"\n-- Batch: {f}")
            print(content)

if __name__ == '__main__':
    main()

