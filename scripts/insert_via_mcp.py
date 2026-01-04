#!/usr/bin/env python3
"""
Insert data into Supabase via direct SQL execution
This script reads the SQL files and prints SQL for manual execution via MCP
"""

def main():
    # Read all models SQL
    with open('all_models.sql', 'r', encoding='utf-8') as f:
        models_sql = f.read()
    
    # Read all mappings SQL
    with open('all_mappings.sql', 'r', encoding='utf-8') as f:
        mappings_sql = f.read()
    
    print("Models SQL length:", len(models_sql))
    print("Mappings SQL length:", len(mappings_sql))
    print("\nTo execute via Supabase MCP:")
    print("1. Execute all_models.sql")
    print("2. Execute all_mappings.sql")
    
    # Split into smaller batches (10 statements each)
    model_statements = [s.strip() for s in models_sql.split(';') if s.strip()]
    mapping_statements = [s.strip() for s in mappings_sql.split(';') if s.strip()]
    
    print(f"\nTotal model statements: {len(model_statements)}")
    print(f"Total mapping statements: {len(mapping_statements)}")
    
    # Create smaller batch files (10 statements per file)
    batch_size = 10
    for i in range(0, len(model_statements), batch_size):
        batch = model_statements[i:i+batch_size]
        with open(f'model_batch_{i//batch_size + 1}.sql', 'w', encoding='utf-8') as f:
            f.write(';\n'.join(batch) + ';')
    
    for i in range(0, len(mapping_statements), batch_size):
        batch = mapping_statements[i:i+batch_size]
        with open(f'mapping_batch_{i//batch_size + 1}.sql', 'w', encoding='utf-8') as f:
            f.write(';\n'.join(batch) + ';')
    
    print(f"\nCreated {(len(model_statements) + batch_size - 1) // batch_size} model batch files")
    print(f"Created {(len(mapping_statements) + batch_size - 1) // batch_size} mapping batch files")

if __name__ == '__main__':
    main()

