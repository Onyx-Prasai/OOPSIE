import json

with open("artifacts/benchmark_v1_2_0/benchmark_results/unblinded_review_key.json", "r", encoding="utf-8") as f:
    key_data = json.load(f)

print(f"Number of cases in key: {len(key_data)}")
# Show first 5 cases
for cid in list(key_data.keys())[:5]:
    print(f"  {cid}: {key_data[cid]}")

