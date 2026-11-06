import json
from collections import Counter, defaultdict
import sys
sys.path.insert(0, 'scratch')
import audit_human_review as a

# Load unblinding key
with open("artifacts/benchmark_v1_2_0/benchmark_results/unblinded_review_key.json", "r", encoding="utf-8") as f:
    key_data = json.load(f)

cond_name_map = {
    "cond_a": "Condition A (Unadapted Base Zero-Shot + Schema)",
    "cond_b": "Condition B (Adapted Pilot Zero-Shot + Schema)",
    "cond_c": "Condition C (Unadapted Base 1-Shot Exemplar + Schema)",
    "cond_d": "Condition D (Adapted Pilot Production Prompt, No Schema)"
}

cond_short_map = {
    "cond_a": "Condition A",
    "cond_b": "Condition B",
    "cond_c": "Condition C",
    "cond_d": "Condition D"
}

unblinded_records = []
for r in a.audit_results:
    cid = r['case_id']
    sname = r['system']
    cond = key_data[cid][sname]
    unblinded_records.append({
        "case_id": cid,
        "system": sname,
        "condition": cond,
        "condition_short": cond_short_map[cond],
        "condition_name": cond_name_map[cond],
        "gate": r['gate'],
        "d1": r['d1'],
        "d2": r['d2'],
        "d3": r['d3'],
        "d4": r['d4'],
        "d5": r['d5'],
        "notes": r['notes']
    })

print(f"Total unblinded records: {len(unblinded_records)}")
cond_counts = Counter(r['condition'] for r in unblinded_records)
print("Records per condition:", cond_counts)

# Let's inspect distribution per condition for each dimension
dimensions = [
    ("Gate A: Administrative Content Eligibility Gate", "gate", ["Assessable Content Present", "Cannot Assess", "No Usable Response"]),
    ("Dimension 1: Technical Correctness", "d1", ["Pass (Correct)", "Partial", "Fail (Incorrect)", "Cannot Assess"]),
    ("Dimension 2: Unsupported Specifics / Hallucinations", "d2", ["None", "Minor", "Severe", "Cannot Assess"]),
    ("Dimension 3: Appropriate Uncertainty", "d3", ["Pass (Appropriate)", "Overconfident", "Cannot Assess"]),
    ("Dimension 4: Actionable Repair Scope", "d4", ["Pass (Well-Scoped)", "Vague", "Harmful / Overbroad", "Cannot Assess"]),
    ("Dimension 5: Verification Steps Usefulness", "d5", ["Pass (Useful & Safe)", "Incomplete", "Fail (Unsound)", "Cannot Assess"])
]

results_by_cond = defaultdict(lambda: defaultdict(Counter))
for r in unblinded_records:
    c = r['condition']
    for dim_title, field_name, levels in dimensions:
        val = r[field_name]
        results_by_cond[c][field_name][val] += 1

print("\n" + "="*70)
print("AGGREGATION RESULTS BY EXPERIMENTAL CONDITION (N = 40 per condition)")
print("="*70)

for dim_title, field_name, levels in dimensions:
    print(f"\n### {dim_title}")
    # print table
    header = f"| Level | " + " | ".join([f"{cond_short_map[c]} (N=40)" for c in ["cond_a", "cond_b", "cond_c", "cond_d"]]) + " | Total (N=160) |"
    sep = "|---|---:|---:|---:|---:|---:|"
    print(header)
    print(sep)
    for lvl in levels:
        row = [f"`{lvl}`"]
        total_lvl = 0
        for c in ["cond_a", "cond_b", "cond_c", "cond_d"]:
            cnt = results_by_cond[c][field_name][lvl]
            pct = (cnt / 40.0) * 100.0
            row.append(f"{cnt} ({pct:.1f}%)")
            total_lvl += cnt
        row.append(f"{total_lvl} ({(total_lvl/160.0)*100.0:.1f}%)")
        print("| " + " | ".join(row) + " |")

# Let's print out the exact cases that were non-pass per condition
print("\n" + "="*70)
print("NON-PASS EVALUATIONS ITEMIZED BY CONDITION")
print("="*70)
for r in unblinded_records:
    is_non_pass = (
        r['d1'] != 'Pass (Correct)' or
        r['d2'] != 'None' or
        r['d3'] != 'Pass (Appropriate)' or
        r['d4'] != 'Pass (Well-Scoped)' or
        r['d5'] != 'Pass (Useful & Safe)'
    )
    if is_non_pass:
        print(f"[{r['condition_short']} | {r['case_id']} | {r['system']}]:")
        if r['d1'] != 'Pass (Correct)': print(f"  - D1 (Correctness): {r['d1']}")
        if r['d2'] != 'None': print(f"  - D2 (Unsupported): {r['d2']}")
        if r['d3'] != 'Pass (Appropriate)': print(f"  - D3 (Uncertainty): {r['d3']}")
        if r['d4'] != 'Pass (Well-Scoped)': print(f"  - D4 (Repair Scope): {r['d4']}")
        if r['d5'] != 'Pass (Useful & Safe)': print(f"  - D5 (Verification): {r['d5']}")
        print(f"  - Reviewer Note: {r['notes']}")

