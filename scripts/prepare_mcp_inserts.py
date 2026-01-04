#!/usr/bin/env python3
"""
Prepare model card inserts for MCP execution
Outputs JSON that can be used to generate SQL
"""

import json

with open('model_cards_test_results.json', encoding='utf-8') as f:
    data = json.load(f)

# For MCP, we'll insert in very small batches
# Let's prepare first 10 as a demonstration
print("First 10 model cards for MCP insertion:\n")

for i, r in enumerate(data['results'][:10], 1):
    model_id = r['model_id']
    card_hash = r['card_hash']
    token_count = r['token_count']
    card_preview = r['card_text'][:200].replace('\n', ' ').replace('\r', '')
    
    print(f"{i}. {model_id}")
    print(f"   Hash: {card_hash}")
    print(f"   Tokens: {token_count}")
    print(f"   Preview: {card_preview}...")
    print()

# Save full data for programmatic insertion
output = {
    'total': len(data['results']),
    'cards': [
        {
            'model_id': r['model_id'],
            'card_text': r['card_text'],
            'card_hash': r['card_hash'],
            'token_count': r['token_count'],
            'tokenizer_name': 'tiktoken:cl100k_base'
        }
        for r in data['results']
    ]
}

with open('model_cards_for_db.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Full data saved to model_cards_for_db.json ({len(output['cards'])} cards)")

