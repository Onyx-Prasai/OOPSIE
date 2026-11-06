from inspect_all_evals import all_evals

fb4_evals = [e for e in all_evals if e['case_id'] == 'bench-firebase-04']
for e in fb4_evals:
    print(f"=== {e['system']} ===")
    print(e['raw'][:500])
    print()

