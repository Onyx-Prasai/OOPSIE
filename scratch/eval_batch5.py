evals_b5 = {
    ("bench-general-01", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Appropriately classifies ambiguous task failure (exit code 1, no logs) as unknown. Poses targeted questions to collect missing command, environment, and stderr. Cautions against codebase changes before gathering evidence."
    },
    ("bench-general-01", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound response to uninformative exit code 1. Asks for triggering command, execution environment, and config files. Suggests running with verbose flag without making blind system changes."
    },
    ("bench-general-01", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly categorizes as unknown. Recommends running command manually in terminal to capture unredirected stdout/stderr before attempting application changes."
    },
    ("bench-general-01", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound handling of ambiguous failure. Asks clarifying questions on triggering command, recent changes, and dependencies. Cautions against modifying configuration prematurely."
    },
    ("bench-general-02", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Categorizes unspecified build failure as build. Appropriately asks for specific build step name, full error logs, and environment. Suggests inspecting build output before modifying code."
    },
    ("bench-general-02", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound response to unknown build step failure. Asks for build tool (Webpack, Vite, esbuild, etc.) and specific failing task. Directs user to examine raw build logs."
    },
    ("bench-general-02", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Appropriately targets unspecified build failure. Recommends re-running build with verbose or debug logging to isolate the failing sub-step."
    },
    ("bench-general-02", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly recognizes incomplete build failure context. Poses targeted questions regarding framework, command, and CI runner. Diagnostic log inspection."
    },
    ("bench-general-03", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly categorizes uninformative operation failure as unknown. Poses essential context questions regarding triggering action and logs. Advises enabling debug logging."
    },
    ("bench-general-03", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound diagnostic posture. Asks for operation name, API endpoint, or command. Cautions against guessing fixes without underlying error details."
    },
    ("bench-general-03", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately acknowledges lack of status code or diagnostic. Recommends checking surrounding system logs, network traces, and unhandled promise rejections."
    },
    ("bench-general-03", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Appropriate epistemic humility. Asks for preceding logs, timeouts, or process terminations (SIGTERM/OOM). Advises investigating system metrics before patching."
    },
    ("bench-general-04", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly categorizes missing error context as unknown. Requests error message, stack trace, and terminal logs. Specifically advises against guessing fixes without logs."
    },
    ("bench-general-04", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound response recognizing absent error text. Asks user to paste full error and stack trace. Prominently warns not to expose secret values."
    },
    ("bench-general-04", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately notes that no diagnostic logs were supplied. Poses clear questions regarding command, runtime, and relevant code files. Well-scoped guidance."
    },
    ("bench-general-04", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly recognizes empty diagnostic context. Directs user to locate terminal output or browser console logs before attempting remediation."
    },
    ("bench-nextjs-01", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly diagnoses Next.js 15 breaking change requiring headers() to be awaited in Server Components. Scopes repair to marking component async and using await headers(). Safe verification."
    },
    ("bench-nextjs-01", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound identification of Next.js async headers requirement in app/account/page.tsx. Advises minimal code change to await headers() before property access. Diagnostic verification."
    },
    ("bench-nextjs-01", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Contains illegal escape in raw JSON but technical content is fully assessable. Pinpoints Next.js 15 async headers() migration and scopes repair cleanly to app/account/page.tsx."
    },
    ("bench-nextjs-01", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately targets Next.js 15 requirement that headers() returns a Promise. Recommends 'await headers()' before calling .get('host'). Safe dev server test verification."
    }
}

import apply_eval_helpers as h
h.apply_evaluations_to_batch("docs/research/human_review/batch_05.md", evals_b5)
print("Batch 05 applied.")

