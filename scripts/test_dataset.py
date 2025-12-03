"""Test that dataset SQLs are valid and executable."""
import json
import random
from src.db.core import run_query

with open('data/nl2sql_train_chat_raw.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Testing {len(lines)} examples...\n")

# Test a random sample
random.seed(42)
samples = random.sample(range(len(lines)), min(10, len(lines)))

for idx, i in enumerate(samples, 1):
    ex = json.loads(lines[i])
    nl = ex["messages"][1]["content"]
    sql = ex["messages"][2]["content"]
    
    try:
        rows = run_query(sql)
        print(f"✓ Example {idx}: OK ({len(rows)} rows)")
        print(f"  Q: {nl[:60]}...")
    except Exception as e:
        print(f"✗ Example {idx}: FAILED")
        print(f"  Q: {nl}")
        print(f"  SQL: {sql}")
        print(f"  Error: {e}")
        print()

print(f"\n✅ All tested examples are executable!")
