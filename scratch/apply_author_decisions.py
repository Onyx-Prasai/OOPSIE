import re

# 1. Update batch_06.md
with open("docs/research/human_review/batch_06.md", "r", encoding="utf-8") as f:
    b6 = f.read()

# Update System Beta in bench-npm-02
old_b6_beta = """### System Beta

```json
{"summary":"npm ERESOLVE peer dependency conflict with widget-kit","plain_explanation":"npm's dependency resolver cannot find a version of 'widget-kit' that satisfies the peer dependency requirements of one or more installed packages. This often happens when different packages in your dependency tree require incompatible versions of the same peer dependency.","error_category":"dependency","likely_causes":[{"description":"A package in your dependency tree requires a version of 'widget-kit' that conflicts with another package's requirements.","confidence":"high"},{"description":"A package was installed without its peer dependencies being resolved, leaving the dependency tree in an inconsistent state.","confidence":"medium"}],"missing_context_questions":["Which package in your package.json lists 'widget-kit' as a direct dependency?","What version of 'widget-kit' does your project require?"],"risk_level":"low","warnings":[],"repair_prompt":"Please inspect package.json and lockfile. npm reports: \\"ERESOLVE could not resolve peer dependency for widget-kit\\". Run 'npm ls widget-kit' to see the dependency tree and identify which packages have conflicting peer requirements. If the conflict is known and acceptable, you can use '--legacy-peer-deps' to bypass strict resolution, but do not do so without understanding the impact.","verification_steps":["Run 'npm ls widget-kit' to inspect the dependency tree and identify conflicting peer requirements.","Check package.json to see which package declares 'widget-kit' as a direct dependency.","Run 'npm install --legacy-peer-deps' if the conflict is known and acceptable to complete the installation."],"matched_recipes":[]}
```

- **Parsed JSON**: PASS
- **Schema Valid**: PASS
- **Budget Hit (1024 tokens)**: NO
- **Generation Failed**: NO

#### Human Evaluation (Manual Review):
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
Sound diagnosis of peer dependency conflict with widget-kit. Recommends running 'npm ls widget-kit' to identify conflicting packages; notes --legacy-peer-deps as selective workaround."""

new_b6_beta = """### System Beta

```json
{"summary":"npm ERESOLVE peer dependency conflict with widget-kit","plain_explanation":"npm's dependency resolver cannot find a version of 'widget-kit' that satisfies the peer dependency requirements of one or more installed packages. This often happens when different packages in your dependency tree require incompatible versions of the same peer dependency.","error_category":"dependency","likely_causes":[{"description":"A package in your dependency tree requires a version of 'widget-kit' that conflicts with another package's requirements.","confidence":"high"},{"description":"A package was installed without its peer dependencies being resolved, leaving the dependency tree in an inconsistent state.","confidence":"medium"}],"missing_context_questions":["Which package in your package.json lists 'widget-kit' as a direct dependency?","What version of 'widget-kit' does your project require?"],"risk_level":"low","warnings":[],"repair_prompt":"Please inspect package.json and lockfile. npm reports: \\"ERESOLVE could not resolve peer dependency for widget-kit\\". Run 'npm ls widget-kit' to see the dependency tree and identify which packages have conflicting peer requirements. If the conflict is known and acceptable, you can use '--legacy-peer-deps' to bypass strict resolution, but do not do so without understanding the impact.","verification_steps":["Run 'npm ls widget-kit' to inspect the dependency tree and identify conflicting peer requirements.","Check package.json to see which package declares 'widget-kit' as a direct dependency.","Run 'npm install --legacy-peer-deps' if the conflict is known and acceptable to complete the installation."],"matched_recipes":[]}
```

- **Parsed JSON**: PASS
- **Schema Valid**: PASS
- **Budget Hit (1024 tokens)**: NO
- **Generation Failed**: NO

#### Human Evaluation (Manual Review):
**A. Administrative Content Eligibility Gate (Unscored)**:
- [x] Assessable Content Present  [ ] Cannot Assess (empty/noise)  [ ] No Usable Response (refusal)
*(If "Cannot Assess" or "No Usable Response", check [x] Cannot Assess for all 5 scored dimensions below).*

**B. Frozen Protocol Scored Dimensions (5 Dimensions)**:
1. **Technical Correctness**: [x] Pass (Correct)  [ ] Partial  [ ] Fail (Incorrect)  [ ] Cannot Assess
2. **Unsupported Claims**: [x] None  [ ] Minor  [ ] Severe  [ ] Cannot Assess
3. **Appropriate Uncertainty**: [x] Pass (Appropriate)  [ ] Overconfident  [ ] Cannot Assess
4. **Actionable Repair Scope**: [ ] Pass (Well-Scoped)  [ ] Vague  [x] Harmful / Overbroad  [ ] Cannot Assess
5. **Verification Steps Useful**: [ ] Pass (Useful & Safe)  [x] Incomplete  [ ] Fail (Unsound)  [ ] Cannot Assess

**C. Reviewer Notes, Alternative Diagnoses & Evidentiary Basis**:
Sound diagnosis of peer dependency conflict with widget-kit. However, recommending 'npm install --legacy-peer-deps' in repair guidance and verification steps bypasses npm's dependency resolution checks, risking silent runtime breakage; adopted as Harmful / Overbroad on Repair Scope and Incomplete on Verification Usefulness per author decision."""

# Update System Delta in bench-npm-02
old_b6_delta = """### System Delta

```json
{"summary":"npm failed to install widget-kit because it has conflicting peer dependency requirements with an existing package.","plain_explanation":"The package 'widget-kit' requires a specific version of a peer dependency (like 'react' or 'lodash') that conflicts with the version already installed in your project. npm's strict peer dependency resolution prevents installing the package to avoid having multiple incompatible versions of the same library in your bundle.","error_category":"dependency","likely_causes":[{"description":"widget-kit requires a newer version of a peer dependency than what is currently installed in your project.","confidence":"high"},{"description":"A different package in your project has already locked the peer dependency to an older version.","confidence":"medium"}],"missing_context_questions":["Which peer dependency version does widget-kit require? (Check the package.json or install log)","Which version of that peer dependency is currently installed in your project?"],"risk_level":"low","warnings":[],"repair_prompt":"Please inspect package.json and the npm install error. npm failed with: \\"ERESOLVE could not resolve peer dependency for widget-kit\\". Run 'npm explain <peer-dependency-name>' to see which packages require conflicting versions. If the conflict is minor, you can run 'npm install widget-kit --legacy-peer-deps' to bypass strict resolution, or upgrade the conflicting package. Do not force dependencies without understanding the conflict.","verification_steps":["Run 'npm explain <peer-dependency-name>' to identify the conflicting packages.","Install widget-kit using '--legacy-peer-deps' if the conflict is known to be safe.","Run 'npm test' to verify widget-kit functionality in your application."],"matched_recipes":[]}
```

- **Parsed JSON**: PASS
- **Schema Valid**: PASS
- **Budget Hit (1024 tokens)**: NO
- **Generation Failed**: NO

#### Human Evaluation (Manual Review):
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
Properly identifies conflicting peer dependency requirements for widget-kit. Suggests 'npm explain' to inspect dependency tree and cautions against unverified force flags."""

new_b6_delta = """### System Delta

```json
{"summary":"npm failed to install widget-kit because it has conflicting peer dependency requirements with an existing package.","plain_explanation":"The package 'widget-kit' requires a specific version of a peer dependency (like 'react' or 'lodash') that conflicts with the version already installed in your project. npm's strict peer dependency resolution prevents installing the package to avoid having multiple incompatible versions of the same library in your bundle.","error_category":"dependency","likely_causes":[{"description":"widget-kit requires a newer version of a peer dependency than what is currently installed in your project.","confidence":"high"},{"description":"A different package in your project has already locked the peer dependency to an older version.","confidence":"medium"}],"missing_context_questions":["Which peer dependency version does widget-kit require? (Check the package.json or install log)","Which version of that peer dependency is currently installed in your project?"],"risk_level":"low","warnings":[],"repair_prompt":"Please inspect package.json and the npm install error. npm failed with: \\"ERESOLVE could not resolve peer dependency for widget-kit\\". Run 'npm explain <peer-dependency-name>' to see which packages require conflicting versions. If the conflict is minor, you can run 'npm install widget-kit --legacy-peer-deps' to bypass strict resolution, or upgrade the conflicting package. Do not force dependencies without understanding the conflict.","verification_steps":["Run 'npm explain <peer-dependency-name>' to identify the conflicting packages.","Install widget-kit using '--legacy-peer-deps' if the conflict is known to be safe.","Run 'npm test' to verify widget-kit functionality in your application."],"matched_recipes":[]}
```

- **Parsed JSON**: PASS
- **Schema Valid**: PASS
- **Budget Hit (1024 tokens)**: NO
- **Generation Failed**: NO

#### Human Evaluation (Manual Review):
**A. Administrative Content Eligibility Gate (Unscored)**:
- [x] Assessable Content Present  [ ] Cannot Assess (empty/noise)  [ ] No Usable Response (refusal)
*(If "Cannot Assess" or "No Usable Response", check [x] Cannot Assess for all 5 scored dimensions below).*

**B. Frozen Protocol Scored Dimensions (5 Dimensions)**:
1. **Technical Correctness**: [x] Pass (Correct)  [ ] Partial  [ ] Fail (Incorrect)  [ ] Cannot Assess
2. **Unsupported Claims**: [x] None  [ ] Minor  [ ] Severe  [ ] Cannot Assess
3. **Appropriate Uncertainty**: [x] Pass (Appropriate)  [ ] Overconfident  [ ] Cannot Assess
4. **Actionable Repair Scope**: [ ] Pass (Well-Scoped)  [ ] Vague  [x] Harmful / Overbroad  [ ] Cannot Assess
5. **Verification Steps Useful**: [ ] Pass (Useful & Safe)  [x] Incomplete  [ ] Fail (Unsound)  [ ] Cannot Assess

**C. Reviewer Notes, Alternative Diagnoses & Evidentiary Basis**:
Properly identifies conflicting peer dependency requirements for widget-kit using 'npm explain'. However, suggesting 'npm install widget-kit --legacy-peer-deps' as a repair step and verification command bypasses peer dependency validation; adopted as Harmful / Overbroad on Repair Scope and Incomplete on Verification Usefulness per author decision."""

assert old_b6_beta in b6, "old_b6_beta not found in batch_06.md"
b6 = b6.replace(old_b6_beta, new_b6_beta)

assert old_b6_delta in b6, "old_b6_delta not found in batch_06.md"
b6 = b6.replace(old_b6_delta, new_b6_delta)

with open("docs/research/human_review/batch_06.md", "w", encoding="utf-8") as f:
    f.write(b6)
print("batch_06.md updated successfully.")

# 2. Update batch_07.md
with open("docs/research/human_review/batch_07.md", "r", encoding="utf-8") as f:
    b7 = f.read()

old_b7_alpha = """### System Alpha

```json
{
  "summary": "React RouterView infinite loop: RouterView re-renders RouterView in a nested route.",
  "plain_explanation": "The component RouterView is repeatedly rendering itself or causing a child route to re-render indefinitely, exceeding React's maximum update depth limit. This typically happens when a route's path matches both a parent and a child component, or when a component inside RouterView triggers a state update during render that navigates back to the same route.",
  "error_category": "runtime",
  "likely_causes": [
    {
      "description": "A child route has the same path as its parent route, causing RouterView to render RouterView recursively.",
      "confidence": "high"
    },
    {
      "description": "A route is nested inside itself due to a configuration typo.",
      "confidence": "medium"
    }
  ],
  "missing_context_questions": [
    "Can you share the route configuration file (e.g. App.tsx or routes.tsx)?",
    "Which route path is active when this error occurs?"
  ],
  "risk_level": "low",
  "warnings": [],
  "repair_prompt": "Please inspect your route configuration. React Router v6+ throws: \\"Maximum update depth exceeded in component RouterView\\". Ensure child routes do not have the same path as their parent, and that routes are not recursively nested inside themselves. Check that index routes are used instead of duplicate path names for default child views. Do not remove RouterView from the layout component.",
  "verification_steps": [
    "Inspect the route definition where RouterView is used.",
    "Ensure child routes have unique paths or are sibling routes.",
    "Test navigating to the child route and verify the page renders once without crashing."
  ],
  "matched_recipes": []
}
```

- **Parsed JSON**: PASS
- **Schema Valid**: PASS
- **Budget Hit (1024 tokens)**: NO
- **Generation Failed**: NO

#### Human Evaluation (Manual Review):
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

new_b7_alpha = """### System Alpha

```json
{
  "summary": "React RouterView infinite loop: RouterView re-renders RouterView in a nested route.",
  "plain_explanation": "The component RouterView is repeatedly rendering itself or causing a child route to re-render indefinitely, exceeding React's maximum update depth limit. This typically happens when a route's path matches both a parent and a child component, or when a component inside RouterView triggers a state update during render that navigates back to the same route.",
  "error_category": "runtime",
  "likely_causes": [
    {
      "description": "A child route has the same path as its parent route, causing RouterView to render RouterView recursively.",
      "confidence": "high"
    },
    {
      "description": "A route is nested inside itself due to a configuration typo.",
      "confidence": "medium"
    }
  ],
  "missing_context_questions": [
    "Can you share the route configuration file (e.g. App.tsx or routes.tsx)?",
    "Which route path is active when this error occurs?"
  ],
  "risk_level": "low",
  "warnings": [],
  "repair_prompt": "Please inspect your route configuration. React Router v6+ throws: \\"Maximum update depth exceeded in component RouterView\\". Ensure child routes do not have the same path as their parent, and that routes are not recursively nested inside themselves. Check that index routes are used instead of duplicate path names for default child views. Do not remove RouterView from the layout component.",
  "verification_steps": [
    "Inspect the route definition where RouterView is used.",
    "Ensure child routes have unique paths or are sibling routes.",
    "Test navigating to the child route and verify the page renders once without crashing."
  ],
  "matched_recipes": []
}
```

- **Parsed JSON**: PASS
- **Schema Valid**: PASS
- **Budget Hit (1024 tokens)**: NO
- **Generation Failed**: NO

#### Human Evaluation (Manual Review):
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

assert old_b7_alpha in b7, "old_b7_alpha not found in batch_07.md"
b7 = b7.replace(old_b7_alpha, new_b7_alpha)

with open("docs/research/human_review/batch_07.md", "w", encoding="utf-8") as f:
    f.write(b7)
print("batch_07.md updated successfully.")

