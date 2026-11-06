from inspect_all_evals import all_evals

for b in range(2, 9):
    b_evals = [e for e in all_evals if e['batch'] == b]
    cases = sorted(list(set(e['case_id'] for e in b_evals)))
    print(f"=== BATCH {b:02d} ({len(b_evals)} evals) ===")
    for cid in cases:
        c_evals = [e for e in b_evals if e['case_id'] == cid]
        print(f"  Case: {cid}")
        for ce in c_evals:
            parsed_str = "OK" if ce['parsed_ok'] else "PARSE_FAIL"
            cat = ce['parsed'].get('error_category') if ce['parsed'] else "N/A"
            risk = ce['parsed'].get('risk_level') if ce['parsed'] else "N/A"
            print(f"    {ce['system']}: [{parsed_str}] Cat={cat}, Risk={risk}")

