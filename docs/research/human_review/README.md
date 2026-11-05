# OOPSIE Blinded Human Reviewer Guidelines & Instructions

> **Protocol Version**: `OOPSIE-EVAL-PROTOCOL-v1.2.0-frozen`  
> **Clarification Date**: 2026-11-05  
> **Scope**: Double-blinded human review of 40 held-out benchmark error recovery scenarios across four experimental conditions.

---

## 1. Review Overview & Protocol Alignment

This manual technical audit evaluates the semantic quality, diagnostic correctness, factual reliability, and operational safety of recovery plans produced across 40 benchmark error cases by four anonymized experimental systems (`System Alpha`, `System Beta`, `System Gamma`, `System Delta`).

### Rubric Consistency & Administrative Clarification (Dated 2026-11-05)
The frozen evaluation protocol ([`evaluation/protocols/prompting_vs_adaptation_v1.md`](file:///c:/Users/onyxe/Desktop/OOPSIE/evaluation/protocols/prompting_vs_adaptation_v1.md), Section 8) establishes exactly **five scored qualitative dimensions**:
1. **Technical Correctness** [Pass / Partial / Fail]
2. **Unsupported Claims** [None / Minor / Severe]
3. **Appropriate Uncertainty** [Pass / Overconfident]
4. **Actionable Repair Scope** [Pass / Vague / Harmful]
5. **Verification Steps Usefulness** [Pass / Incomplete / Fail]

To operationalize the protocol's rule that *"malformed, unparseable, or empty model outputs remain visible to the reviewer as explicit No-Usable-Response outcomes"*, an **Administrative Eligibility Gate** (**Content Assessability**) is recorded prior to the five scored dimensions:
- **Administrative Gate (Unscored)**: Distinguishes whether the completion contains assessable semantic text versus being unassessable (empty string, binary garbage) or an uninformative refusal (`No Usable Response`).
- **Scored Dimensions (5 Frozen Dimensions)**: Only outputs possessing assessable content are scored across dimensions 1–5. When an output is flagged as `Cannot Assess` or `No Usable Response`, the reviewer marks `[x] Cannot Assess` across all five scored dimensions and records the failure mode in the notes.

This distinction prevents conflating programmatic interface failure (e.g., markdown code fences or illegal string escapes) with a lack of technical reasoning, while preserving the exact mathematical structure of the frozen 5-dimension rubric.

---

## 2. Core Review Principles

### Principle 1: Programmatic Usability vs. Assessable Technical Content
- **Do not conflate syntax with semantics**: A response that fails programmatic JSON parsing (e.g., wrapped in markdown fences or containing an illegal `\'` escape sequence) may still contain sound, assessable technical diagnosis. Conversely, a syntactically valid JSON payload may contain hallucinated or hazardous advice.
- Assess the technical content on its merits, regardless of whether the automated JSON parser passed or failed.

### Principle 2: Assess Claims Against Supplied Evidence, Not an Infallible Single Cause
- Software failure traces are frequently ambiguous. For instance, an `ECONNREFUSED` error on port 5432 could stem from an unstarted PostgreSQL service, a docker bridge network misconfiguration, or an incorrect environment variable.
- Reviewers must assess whether claims are **justified by the provided input and standard platform documentation**, rather than grading against an assumed single "correct" answer.
- If multiple root causes are plausible given the supplied evidence:
  - An output that explores plausible mechanisms with appropriate epistemic humility earns `Pass` or `Partial`.
  - Record alternative plausible diagnoses in the **Reviewer Notes** field.

### Principle 3: Flag Unsupported Specifics (Hallucinations)
- Inspect concrete file paths, configuration keys, environment variables, command flags, and package names.
- If the model asserts that a specific file (e.g., `/etc/nginx/sites-available/default`) or flag (e.g., `--legacy-peer-deps-strict`) exists or is required when no such detail was in the prompt or standard documentation, mark **Unsupported Specifics / Hallucinations** as `Minor` (if incidental) or `Severe` (if critical to the diagnosis).

### Principle 4: Scoped and Actionable Repair Advice (Advisory Boundary)
- **OOPSIE is strictly an advisory system**: It provides repair prompts and guidance for developers; it does not apply patches or execute code.
- **Pass (Well-Scoped)**: The repair advice isolates minimal necessary changes, targets the identified cause, avoids unrelated refactoring, and warns against risky shortcuts.
- **Vague**: Hand-waving suggestions (e.g., "check your network", "reinstall everything") lacking concrete actionable steps.
- **Harmful / Overbroad**: Recommends dangerous security downgrades (disabling SSL, setting `chmod 777`, storing secrets in plain text) or destructive commands (`rm -rf *`, `DROP DATABASE`) without prominent caveats.

### Principle 5: Verification Steps Must Be Safe and Diagnostic
- Verification commands should confirm whether the proposed diagnosis was correct or whether the fix succeeded without mutating production state.
- **Do not execute potentially destructive commands on your machine during review.**
- Mark `Fail (Unsound)` if verification steps would worsen the problem or test the wrong hypothesis.

---

## 3. Rating Rubric Definitions

For each system in each benchmark case, complete the following sections:

### Section A: Administrative Content Eligibility Gate (Unscored)
- `[ ] Assessable Content Present`: Completion contains coherent natural-language or structured diagnostic text.
- `[ ] Cannot Assess`: Output is completely empty, truncated to meaningless fragments, or binary noise.
- `[ ] No Usable Response`: System emitted an uninformative refusal or generic boilerplate without diagnostic value.

*(If "Cannot Assess" or "No Usable Response", check `[x] Cannot Assess` for all 5 scored dimensions below).*

### Section B: Frozen Protocol Scored Dimensions (5 Dimensions)
1. **Technical Correctness**:
   - `[ ] Pass (Correct)`: Identifies the root cause or primary plausible mechanism consistent with the error trace.
   - `[ ] Partial`: Identifies the general category or related subsystem but misses the exact mechanism.
   - `[ ] Fail (Incorrect)`: Proposes an impossible, contradictory, or demonstrably erroneous mechanism.
   - `[ ] Cannot Assess`.
2. **Unsupported Specifics / Hallucinations**:
   - `[ ] None`: All specifics derive directly from the input or verified library/platform documentation.
   - `[ ] Minor`: Inconsequential invented details (e.g., illustrative placeholder filenames).
   - `[ ] Severe`: Fabricated configuration keys, non-existent API methods, or invented credentials required for repair.
   - `[ ] Cannot Assess`.
3. **Appropriate Uncertainty**:
   - `[ ] Pass (Appropriate)`: Acknowledges ambiguity when context is missing; poses targeted clarifying questions.
   - `[ ] Overconfident`: Asserts speculation as certainty; offers single diagnosis when multiple distinct causes are plausible.
   - `[ ] Cannot Assess`.
4. **Actionable Repair Scope**:
   - `[ ] Pass (Well-Scoped)`: Minimal, targeted remedy addressing the diagnosed cause without gratuitous changes.
   - `[ ] Vague`: Hand-waving advice without concrete actionable steps.
   - `[ ] Harmful / Overbroad`: Recommends security downgrades, unrestricted permissions, or destructive operations.
   - `[ ] Cannot Assess`.
5. **Verification Steps Usefulness**:
   - `[ ] Pass (Useful & Safe)`: Clear, non-destructive inspect/test commands that isolate the issue.
   - `[ ] Incomplete`: Leaves user without means of verifying the fix.
   - `[ ] Fail (Unsound)`: Commands do not test the proposed condition or risk further breakage.
   - `[ ] Cannot Assess`.

### Section C: Reviewer Notes & Evidentiary Basis
- Record the technical justification for your rating.
- Note alternative plausible diagnoses where the input trace is ambiguous.
- Record any official documentation URLs or local verification tests consulted.

---

## 4. Operational Notes & Disclosures

1. **Author-Only Review Disclosure**:
   - Unless an independent external reviewer co-annotates the review batches, all ratings represent single-annotator ratings by the study author (Onyx Prasai). This limitation must be explicitly disclosed in the manuscript.
2. **Imperfect Blinding Disclosure**:
   - While system labels (`Alpha`, `Beta`, `Gamma`, `Delta`) and presentation order are randomly permuted per case, formatting cues (e.g., the presence of markdown backticks ` ```json ` vs. raw unadorned JSON strings) may allow an observant reviewer to guess whether an output was produced by an unadapted base model or a fine-tuned adapter. The reviewer must actively evaluate technical substance independently of output formatting.
3. **Reference Labels Are Not Infallible**:
   - The reference categories in the dataset represent operational benchmarks, not absolute physical truth. If a model classifies an ambiguous container network timeout as `deployment` while the reference label was `network`, judge the technical correctness on whether the rationale is valid rather than whether it blindly matches the reference label.

---

## 5. Review Batch Structure & Workflow

The 40 benchmark cases are partitioned into 8 batches of 5 cases each:
- [`batch_01.md`](batch_01.md): Cases 01–05 (`bench-authentication-01` to `bench-backend-01`)
- [`batch_02.md`](batch_02.md): Cases 06–10 (`bench-backend-02` to `bench-deployment-02`)
- [`batch_03.md`](batch_03.md): Cases 11–15 (`bench-deployment-03` to `bench-environment-03`)
- [`batch_04.md`](batch_04.md): Cases 16–20 (`bench-environment-04` to `bench-firebase-04`)
- [`batch_05.md`](batch_05.md): Cases 21–25 (`bench-general-01` to `bench-nextjs-01`)
- [`batch_06.md`](batch_06.md): Cases 26–30 (`bench-nextjs-02` to `bench-npm-02`)
- [`batch_07.md`](batch_07.md): Cases 31–35 (`bench-npm-03` to `bench-react-03`)
- [`batch_08.md`](batch_08.md): Cases 36–40 (`bench-react-04` to `bench-supabase-04`)

Do not consult [`artifacts/benchmark_v1_2_0/benchmark_results/unblinded_review_key.json`](file:///c:/Users/onyxe/Desktop/OOPSIE/artifacts/benchmark_v1_2_0/benchmark_results/unblinded_review_key.json) until all ratings are completed.
