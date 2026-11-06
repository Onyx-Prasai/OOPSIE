from inspect_all_evals import all_evals

n1_evals = [e for e in all_evals if e['case_id'] == 'bench-nextjs-01']
for e in n1_evals:
    print(f"=== {e['system']} ===")
    p = e['parsed']
    if p:
        print(f"  Cat: {p.get('error_category')}, Risk: {p.get('risk_level')}")
        print(f"  Summary: {p.get('summary')}")
        print(f"  Causes: {[c.get('description') for c in p.get('likely_causes', [])]}")
        print(f"  Repair: {p.get('repair_prompt')}")
        print(f"  Verif: {p.get('verification_steps')}")
    else:
        print("  [PARSE FAIL]")
        print(f"  Raw: {e['raw'][:300]}")
    print()

