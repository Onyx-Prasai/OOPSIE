from inspect_all_evals import all_evals

npm2_evals = [e for e in all_evals if e['case_id'] == 'bench-npm-02']
for e in npm2_evals:
    print(f"=== {e['system']} ===")
    print(e['raw'])
    print()

