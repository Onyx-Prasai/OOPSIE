from inspect_all_evals import all_evals

b2_evals = [e for e in all_evals if e['batch'] == 2]
print(f"Batch 2 evals: {len(b2_evals)}")
for e in b2_evals:
    print(f"--- {e['case_id']} | {e['system']} ---")
    if e['parsed']:
        p = e['parsed']
        print(f"  Cat: {p.get('error_category')}, Risk: {p.get('risk_level')}")
        print(f"  Summary: {p.get('summary')[:70]}...")
        print(f"  Causes: {[c.get('description')[:40] for c in p.get('likely_causes', [])]}")
        print(f"  Repair: {p.get('repair_prompt')[:70]}...")
    else:
        print("  [NOT PARSED]")

