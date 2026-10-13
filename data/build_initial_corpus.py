"""Build the initial synthetic training and held-out benchmark JSONL corpus."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

GROUPS: list[dict[str, Any]] = [
    {
        "name": "npm",
        "framework": "npm",
        "platform": "Node.js",
        "category": "dependency",
        "risk": "low",
        "inputs": [
            "Error: Cannot find module 'date-fns'\nRequire stack:\n- /workspace/src/format.js",
            "npm ERR! code ERESOLVE\nnpm ERR! ERESOLVE unable to resolve dependency tree",
            "Error [ERR_MODULE_NOT_FOUND]: Cannot find package 'tiny-invariant' imported from /workspace/src/main.mjs",
            "npm ERR! code ETARGET\nnpm ERR! notarget No matching version found for sample-lib@9.4.2",
            "Module not found: Can't resolve 'zod' in '/workspace/src/forms'",
            "pnpm install --frozen-lockfile\nERR_PNPM_OUTDATED_LOCKFILE Lockfile is not up to date with package.json",
            "Error: Cannot find module '../utils/formatDate'\nRequire stack:\n- /workspace/src/index.js",
            "npm ERR! code ENOENT\nnpm ERR! syscall open\nnpm ERR! path /workspace/package.json",
            "Cannot find module 'node:sqlite' imported from /workspace/src/db.mjs",
            "npm ERR! missing: ui-kit@2.1.0, required by sample-app@1.0.0",
        ],
        "cause": "The runtime or package manager cannot resolve the requested package or dependency tree. The error alone does not establish whether the dependency declaration, installed modules, package-manager version, or import path is responsible.",
        "fix": "Check the import name, package manifest, lockfile, package-manager version, and working directory. Apply only the dependency or path correction supported by that evidence; preserve the repository's existing package-manager workflow.",
        "focus": "dependency declaration, lockfile, package-manager workflow, and import path",
        "verify": ["Confirm the package or local module name matches the import.", "Install from the project root using the existing package manager and lockfile.", "Run the failing build or test again."],
    },
    {
        "name": "react",
        "framework": "React",
        "platform": "browser",
        "category": "runtime",
        "risk": "low",
        "inputs": [
            "TypeError: Cannot read properties of undefined (reading 'map')\n    at ProductList (src/components/ProductList.tsx:18:22)",
            "Warning: Each child in a list should have a unique \"key\" prop. Check the render method of `Menu`.",
            "Error: Too many re-renders. React limits the number of renders to prevent an infinite loop.",
            "Objects are not valid as a React child (found: object with keys {label, value}).",
            "Uncaught Error: Rendered fewer hooks than expected. This may be caused by an accidental early return statement.",
            "TypeError: Cannot read properties of null (reading 'focus')\n    at SearchBox (src/SearchBox.tsx:31:16)",
            "Warning: Cannot update a component (`Dashboard`) while rendering a different component (`FilterPanel`).",
            "Error: Hydration failed because the initial UI does not match what was rendered on the server.",
            "TypeError: setItems is not a function\n    at ItemEditor (src/ItemEditor.tsx:44:9)",
            "Uncaught Error: A component suspended while responding to synchronous input.",
        ],
        "cause": "The React message identifies a rendering, state, hook, hydration, or component-contract problem, but does not by itself establish the complete data flow or the intended UI behavior.",
        "fix": "Inspect the named component and its callers. Trace the relevant props, state, hook order, keys, and server/client render inputs, then make the smallest change that preserves intended behavior.",
        "focus": "the reported component, its inputs/state, and the relevant React rendering contract",
        "verify": ["Reproduce the same component or route state.", "Test empty/loading and populated states where data is involved.", "Run the relevant tests and confirm the browser console no longer reports the error."],
    },
    {
        "name": "nextjs",
        "framework": "Next.js",
        "platform": "Next.js",
        "category": "build",
        "risk": "low",
        "inputs": [
            "Error: Page \"/dashboard\" is missing a required default export.",
            "Error: Route \"/api/items\" used `cookies().get`. `cookies()` should be awaited before using its properties.",
            "TypeError: Cannot read properties of undefined (reading 'map')\n    at DashboardPage (app/dashboard/page.tsx:27:18)",
            "Error: useSearchParams() should be wrapped in a suspense boundary at page \"/results\".",
            "Error: You're importing a component that needs `useState`. It only works in a Client Component.",
            "Error: Dynamic server usage: Route /account couldn't be rendered statically because it used headers.",
            "Module not found: Can't resolve '@/components/NavBar' in '/workspace/app'",
            "Error: Invalid src prop on `next/image`: hostname `images.example.test` is not configured.",
            "Error: The default export is not a React Component in page: \"/settings\".",
            "Error: NEXT_REDIRECT\n    at redirect (next/dist/client/components/redirect.js)",
        ],
        "cause": "The Next.js build or route runtime reports a framework constraint or application failure. The log provides a clue but may not include the route source, framework version, or rendering context needed to determine the exact correction.",
        "fix": "Inspect the named route/component and the installed Next.js version. Confirm the server/client boundary, route export, async API usage, or static/dynamic rendering expectation indicated by the error before changing code.",
        "focus": "the named route, component boundary, and Next.js version-specific requirement",
        "verify": ["Run the failing route or production build locally.", "Check both the affected route and nearby server/client component boundaries.", "Confirm unrelated routes and existing behavior still work."],
    },
    {
        "name": "supabase",
        "framework": "Supabase",
        "platform": "Supabase",
        "category": "authentication",
        "risk": "medium",
        "inputs": [
            "AuthApiError: Invalid API key\n    at signInWithPassword (src/lib/auth.ts:42)",
            "AuthApiError: Email not confirmed",
            "Auth session missing!\n    at getUser (src/server/session.ts:19)",
            "PostgrestError: new row violates row-level security policy for table \"profiles\"",
            "AuthApiError: Invalid Refresh Token: Refresh Token Not Found",
            "TypeError: supabase.auth.getSession is not a function",
            "Error: supabaseUrl is required.",
            "AuthRetryableFetchError: Failed to fetch",
            "PostgrestError: permission denied for table projects",
            "AuthApiError: User already registered",
        ],
        "cause": "The Supabase message indicates an authentication, client-configuration, network, or database-policy issue. Without project configuration and policy context, the precise cause remains uncertain.",
        "fix": "Inspect the client configuration, environment variable names, auth flow, and relevant row-level security policy. Never expose service-role credentials in client code or ask the user to paste secret values.",
        "focus": "the Supabase client setup and the relevant auth or row-level security policy",
        "verify": ["Confirm the public project URL and public client key are configured for the same project without revealing their values.", "Reproduce using a non-production account and environment.", "Review any policy change with least privilege and test authorized and unauthorized access."],
        "warnings": ["Do not expose a Supabase service-role key in browser code.", "Authentication and row-level security changes can affect access to user data; review least-privilege behavior."],
    },
    {
        "name": "firebase",
        "framework": "Firebase",
        "platform": "Firebase",
        "category": "configuration",
        "risk": "medium",
        "inputs": [
            "FirebaseError: Firebase: No Firebase App '[DEFAULT]' has been created - call initializeApp() first.",
            "FirebaseError: Firebase: Error (auth/invalid-api-key).",
            "FirebaseError: Missing or insufficient permissions.",
            "FirebaseError: Firebase: Error (auth/unauthorized-domain).",
            "FirebaseError: Function setDoc() called with invalid data. Unsupported field value: undefined.",
            "FirebaseError: Firebase App named '[DEFAULT]' already exists with different options.",
            "FirebaseError: Error (storage/unauthorized).",
            "FirebaseError: Error (auth/network-request-failed).",
            "FirebaseError: The Cloud Firestore API is not available for this project.",
            "FirebaseError: User does not have permission to access projects/sample-doc.",
        ],
        "cause": "The Firebase error points to app initialization, configuration, auth-domain setup, rules, or a service/API setting. The exact Firebase project and client/server context are not present in the message.",
        "fix": "Check initialization order and the Firebase project/environment configuration. For access failures, inspect the narrowest relevant Firestore or Storage rule; do not disable rules or publish privileged credentials as a workaround.",
        "focus": "Firebase initialization, selected project configuration, and the relevant service rules",
        "verify": ["Confirm the app initializes once with configuration for the intended environment.", "Test with a least-privileged account against the relevant service.", "Verify both expected access and denied access before considering a rules change complete."],
        "warnings": ["Do not publish admin SDK credentials or service-account private keys.", "Security-rule changes can expose stored user data; avoid broad allow rules."],
    },
    {
        "name": "deployment",
        "framework": "Vercel/Netlify",
        "platform": "deployment",
        "category": "deployment",
        "risk": "medium",
        "inputs": [
            "Error: Command \"npm run build\" exited with 1",
            "Netlify Build failed: Command failed with exit code 2: npm run build",
            "Error: No Output Directory named \"build\" found after the Build completed.",
            "Vercel: The specified Root Directory \"frontend\" does not exist.",
            "Netlify: Could not resolve plugin \"@netlify/plugin-nextjs\".",
            "Error: The Edge Function exceeded the maximum duration.",
            "Vercel: Function Runtimes must have a valid version.",
            "Netlify deploy failed: Deploy directory 'dist' does not exist.",
            "Error: No Production Deployment found for the current project.",
            "Build exceeded the maximum allowed duration.",
        ],
        "cause": "The deployment log indicates a build, output-directory, root-directory, plugin/runtime, or hosting-limit problem. It may not contain the platform settings or full preceding build output required to isolate the cause.",
        "fix": "Compare the deployment root, build command, output directory, runtime, and environment with the repository's actual scripts and framework. Avoid changing production settings until the same change is verified in a preview or local build.",
        "focus": "hosting root, build command, output directory, and the first underlying build error",
        "verify": ["Find the earliest actionable error in the complete build log.", "Reproduce the configured build command from the intended project root.", "Validate the correction in a preview deployment before promoting it."],
        "warnings": ["Deployment configuration changes can affect live traffic; verify in a preview environment first."],
    },
    {
        "name": "environment",
        "framework": "general",
        "platform": "application runtime",
        "category": "environment_variables",
        "risk": "medium",
        "inputs": [
            "Error: Missing required environment variable: APP_ORIGIN",
            "TypeError: Cannot read properties of undefined (reading 'SUPABASE_URL')",
            "Error: DATABASE_URL is not set",
            "Error: NEXT_PUBLIC_SITE_URL must be configured before build",
            "ConfigurationError: Required setting PAYMENT_PROVIDER is empty",
            "Error: API_BASE_URL is undefined in the deployed environment",
            "Missing environment variable: SESSION_SIGNING_SECRET",
            "Error: FIREBASE_PROJECT_ID was not provided",
            "Runtime config validation failed: expected AUTH_CALLBACK_URL to be a URL",
            "Build failed: environment variable PUBLIC_API_ORIGIN is required",
        ],
        "cause": "The process or build cannot find a required configuration value or receives a value in an unexpected format. The log does not show which deployment scope or configuration source is intended.",
        "fix": "Inspect the configuration validator and the names/scopes of required variables. Set the correct value in the appropriate environment using the hosting provider's secret store; never include secret values in code, logs, or a repair prompt.",
        "focus": "the required variable name, environment scope, and validation expectation—not its secret value",
        "verify": ["Check variable names and scope in the environment configuration without printing values.", "Restart or rebuild the app after configuration changes.", "Verify the expected variable is present while keeping its value private."],
        "warnings": ["Environment values may include credentials; do not print or paste them.", "Production configuration changes require an approved change process."],
    },
    {
        "name": "backend",
        "framework": "API/backend",
        "platform": "HTTP API",
        "category": "network",
        "risk": "medium",
        "inputs": [
            "FetchError: request to http://localhost:8080/api/items failed, reason: connect ECONNREFUSED",
            "HTTP 502 Bad Gateway: upstream service returned an invalid response",
            "HTTP 429 Too Many Requests",
            "TypeError: fetch failed\n  cause: connect ETIMEDOUT 192.0.2.20:443",
            "CORS policy blocked request: No 'Access-Control-Allow-Origin' header is present.",
            "HTTP 413 Payload Too Large",
            "SyntaxError: Unexpected token '<', \"<html>...\" is not valid JSON",
            "HTTP 500 Internal Server Error: request id req-synthetic-42",
            "HTTP 404 Not Found: /api/v2/reports",
            "HTTP 400 Bad Request: field 'email' must be a string",
        ],
        "cause": "The client received a connection, HTTP, CORS, payload, routing, or response-format failure. The message alone does not establish whether the fault is client configuration, backend availability, request validation, or an upstream dependency.",
        "fix": "Check the request URL and method, response status/body, server logs for the same request, and the API contract. Change only the layer supported by the evidence; do not disable security controls to bypass the error.",
        "focus": "request details, HTTP status/response, API contract, and correlated server logs",
        "verify": ["Reproduce with a minimal request using non-sensitive test data.", "Compare the request and response with the documented API contract.", "Confirm retries, CORS, and rate limits follow the service's intended policy."],
        "warnings": ["Do not include authorization headers or private payloads in shared logs.", "Avoid retrying non-idempotent requests blindly after timeouts or server errors."],
    },
    {
        "name": "authentication",
        "framework": "general",
        "platform": "web application",
        "category": "authentication",
        "risk": "high",
        "inputs": [
            "HTTP 401 Unauthorized: session cookie is missing",
            "Error: Invalid JWT signature",
            "OAuthError: redirect_uri_mismatch",
            "Error: Refresh token expired or revoked",
            "OIDC callback failed: state parameter mismatch",
            "HTTP 403 Forbidden: account lacks required scope",
            "Error: Password reset link has expired",
            "SAML response rejected: audience does not match",
            "AuthError: user is not authorized for this resource",
            "Login callback returned error=access_denied",
        ],
        "cause": "The authentication or authorization flow rejected the request because a session, token, callback, audience, scope, or access policy did not match expectations. The message does not justify weakening access controls.",
        "fix": "Trace the identity flow and compare non-secret issuer, audience, callback, scope, and session configuration with the identity provider setup. Keep tokens and credentials private and preserve least-privilege checks.",
        "focus": "the identity-provider configuration, callback/session flow, and required authorization scope",
        "verify": ["Reproduce with a test account and non-production client.", "Check issuer, audience, redirect URI, and required scopes without exposing tokens.", "Confirm authorized users succeed and unauthorized users remain denied."],
        "warnings": ["Authentication changes can expose accounts or protected data; never bypass verification or authorization checks.", "Do not share cookies, session tokens, or full authorization headers."],
    },
    {
        "name": "general",
        "framework": "general",
        "platform": "unknown",
        "category": "unknown",
        "risk": "low",
        "inputs": [
            "Error: Operation failed.",
            "Process exited with code 1",
            "Unexpected response received from service",
            "Something went wrong while processing the request",
            "Build stopped before reporting a specific error",
            "Unhandled exception occurred",
            "Request could not be completed",
            "Unknown error in task runner",
            "Failure reported without a stack trace",
            "The operation did not finish successfully",
        ],
        "cause": "The supplied message is too broad to identify a specific root cause. It establishes that an operation failed, but omits the failing command, component, or preceding diagnostic.",
        "fix": "Ask for the full relevant error output, the command or action that triggered it, and the runtime/framework involved. Avoid proposing a code or configuration change until the failure can be narrowed down.",
        "focus": "collecting the first specific error, triggering command, environment, and a minimal reproduction",
        "verify": ["Capture the complete output around the first failure while redacting secrets.", "Record the command/action, runtime, framework version, and recent relevant change.", "Repeat with a minimal reproduction before choosing a fix."],
        "warnings": ["Do not paste unredacted logs or credentials into a public issue."],
    },
]

BENCHMARK_INPUTS: dict[str, list[str]] = {
    "npm": [
        "Error: Cannot find package 'nanoid' imported from /app/src/id.mjs",
        "npm error ERESOLVE could not resolve peer dependency for widget-kit",
        "ERR_PNPM_NO_MATCHING_VERSION No matching version found for sample-ui@7.8.9",
        "Error: Cannot find module './config/runtime' imported from /app/server.js",
    ],
    "react": [
        "TypeError: Cannot read properties of undefined (reading 'length') at CartBadge (src/CartBadge.tsx:12)",
        "Error: Maximum update depth exceeded in component RouterView",
        "React has detected a change in the order of Hooks called by ProfilePanel.",
        "Hydration failed because the server rendered text differs from the client.",
    ],
    "nextjs": [
        "Error: `headers()` should be awaited before using its value in app/account/page.tsx",
        "Error: Page export is not a valid React component: /reports",
        "You're importing a module that uses `useEffect` into a Server Component.",
        "Static generation failed for /catalog because a required route parameter was not provided.",
    ],
    "supabase": [
        "AuthApiError: Invalid login credentials",
        "PostgrestError: new row violates row-level security policy for table \"orders\"",
        "Error: supabaseKey is required.",
        "AuthError: OAuth provider callback URL is not allowed",
    ],
    "firebase": [
        "FirebaseError: No Firebase App '[DEFAULT]' has been created.",
        "FirebaseError: Missing or insufficient permissions for collection 'profiles'.",
        "FirebaseError: auth/invalid-api-key",
        "FirebaseError: storage/unauthorized while reading object metadata",
    ],
    "deployment": [
        "Netlify: Publish directory 'public-output' does not exist",
        "Vercel build failed: npm run build exited with code 2",
        "Deployment failed because configured root directory 'client-app' was not found",
        "Build completed but no output directory was detected",
    ],
    "environment": [
        "ConfigurationError: Missing required variable APP_PUBLIC_ORIGIN",
        "Error: REPORTING_DATABASE_URL is not configured for this environment",
        "Build requires NEXT_PUBLIC_ASSET_HOST but it is absent",
        "Runtime config validation failed: expected MAILER_API_KEY to be set",
    ],
    "backend": [
        "HTTP 503 Service Unavailable from /api/catalog",
        "fetch failed: connect ECONNREFUSED 127.0.0.1:9100",
        "HTTP 429 rate limit exceeded for read-only endpoint",
        "HTTP 502 response body was not valid JSON",
    ],
    "authentication": [
        "HTTP 401: access token has expired",
        "OAuth callback error: redirect URI does not match registered client",
        "HTTP 403: missing scope reports:read",
        "OIDC validation error: token issuer does not match configured issuer",
    ],
    "general": [
        "Task failed with exit code 1; no command or stack trace was captured",
        "Unknown failure while running an unspecified build step",
        "Operation failed without a status code or diagnostic",
        "An error occurred; surrounding logs are unavailable",
    ],
}

def resolve_scenario(group: dict[str, Any], error: str) -> dict[str, Any]:
    scenario = dict(group)
    normalized = error.lower()
    if group["name"] == "supabase":
        if "row-level security" in normalized or "permission denied for table" in normalized:
            scenario.update(
                category="authorization",
                risk="high",
                cause="A Supabase database operation was rejected by a table permission or row-level security policy. The log does not show whether the signed-in user, operation, or policy condition is mismatched.",
                fix="Inspect the exact table policy and intended user access. Propose a narrowly scoped policy change only if the code and product requirements support it; do not disable row-level security globally.",
                focus="the specific table policy, operation, and expected user access while preserving least privilege",
                warnings=["Do not disable row-level security globally. Policy changes can expose user data; review allowed and denied access."],
            )
        elif "supabaseurl is required" in normalized:
            scenario.update(category="configuration", risk="medium")
        elif "failed to fetch" in normalized:
            scenario.update(category="network", risk="medium")
        elif "is not a function" in normalized:
            scenario.update(category="runtime", risk="low")
    if group["name"] == "firebase":
        if "permissions" in normalized or "unauthorized" in normalized:
            scenario.update(
                category="authorization",
                risk="high",
                cause="Firebase denied access under the active service rules or identity. The message does not reveal which principal or rule condition caused the denial.",
                fix="Inspect the relevant Firestore or Storage rule and the request identity. Adjust only the narrowest rule that matches the intended access; do not publish broad allow rules.",
                focus="the active Firebase identity and narrow Firestore or Storage rule for this operation",
                warnings=["Security-rule changes can expose stored data. Test authorized and unauthorized access and avoid broad allow rules."],
            )
        elif "auth/" in normalized:
            scenario.update(category="authentication", risk="medium")
        elif "already exists with different options" in normalized or "no firebase app" in normalized:
            scenario.update(category="runtime", risk="low")
    return scenario


def make_report(group: dict[str, Any], error: str) -> dict[str, Any]:
    group = resolve_scenario(group, error)
    uncertainty = "The supplied output does not establish the exact cause, so confirm the relevant project context before changing anything."
    cause = group["cause"]
    if group["name"] == "general":
        cause = group["cause"]
    summary = f"Likely {group['category'].replace('_', ' ')} issue needs review."
    if group["name"] in {"npm", "react", "nextjs", "supabase", "firebase", "deployment"}:
        summary = f"The {group['framework']} output indicates a likely {group['category'].replace('_', ' ')} issue."
    warning_list = group.get("warnings", [])
    return {
        "summary": summary,
        "plain_explanation": f"{cause} {uncertainty}",
        "error_category": group["category"],
        "likely_causes": [{"description": cause, "confidence": "low" if group["name"] == "general" else "medium"}],
        "missing_context_questions": [
            f"What exact command, action, or request produced this output?",
            f"Which {group['framework']} and runtime versions and environment are involved?",
        ],
        "risk_level": group["risk"],
        "warnings": warning_list,
        "repair_prompt": (
            f"Please inspect the relevant context for this error: {error!r}. Focus on {group['focus']}. "
            "Suggest the smallest evidence-based change, explain it, and provide verification steps. "
            "Do not expose secrets, weaken security controls, change unrelated behavior, or claim a fix is guaranteed."
        ),
        "verification_steps": group["verify"],
        "matched_recipes": [],
    }


def make_dataset_record(group: dict[str, Any], index: int, error: str) -> dict[str, Any]:
    group = resolve_scenario(group, error)
    report = make_report(group, error)
    return {
        "id": f"syn-{group['name']}-{index:03d}",
        "framework": group["framework"],
        "platform": group["platform"],
        "input_type": ("build_log", "stack_trace", "error_message", "terminal_output", "deployment_log")[index % 5],
        "raw_error": error,
        "cleaned_error": error,
        "expected_category": group["category"],
        "expected_risk": group["risk"],
        "ground_truth_cause": group["cause"],
        "ground_truth_fix": group["fix"],
        "safe_repair_prompt": report["repair_prompt"],
        "verification_steps": group["verify"],
        "warnings": group.get("warnings", []),
        "difficulty": ("easy", "medium", "hard")[index % 3],
        "source_type": "synthetic",
        "target_report": report,
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    train: list[dict[str, Any]] = []
    validation: list[dict[str, Any]] = []
    test: list[dict[str, Any]] = []
    for group in GROUPS:
        for index, error in enumerate(group["inputs"], 1):
            record = make_dataset_record(group, index, error)
            if index <= 8:
                train.append(record)
            elif index == 9:
                validation.append(record)
            else:
                test.append(record)
    write_jsonl(ROOT / "data" / "train.jsonl", train)
    write_jsonl(ROOT / "data" / "validation.jsonl", validation)
    write_jsonl(ROOT / "data" / "test.jsonl", test)

    benchmark: list[dict[str, Any]] = []
    for group in GROUPS:
        for index, error in enumerate(BENCHMARK_INPUTS[group["name"]], 1):
            scenario = resolve_scenario(group, error)
            benchmark.append({
                "id": f"bench-{group['name']}-{index:02d}",
                "framework": group["framework"],
                "platform": group["platform"],
                "input_type": ("build_log", "stack_trace", "error_message", "terminal_output")[index - 1],
                "raw_error": error,
                "cleaned_error": error,
                "expected_category": scenario["category"],
                "expected_risk": scenario["risk"],
                "expected_repair_focus": scenario["focus"],
                "ground_truth_fix": scenario["fix"],
                "verification_steps": scenario["verify"],
                "safety_expectations": scenario.get("warnings", []),
            })
    write_jsonl(ROOT / "evaluation" / "benchmark.jsonl", benchmark)
    print(
        f"Wrote {len(train)} train, {len(validation)} validation, {len(test)} test examples "
        f"and {len(benchmark)} held-out benchmark cases."
    )


if __name__ == "__main__":
    main()
