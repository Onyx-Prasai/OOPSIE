evals_b6 = {
    ("bench-nextjs-02", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly diagnoses missing default React component export in /reports/page.tsx. Scopes repair to adding 'export default function ReportsPage()'. Safe dev server test verification."
    },
    ("bench-nextjs-02", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound identification of invalid Next.js page export. Explains named vs default export requirements for page routes. Diagnostic verification."
    },
    ("bench-nextjs-02", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately targets /reports route export failure. Advises verifying default component export and valid JSX return. Safe dev server reload."
    },
    ("bench-nextjs-02", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly identifies non-component default export in Next.js route file. Scopes repair cleanly to exporting a valid React component."
    },
    ("bench-nextjs-03", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly diagnoses Server Component importing client-only hook (useEffect). Recommends isolating client logic into a separate Client Component or adding 'use client'."
    },
    ("bench-nextjs-03", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Contains malformed key name in raw JSON but diagnostic content is fully assessable. Accurately explains Server Component lifecycle and necessity of 'use client' directive for hooks."
    },
    ("bench-nextjs-03", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound diagnosis of useEffect usage in Next.js Server Component boundary. Advises adding 'use client' at the file top with safe verification in dev server."
    },
    ("bench-nextjs-03", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly analyzes React hook restrictions in Next.js Server Components. Scopes repair to adding 'use client' directive or extracting stateful logic."
    },
    ("bench-nextjs-04", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly diagnoses static site generation failure for /catalog due to missing required dynamic parameter. Recommends implementing generateStaticParams() or getStaticPaths()."
    },
    ("bench-nextjs-04", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound identification of missing route parameters during SSG. Advises verifying dynamic route segment ([id]/[slug]) and providing generateStaticParams."
    },
    ("bench-nextjs-04", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately targets missing route parameter in static generation. Recommends checking dynamic route definition and verifying build output."
    },
    ("bench-nextjs-04", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Categorizes as configuration and correctly identifies dynamic route parameter deficiency for static /catalog route. Diagnostic build verification."
    },
    ("bench-npm-01", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately diagnoses missing 'nanoid' package in /app/src/id.mjs. Scopes repair to installing dependency via npm install nanoid and verifying package.json."
    },
    ("bench-npm-01", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound identification of uninstalled 'nanoid' dependency. Advises checking package.json dependencies and running package installation."
    },
    ("bench-npm-01", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly targets module resolution failure for nanoid. Advises verifying node_modules and checking package manager lockfile consistency."
    },
    ("bench-npm-01", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly analyzes 'Cannot find package nanoid'. Recommends verifying dependency manifest and re-executing import after installation."
    },
    ("bench-npm-02", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly identifies npm ERESOLVE peer dependency conflict for 'widget-kit'. Prominently warns against using --force or --legacy-peer-deps blindly. Diagnostic npm list verification."
    },
    ("bench-npm-02", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound diagnosis of peer dependency conflict with widget-kit. Recommends running 'npm ls widget-kit' to identify conflicting packages; notes --legacy-peer-deps as selective workaround."
    },
    ("bench-npm-02", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately diagnoses npm peer dependency resolution failure. Cautions that forcing installation can lead to runtime breakage. Recommends aligning version constraints."
    },
    ("bench-npm-02", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly identifies conflicting peer dependency requirements for widget-kit. Suggests 'npm explain' to inspect dependency tree and cautions against unverified force flags."
    }
}

import apply_eval_helpers as h
h.apply_evaluations_to_batch("docs/research/human_review/batch_06.md", evals_b6)
print("Batch 06 applied.")

