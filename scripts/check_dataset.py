"""Quick script to check dataset quality."""
import json
import random

with open('data/nl2sql_train_chat_raw.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total examples: {len(lines)}\n")
print("=== Sample Training Examples ===\n")

random.seed(42)
samples = random.sample(range(len(lines)), 5)

for idx, i in enumerate(samples, 1):
    ex = json.loads(lines[i])
    nl = ex["messages"][1]["content"]
    sql = ex["messages"][2]["content"]
    print(f"Example {idx}:")
    print(f"Q: {nl}")
    print(f"SQL: {sql}")
    print()
