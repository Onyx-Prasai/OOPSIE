import re, json

def clean_json_str(s):
    # strip markdown code fences if present
    s = s.strip()
    if s.startswith("```json"):
        s = s[7:]
    elif s.startswith("```"):
        s = s[3:]
    if s.endswith("```"):
        s = s[:-3]
    return s.strip()

with open("docs/research/human_review/batch_01.md", "r", encoding="utf-8") as f:
    text = f.read()

case_blocks = re.split(r'\n(?=## Case: `)', text)[1:]
for cb in case_blocks:
    cid = re.search(r'## Case: `([^`]+)`', cb).group(1)
    err = re.search(r'### Developer Error Input\n```\n([\s\S]*?)\n```', cb).group(1).strip()
    print("="*60)
    print(f"CASE: {cid} | Error: {err}")
    sys_blocks = re.split(r'\n(?=### System (?:Alpha|Beta|Gamma|Delta))', cb)[1:]
    for sb in sys_blocks:
        sname = re.search(r'### (System (?:Alpha|Beta|Gamma|Delta))', sb).group(1)
        # extract code
        m = re.search(r'```json\n([\s\S]*?)\n```\n\n- \*\*Parsed JSON\*\*', sb)
        if not m:
            m = re.search(r'```[a-z]*\n([\s\S]*?)\n```\n\n- \*\*Parsed JSON\*\*', sb)
        raw_code = m.group(1).strip() if m else ""
        try:
            parsed = json.loads(clean_json_str(raw_code))
            print(f"  [{sname}]")
            print(f"    Category: {parsed.get('error_category')}")
            print(f"    Summary: {parsed.get('summary')[:80]}...")
            print(f"    Causes: {[c.get('description')[:50] for c in parsed.get('likely_causes', [])]}")
            print(f"    Repair: {parsed.get('repair_prompt')[:100]}...")
            print(f"    Verif: {[v[:50] for v in parsed.get('verification_steps', [])]}")
        except Exception as e:
            print(f"  [{sname}] Failed to parse cleaned: {e}")
            print(f"    Raw starts with: {raw_code[:100]}")

