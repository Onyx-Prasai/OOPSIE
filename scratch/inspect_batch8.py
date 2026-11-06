from inspect_all_evals import all_evals

b8_evals = [e for e in all_evals if e['batch'] == 8]
for e in b8_evals:
    print(f"=== {e['case_id']} | {e['system']} ===")
    p = e['parsed']
    if p:
        print(f"  Cat: {p.get('error_category')}, Risk: {p.get('risk_level')}")
        print(f"  Summary: {p.get('summary')[:80]}...")
        print(f"  Causes: {[c.get('description')[:40] for c in p.get('likely_causes', [])]}")
        print(f"  Repair: {p.get('repair_prompt')[:80]}...")
        print(f"  Verif: {[v[:40] for v in p.get('verification_steps', [])]}")
    else:
        print("  [PARSE FAIL]")
    print()

