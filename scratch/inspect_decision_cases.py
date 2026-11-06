import json, re
from inspect_all_evals import all_evals

def get_eval(case_id, sys_name):
    for e in all_evals:
        if e['case_id'] == case_id and e['system'] == sys_name:
            return e
    return None

cases_to_check = [
    ("bench-authentication-03", "System Beta"),
    ("bench-firebase-02", "System Alpha"),
    ("bench-firebase-02", "System Beta"),
    ("bench-firebase-04", "System Alpha"),
    ("bench-firebase-04", "System Beta"),
    ("bench-firebase-04", "System Delta"),
    ("bench-npm-02", "System Beta"),
    ("bench-npm-02", "System Delta"),
    ("bench-firebase-04", "System Gamma"),
    ("bench-react-02", "System Alpha"),
    ("bench-general-02", "System Alpha"),
    ("bench-firebase-01", "System Alpha"),
    ("bench-nextjs-01", "System Gamma"),
    ("bench-nextjs-03", "System Beta"),
    ("bench-supabase-02", "System Gamma"),
]

for cid, sname in cases_to_check:
    e = get_eval(cid, sname)
    if e:
        print(f"=== {cid} | {sname} ===")
        p = e['parsed']
        if p:
            print("  Category:", p.get('error_category'))
            print("  Summary:", p.get('summary'))
            print("  Repair:", p.get('repair_prompt')[:120])
            print("  Verif:", p.get('verification_steps'))
        else:
            print("  [PARSE FAIL] Raw start:", e['raw'][:100])
    print()

