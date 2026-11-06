import sys
sys.path.insert(0, 'scratch')
import audit_human_review as a

b1_res = [r for r in a.audit_results if r['batch'] == 'batch_01.md']
print(f"Batch 01 evals audited: {len(b1_res)}")
b1_issues = [r for r in b1_res if r['issues']]
print(f"Batch 01 evals with issues: {len(b1_issues)}")
for r in b1_issues:
    print(f"  [{r['case_id']} | {r['system']}]: {r['issues']}")

print("\nAll 20 evaluations in Batch 01:")
for r in b1_res:
    print(f"  [{r['case_id']} | {r['system']}]: Gate={r['gate']}, D1={r['d1']}, D2={r['d2']}, D3={r['d3']}, D4={r['d4']}, D5={r['d5']}")
