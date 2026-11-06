from inspect_all_evals import all_evals

repetitive = []
for e in all_evals:
    words = e['raw'].split()
    if len(words) > 30:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.2:
            repetitive.append((e['batch'], e['case_id'], e['system'], unique_ratio))

print("Repetitive completions:", repetitive)

