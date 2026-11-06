from build_checklist_data import checklist_items

generic_list = []
for item in checklist_items:
    notes = item['notes']
    words = notes.split()
    # Check if notes quote specific terms from response or error trace
    has_quotes = ("'" in notes or '"' in notes or '`' in notes)
    has_file_or_param = any(x in notes for x in ['.', '/', ':', '()', '_'])
    # Flag if word count is small (<22 words) or lacks specific quotes
    if len(words) < 22 or not has_quotes:
        generic_list.append((item['batch'], item['case_id'], item['system'], len(words), notes))

print(f"Notes flagged as potentially generic / brief ({len(generic_list)} items):")
for g in generic_list[:25]:
    print(f"[{g[0]} | {g[1]} | {g[2]}] (words={g[3]}): {g[4]}")
if len(generic_list) > 25:
    print(f"... and {len(generic_list) - 25} more.")

