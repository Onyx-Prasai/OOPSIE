evals_b7 = {
    ("bench-npm-03", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately diagnoses pnpm ERR_PNPM_NO_MATCHING_VERSION for sample-ui@7.8.9. Highlights non-existent version, typo, or unauthenticated private registry. Diagnostic registry check."
    },
    ("bench-npm-03", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound identification of unresolvable package version constraint. Advises checking package.json dependencies and pnpm-lock.yaml. Safe verification."
    },
    ("bench-npm-03", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly targets missing version 7.8.9 in registry. Recommends 'npm view sample-ui versions' to inspect available releases and check .npmrc for private registry config."
    },
    ("bench-npm-03", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly identifies version mismatch in pnpm install. Advises confirming published version numbers and updating package.json."
    },
    ("bench-npm-04", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly diagnoses missing relative module './config/runtime' imported from server.js. Advises checking file existence, extension, and working directory."
    },
    ("bench-npm-04", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound diagnosis of module resolution error. Recommends checking config/runtime.js path relative to server.js before modifying server startup."
    },
    ("bench-npm-04", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately targets relative import failure in Node.js. Highlights file extension and directory nesting. Safe non-destructive verification."
    },
    ("bench-npm-04", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Categorizes as build and analyzes missing ./config/runtime artifact in Docker/build output directory. Diagnostic verification."
    },
    ("bench-react-01", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly diagnoses TypeError in CartBadge.tsx:12 when reading .length of undefined array prop/state. Recommends optional chaining (items?.length) and default values. Safe UI test."
    },
    ("bench-react-01", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound identification of undefined array access in CartBadge. Analyzes asynchronous cart fetching and missing default prop. Diagnostic component test."
    },
    ("bench-react-01", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately targets undefined property read on line 12. Advises adding defensive fallback or optional chaining to avoid runtime rendering crash."
    },
    ("bench-react-01", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly analyzes CartBadge runtime crash. Scopes repair to checking cart items data flow from parent and providing fallback count."
    },
    ("bench-react-02", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly diagnoses 'Maximum update depth exceeded' in RouterView. Identifies self-referential route nesting or unconditional redirection in render. Diagnostic route check."
    },
    ("bench-react-02", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound identification of infinite re-render loop inside component rendered by RouterView. Advises moving state updates out of render body into useEffect or event handlers."
    },
    ("bench-react-02", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately targets React infinite render cycle in RouterView. Analyzes useEffect dependency array omission and synchronous state setters in render. Diagnostic browser test."
    },
    ("bench-react-02", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly diagnoses maximum update depth error. Recommends tracing state updates and ensuring state modifications are triggered conditionally or via user interaction."
    },
    ("bench-react-03", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly diagnoses React Hook order violation in ProfilePanel. Identifies hooks placed inside conditional 'if' statements or loops. Recommends moving all hooks to top level."
    },
    ("bench-react-03", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound identification of Rules of Hooks violation. Explains conditional returns preceding hook calls and conditional hook invocations. Safe browser reload verification."
    },
    ("bench-react-03", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately targets hook order change in ProfilePanel. Outlines top-level hook declaration requirement before early returns. Diagnostic component test."
    },
    ("bench-react-03", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly analyzes hook order instability between renders. Scopes repair to hoisting hook invocations to component root and placing conditions inside hook callbacks."
    }
}

import apply_eval_helpers as h
h.apply_evaluations_to_batch("docs/research/human_review/batch_07.md", evals_b7)
print("Batch 07 applied.")

