"""Show NL variants for the same SQL."""
import json
from collections import defaultdict

with open('data/nl2sql_train_chat_raw.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Group by SQL
sql_to_nls = defaultdict(list)
for line in lines:
    ex = json.loads(line)
    sql = ex["messages"][2]["content"]
    nl = ex["messages"][1]["content"]
    sql_to_nls[sql].append(nl)

# Find SQLs with multiple NL variants
multi_variant_sqls = [(sql, nls) for sql, nls in sql_to_nls.items() if len(nls) > 1]

print("Examples of NL Paraphrasing (same SQL, different questions):")
print("=" * 70)

for i, (sql, nls) in enumerate(multi_variant_sqls[:3], 1):
    print(f"\n{i}. SQL: {sql[:80]}...")
    print(f"   NL Variants:")
    for nl in nls:
        print(f"   • {nl}")

print(f"\n✅ {len(multi_variant_sqls)} SQLs have multiple NL variants")
print(f"📊 This increases dataset robustness and helps the model generalize!")
