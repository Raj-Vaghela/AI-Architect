import json
import statistics

with open('model_cards_test_results.json') as f:
    data = json.load(f)

print(f"Total: {data['stats']['total']}")
print(f"Successful: {data['stats']['successful']}")
print(f"Failed: {data['stats']['failed']}")

tokens = [r['token_count'] for r in data['results']]
tokens_sorted = sorted(tokens)

print(f"\nToken count statistics:")
print(f"  Min: {min(tokens)}")
print(f"  Median: {tokens_sorted[len(tokens)//2]}")
print(f"  P95: {tokens_sorted[int(len(tokens)*0.95)]}")
print(f"  Max: {max(tokens)}")
print(f"  Mean: {statistics.mean(tokens):.0f}")

print(f"\nTop 10 by token count:")
results_sorted = sorted(data['results'], key=lambda x: x['token_count'], reverse=True)
for r in results_sorted[:10]:
    print(f"  {r['model_id']}: {r['token_count']} tokens")

print(f"\nFailures: {len(data['failures'])}")
for f in data['failures'][:20]:
    print(f"  - {f['model_id']}: {f['reason']}")

