import sys
sys.path.insert(0, 'scratch')
import audit_human_review as a

partials = [r for r in a.audit_results if r['d1'] == 'Partial']
print(f"Total Partial cases: {len(partials)}")
for p in partials:
    print(f"  [{p['batch']} | {p['case_id']} | {p['system']}]:")
    print(f"    Notes: {p['notes']}")

