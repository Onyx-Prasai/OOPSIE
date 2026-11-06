import glob, re

for b in range(1, 9):
    fn = f"docs/research/human_review/batch_{b:02d}.md"
    with open(fn, "r", encoding="utf-8") as f:
        txt = f.read()
    cases = re.findall(r"## Case: `([^`]+)`", txt)
    gen_failed = len(re.findall(r"Generation Failed\*\*: YES", txt))
    budget_hits = len(re.findall(r"Budget Hit \(1024 tokens\)\*\*: YES", txt))
    parsed_fails = len(re.findall(r"Parsed JSON\*\*: FAIL", txt))
    print(f"Batch {b:02d}: {len(cases)} cases, Gen Failed: {gen_failed}, Budget Hit: {budget_hits}, Parse Fail: {parsed_fails}")

