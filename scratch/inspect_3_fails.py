import re, json

with open("docs/research/human_review/batch_04.md", "r", encoding="utf-8") as f:
    t4 = f.read()
with open("docs/research/human_review/batch_05.md", "r", encoding="utf-8") as f:
    t5 = f.read()
with open("docs/research/human_review/batch_06.md", "r", encoding="utf-8") as f:
    t6 = f.read()

def examine(text, case_id, sys_name):
    print(f"=== {case_id} {sys_name} ===")
    cb = [c for c in re.split(r'\n(?=## Case: `)', text) if case_id in c][0]
    sb = [s for s in re.split(r'\n(?=### System (?:Alpha|Beta|Gamma|Delta))', cb) if sys_name in s][0]
    m = re.search(r'```json\n([\s\S]*?)\n```\n\n- \*\*Parsed JSON\*\*', sb)
    if not m:
        m = re.search(r'```[a-z]*\n([\s\S]*?)\n```\n\n- \*\*Parsed JSON\*\*', sb)
    raw = m.group(1).strip()
    # strip triple backticks if any inside
    clean = re.sub(r'^```(?:json)?\s*', '', raw).rstrip('`\n\r ')
    try:
        json.loads(clean)
        print("Parsed successfully!")
    except Exception as e:
        print("JSON Error:", e)
        pos = getattr(e, 'pos', None)
        if pos:
            print("At pos:", pos)
            print("Snippet:", repr(clean[max(0, pos-40):pos+40]))

examine(t4, "bench-firebase-01", "System Alpha")
examine(t5, "bench-nextjs-01", "System Gamma")
examine(t6, "bench-nextjs-03", "System Beta")

