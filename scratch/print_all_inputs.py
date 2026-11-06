import re

for b in range(1, 9):
    fn = f"docs/research/human_review/batch_{b:02d}.md"
    with open(fn, "r", encoding="utf-8") as f:
        t = f.read()
    case_blocks = re.split(r'\n(?=## Case: `)', t)[1:]
    for cb in case_blocks:
        cid = re.search(r'## Case: `([^`]+)`', cb).group(1)
        # find error input
        m = re.search(r'### Developer Error Input\n```[a-z]*\n([\s\S]*?)\n```', cb)
        err = m.group(1).strip() if m else "NOT_FOUND"
        print(f"Batch {b:02d} | {cid}: {err[:80]}")

