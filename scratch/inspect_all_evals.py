import glob, re, json

def clean_json_str(s):
    s = s.strip()
    if s.startswith("```json"):
        s = s[7:]
    elif s.startswith("```"):
        s = s[3:]
    if s.endswith("```"):
        s = s[:-3]
    return s.strip()

all_evals = []

for b in range(1, 9):
    fn = f"docs/research/human_review/batch_{b:02d}.md"
    with open(fn, "r", encoding="utf-8") as f:
        text = f.read()
    case_blocks = re.split(r'\n(?=## Case: `)', text)[1:]
    for cb in case_blocks:
        cid = re.search(r'## Case: `([^`]+)`', cb).group(1)
        sys_blocks = re.split(r'\n(?=### System (?:Alpha|Beta|Gamma|Delta))', cb)[1:]
        for sb in sys_blocks:
            sname = re.search(r'### (System (?:Alpha|Beta|Gamma|Delta))', sb).group(1)
            m = re.search(r'```json\n([\s\S]*?)\n```\n\n- \*\*Parsed JSON\*\*', sb)
            if not m:
                m = re.search(r'```[a-z]*\n([\s\S]*?)\n```\n\n- \*\*Parsed JSON\*\*', sb)
            raw = m.group(1).strip() if m else ""
            
            # Check length, check if valid json
            parsed = None
            try:
                parsed = json.loads(clean_json_str(raw))
            except Exception as e:
                pass
            
            all_evals.append({
                "batch": b,
                "case_id": cid,
                "system": sname,
                "raw_len": len(raw),
                "parsed_ok": parsed is not None,
                "parsed": parsed,
                "raw": raw
            })

print(f"Total evaluations parsed: {len(all_evals)}")
non_parseable = [e for e in all_evals if not e["parsed_ok"]]
print(f"Non-parseable completions (even after stripping markdown): {len(non_parseable)}")
for np in non_parseable:
    print(f"  Batch {np['batch']}, {np['case_id']}, {np['system']}: len={np['raw_len']}")
    print(f"    Raw start: {np['raw'][:100]}")
    print(f"    Raw end: {np['raw'][-100:]}")

