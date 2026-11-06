import sys
sys.path.insert(0, 'scratch')
import audit_human_review as a
from collections import Counter

total = len(a.audit_results)
print(f"Total Evaluations: {total}")

def print_dist(name, values):
    print(f"\n### {name} (N = {total})")
    counts = Counter(values)
    for k, v in counts.items():
        pct = (v / total) * 100
        print(f"- **{k}**: {v} ({pct:.2f}%)")

print_dist("Administrative Content Eligibility Gate (Unscored)", [r['gate'] for r in a.audit_results])
print_dist("Dimension 1: Technical Correctness", [r['d1'] for r in a.audit_results])
print_dist("Dimension 2: Unsupported Claims", [r['d2'] for r in a.audit_results])
print_dist("Dimension 3: Appropriate Uncertainty", [r['d3'] for r in a.audit_results])
print_dist("Dimension 4: Actionable Repair Scope", [r['d4'] for r in a.audit_results])
print_dist("Dimension 5: Verification Usefulness", [r['d5'] for r in a.audit_results])

