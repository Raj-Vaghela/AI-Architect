import json

def escape_sql(s):
    if s is None:
        return 'NULL'
    return "'" + str(s).replace("'", "''").replace("\\", "\\\\") + "'"

with open('model_cards_test_results.json') as f:
    data = json.load(f)

print("-- Insert model cards (batch of 50)")
print("INSERT INTO hf.model_cards (model_id, card_text, card_hash, token_count, tokenizer_name) VALUES")

values = []
for r in data['results']:
    model_id = escape_sql(r['model_id'])
    # Truncate card_text to first 5000 chars for SQL readability, but store full hash and token count
    card_text = escape_sql(r['card_text'][:5000] + ('...' if len(r['card_text']) > 5000 else ''))
    card_hash = escape_sql(r['card_hash'])
    token_count = r['token_count']
    tokenizer_name = escape_sql('tiktoken:cl100k_base')
    
    values.append(f"({model_id}, {card_text}, {card_hash}, {token_count}, {tokenizer_name})")

print(',\n'.join(values))
print("ON CONFLICT (model_id) DO NOTHING;")

print(f"\n-- Total: {len(values)} model cards")

