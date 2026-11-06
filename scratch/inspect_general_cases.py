from inspect_all_evals import all_evals

gen_evals = [e for e in all_evals if e['case_id'].startswith('bench-general')]
for e in gen_evals:
    print(f"=== {e['case_id']} | {e['system']} ===")
    print(f"Summary: {e['raw'][:200]}...")
    if e['parsed']:
        print(f"  Category: {e['parsed'].get('error_category')}")
        print(f"  Questions: {e['parsed'].get('missing_context_questions')}")
        print(f"  Causes: {[c.get('description') for c in e['parsed'].get('likely_causes', [])]}")
        print(f"  Repair: {e['parsed'].get('repair_prompt')}")
    print()

