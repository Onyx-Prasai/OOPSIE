import glob
import re
import os

batch_files = sorted(glob.glob("docs/research/human_review/batch_*.md"))

systems_order = ["System Alpha", "System Beta", "System Gamma", "System Delta"]

audit_results = []
# Each item: {batch, case_id, system, gate, d1, d2, d3, d4, d5, notes, issues}

for bf in batch_files:
    bname = os.path.basename(bf)
    with open(bf, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Split by case
    case_blocks = re.split(r'\n(?=## Case: `)', content)[1:]
    
    for cb in case_blocks:
        case_match = re.search(r'## Case: `([^`]+)`', cb)
        if not case_match:
            continue
        case_id = case_match.group(1)
        
        # Split by system
        system_blocks = re.split(r'\n(?=### System (?:Alpha|Beta|Gamma|Delta))', cb)[1:]
        
        for sb in system_blocks:
            sys_match = re.search(r'### (System (?:Alpha|Beta|Gamma|Delta))', sb)
            if not sys_match:
                continue
            sys_name = sys_match.group(1)
            
            issues = []
            
            # 1. Administrative Gate
            # - [ ] Assessable Content Present  [ ] Cannot Assess (empty/noise)  [ ] No Usable Response (refusal)
            gate_match = re.search(r'\*\*A\. Administrative Content Eligibility Gate[^\n]*\n([^\n]+)', sb)
            gate_val = None
            if gate_match:
                gate_line = gate_match.group(1)
                # Find checked boxes
                checked = re.findall(r'\[([xX])\]\s*([^\[]+)', gate_line)
                if len(checked) == 0:
                    # check if marked with other char or empty
                    all_boxes = re.findall(r'\[(.*?)\]\s*([^\[]+)', gate_line)
                    non_empty = [b for b in all_boxes if b[0].strip()]
                    if non_empty:
                        checked = non_empty
                if len(checked) == 0:
                    issues.append("Gate A unselected")
                elif len(checked) > 1:
                    issues.append(f"Gate A multiple selections: {[c[1].strip() for c in checked]}")
                else:
                    gate_val = checked[0][1].strip()
            else:
                issues.append("Gate A line missing")
            
            # Helper to check a dimension line
            def parse_dim(dim_num, dim_name, pattern):
                m = re.search(pattern, sb)
                if not m:
                    return None, [f"Dimension {dim_num} ({dim_name}) missing line"]
                line = m.group(0)
                # find all checkboxes
                boxes = re.findall(r'\[(.*?)\]\s*([^\[\n]+)', line)
                checked = [b[1].strip() for b in boxes if b[0].strip().lower() in ['x', 'v', '✓', 'yes']]
                dim_issues = []
                if len(checked) == 0:
                    dim_issues.append(f"Dimension {dim_num} ({dim_name}) unselected")
                    return None, dim_issues
                elif len(checked) > 1:
                    dim_issues.append(f"Dimension {dim_num} ({dim_name}) multiple selections: {checked}")
                    return checked, dim_issues
                else:
                    return checked[0], []
            
            # 2. Scored Dimensions
            d1_val, d1_iss = parse_dim(1, "Technical Correctness", r'1\.\s*\*\*Technical Correctness\*\*:[^\n]+')
            d2_val, d2_iss = parse_dim(2, "Unsupported Claims", r'2\.\s*\*\*Unsupported Claims\*\*:[^\n]+')
            d3_val, d3_iss = parse_dim(3, "Appropriate Uncertainty", r'3\.\s*\*\*Appropriate Uncertainty\*\*:[^\n]+')
            d4_val, d4_iss = parse_dim(4, "Actionable Repair Scope", r'4\.\s*\*\*Actionable Repair Scope\*\*:[^\n]+')
            d5_val, d5_iss = parse_dim(5, "Verification Steps Useful", r'5\.\s*\*\*Verification Steps Useful\*\*:[^\n]+')
            
            issues.extend(d1_iss + d2_iss + d3_iss + d4_iss + d5_iss)
            
            # Check gate consistency:
            # If gate is Cannot Assess or No Usable Response, did they check Cannot Assess on dims?
            if gate_val and any(term in gate_val.lower() for term in ["cannot assess", "no usable"]):
                # dims should ideally be Cannot Assess
                for d_idx, (d_name, d_v) in enumerate([(1, d1_val), (2, d2_val), (3, d3_val), (4, d4_val), (5, d5_val)]):
                    if d_v and "cannot assess" not in str(d_v).lower():
                        issues.append(f"Inconsistency: Gate is '{gate_val}' but Dim {d_name} is '{d_v}'")
            
            # Reviewer Notes
            notes_match = re.search(r'\*\*C\. Reviewer Notes[^\n]*\n([\s\S]*?)(?=\n---|####|\Z)', sb)
            notes = ""
            if notes_match:
                notes = notes_match.group(1).replace('_', '').strip()
            
            audit_results.append({
                "batch": bname,
                "case_id": case_id,
                "system": sys_name,
                "gate": gate_val,
                "d1": d1_val,
                "d2": d2_val,
                "d3": d3_val,
                "d4": d4_val,
                "d5": d5_val,
                "notes": notes,
                "issues": issues
            })

print(f"Total system evaluations audited: {len(audit_results)} (expected 160)")

# Summarize issues
all_issues = [r for r in audit_results if r["issues"]]
print(f"Total evaluations with issues: {len(all_issues)}")

for r in all_issues[:30]:
    print(f"[{r['batch']} | {r['case_id']} | {r['system']}]: {', '.join(r['issues'])}")

if len(all_issues) > 30:
    print(f"... and {len(all_issues) - 30} more.")

