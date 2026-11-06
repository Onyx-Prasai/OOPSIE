from inspect_all_evals import all_evals

refusal_keywords = ["as an ai", "i cannot fulfill", "i am unable to", "sorry, but", "i'm sorry"]

flagged = []
for e in all_evals:
    text_lower = e['raw'].lower()
    for kw in refusal_keywords:
        if kw in text_lower:
            flagged.append((e['batch'], e['case_id'], e['system'], kw))

print(f"Flagged for potential refusal keywords: {len(flagged)}")
for f in flagged:
    print(f)

