with open("docs/research/human_review/batch_07.md", "r", encoding="utf-8") as f:
    b7 = f.read()

old_b7_eval = """#### Human Evaluation (Manual Review):
**A. Administrative Content Eligibility Gate (Unscored)**:
- [x] Assessable Content Present  [ ] Cannot Assess (empty/noise)  [ ] No Usable Response (refusal)
*(If "Cannot Assess" or "No Usable Response", check [x] Cannot Assess for all 5 scored dimensions below).*

**B. Frozen Protocol Scored Dimensions (5 Dimensions)**:
1. **Technical Correctness**: [x] Pass (Correct)  [ ] Partial  [ ] Fail (Incorrect)  [ ] Cannot Assess
2. **Unsupported Claims**: [x] None  [ ] Minor  [ ] Severe  [ ] Cannot Assess
3. **Appropriate Uncertainty**: [x] Pass (Appropriate)  [ ] Overconfident  [ ] Cannot Assess
4. **Actionable Repair Scope**: [x] Pass (Well-Scoped)  [ ] Vague  [ ] Harmful / Overbroad  [ ] Cannot Assess
5. **Verification Steps Useful**: [x] Pass (Useful & Safe)  [ ] Incomplete  [ ] Fail (Unsound)  [ ] Cannot Assess

**C. Reviewer Notes, Alternative Diagnoses & Evidentiary Basis**:
Correctly diagnoses 'Maximum update depth exceeded' in RouterView. Identifies self-referential route nesting or unconditional redirection in render. Diagnostic route check."""

new_b7_eval = """#### Human Evaluation (Manual Review):
**A. Administrative Content Eligibility Gate (Unscored)**:
- [x] Assessable Content Present  [ ] Cannot Assess (empty/noise)  [ ] No Usable Response (refusal)
*(If "Cannot Assess" or "No Usable Response", check [x] Cannot Assess for all 5 scored dimensions below).*

**B. Frozen Protocol Scored Dimensions (5 Dimensions)**:
1. **Technical Correctness**: [ ] Pass (Correct)  [x] Partial  [ ] Fail (Incorrect)  [ ] Cannot Assess
2. **Unsupported Claims**: [x] None  [ ] Minor  [ ] Severe  [ ] Cannot Assess
3. **Appropriate Uncertainty**: [ ] Pass (Appropriate)  [x] Overconfident  [ ] Cannot Assess
4. **Actionable Repair Scope**: [x] Pass (Well-Scoped)  [ ] Vague  [ ] Harmful / Overbroad  [ ] Cannot Assess
5. **Verification Steps Useful**: [x] Pass (Useful & Safe)  [ ] Incomplete  [ ] Fail (Unsound)  [ ] Cannot Assess

**C. Reviewer Notes, Alternative Diagnoses & Evidentiary Basis**:
Identifies 'Maximum update depth exceeded' in RouterView, but asserts self-referential route recursion as the sole high-confidence explanation. Omitting the primary mechanism (unconditional state updates or missing useEffect dependencies inside rendered child components) warrants Partial on Technical Correctness and Overconfident on Appropriate Uncertainty per author decision."""

assert old_b7_eval in b7, "old_b7_eval not found in batch_07.md"
b7 = b7.replace(old_b7_eval, new_b7_eval)

with open("docs/research/human_review/batch_07.md", "w", encoding="utf-8") as f:
    f.write(b7)

print("batch_07.md updated successfully.")

