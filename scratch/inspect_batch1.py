import re, json

with open("docs/research/human_review/batch_01.md", "r", encoding="utf-8") as f:
    text = f.read()

case_blocks = re.split(r'\n(?=## Case: `)', text)[1:]
print(f"Cases in batch 1: {len(case_blocks)}")

for i, cb in enumerate(case_blocks):
    cid = re.search(r'## Case: `([^`]+)`', cb).group(1)
    err = re.search(r'### Developer Error Input\n```\n([\s\S]*?)\n```', cb).group(1).strip()
    print(f"\n--- Case {i+1}: {cid} ---")
    print(f"Error: {err}")
    sys_blocks = re.split(r'\n(?=### System (?:Alpha|Beta|Gamma|Delta))', cb)[1:]
    for sb in sys_blocks:
        sname = re.search(r'### (System (?:Alpha|Beta|Gamma|Delta))', sb).group(1)
        # extract parsed JSON status
        parsed = "PASS" if "- **Parsed JSON**: PASS" in sb else "FAIL"
        # check summary or category in output
        cat_m = re.search(r'"error_category":\s*"([^"]+)"', sb)
        cat = cat_m.group(1) if cat_m else "N/A"
        print(f"  {sname}: Parsed={parsed}, category={cat}")

