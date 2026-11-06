from inspect_all_evals import all_evals

c3_evals = [e for e in all_evals if e['case_id'] == 'bench-authentication-03']
for e in c3_evals:
    print(f"=== {e['system']} ===")
    print(f"Category: {e['parsed'].get('error_category') if e['parsed'] else 'N/A'}")
    print(f"Summary: {e['parsed'].get('summary') if e['parsed'] else 'N/A'}")
    print(f"Causes: {[c.get('description') for c in e['parsed'].get('likely_causes', [])] if e['parsed'] else 'N/A'}")
    print(f"Repair: {e['parsed'].get('repair_prompt') if e['parsed'] else 'N/A'}")
    print(f"Verif: {e['parsed'].get('verification_steps') if e['parsed'] else 'N/A'}")
    print()

