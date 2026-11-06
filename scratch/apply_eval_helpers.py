import re

def apply_evaluations_to_batch(filepath, evals_dict):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 1. Update header status label
    status_label = "> **Rating Status**: AI-generated provisional ratings, subject to author review and final adoption.\n"
    if "AI-generated provisional ratings" not in content:
        # insert before first ---
        m = re.search(r'(> \*\*Disclosures\*\*:.*?\n)', content)
        if m:
            content = content[:m.end()] + status_label + content[m.end():]
        else:
            # fallback: insert before first ---
            content = re.sub(r'(\n---)', r'\n' + status_label + r'---', content, count=1)
    
    # 2. Split by case
    cases = re.split(r'\n(?=## Case: `)', content)
    header = cases[0]
    out_cases = [header]
    
    d1_map = {
        "Pass (Correct)": "1. **Technical Correctness**: [x] Pass (Correct)  [ ] Partial  [ ] Fail (Incorrect)  [ ] Cannot Assess",
        "Partial": "1. **Technical Correctness**: [ ] Pass (Correct)  [x] Partial  [ ] Fail (Incorrect)  [ ] Cannot Assess",
        "Fail (Incorrect)": "1. **Technical Correctness**: [ ] Pass (Correct)  [ ] Partial  [x] Fail (Incorrect)  [ ] Cannot Assess",
        "Cannot Assess": "1. **Technical Correctness**: [ ] Pass (Correct)  [ ] Partial  [ ] Fail (Incorrect)  [x] Cannot Assess"
    }
    
    d2_map = {
        "None": "2. **Unsupported Claims**: [x] None  [ ] Minor  [ ] Severe  [ ] Cannot Assess",
        "Minor": "2. **Unsupported Claims**: [ ] None  [x] Minor  [ ] Severe  [ ] Cannot Assess",
        "Severe": "2. **Unsupported Claims**: [ ] None  [ ] Minor  [x] Severe  [ ] Cannot Assess",
        "Cannot Assess": "2. **Unsupported Claims**: [ ] None  [ ] Minor  [ ] Severe  [x] Cannot Assess"
    }
    
    d3_map = {
        "Pass (Appropriate)": "3. **Appropriate Uncertainty**: [x] Pass (Appropriate)  [ ] Overconfident  [ ] Cannot Assess",
        "Overconfident": "3. **Appropriate Uncertainty**: [ ] Pass (Appropriate)  [x] Overconfident  [ ] Cannot Assess",
        "Cannot Assess": "3. **Appropriate Uncertainty**: [ ] Pass (Appropriate)  [ ] Overconfident  [x] Cannot Assess"
    }
    
    d4_map = {
        "Pass (Well-Scoped)": "4. **Actionable Repair Scope**: [x] Pass (Well-Scoped)  [ ] Vague  [ ] Harmful / Overbroad  [ ] Cannot Assess",
        "Vague": "4. **Actionable Repair Scope**: [ ] Pass (Well-Scoped)  [x] Vague  [ ] Harmful / Overbroad  [ ] Cannot Assess",
        "Harmful / Overbroad": "4. **Actionable Repair Scope**: [ ] Pass (Well-Scoped)  [ ] Vague  [x] Harmful / Overbroad  [ ] Cannot Assess",
        "Cannot Assess": "4. **Actionable Repair Scope**: [ ] Pass (Well-Scoped)  [ ] Vague  [ ] Harmful / Overbroad  [x] Cannot Assess"
    }
    
    d5_map = {
        "Pass (Useful & Safe)": "5. **Verification Steps Useful**: [x] Pass (Useful & Safe)  [ ] Incomplete  [ ] Fail (Unsound)  [ ] Cannot Assess",
        "Incomplete": "5. **Verification Steps Useful**: [ ] Pass (Useful & Safe)  [x] Incomplete  [ ] Fail (Unsound)  [ ] Cannot Assess",
        "Fail (Unsound)": "5. **Verification Steps Useful**: [ ] Pass (Useful & Safe)  [ ] Incomplete  [x] Fail (Unsound)  [ ] Cannot Assess",
        "Cannot Assess": "5. **Verification Steps Useful**: [ ] Pass (Useful & Safe)  [ ] Incomplete  [ ] Fail (Unsound)  [x] Cannot Assess"
    }
    
    gate_map = {
        "Assessable Content Present": "- [x] Assessable Content Present  [ ] Cannot Assess (empty/noise)  [ ] No Usable Response (refusal)",
        "Cannot Assess": "- [ ] Assessable Content Present  [x] Cannot Assess (empty/noise)  [ ] No Usable Response (refusal)",
        "No Usable Response": "- [ ] Assessable Content Present  [ ] Cannot Assess (empty/noise)  [x] No Usable Response (refusal)"
    }
    
    for cb in cases[1:]:
        cid_m = re.search(r'## Case: `([^`]+)`', cb)
        if not cid_m:
            out_cases.append(cb)
            continue
        cid = cid_m.group(1)
        
        sys_blocks = re.split(r'\n(?=### System (?:Alpha|Beta|Gamma|Delta))', cb)
        case_header = sys_blocks[0]
        out_sys = [case_header]
        
        for sb in sys_blocks[1:]:
            sname = re.search(r'### (System (?:Alpha|Beta|Gamma|Delta))', sb).group(1)
            key = (cid, sname)
            if key not in evals_dict:
                print(f"Warning: missing evaluation for {key}")
                out_sys.append(sb)
                continue
            
            ev = evals_dict[key]
            
            # Replace Gate A
            sb = re.sub(
                r'- \[.\] Assessable Content Present\s+\[.\] Cannot Assess \(empty/noise\)\s+\[.\] No Usable Response \(refusal\)',
                gate_map[ev["gate"]],
                sb
            )
            
            # Replace Dim 1
            sb = re.sub(r'1\.\s*\*\*Technical Correctness\*\*:[^\n]+', d1_map[ev["d1"]], sb)
            
            # Replace Dim 2
            sb = re.sub(r'2\.\s*\*\*Unsupported Claims\*\*:[^\n]+', d2_map[ev["d2"]], sb)
            
            # Replace Dim 3
            sb = re.sub(r'3\.\s*\*\*Appropriate Uncertainty\*\*:[^\n]+', d3_map[ev["d3"]], sb)
            
            # Replace Dim 4
            sb = re.sub(r'4\.\s*\*\*Actionable Repair Scope\*\*:[^\n]+', d4_map[ev["d4"]], sb)
            
            # Replace Dim 5
            sb = re.sub(r'5\.\s*\*\*Verification Steps Useful\*\*:[^\n]+', d5_map[ev["d5"]], sb)
            
            # Replace Notes
            sb = re.sub(
                r'\*\*C\. Reviewer Notes, Alternative Diagnoses & Evidentiary Basis\*\*:\n(?:_+|.*?\n(?=\n---|####|\Z))',
                f"**C. Reviewer Notes, Alternative Diagnoses & Evidentiary Basis**:\n{ev['notes']}\n",
                sb,
                flags=re.DOTALL
            )
            
            out_sys.append(sb)
        
        out_cases.append("".join(out_sys))
    
    new_content = "".join(out_cases)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated {filepath} with {len(evals_dict)} evaluations.")

