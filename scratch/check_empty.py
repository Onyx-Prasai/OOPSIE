import re, json

empty_or_refusals = []

for b in range(1, 9):
    fn = f"docs/research/human_review/batch_{b:02d}.md"
    with open(fn, "r", encoding="utf-8") as f:
        content = f.read()
    
    case_blocks = re.split(r'\n(?=## Case: `)', content)[1:]
    for cb in case_blocks:
        case_id = re.search(r'## Case: `([^`]+)`', cb).group(1)
        system_blocks = re.split(r'\n(?=### System (?:Alpha|Beta|Gamma|Delta))', cb)[1:]
        for sb in system_blocks:
            sys_name = re.search(r'### (System (?:Alpha|Beta|Gamma|Delta))', sb).group(1)
            # Find the code block
            # code block is between ```json and the metadata
            m = re.search(r'### System \w+\n\n```json\n([\s\S]*?)\n```\n\n- \*\*Parsed JSON\*\*', sb)
            if not m:
                # check alternative pattern
                m = re.search(r'### System \w+\n\n```[a-z]*\n([\s\S]*?)\n```\n\n- \*\*Parsed JSON\*\*', sb)
            if not m:
                print(f"Pattern failed for {fn} {case_id} {sys_name}")
                continue
            raw_text = m.group(1).strip()
            if len(raw_text) == 0:
                empty_or_refusals.append((b, case_id, sys_name, "EMPTY"))
            elif len(raw_text) < 50:
                empty_or_refusals.append((b, case_id, sys_name, f"SHORT: {raw_text}"))

print(f"Empty or refusals found: {len(empty_or_refusals)}")
for item in empty_or_refusals:
    print(item)

