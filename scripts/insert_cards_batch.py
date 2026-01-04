#!/usr/bin/env python3
"""
Insert model cards into database in small batches
Outputs SQL for MCP execution
"""

import json

def escape_sql(s):
    if s is None:
        return 'NULL'
    # Escape single quotes and backslashes
    return "'" + str(s).replace("\\", "\\\\").replace("'", "''") + "'"

with open('model_cards_test_results.json') as f:
    data = json.load(f)

# Insert in batches of 5 to avoid SQL length issues
batch_size = 5
results = data['results']

for i in range(0, len(results), batch_size):
    batch = results[i:i+batch_size]
    
    print(f"\n-- Batch {i//batch_size + 1}: Models {i+1} to {min(i+batch_size, len(results))}")
    print("INSERT INTO hf.model_cards (model_id, card_text, card_hash, token_count, tokenizer_name) VALUES")
    
    values = []
    for r in batch:
        model_id = escape_sql(r['model_id'])
        card_text = escape_sql(r['card_text'])
        card_hash = escape_sql(r['card_hash'])
        token_count = r['token_count']
        tokenizer_name = escape_sql('tiktoken:cl100k_base')
        
        values.append(f"({model_id}, {card_text}, {card_hash}, {token_count}, {tokenizer_name})")
    
    print(',\n'.join(values))
    print("ON CONFLICT (model_id) DO NOTHING;")
    print()

print(f"-- Total: {len(results)} model cards to insert")

