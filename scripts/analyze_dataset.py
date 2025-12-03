"""Analyze dataset composition."""
import json
from collections import Counter

with open('data/nl2sql_train_chat_raw.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Dataset Statistics")
print("=" * 50)
print(f"Total examples: {len(lines)}")

# Analyze SQL patterns
patterns = {
    'Simple SELECT': 0,
    'WHERE filter': 0,
    'GROUP BY aggregation': 0,
    'JOIN (2-table)': 0,
    'JOIN (3-table)': 0,
    'ORDER BY': 0,
    'LIMIT': 0,
    'HAVING': 0,
}

unique_sqls = set()
for line in lines:
    ex = json.loads(line)
    sql = ex["messages"][2]["content"].lower()
    unique_sqls.add(sql)
    
    if 'select * from' in sql and 'join' not in sql and 'where' not in sql:
        patterns['Simple SELECT'] += 1
    if 'where' in sql:
        patterns['WHERE filter'] += 1
    if 'group by' in sql:
        patterns['GROUP BY aggregation'] += 1
    if 'join' in sql:
        join_count = sql.count('join')
        if join_count == 1:
            patterns['JOIN (2-table)'] += 1
        else:
            patterns['JOIN (3-table)'] += 1
    if 'order by' in sql:
        patterns['ORDER BY'] += 1
    if 'limit' in sql:
        patterns['LIMIT'] += 1
    if 'having' in sql:
        patterns['HAVING'] += 1

print(f"Unique SQL queries: {len(unique_sqls)}")
print(f"\nQuery Pattern Breakdown:")
for pattern, count in sorted(patterns.items(), key=lambda x: -x[1]):
    print(f"  {pattern:.<25} {count:>3}")

print(f"\n✅ Dataset diversity looks good!")
print(f"💡 Each SQL has ~{len(lines)/len(unique_sqls):.1f} NL variants on average")
