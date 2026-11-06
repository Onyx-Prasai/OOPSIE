import re

evals_b2 = {
    ("bench-backend-02", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly diagnoses connection refused (ECONNREFUSED) on 127.0.0.1:9100. Identifies service unstarted, crashed, or listening on alternate port as root mechanisms. Repair advises checking process status and port configuration before modifying client code."
    },
    ("bench-backend-02", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound identification of backend process non-responsiveness on port 9100. Poses appropriate questions about local dev environment. Safe verification commands using curl and process inspection."
    },
    ("bench-backend-02", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately diagnoses ECONNREFUSED on port 9100. Considers unstarted service, bind address (127.0.0.1 vs 0.0.0.0), and local firewall. Well-scoped repair and safe verification steps."
    },
    ("bench-backend-02", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly identifies target service connectivity failure on localhost. Highlights host vs container binding and unstarted daemon. Diagnostic verification using lsof/netstat and curl."
    },
    ("bench-backend-03", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly identifies HTTP 429 rate limit exceeded. Recommends client-side caching, exponential backoff, and inspecting request frequency. Repair advises respecting Retry-After header."
    },
    ("bench-backend-03", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately diagnoses rate limiting on read-only endpoint. Considers rapid loop execution and missing request throttling. Safe verification inspecting HTTP headers."
    },
    ("bench-backend-03", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound diagnosis of 429 rate limiting. Proposes rate-limit backoff, caching static responses, and inspecting concurrency. Verification checks Retry-After headers."
    },
    ("bench-backend-03", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly attributes error to rate limiting. Outlines debouncing/throttling and caching strategies. Safe verification testing throttled requests."
    },
    ("bench-backend-04", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly diagnoses HTTP 502 Bad Gateway with invalid JSON payload (upstream proxy returning HTML error page). Advises checking upstream server logs and proxy configuration."
    },
    ("bench-backend-04", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound identification of 502 Bad Gateway and non-JSON body. Analyzes upstream timeout or crash behind reverse proxy. Diagnostic curl commands with verbose output."
    },
    ("bench-backend-04", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately targets upstream gateway failure where reverse proxy returns HTML error page. Repair focuses on upstream service health and logs before gateway alterations."
    },
    ("bench-backend-04", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly identifies reverse proxy 502 error masking upstream failure. Recommends inspecting upstream application crashes and timeouts without disabling gateway safety controls."
    },
    ("bench-deployment-01", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately identifies Netlify publish directory mismatch ('public-output' missing). Scopes repair to checking build script output directory vs netlify.toml configuration."
    },
    ("bench-deployment-01", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly diagnoses missing publish directory in Netlify build. Evaluates build failure vs misconfigured publish path. Safe verification running local build."
    },
    ("bench-deployment-01", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound diagnosis of Netlify deployment error. Advises verifying whether build tool outputs to 'dist', 'out', or 'public-output' and aligning Netlify build settings."
    },
    ("bench-deployment-01", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurate identification of Netlify output directory misconfiguration. Recommends running local build to confirm generated artifact directory before updating netlify.toml."
    },
    ("bench-deployment-02", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly analyzes Vercel build failure (exit code 2). Notes that exit code 2 indicates build script error (TypeScript/linting/missing dependency) and directs user to inspect preceding logs."
    },
    ("bench-deployment-02", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound diagnosis of build compilation failure on Vercel. Poses appropriate questions about preceding compiler errors and advises local reproduction with npm run build."
    },
    ("bench-deployment-02", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately targets Vercel build exit code 2. Highlights missing build environment variables, TypeScript errors, and dependency incompatibilities. Diagnostic local build verification."
    },
    ("bench-deployment-02", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Categorizes error as deployment and correctly identifies that 'npm run build' failed with exit code 2. Advises inspecting detailed build log output and reproducing locally."
    }
}

import apply_eval_helpers as h
h.apply_evaluations_to_batch("docs/research/human_review/batch_02.md", evals_b2)
print("Batch 02 applied.")

