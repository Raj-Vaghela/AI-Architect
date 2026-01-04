#!/usr/bin/env python3
"""
Simple script to output model card data for manual SQL insertion
"""

import json
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

with open('model_cards_test_results.json', encoding='utf-8') as f:
    data = json.load(f)

print("Model cards ready for insertion:")
print(f"Total: {len(data['results'])}")
print(f"Successful: {data['stats']['successful']}")
print(f"Failed: {data['stats']['failed']}")

# Save a simpler version for SQL generation
simple_data = []
for r in data['results']:
    simple_data.append({
        'model_id': r['model_id'],
        'card_hash': r['card_hash'],
        'token_count': r['token_count'],
        'card_length': len(r['card_text'])
    })

with open('model_cards_simple.json', 'w', encoding='utf-8') as f:
    json.dump(simple_data, f, indent=2, ensure_ascii=False)

print("\nSimple data saved to model_cards_simple.json")
print("\nSample (first 5):")
for item in simple_data[:5]:
    print(f"  {item['model_id']}: {item['token_count']} tokens, {item['card_length']} chars")

