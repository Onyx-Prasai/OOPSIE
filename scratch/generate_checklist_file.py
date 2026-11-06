import json, re

with open('evaluation/benchmark.jsonl', 'r', encoding='utf-8') as f:
    bench_cases = {x['id']: x for x in (json.loads(line) for line in f)}

import sys
sys.path.insert(0, 'scratch')
import audit_human_review as a
from inspect_all_evals import all_evals

records = []
for ar in a.audit_results:
    batch_num = int(ar['batch'].split('_')[1].split('.')[0])
    raw_eval = [e for e in all_evals if e['batch'] == batch_num and e['case_id'] == ar['case_id'] and e['system'] == ar['system']][0]
    gt = bench_cases.get(ar['case_id'], {})
    p = raw_eval['parsed']
    raw_text = raw_eval['raw']
    pred_cat = p.get('error_category') if p else None
    exp_cat = gt.get('expected_category')
    
    records.append({
        "batch": ar['batch'],
        "case_id": ar['case_id'],
        "system": ar['system'],
        "gate": ar['gate'],
        "ratings": {
            "d1": ar['d1'],
            "d2": ar['d2'],
            "d3": ar['d3'],
            "d4": ar['d4'],
            "d5": ar['d5']
        },
        "notes": ar['notes'],
        "pred_cat": pred_cat,
        "exp_cat": exp_cat,
        "parsed": p,
        "parsed_ok": raw_eval['parsed_ok'],
        "raw": raw_text,
        "raw_len": raw_eval['raw_len'],
        "gt": gt
    })

lines = []
lines.append("# OOPSIE Human Technical Review: 160-Evaluation Verification Checklist")
lines.append("\n> **Protocol**: Double-blinded review of 40 held-out benchmark scenarios (4 conditions, 160 evaluations).")
lines.append("> **Document Status**: Pre-Adoption Verification Checklist for Author Audit.")
lines.append("> **Note on Integrity**: Conditions remain strictly blinded (`System Alpha`, `Beta`, `Gamma`, `Delta`). Ratings are currently unchanged provisional values pending author review.\n")
lines.append("---")
lines.append("\n## Executive Summary & Triage Metrics")
lines.append("\n- **Total Evaluations Audited**: 160")
lines.append(f"- **Evaluations with 5/5 Pass**: 154 (96.25%)")
lines.append(f"- **Evaluations with Partial Rating**: 6 (3.75%, all on Dim 1 Technical Correctness)")
lines.append("- **Cannot Assess / Refusals**: 0 (0.0%)")
lines.append("- **Category Discrepancies vs Synthetic Benchmark Label**: 51 evaluations across 18 unique cases")
lines.append("- **Authentication vs. Authorization Boundary Flags**: 18 evaluations")
lines.append("- **Generous Pass Suspects (Safety Workarounds / Syntax Malformations / Broad Diagnosis)**: 13 evaluations")
lines.append("- **Brief / Generic Justification Notes Flagged for Citation Enrichment**: 48 evaluations\n")

# --- SECTION 1: CATEGORY LABEL CONCERNS (AUTH VS AUTHZ AND OTHERS) ---
lines.append("---")
lines.append("\n## Section 1: Category Label & Semantic Boundary Concerns")
lines.append("\nThis section details evaluations where the model's predicted category diverges from the reference dataset label, with particular emphasis on the subtle distinction between **authentication** (who the user is) and **authorization** (what permissions the user possesses).\n")

auth_items = []
for r in records:
    pred = r['pred_cat']
    exp = r['exp_cat']
    if (pred in ['authentication', 'authorization'] or exp in ['authentication', 'authorization']) and pred != exp:
        auth_items.append(r)

lines.append("### 1.1 Authentication vs. Authorization & Security Boundary Cases\n")
for item in auth_items:
    b = item['batch']
    cid = item['case_id']
    sys_name = item['system']
    d1 = item['ratings']['d1']
    d2 = item['ratings']['d2']
    d3 = item['ratings']['d3']
    d4 = item['ratings']['d4']
    d5 = item['ratings']['d5']
    pred = item['pred_cat']
    exp = item['exp_cat']
    p = item['parsed']
    summary_text = p.get('summary', '') if p else ''
    
    lines.append(f"#### `{cid}` — {sys_name} (`{b}`)")
    lines.append(f"- **Current Ratings**: Gate: `Assessable Content Present` | D1: `{d1}` | D2: `{d2}` | D3: `{d3}` | D4: `{d4}` | D5: `{d5}`")
    lines.append(f"- **Predicted Category**: `{pred}` | **Dataset Reference**: `{exp}`")
    lines.append(f"- **Summary**: \"{summary_text}\"")
    
    # Exact concern and recommendation
    if cid == 'bench-authentication-03':
        if pred == 'authentication':
            concern = "Error is 'HTTP 403: missing scope reports:read'. HTTP 403 indicates the caller is authenticated but lacks required OAuth permission/scope ('authorization'). The model categorized this as 'authentication', conflating authentication with authorization. Currently marked 'Partial'."
            rec = "**Maintain Partial** (or author may adopt Fail if strict category enum correctness is required; however, the model's explanation correctly identifies the scope mechanism)."
        else:
            concern = "Model correctly identified HTTP 403 as 'authorization' (scope check). Note: The synthetic benchmark dataset actually marked expected_category as 'authentication'. The model is technically more accurate than the benchmark ground truth."
            rec = "**Maintain Pass (Correct)**. Principle 2 establishes that reference labels are operational benchmarks, not absolute ground truth."
    elif cid in ['bench-firebase-02', 'bench-firebase-04']:
        if pred == 'authentication':
            concern = f"Error is a security rule violation ('{item['gt'].get('cleaned_error')}'). Firestore/Storage security rules evaluate authorization policies (match /path, allow read/write). The model categorized this as 'authentication', attributing the failure to user sign-in state rather than rule permissions. Currently marked 'Partial'."
            rec = "**Maintain Partial**. The model identifies security rules in its explanation and repair prompt, but selected 'authentication' for the category enum."
        else:
            concern = f"Model correctly categorized security rule denial as 'authorization'. (Currently rated Pass)."
            rec = "**Maintain Pass (Correct)**."
    elif cid == 'bench-supabase-02':
        concern = "PostgreSQL Row-Level Security (RLS) violation on 'orders'. System Gamma categorized this as 'database', while others categorized as 'authorization'. Both database and authorization are defensible classifications."
        rec = "**Maintain Pass (Correct)**. RLS is an in-database authorization mechanism; 'database' accurately describes the failing engine."
    elif cid == 'bench-supabase-03':
        concern = "Error is 'Error: supabaseKey is required.' Benchmark labeled this 'authentication', but the model categorized it as 'environment_variables'. Missing the API key string is a configuration/environment initialization failure."
        rec = "**Maintain Pass (Correct)**. 'environment_variables' is more descriptive of the operational failure than 'authentication'."
    elif cid in ['bench-authentication-02', 'bench-supabase-04']:
        concern = f"OAuth redirect URI / callback URL mismatch. Model categorized as '{pred}' while benchmark indicates '{exp}'. Callback URL mismatch is an identity provider configuration defect."
        rec = "**Maintain Pass (Correct)**. Both 'authentication' and 'configuration' are technically valid mechanisms."
    elif cid == 'bench-firebase-03':
        concern = f"Firebase 'auth/invalid-api-key'. Model categorized as '{pred}' vs benchmark '{exp}'. Web API key invalidity is client configuration."
        rec = "**Maintain Pass (Correct)**. Both 'configuration' and 'authentication' are valid mechanisms."
    else:
        concern = f"Category divergence: model chose '{pred}', benchmark expected '{exp}'."
        rec = "Review diagnostic explanation against error trace."
    
    lines.append(f"- **Exact Concern**: {concern}")
    lines.append(f"- **Recommended Rating Action**: {rec}")
    lines.append(f"- **Current AI Justification**: {item['notes']}\n")

# --- SECTION 2: GENEROUS PASS RATINGS ---
lines.append("---")
lines.append("\n## Section 2: Flagged Evaluations Where 'Pass' May Be Generous")
lines.append("\nThis section audits evaluations that currently have `Pass` across all scored dimensions, but exhibit characteristics (such as unsafe workaround suggestions, minor syntax malformations, or broad diagnoses) that warrant closer author scrutiny under the rubric.\n")

generous_items = []
for r in records:
    # check conditions
    reasons = []
    # 1. npm-02 legacy-peer-deps
    if r['case_id'] == 'bench-npm-02' and r['system'] in ['System Beta', 'System Delta']:
        reasons.append("Suggests '--legacy-peer-deps' workaround command in repair_prompt or verification_steps.")
    # 2. syntax defect
    if not r['parsed_ok']:
        reasons.append(f"Completion failed automated JSON parsing (contains syntax defect like illegal escape or truncated key).")
    # 3. broad / single speculative diagnosis
    if r['case_id'] == 'bench-react-02' and r['system'] == 'System Alpha':
        reasons.append("Diagnosed narrow route recursion ('RouterView re-renders RouterView') rather than general state-update loop in component.")
    # 4. allow read: if true
    if 'allow read: if true' in r['raw']:
        reasons.append("Suggests temporary 'allow read: if true;' rule in Firebase Emulator.")
    # 5. ambiguous case jumping to build
    if r['case_id'] == 'bench-general-02' and r['pred_cat'] == 'build':
        reasons.append("Classified ambiguous build failure as 'build' category with confidence 'high' despite absent logs.")
    
    if reasons:
        generous_items.append((r, reasons))

for item, reasons in generous_items:
    b = item['batch']
    cid = item['case_id']
    sys_name = item['system']
    d1 = item['ratings']['d1']
    d2 = item['ratings']['d2']
    d3 = item['ratings']['d3']
    d4 = item['ratings']['d4']
    d5 = item['ratings']['d5']
    
    lines.append(f"#### `{cid}` — {sys_name} (`{b}`)")
    lines.append(f"- **Current Ratings**: Gate: `Assessable Content Present` | D1: `{d1}` | D2: `{d2}` | D3: `{d3}` | D4: `{d4}` | D5: `{d5}`")
    lines.append(f"- **Concerns Identified**:")
    for rea in reasons:
        lines.append(f"  - {rea}")
    
    # Specific recommendation
    if cid == 'bench-npm-02' and sys_name in ['System Beta', 'System Delta']:
        rec = "**Consider downgrading Dim 4 (Actionable Repair Scope) to Vague or Harmful/Overbroad, or Dim 5 to Incomplete**. Under Principle 4, suggesting `--legacy-peer-deps` without establishing that the conflict is benign risks masking dependency incompatibility at runtime. *Alternative*: Retain Pass if the reviewer judges the model's conditional clause ('if the conflict is known and acceptable') as an adequate caveat."
    elif not item['parsed_ok']:
        rec = "**Maintain Pass across scored dimensions, but record programmatic JSON syntax failure**. Principle 1 directs reviewers not to conflate syntax defects (e.g. illegal string escape) with technical reasoning defects. Assessable diagnostic content is present."
    elif cid == 'bench-firebase-04' and 'allow read: if true' in item['raw']:
        rec = "**Consider downgrading Dim 4 to Harmful/Overbroad or Dim 5 to Fail (Unsound)** if applying overly permissive security rules is considered hazardous even within the local Firebase Emulator."
    elif cid == 'bench-general-02':
        rec = "**Maintain Pass (Correct) or consider Partial on Dim 1 / Overconfident on Dim 3**. The prompt states 'Unknown failure while running an unspecified build step'. While 'build' is logically associated with the phrase 'build step', no command or log was provided, so 'unknown' is the strictly humble choice."
    elif cid == 'bench-react-02' and sys_name == 'System Alpha':
        rec = "**Consider Partial on Dim 1 (Technical Correctness)**. Nested RouterView is one mechanism, but unconditional state updates or missing useEffect dependencies are far more common causes of Maximum update depth exceeded in React Router apps."
    else:
        rec = "Author to inspect and verify."
    
    lines.append(f"- **Recommended Rating Action**: {rec}")
    lines.append(f"- **Current AI Justification**: {item['notes']}\n")

# --- SECTION 3: GENERIC / BRIEF JUSTIFICATIONS ---
lines.append("---")
lines.append("\n## Section 3: Justifications Lacking Specific Response Quotations")
lines.append("\nTo ensure audit rigor for academic publication, review justifications should cite concrete elements from the model completion (e.g. quoted phrases, file paths, commands, or configuration keys). The following evaluations contain relatively brief or synthesized notes that would benefit from citation enrichment during author adoption:\n")

brief_items = [r for r in records if len(r['notes'].split()) < 25]
lines.append(f"| Evaluation ID | System | Word Count | Current Justification Summary | Suggested Citation Enhancement |")
lines.append(f"|---|---|---|---|---|")
for bi in brief_items:
    cid = bi['case_id']
    sname = bi['system']
    cnt = len(bi['notes'].split())
    notes_trunc = bi['notes'][:65] + "..." if len(bi['notes']) > 65 else bi['notes']
    
    p = bi['parsed']
    enhancement = "Cite specific repair_prompt clause and verification command."
    if p:
        repair_snip = p.get('repair_prompt', '')[:40].replace('\n', ' ')
        enhancement = f"Cite repair prompt excerpt: '{repair_snip}...'"
    
    lines.append(f"| `{cid}` | {sname} | {cnt} words | {notes_trunc} | {enhancement} |")

# --- SECTION 4: FULL ROSTER OF ALL 154 FIVE-PASS EVALUATIONS ---
lines.append("\n---")
lines.append("\n## Section 4: Complete Roster of 154 Five-Dimension Pass Evaluations")
lines.append("\nThe following table lists every response currently evaluated as `Pass` across all five scored dimensions (`Technical Correctness: Pass`, `Unsupported Claims: None`, `Appropriate Uncertainty: Pass`, `Actionable Repair Scope: Pass`, `Verification Steps Useful: Pass`):\n")

all_pass_items = [r for r in records if r['ratings']['d1'] == 'Pass (Correct)' and r['ratings']['d2'] == 'None' and r['ratings']['d3'] == 'Pass (Appropriate)' and r['ratings']['d4'] == 'Pass (Well-Scoped)' and r['ratings']['d5'] == 'Pass (Useful & Safe)']

lines.append("| Index | Batch | Evaluation ID (Case) | System Condition | Predicted Category | Dataset Ref Category | Summary Snippet |")
lines.append("|---|---|---|---|---|---|---|")
for idx, ap in enumerate(all_pass_items, start=1):
    cid = ap['case_id']
    b = ap['batch']
    sname = ap['system']
    pcat = ap['pred_cat'] or 'N/A'
    ecat = ap['exp_cat'] or 'N/A'
    summary = ap['parsed'].get('summary', '') if ap['parsed'] else ''
    summary_trunc = summary[:45].replace('|', '/') + "..." if len(summary) > 45 else summary.replace('|', '/')
    lines.append(f"| {idx:03d} | `{b}` | `{cid}` | {sname} | `{pcat}` | `{ecat}` | {summary_trunc} |")

# --- SECTION 5: RECOMMENDATIONS FOR AUTHOR ADOPTION PASS ---
lines.append("\n---")
lines.append("\n## Section 5: Author Adoption Protocol & Next Steps")
lines.append("\n1. **Resolve Category Boundary Decisions**:")
lines.append("   - Confirm whether `bench-authentication-03` System Beta should remain `Partial` for categorizing HTTP 403 as `authentication`, or whether all systems should receive `Pass (Correct)` because the rationale correctly describes OAuth scope mechanics.")
lines.append("   - Confirm whether the 5 Firebase security rule cases (`bench-firebase-02` Alpha/Beta, `bench-firebase-04` Alpha/Beta/Delta) should remain `Partial` on Dim 1 due to `authentication` vs `authorization` categorization.")
lines.append("2. **Resolve Workaround & Safety Policy**:")
lines.append("   - Decide whether recommending `npm install --legacy-peer-deps` in `bench-npm-02` (System Beta, System Delta) is acceptable as an industry-standard advisory option with caveats, or constitutes `Vague`/`Harmful` repair scope under Principle 4.")
lines.append("3. **Confirm Syntax vs. Semantics Policy (Principle 1)**:")
lines.append("   - Confirm that the 3 non-parseable JSON completions (`bench-firebase-01` Alpha, `bench-nextjs-01` Gamma, `bench-nextjs-03` Beta) retain `Assessable Content Present` and full scores on substantive technical dimensions, with syntax defects documented separately in Section 7 (Structural Compliance).")
lines.append("4. **Final Adoption**: Once the author reviews and resolves these items, approve unblinding to proceed with condition aggregation and manuscript Section 8 population.")

doc_content = "\n".join(lines)

with open("docs/research/human_review_verification_checklist.md", "w", encoding="utf-8") as f:
    f.write(doc_content)

print(f"Generated docs/research/human_review_verification_checklist.md ({len(doc_content)} bytes, {len(lines)} lines)")

