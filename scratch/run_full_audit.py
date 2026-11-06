import sys
sys.path.insert(0, 'scratch')
import audit_human_review as a

print(f"Total system evaluations audited: {len(a.audit_results)} (expected 160)")
all_issues = [r for r in a.audit_results if r['issues']]
print(f"Total evaluations with issues: {len(all_issues)}")

for r in all_issues:
    print(f"  [{r['batch']} | {r['case_id']} | {r['system']}]: {', '.join(r['issues'])}")

if len(all_issues) == 0:
    print("\nSUCCESS: All 160 evaluations are complete, valid, and issue-free!")

# Summarize breakdown of dimensions
from collections import Counter
print("\n--- Summary Distribution Across 160 Evaluations ---")
print("Gate A:", Counter(r['gate'] for r in a.audit_results))
print("Dim 1 (Technical Correctness):", Counter(r['d1'] for r in a.audit_results))
print("Dim 2 (Unsupported Claims):", Counter(r['d2'] for r in a.audit_results))
print("Dim 3 (Appropriate Uncertainty):", Counter(r['d3'] for r in a.audit_results))
print("Dim 4 (Actionable Repair Scope):", Counter(r['d4'] for r in a.audit_results))
print("Dim 5 (Verification Steps Useful):", Counter(r['d5'] for r in a.audit_results))

cannot_assess = [r for r in a.audit_results if 'cannot assess' in str(r['gate']).lower() or 'cannot assess' in str(r['d1']).lower()]
print(f"\nCannot Assess cases: {len(cannot_assess)}")
for ca in cannot_assess:
    print(f"  [{ca['batch']} | {ca['case_id']} | {ca['system']}]")

