from build_checklist_data import checklist_items

print("=== AUTH / AUTHZ CONFUSION (18 items) ===")
for item in [x for x in checklist_items if x['auth_confusion']]:
    print(f"[{item['batch']} | {item['case_id']} | {item['system']}]: Model={item['pred_cat']} vs Exp={item['exp_cat']} | D1={item['ratings']['d1']}")
    print(f"   Notes: {item['notes']}")

print("\n=== GENEROUS PASS CONCERNS (13 items) ===")
for item in [x for x in checklist_items if x['generous_concerns']]:
    print(f"[{item['batch']} | {item['case_id']} | {item['system']}]: D1={item['ratings']['d1']}, D4={item['ratings']['d4']}, D5={item['ratings']['d5']}")
    for c in item['generous_concerns']:
        print(f"   Concern: {c}")

