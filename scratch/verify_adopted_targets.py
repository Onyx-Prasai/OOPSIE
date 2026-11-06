import sys
sys.path.insert(0, 'scratch')
import audit_human_review as a

targets = [
    ('bench-authentication-03', 'System Beta'),
    ('bench-firebase-02', 'System Alpha'),
    ('bench-firebase-02', 'System Beta'),
    ('bench-firebase-04', 'System Alpha'),
    ('bench-firebase-04', 'System Beta'),
    ('bench-firebase-04', 'System Delta'),
    ('bench-npm-02', 'System Beta'),
    ('bench-npm-02', 'System Delta'),
    ('bench-react-02', 'System Alpha')
]

for t_cid, t_sys in targets:
    r = [x for x in a.audit_results if x['case_id'] == t_cid and x['system'] == t_sys][0]
    print(f"[{r['case_id']} | {r['system']}]:")
    print(f"  Gate: {r['gate']}")
    print(f"  D1 (Correctness):   {r['d1']}")
    print(f"  D2 (Unsupported):   {r['d2']}")
    print(f"  D3 (Uncertainty):   {r['d3']}")
    print(f"  D4 (Repair Scope):  {r['d4']}")
    print(f"  D5 (Verification):  {r['d5']}")
    print(f"  Notes: {r['notes']}")
    print()

