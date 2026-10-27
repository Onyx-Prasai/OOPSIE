import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import json
from typing import Any

RECORDS: list[dict[str, Any]] = [
    # ---------------------------------------------------------------
    # TRAIN SPLIT (22 records: syn-*-061 through syn-*-082)
    # ---------------------------------------------------------------
    {
        "id": "syn-run-061",
        "scenario_group": "nextjs-use-client-missing-server-component",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Next.js App Router error when hooks are used in Server Component without use client directive."},
        "model_input": {
            "raw_error": "Error: useState is not a function. (In 'useState(false)', 'useState' is undefined)\n\nYou're importing a component that needs useState. It only works in a Client Component but none of its parents are marked with \"use client\", so they're Server Components by default.\n\nLearn more: https://nextjs.org/docs/getting-started/react-essentials\n\n   ,-[src/app/dashboard/page.tsx:3:1]\n 3 | import { useState } from 'react';\n   `----",
            "context": {"language_or_framework": "Next.js 14 (App Router)", "environment": "local_development", "recent_changes": "Added interactive toggle state to the dashboard page component."}
        },
        "reference_annotations": {
            "reference_cause": "In the Next.js App Router, all components under app/ are Server Components by default and cannot use React hooks like useState or event handlers. The 'use client' directive was not added.",
            "reference_repair": "Add '\"use client\";' as the first line of the component file, or extract the interactive part into a separate client component with the directive.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "Next.js dashboard page used useState in a Server Component without the 'use client' directive.",
            "plain_explanation": "In the Next.js App Router, every file inside the 'app/' directory is a Server Component by default. Server Components run on the server side during rendering and do not support React hooks like 'useState', 'useEffect', or browser event handlers like 'onClick'. To use these features, the component must be marked as a Client Component by adding '\"use client\";' at the very top of the file.",
            "error_category": "runtime",
            "likely_causes": [
                {"description": "The component file imports useState or uses event handlers without the '\"use client\";' directive at the top.", "confidence": "high"},
                {"description": "A shared component from the pages/ router was moved to the app/ router without adapting to Server Component rules.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Does the component need to fetch data on the server, or is it purely interactive UI?",
                "Can the stateful interactive portion be extracted into a smaller child component?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect src/app/dashboard/page.tsx. Next.js reports: \"You're importing a component that needs useState... none of its parents are marked with 'use client'\". Add '\"use client\";' as the very first line of the file. If this page also fetches server-side data, consider splitting it: keep a Server Component for data fetching and create a separate Client Component child for interactive UI. Do not add 'use client' to layout.tsx or root page unless necessary.",
            "verification_steps": [
                "Add '\"use client\";' as the first line of src/app/dashboard/page.tsx.",
                "Restart the dev server and verify the dashboard page compiles and renders in browser.",
                "Test that the toggle state updates correctly in the UI."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-run-062",
        "scenario_group": "nextjs15-cookies-sync-deprecated",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Next.js 15 async cookies/headers API migration warning causing runtime error."},
        "model_input": {
            "raw_error": "Error: Route /api/auth/session used `cookies()`. `cookies()` should be awaited before using its value. Learn more: https://nextjs.org/docs/messages/sync-dynamic-apis\n    at getCookies (src/lib/auth.ts:12:22)\n    at GET (src/app/api/auth/session/route.ts:8:18)",
            "context": {"language_or_framework": "Next.js 15 (App Router)", "environment": "local_development", "recent_changes": "Upgraded from Next.js 14 to Next.js 15."}
        },
        "reference_annotations": {
            "reference_cause": "Next.js 15 changed cookies(), headers(), and params to be async; calling them synchronously without await causes a runtime error.",
            "reference_repair": "Await the cookies() call: 'const cookieStore = await cookies();'",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "Next.js 15 requires cookies() to be awaited but the route called it synchronously.",
            "plain_explanation": "Next.js 15 made several dynamic APIs asynchronous: 'cookies()', 'headers()', and route params. Code that calls these without 'await' was valid in Next.js 14 but fails in Next.js 15. The route handler must now use 'const cookieStore = await cookies();' before reading values.",
            "error_category": "runtime",
            "likely_causes": [
                {"description": "The application was upgraded from Next.js 14 where cookies() was synchronous to Next.js 15 where it is async.", "confidence": "high"},
                {"description": "A shared utility function calls cookies() synchronously without awareness of the Next.js version requirement.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Which version of Next.js was the project on before this upgrade?",
                "Are there other places in your codebase calling cookies(), headers(), or accessing params without await?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect src/lib/auth.ts around line 12 and src/app/api/auth/session/route.ts. Next.js 15 requires: 'const cookieStore = await cookies();' instead of the synchronous form. Update all calls to cookies(), headers(), and dynamic params to use await in async functions. Run 'npx @next/codemod@canary upgrade latest' to automate the migration. Do not change the logic of session or auth handling.",
            "verification_steps": [
                "Search codebase for calls to cookies() and headers() without await using your IDE.",
                "Update each call site to use async/await syntax.",
                "Restart the Next.js dev server and verify /api/auth/session returns a valid response."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-dat-063",
        "scenario_group": "supabase-foreign-key-constraint-violation",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic PostgreSQL 23503 foreign key violation on cascade delete."},
        "model_input": {
            "raw_error": "PostgrestError: insert or update on table \"posts\" violates foreign key constraint \"posts_author_id_fkey\"\n  code: \"23503\"\n  details: \"Key (author_id)=(a1b2c3d4-e5f6-7890-abcd-ef1234567890) is not present in table \\\"profiles\\\".\"\n  hint: null\n  message: \"insert or update on table \\\"posts\\\" violates foreign key constraint \\\"posts_author_id_fkey\\\"\"",
            "context": {"language_or_framework": "Supabase / PostgreSQL", "environment": "local_development", "recent_changes": "Inserted a post record after deleting and recreating the user profile."}
        },
        "reference_annotations": {
            "reference_cause": "A post record was inserted referencing an author_id that does not exist in the profiles table, violating the foreign key constraint.",
            "reference_repair": "Ensure the profile row for the user exists before inserting posts, or investigate why the profile was deleted.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "Supabase rejected the post insert because the referenced author_id does not exist in the profiles table.",
            "plain_explanation": "A foreign key constraint ('posts_author_id_fkey') ensures that every 'author_id' in the 'posts' table must match an existing row in the 'profiles' table. When you tried to insert a post referencing a user ID that no longer has a corresponding profile row, PostgreSQL rejected the operation to maintain referential integrity.",
            "error_category": "database",
            "likely_causes": [
                {"description": "The user profile row was deleted (or never created) while an attempt was made to insert a post referencing that user.", "confidence": "high"},
                {"description": "User auth.users and profiles tables are out of sync because the trigger or database function that creates a profile on signup failed silently.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Does a row exist in the 'profiles' table for the UUID 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'?",
                "Is there a database trigger that should automatically create a profile row when a new user signs up via Supabase Auth?"
            ],
            "risk_level": "high",
            "warnings": [
                "Do not disable foreign key constraints to bypass this error; doing so would allow orphaned records and data corruption."
            ],
            "repair_prompt": "Please inspect the Supabase database. The insert fails with: \"23503: insert or update on table 'posts' violates foreign key constraint 'posts_author_id_fkey'\". Verify that the profile row for user 'a1b2c3d4-...' exists by querying 'SELECT * FROM profiles WHERE id = ...' in SQL Editor. If profiles are missing, check whether your signup trigger (on auth.users insert) is functioning correctly. Do not remove the foreign key constraint.",
            "verification_steps": [
                "Query 'SELECT id FROM profiles WHERE id = <author_id>;' to confirm the profile row exists.",
                "Check for a database trigger in Supabase Dashboard that creates profile rows on new user creation.",
                "After the profile row is confirmed, retry the post insert."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-dat-064",
        "scenario_group": "prisma-connection-pool-timeout-serverless",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Prisma P2024 connection pool timeout under serverless cold-start load."},
        "model_input": {
            "raw_error": "PrismaClientKnownRequestError:\nInvalid `prisma.user.findMany()` invocation:\n\nTimed out fetching a new connection from the connection pool. More info: https://pris.ly/d/connection-pool (Current connection pool timeout: 10, connection limit: 5)\n   code: 'P2024'\n   meta: { clientVersion: '5.4.2', timeout: 10, connection_limit: 5 }",
            "context": {"language_or_framework": "Prisma / Vercel (Serverless)", "environment": "production", "recent_changes": "Deployed Prisma ORM to Vercel serverless functions."}
        },
        "reference_annotations": {
            "reference_cause": "Prisma's default connection pool is designed for long-running servers. In serverless environments many function instances each create their own connection pool, exhausting PostgreSQL's max connection limit.",
            "reference_repair": "Use Prisma Accelerate or configure DATABASE_URL to use a connection pooler like Supabase Pooler (pgbouncer) and add ?pgbouncer=true to the URL.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "Prisma timed out (P2024) waiting for a database connection in a serverless deployment.",
            "plain_explanation": "Prisma maintains a pool of persistent database connections. In serverless platforms like Vercel, each function instance creates its own Prisma Client with its own connection pool. Under concurrent traffic, dozens of function instances each hold open connections simultaneously, exhausting PostgreSQL's connection limit and forcing new requests to wait until a timeout occurs.",
            "error_category": "database",
            "likely_causes": [
                {"description": "Multiple serverless function cold-starts each opened a separate Prisma connection pool, hitting PostgreSQL's max_connections limit.", "confidence": "high"},
                {"description": "Prisma Client is being instantiated inside the handler function rather than at module scope, creating a new pool per request.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Is your PrismaClient instantiated once at module scope or inside each serverless handler function?",
                "Are you using a connection pooler (like Supabase Pooler or PgBouncer) in front of PostgreSQL?"
            ],
            "risk_level": "high",
            "warnings": [
                "High connection load can degrade or crash the database for all users; address pooling before scaling to production traffic."
            ],
            "repair_prompt": "Please inspect how PrismaClient is instantiated in your serverless routes. Prisma throws P2024 (connection pool timeout) under serverless load. Move PrismaClient to a module-level singleton rather than creating it per-request. Use a connection pooler: in Supabase, switch DATABASE_URL to the Supabase Pooler endpoint (port 6543, pgbouncer mode) and add '?pgbouncer=true&connection_limit=1'. Alternatively, use Prisma Accelerate. Do not increase connection_limit beyond the pooler's capacity.",
            "verification_steps": [
                "Switch the DATABASE_URL to use pgbouncer/Supabase Pooler.",
                "Instantiate PrismaClient at module scope to share across invocations.",
                "Run a load test and verify P2024 errors no longer appear under concurrent requests."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-run-065",
        "scenario_group": "nextjs-localstorage-ssr-window-undefined",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic window is not defined error when accessing localStorage during Next.js SSR."},
        "model_input": {
            "raw_error": "ReferenceError: window is not defined\n    at getStoredTheme (src/hooks/useTheme.ts:5:10)\n    at useTheme (src/hooks/useTheme.ts:12:18)\n    at ThemeProvider (src/components/ThemeProvider.tsx:8:24)\n\n// src/hooks/useTheme.ts:5\nconst stored = window.localStorage.getItem('theme');",
            "context": {"language_or_framework": "Next.js 14", "environment": "local_development", "recent_changes": "Added theme persistence using localStorage in a custom hook."}
        },
        "reference_annotations": {
            "reference_cause": "window.localStorage is a browser-only API. Accessing it at module evaluation time during Next.js server-side rendering causes ReferenceError because window does not exist on the server.",
            "reference_repair": "Guard localStorage access inside a useEffect hook, or check 'typeof window !== \"undefined\"' before reading.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "Next.js crashed during SSR because localStorage was accessed outside of the browser.",
            "plain_explanation": "Next.js renders components on the server before sending HTML to the browser. During server-side rendering, browser APIs like 'window', 'document', and 'localStorage' do not exist. Accessing 'window.localStorage' at the top level of a hook causes a 'ReferenceError: window is not defined' crash during server-side rendering.",
            "error_category": "runtime",
            "likely_causes": [
                {"description": "localStorage is accessed at module scope or during synchronous function calls that run during SSR.", "confidence": "high"},
                {"description": "A third-party library accessing window was imported without dynamic import and SSR disabled.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Is 'getStoredTheme' called at module load time or inside a component function?",
                "Is the hook used inside a component marked as a Client Component with '\"use client\"'?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect src/hooks/useTheme.ts. Next.js crashes with: \"ReferenceError: window is not defined\". Move the localStorage access inside a useEffect hook which only runs in the browser: 'useEffect(() => { const stored = localStorage.getItem(\"theme\"); setTheme(stored || \"light\"); }, []);'. Never access window or localStorage at the top-level of a module or synchronous function. Alternatively, guard with: 'if (typeof window === \"undefined\") return;'.",
            "verification_steps": [
                "Wrap the localStorage.getItem call inside a useEffect in src/hooks/useTheme.ts.",
                "Restart the Next.js dev server and verify SSR pages load without ReferenceError.",
                "Confirm theme preference is correctly restored after a page refresh in the browser."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-run-066",
        "scenario_group": "react19-useactionstate-no-pending-guard",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic React 19 useActionState form double-submit without pending guard."},
        "model_input": {
            "raw_error": "Error: Cannot update a component (`ContactForm`) while rendering a different component (`ContactForm`).\n    at ContactForm (src/components/ContactForm.tsx:14:5)\n\n// Observed behavior: form submits twice when button is clicked rapidly",
            "context": {"language_or_framework": "React 19 / Next.js App Router", "environment": "local_development", "recent_changes": "Migrated form handling from useState to useActionState."}
        },
        "reference_annotations": {
            "reference_cause": "The form submit button was not disabled during pending state, allowing double-submission that triggered concurrent state updates during render.",
            "reference_repair": "Use the isPending flag from useActionState to disable the submit button: '<button disabled={isPending}>'.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "ContactForm allowed double-submission because the submit button was not disabled during the pending action.",
            "plain_explanation": "React 19's 'useActionState' hook returns an 'isPending' flag indicating when an async action is in progress. Without disabling the submit button during this time, rapid clicks can trigger multiple concurrent form submissions. This causes React to attempt conflicting state updates during rendering, leading to the error.",
            "error_category": "runtime",
            "likely_causes": [
                {"description": "The form submit button is not disabled while 'isPending' is true from useActionState.", "confidence": "high"},
                {"description": "The server action is called multiple times concurrently because the form can be submitted repeatedly.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Does your submit button currently use the 'isPending' value from useActionState?",
                "Is the form action a server action or a client-side async function?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect src/components/ContactForm.tsx. React reports: \"Cannot update a component while rendering a different component\". Destructure 'isPending' from useActionState and use it to disable the submit button during submission: '<button type=\"submit\" disabled={isPending}>{isPending ? \"Sending...\" : \"Send\"}</button>'. This prevents duplicate submissions. Do not add additional manual state for loading tracking.",
            "verification_steps": [
                "Confirm useActionState returns [state, action, isPending] and isPending is passed to the button's disabled prop.",
                "Click the submit button rapidly and verify only one submission is processed.",
                "Test the form with a slow network (browser DevTools throttling) to confirm the pending state displays correctly."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-bld-067",
        "scenario_group": "turborepo-missing-task-depends-on",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Turborepo pipeline task ordering failure due to missing dependsOn."},
        "model_input": {
            "raw_error": "turbo run build\nERROR: cannot find task \"build\" for package \"@myapp/ui\"\n[ui] WARN  No \"build\" script found in package \"@myapp/ui\". Skipping...\n[web] ERROR Could not resolve \"@myapp/ui/dist/index.js\".\nBuild failed (exit code 1)",
            "context": {"language_or_framework": "Turborepo / pnpm Monorepo", "environment": "ci_build", "recent_changes": "Added new shared UI package @myapp/ui to monorepo."}
        },
        "reference_annotations": {
            "reference_cause": "The 'web' app depends on the built output of '@myapp/ui', but turbo.json does not declare 'dependsOn: [\"^build\"]' for the build task, so Turborepo does not guarantee building @myapp/ui before @myapp/web.",
            "reference_repair": "Add 'dependsOn: [\"^build\"]' to the build task in turbo.json to enforce correct build order.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "Turborepo built @myapp/web before @myapp/ui because turbo.json is missing 'dependsOn: [\"^build\"]'.",
            "plain_explanation": "Turborepo determines which packages to build and in what order using the 'dependsOn' configuration in 'turbo.json'. The '^build' syntax means 'run the build task of all workspace dependencies first'. Without this setting, Turborepo may build packages in any order, so '@myapp/web' tried to resolve '@myapp/ui/dist/index.js' before it was compiled.",
            "error_category": "build",
            "likely_causes": [
                {"description": "The build task in turbo.json lacks 'dependsOn: [\"^build\"]', so internal package build ordering is not enforced.", "confidence": "high"},
                {"description": "The new @myapp/ui package is missing a 'build' script in its package.json.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "What does the 'build' task entry look like in turbo.json?",
                "Does packages/ui/package.json have a 'build' script that outputs to dist/?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect turbo.json and packages/ui/package.json. Turborepo fails: \"Could not resolve '@myapp/ui/dist/index.js'\". In turbo.json, update the build task to include: '\"build\": { \"dependsOn\": [\"^build\"], \"outputs\": [\"dist/**\"] }'. Also verify that packages/ui/package.json has a 'build' script (e.g. 'tsc -p tsconfig.json' or 'vite build'). Do not skip dependency builds.",
            "verification_steps": [
                "Add 'dependsOn: [\"^build\"]' to the build task in turbo.json.",
                "Verify @myapp/ui/package.json has a build script producing dist/.",
                "Run 'turbo run build' and confirm @myapp/ui builds before @myapp/web."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-bld-068",
        "scenario_group": "vite-asset-import-query-param-syntax",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Vite ?url vs ?raw query parameter import confusion."},
        "model_input": {
            "raw_error": "[vite] Internal server error: Failed to resolve import \"./shader.glsl?raw\" from \"src/three/Scene.jsx\".\nThe ?raw and ?url suffixes are not recognized as part of a URL specifier. Use Vite's explicit asset query imports instead.\n    at formatError (node_modules/vite/dist/node/chunks/dep-BHn8PXSE.js:9842:14)",
            "context": {"language_or_framework": "Vite / Three.js", "environment": "local_development", "recent_changes": "Attempted to import a GLSL shader file as a string."}
        },
        "reference_annotations": {
            "reference_cause": "Vite supports ?raw and ?url asset import suffixes only in files processed by Vite's pipeline; the import string was malformed or the Vite version does not support this syntax for this file type.",
            "reference_repair": "Use the correct Vite import syntax: 'import shaderSource from \"./shader.glsl?raw\";' ensuring Vite 3+ is installed and the file type is not excluded in vite.config.js.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "Vite could not resolve './shader.glsl?raw' because the asset query import syntax was not recognized.",
            "plain_explanation": "Vite supports importing files as raw strings using the '?raw' suffix (e.g. 'import text from \"./file.txt?raw\"'). This feature works out of the box in Vite 3+, but can fail if the asset type is excluded in the 'assetsInclude' configuration, if an older Vite version is installed, or if there is a conflict with a plugin that intercepts the import.",
            "error_category": "build",
            "likely_causes": [
                {"description": "The Vite version is older than v3 which introduced ?raw query import support.", "confidence": "medium"},
                {"description": "A Vite plugin or custom resolver intercepts .glsl imports before Vite's asset pipeline processes the ?raw suffix.", "confidence": "high"}
            ],
            "missing_context_questions": [
                "What version of Vite is installed (check package.json)?",
                "Are there any vite-plugin-glsl or custom transform plugins configured in vite.config.js?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect vite.config.js and package.json. Vite fails to resolve: \"./shader.glsl?raw\". Ensure Vite version is 3.0 or newer. If using a 'vite-plugin-glsl' plugin, it may intercept the import before Vite can apply ?raw; configure the plugin to exclude files ending in '?raw', or remove the plugin and rely on Vite's built-in ?raw for string imports. Do not modify rendering logic.",
            "verification_steps": [
                "Check Vite version in package.json; upgrade to latest if below 3.0.",
                "Inspect vite.config.js for conflicting GLSL or asset plugins.",
                "Verify 'import shader from \"./shader.glsl?raw\"; console.log(typeof shader)' logs 'string' in the browser console."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-ath-069",
        "scenario_group": "nextauth-secret-missing-production",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic NextAuth.js NEXTAUTH_SECRET missing in production causing session encryption failures."},
        "model_input": {
            "raw_error": "[next-auth][error][NO_SECRET] \nhttps://next-auth.js.org/errors#no_secret\nError: Please define a `NEXTAUTH_SECRET` environment variable.\n  at Object.encode (node_modules/next-auth/jwt/index.js:16:15)\n  at Object.getToken (node_modules/next-auth/jwt/index.js:66:22)",
            "context": {"language_or_framework": "Next.js / Auth.js (NextAuth v4)", "environment": "production", "recent_changes": "Deployed application to Vercel for the first time."}
        },
        "reference_annotations": {
            "reference_cause": "NEXTAUTH_SECRET is required in production for encrypting JWT session tokens but was not added to the deployment environment variables.",
            "reference_repair": "Generate a secret with 'openssl rand -base64 32' and add it as NEXTAUTH_SECRET to the hosting platform's environment variables.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "NextAuth.js failed in production because the required NEXTAUTH_SECRET environment variable was not configured.",
            "plain_explanation": "NextAuth.js uses 'NEXTAUTH_SECRET' to sign and encrypt JWT session tokens. In development, Auth.js falls back to a default value, but in production this variable is strictly required for security. Without it, session encoding fails and users cannot log in.",
            "error_category": "authentication",
            "likely_causes": [
                {"description": "NEXTAUTH_SECRET was not added to Vercel or production hosting environment variables.", "confidence": "high"},
                {"description": "The variable is present in the local .env.local file but was not copied to the deployment dashboard.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Is NEXTAUTH_SECRET defined in your Vercel project's Environment Variables settings?",
                "Is NEXTAUTH_URL also configured to match the production domain?"
            ],
            "risk_level": "high",
            "warnings": [
                "Generate a cryptographically strong secret using 'openssl rand -base64 32'; do not use a simple or guessable string.",
                "Keep NEXTAUTH_SECRET confidential; do not commit it to version control or expose it in client-side code."
            ],
            "repair_prompt": "Please configure your deployment environment. NextAuth.js throws: \"Please define a NEXTAUTH_SECRET environment variable\". Generate a secure secret ('openssl rand -base64 32') and add it as 'NEXTAUTH_SECRET' to your Vercel project's Environment Variables under Settings -> Environment Variables. Also set 'NEXTAUTH_URL' to your production domain (e.g. 'https://myapp.com'). Redeploy after adding these variables.",
            "verification_steps": [
                "Verify NEXTAUTH_SECRET is set in the hosting platform's environment variables.",
                "Redeploy the application and attempt to sign in.",
                "Confirm session cookies are created and the [next-auth][error][NO_SECRET] error no longer appears in logs."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-run-070",
        "scenario_group": "dangerouslysetinnerhtml-unsanitized-xss-risk",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic security warning for dangerouslySetInnerHTML with unsanitized user content."},
        "model_input": {
            "raw_error": "Security scan warning (ESLint / react-security-linter):\n[High] react/no-danger-with-children: 'dangerouslySetInnerHTML' is used with user-provided content without sanitization.\nFile: src/components/CommentDisplay.jsx:11\n<div dangerouslySetInnerHTML={{ __html: comment.body }} />",
            "context": {"language_or_framework": "React 18", "environment": "production", "recent_changes": "Added a comment display component that renders user-submitted comment text."}
        },
        "reference_annotations": {
            "reference_cause": "User-supplied comment.body is rendered directly via dangerouslySetInnerHTML without HTML sanitization, creating a Cross-Site Scripting (XSS) vulnerability.",
            "reference_repair": "Sanitize the HTML before rendering using a library like DOMPurify: 'dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(comment.body) }}'",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "CommentDisplay renders unsanitized user HTML directly, creating a Cross-Site Scripting (XSS) vulnerability.",
            "plain_explanation": "Using 'dangerouslySetInnerHTML' with user-provided content without sanitizing it first is a critical security vulnerability. A malicious user could submit a comment containing JavaScript code (e.g. '<script>stealCookies()</script>') that executes in any other user's browser when they view that comment.",
            "error_category": "frontend",
            "likely_causes": [
                {"description": "User comment HTML is passed directly to dangerouslySetInnerHTML without running a sanitization function.", "confidence": "high"},
                {"description": "Comments were previously stored as plain text and displayed safely with React's default text rendering, but a format change introduced raw HTML rendering.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Do comments need to support HTML formatting (bold, links), or can they be displayed as plain text?",
                "Where does 'comment.body' originate — API, database, or user form input?"
            ],
            "risk_level": "high",
            "warnings": [
                "CRITICAL SECURITY RISK: Rendering unsanitized user HTML allows stored XSS attacks. Attackers can steal session tokens, impersonate users, or deface your site.",
                "If comments only need plain text formatting, use React's default text rendering ('{comment.body}') and avoid dangerouslySetInnerHTML entirely."
            ],
            "repair_prompt": "Please inspect src/components/CommentDisplay.jsx line 11. A security scan flags: \"dangerouslySetInnerHTML is used with user-provided content without sanitization\". Install DOMPurify ('npm install dompurify') and sanitize the HTML before rendering: 'import DOMPurify from \"dompurify\"; <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(comment.body) }} />'. If comments are plain text only, replace dangerouslySetInnerHTML with '{comment.body}' and remove the unsafe rendering path entirely.",
            "verification_steps": [
                "Install and import DOMPurify in CommentDisplay.jsx.",
                "Test by submitting a comment containing '<script>alert(1)</script>' and verify it is not executed.",
                "Run your security linter and confirm the no-danger warning is resolved."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-run-071",
        "scenario_group": "cors-preflight-options-405",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic CORS preflight OPTIONS request returning 405 from API server."},
        "model_input": {
            "raw_error": "Access to fetch at 'https://api.example.com/v1/items' from origin 'https://app.example.com' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: It does not have HTTP ok status.\n\nNetwork tab: OPTIONS /v1/items -> 405 Method Not Allowed",
            "context": {"language_or_framework": "Express.js / React", "environment": "staging", "recent_changes": "Enabled CORS middleware on Express server."}
        },
        "reference_annotations": {
            "reference_cause": "The Express router does not have a handler for OPTIONS requests on /v1/items; the CORS preflight is rejected with 405 before reaching the cors() middleware.",
            "reference_repair": "Apply the cors() middleware before route definitions with 'app.options(\"*\", cors())' to handle preflight requests globally.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "CORS preflight OPTIONS request to /v1/items failed with 405 Method Not Allowed.",
            "plain_explanation": "Browsers send a CORS 'preflight' OPTIONS request before making cross-origin requests with custom headers or certain content types. The server must respond to OPTIONS with status 200 and the appropriate CORS headers. If the Express router has no route defined for OPTIONS on '/v1/items', the request falls through to a 405 handler and the browser blocks the actual request.",
            "error_category": "network",
            "likely_causes": [
                {"description": "The cors() middleware is mounted after route definitions or applied only to specific HTTP methods, missing the OPTIONS preflight.", "confidence": "high"},
                {"description": "A reverse proxy or API gateway in front of Express is stripping or rejecting OPTIONS requests before they reach the application.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Is 'app.use(cors())' declared before 'app.use(router)' in the Express server setup?",
                "Is there a reverse proxy (Nginx, Cloudflare) in front of Express that might be handling OPTIONS separately?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect the Express server setup (e.g. src/server.js or app.js). The browser blocks requests: \"Response to preflight request doesn't pass access control check\". Ensure cors() middleware is applied globally before routes and explicitly handle OPTIONS: 'const cors = require(\"cors\"); app.options(\"*\", cors()); app.use(cors());'. Verify the cors options include the correct 'origin', 'methods', and 'allowedHeaders'. Do not disable CORS globally with '*' if credentials are required.",
            "verification_steps": [
                "Confirm 'app.options(\"*\", cors())' appears before route middleware in your Express server.",
                "Use browser DevTools Network tab to verify the OPTIONS request returns 200 with 'Access-Control-Allow-Origin' header.",
                "Test the actual API request from the frontend and confirm it completes successfully."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-dpl-072",
        "scenario_group": "vercel-edge-function-timeout-exceeded",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Vercel Edge Function 25-second execution timeout exceeded."},
        "model_input": {
            "raw_error": "Error: The Edge Function \"middleware\" returned a response with a status of 504.\nFailed to process request: FUNCTION_INVOCATION_TIMEOUT\nVercel deployment logs: Edge Function exceeded maximum execution time of 25 seconds.",
            "context": {"language_or_framework": "Next.js / Vercel Edge Runtime", "environment": "production", "recent_changes": "Added external API call inside Next.js middleware."}
        },
        "reference_annotations": {
            "reference_cause": "The Next.js middleware makes a synchronous blocking external API call that takes longer than Vercel's 25-second Edge Function timeout.",
            "reference_repair": "Move slow external API calls out of middleware into route handlers, or add timeout and fallback logic to the fetch call.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "Vercel Edge Function (middleware) timed out after 25 seconds waiting for an external API response.",
            "plain_explanation": "Vercel Edge Functions have a maximum execution time of 25 seconds. Your middleware is making a blocking external API call that takes longer than this limit. Because middleware runs on every request, a slow external dependency blocks all incoming traffic until the function times out and returns a 504 error.",
            "error_category": "deployment",
            "likely_causes": [
                {"description": "Next.js middleware performs a blocking fetch to a slow external service without a timeout limit.", "confidence": "high"},
                {"description": "The external API is rate-limiting or down, causing requests to hang.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "What external API call is being made inside middleware?",
                "Is this call required for every request or only specific routes?"
            ],
            "risk_level": "high",
            "warnings": [
                "Slow middleware blocks all requests across your application; keep middleware as lightweight as possible.",
                "Never make calls to slow, unreliable, or rate-limited external services from Next.js middleware."
            ],
            "repair_prompt": "Please inspect src/middleware.ts. Vercel reports: \"Edge Function exceeded maximum execution time of 25 seconds\". Move the slow external API call into the specific route handler rather than running it for every request in middleware. If the call must remain in middleware, add an AbortController timeout: 'const controller = new AbortController(); setTimeout(() => controller.abort(), 5000); fetch(url, { signal: controller.signal })'. Add fallback behavior for when the external call fails.",
            "verification_steps": [
                "Move the external API call from middleware to the specific route handler that needs it.",
                "Add a fetch timeout using AbortController if a middleware call is essential.",
                "Deploy and verify requests complete under 2 seconds in Vercel function logs."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-dep-073",
        "scenario_group": "workspace-protocol-unsupported-npm",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic npm failing on workspace: protocol from pnpm monorepo."},
        "model_input": {
            "raw_error": "npm ERR! Invalid version: \"workspace:*\"\nnpm ERR! Invalid tag name \"workspace:*\": Tags may not have any characters that encodeURIComponent encodes.\n\nFor help with npm package.json usage, see:\nhttps://docs.npmjs.com/creating-a-package-json-file",
            "context": {"language_or_framework": "Node.js / npm", "environment": "ci_build", "recent_changes": "Switched CI pipeline from pnpm to npm install."}
        },
        "reference_annotations": {
            "reference_cause": "The package.json dependencies use pnpm's 'workspace:*' protocol for internal packages, which npm does not understand.",
            "reference_repair": "Use pnpm in CI, or replace 'workspace:*' references with explicit version numbers or file: paths for npm compatibility.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "npm failed because the 'workspace:*' dependency protocol is specific to pnpm and Yarn Berry.",
            "plain_explanation": "The 'workspace:*' version specifier is a workspace protocol used by pnpm and Yarn Berry to reference local monorepo packages. Standard npm does not understand this syntax and interprets it as an invalid version tag.",
            "error_category": "dependency",
            "likely_causes": [
                {"description": "The CI pipeline switched from pnpm to npm, but package.json still uses pnpm-specific 'workspace:*' version references.", "confidence": "high"},
                {"description": "A template package.json was used from a pnpm project without adapting it to the active package manager.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Which package manager (npm, pnpm, or yarn) should this project use?",
                "Is there a .npmrc or package.json 'packageManager' field specifying pnpm?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect package.json and your CI configuration. npm fails with: \"Invalid version: 'workspace:*'\". Either restore the CI pipeline to use pnpm ('npm install -g pnpm && pnpm install'), or replace 'workspace:*' dependency references with specific version numbers ('\"1.0.0\"') or relative paths ('\"file:../packages/ui\"') that npm understands. Ensure consistency between local and CI package managers.",
            "verification_steps": [
                "Confirm pnpm is used in CI by checking CI config files (e.g. .github/workflows/).",
                "Run 'pnpm install' in CI and verify workspace packages resolve correctly.",
                "Alternatively, pin package manager in package.json 'packageManager' field."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-run-074",
        "scenario_group": "react-key-array-index-reorder-bug",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic React key prop misuse with array index causing incorrect reorder behavior."},
        "model_input": {
            "raw_error": "Warning: Each child in a list should have a unique \"key\" prop.\n    at li\n    at TaskList (src/components/TaskList.jsx:8:10)\n\n// Code:\nconst items = tasks.map((task, index) => <li key={index}>{task.title}</li>);\n\n// Observed: When tasks are reordered by drag-and-drop, wrong content appears in items",
            "context": {"language_or_framework": "React 18", "environment": "local_development", "recent_changes": "Added drag-and-drop task reordering."}
        },
        "reference_annotations": {
            "reference_cause": "Using array index as React key causes incorrect reconciliation when the array order changes; React reuses DOM elements by index rather than by item identity.",
            "reference_repair": "Use a stable unique identifier from each task (e.g. key={task.id}) instead of the array index.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "TaskList shows incorrect items after reordering because React keys are array indices instead of stable task IDs.",
            "plain_explanation": "React uses 'key' props to track which list items correspond to which rendered elements across re-renders. When 'index' is used as a key, React identifies items by their position. After drag-and-drop reordering, items swap positions but React thinks the same 'index' still maps to the same item, causing stale or mismatched content to display.",
            "error_category": "runtime",
            "likely_causes": [
                {"description": "Array index is used as the React key, causing identity confusion when the array order changes.", "confidence": "high"},
                {"description": "Each task object lacks a unique identifier property, so index was used as a workaround.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Does each task object have a stable unique ID property (e.g. 'task.id')?",
                "How are new tasks created — are unique IDs assigned at creation time?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect src/components/TaskList.jsx. React warns about key props and shows incorrect content after reordering. Replace 'key={index}' with 'key={task.id}' (or another stable unique identifier from the task object). Avoid using array index as a key whenever the list can be reordered, filtered, or have items inserted or removed. Do not generate keys with Math.random() as they change on every render.",
            "verification_steps": [
                "Replace 'key={index}' with 'key={task.id}' in the map call in TaskList.jsx.",
                "Drag and drop tasks to reorder them and verify the correct content stays with each task.",
                "Confirm React no longer shows key-related warnings in browser console."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-cfg-075",
        "scenario_group": "dotenv-not-loaded-before-module-import",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Node.js dotenv module loading order issue."},
        "model_input": {
            "raw_error": "Error: DATABASE_URL is not defined\n    at createPool (src/db/pool.js:5:11)\n    at Object.<anonymous> (src/db/pool.js:12:1)\n    at Object.<anonymous> (src/server.js:3:1)\n\n// src/server.js:\nimport { pool } from './db/pool.js';  // line 3 - pool.js reads process.env.DATABASE_URL\nrequire('dotenv').config();           // line 4 - loaded AFTER pool.js",
            "context": {"language_or_framework": "Node.js 20 / Express", "environment": "local_development", "recent_changes": "Reorganized module imports in src/server.js."}
        },
        "reference_annotations": {
            "reference_cause": "dotenv.config() was called after importing the pool module, so process.env.DATABASE_URL was still undefined when the pool module was evaluated.",
            "reference_repair": "Call require('dotenv').config() or import the dotenv setup module before any other imports that read environment variables.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "DATABASE_URL was undefined because dotenv was loaded after the database pool module evaluated.",
            "plain_explanation": "Node.js evaluates ES module imports at the top of a file before any other code runs. When 'src/db/pool.js' is imported on line 3, it immediately reads 'process.env.DATABASE_URL'. Because 'dotenv.config()' is not called until line 4, the environment variable has not been populated yet and evaluates to 'undefined'.",
            "error_category": "environment_variables",
            "likely_causes": [
                {"description": "dotenv.config() is called after importing modules that read environment variables during module initialization.", "confidence": "high"},
                {"description": "A refactoring moved the dotenv import lower in the file after other imports were added above it.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Is dotenv.config() called at the very beginning of the application entry point (before any other imports)?",
                "Is there a separate dotenv setup file that should be imported first?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect src/server.js. The error: \"DATABASE_URL is not defined\" occurs because 'dotenv.config()' runs after the database pool module loads. Move dotenv initialization to the very first line of your entry point: 'import \"dotenv/config\";' (ESM) or 'require(\"dotenv\").config();' (CJS) before any other imports. Alternatively, create a separate 'src/env.js' file that only calls dotenv.config() and import it first. Do not hardcode environment variable values.",
            "verification_steps": [
                "Move 'import \"dotenv/config\";' to the first line in src/server.js.",
                "Restart the server and verify DATABASE_URL is defined in process.env.",
                "Confirm the database pool initializes without throwing an error."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-bld-076",
        "scenario_group": "typescript-strict-null-checks-undefined",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic TypeScript strictNullChecks errors after enabling strict mode."},
        "model_input": {
            "raw_error": "src/components/Profile.tsx:18:24 - error TS2532: Object is possibly 'undefined'.\n\n18     const email = user.contact.email.toLowerCase();\n                         ~~~~~~~\n\nsrc/components/Profile.tsx:23:9 - error TS2322: Type 'string | undefined' is not assignable to type 'string'.\n23         displayName: user.name,",
            "context": {"language_or_framework": "TypeScript 5 / React", "environment": "local_development", "recent_changes": "Enabled 'strict: true' in tsconfig.json."}
        },
        "reference_annotations": {
            "reference_cause": "Enabling 'strict: true' activates strictNullChecks, which reveals that 'user.contact' and 'user.name' can be undefined per their type definitions.",
            "reference_repair": "Add optional chaining ('user.contact?.email?.toLowerCase()') or null checks before accessing nested properties.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "TypeScript strict mode revealed that 'user.contact' and 'user.name' can be undefined in Profile.tsx.",
            "plain_explanation": "When you enabled 'strict: true' in tsconfig.json, TypeScript activated 'strictNullChecks', which means types like 'string | undefined' must be explicitly handled before use. Your Profile component accessed 'user.contact.email' without checking if 'contact' exists, which TypeScript now flags as a potential null reference.",
            "error_category": "typescript",
            "likely_causes": [
                {"description": "Optional properties (contact, name) on the User type are accessed without null/undefined guards.", "confidence": "high"},
                {"description": "The User type was defined with optional fields (?) that were previously treated as always-present.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Can 'user.contact' legitimately be undefined for some users?",
                "Should Profile.tsx show a fallback UI when contact information is missing?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect src/components/Profile.tsx lines 18 and 23. TypeScript strict mode reports: \"TS2532: Object is possibly 'undefined'\". Use optional chaining to safely access nested properties: 'const email = user.contact?.email?.toLowerCase() ?? \"\";'. For required string fields, either update the type to be non-optional or provide a default value. Do not use 'as string' type assertions to silence these errors without addressing the underlying data handling.",
            "verification_steps": [
                "Replace direct property accesses with optional chaining in Profile.tsx.",
                "Run 'npx tsc --noEmit' and verify TS2532 and TS2322 errors are resolved.",
                "Test Profile component with a user object that has a missing 'contact' field."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-dat-077",
        "scenario_group": "supabase-rls-anon-role-missing-policy",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Supabase public read access returning 0 rows due to missing anon SELECT policy."},
        "model_input": {
            "raw_error": "Query result: { data: [], error: null }\n\n// client code:\nconst { data } = await supabase.from('products').select('*');\nconsole.log(data); // []\n\n// Supabase table editor shows 47 product rows exist.\n// RLS is enabled on products table.",
            "context": {"language_or_framework": "Supabase (public-facing site)", "environment": "production", "recent_changes": "Enabled RLS on the products table."}
        },
        "reference_annotations": {
            "reference_cause": "RLS is enabled on 'products' without a SELECT policy for the 'anon' role, so unauthenticated public visitors see zero rows.",
            "reference_repair": "Add a SELECT policy permitting the anon role to read public product rows: 'CREATE POLICY \"public_read\" ON products FOR SELECT TO anon USING (true);'",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "Product listing returned empty because RLS blocked unauthenticated (anon) access with no SELECT policy.",
            "plain_explanation": "When Row Level Security (RLS) is enabled without explicit policies, PostgreSQL defaults to denying all access. Unauthenticated Supabase clients use the 'anon' role. Since no SELECT policy grants the anon role read access to 'products', all rows are silently filtered out and the query returns an empty array with no error.",
            "error_category": "authorization",
            "likely_causes": [
                {"description": "RLS was enabled on 'products' without creating a SELECT policy for the anon role.", "confidence": "high"},
                {"description": "Existing policies only grant access to 'authenticated' role, excluding anonymous visitors.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Should all products be publicly readable by unauthenticated users?",
                "Are some products intended to be private or require authentication to view?"
            ],
            "risk_level": "high",
            "warnings": [
                "Only grant anon SELECT access if the data is intentionally public; never grant anon access to user profile data or sensitive records."
            ],
            "repair_prompt": "Please inspect RLS policies on the 'products' table in Supabase SQL Editor. The query returns empty because no policy permits the 'anon' role to read rows. If products are publicly visible, create a SELECT policy: 'CREATE POLICY \"public_products_read\" ON products FOR SELECT TO anon USING (true);'. If products should only be visible to authenticated users, grant access to the 'authenticated' role instead. Do not disable RLS.",
            "verification_steps": [
                "Create the appropriate SELECT policy in Supabase SQL Editor.",
                "Test the query from an unauthenticated context and verify products are returned.",
                "Confirm sensitive data is not inadvertently exposed to anonymous users."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-cfg-078",
        "scenario_group": "tsconfig-path-alias-not-working-jest",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Jest cannot resolve TypeScript path aliases without moduleNameMapper."},
        "model_input": {
            "raw_error": "FAIL src/tests/auth.test.ts\n  ● Test suite failed to run\n\n    Cannot find module '@/lib/auth' from 'src/tests/auth.test.ts'\n\n      1 | import { getSession } from '@/lib/auth';\n        | ^\n\n      at Resolver.resolveModule (node_modules/jest-resolve/build/defaultResolver.js:266:11)",
            "context": {"language_or_framework": "TypeScript / Jest", "environment": "local_development", "recent_changes": "Added '@' path alias in tsconfig.json."}
        },
        "reference_annotations": {
            "reference_cause": "TypeScript path aliases (like @/) are resolved by the TypeScript compiler but Jest uses its own module resolver that does not read tsconfig.json paths.",
            "reference_repair": "Add a 'moduleNameMapper' to jest.config.js mapping '@/(.*)' to '<rootDir>/src/$1'.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "Jest cannot resolve '@/lib/auth' because it does not read TypeScript path aliases from tsconfig.json.",
            "plain_explanation": "TypeScript's 'paths' configuration allows using import aliases like '@/lib/auth' instead of relative paths like '../../lib/auth'. However, Jest is a separate runtime that does not parse tsconfig.json. At test time, Jest sees '@/lib/auth' and does not know what directory '@' maps to.",
            "error_category": "configuration",
            "likely_causes": [
                {"description": "Jest does not have a 'moduleNameMapper' entry that mirrors the '@/*' path alias from tsconfig.json.", "confidence": "high"},
                {"description": "A required babel plugin or ts-jest setting for path resolution is missing from jest.config.js.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "What does your jest.config.js currently contain?",
                "Are you using ts-jest or babel-jest as the test transformer?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect jest.config.js (or jest.config.ts). Jest cannot resolve: \"Cannot find module '@/lib/auth'\". Add a 'moduleNameMapper' entry to jest config: '{ \"^@/(.*)$\": \"<rootDir>/src/$1\" }'. Ensure this mirrors the 'paths' setting in tsconfig.json. If using ts-jest, also set 'pathsToModuleNameMapper' from 'ts-jest'. Do not change application source paths.",
            "verification_steps": [
                "Add moduleNameMapper: { \"^@/(.*)$\": \"<rootDir>/src/$1\" } to jest.config.js.",
                "Run 'npx jest auth.test.ts' and verify the test suite runs without module resolution errors.",
                "Confirm all other test files using '@/' aliases also pass."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-amb-079",
        "scenario_group": "ci-no-output-silent-failure",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic CI job silent failure with no log output and non-zero exit code."},
        "model_input": {
            "raw_error": "Run npm test\n\n$ npm test\n\nProcess exited with code 1.",
            "context": {"language_or_framework": "Node.js / GitHub Actions", "environment": "ci_build", "recent_changes": "Added npm test to CI workflow."}
        },
        "reference_annotations": {
            "reference_cause": "The test command exited with code 1 but produced no output, indicating either the test runner did not start or its output was captured/suppressed by the CI environment.",
            "reference_repair": "Run the test command locally with verbose flags and check for missing test runner, missing test files, or pre-execution crashes.",
            "difficulty": "hard"
        },
        "target_report": {
            "summary": "CI test step failed with exit code 1 but produced no output to diagnose the failure.",
            "plain_explanation": "The 'npm test' command exited with a failure code (1) but did not print any error message, warning, or test result. This silent failure pattern usually means the test runner process crashed before outputting anything, the 'test' script in package.json was not found, or a pre-test setup hook failed.",
            "error_category": "unknown",
            "likely_causes": [
                {"description": "The 'test' script is not defined in package.json, causing npm to exit with code 1 silently.", "confidence": "high"},
                {"description": "A test setup file or imported module crashes before the first test runs, suppressing output.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "What is the 'scripts.test' value in your package.json?",
                "Does running 'npm test' locally produce any output?",
                "Are there any CI environment variables that might be capturing or redirecting test output?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect package.json and your CI workflow configuration. The test step fails with: \"Process exited with code 1\" and no output. First, verify the 'test' script exists in package.json and run 'npm test' locally to see actual output. If the test script is missing, add it. If the runner crashes silently, add the '--verbose' flag to your test command in package.json. Do not skip test steps in CI.",
            "verification_steps": [
                "Run 'npm test' locally in a terminal and capture the full output.",
                "Verify the 'test' key exists in package.json scripts.",
                "Add '--verbose' to the test command to force output and identify the failure source."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-amb-080",
        "scenario_group": "uncaught-promise-rejection-swallowed",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic unhandled promise rejection swallowed by missing catch block."},
        "model_input": {
            "raw_error": "(node:12345) UnhandledPromiseRejectionWarning: Error: connect ECONNREFUSED 127.0.0.1:5432\n(Use `node --trace-warnings ...` to show where the warning was created)\n(node:12345) UnhandledPromiseRejectionWarning: Unhandled promise rejection. This error originated either by throwing inside of an async function without a catch block, or by rejecting a promise which was not handled with .catch().\n(node:12345) [DEP0018] DeprecationWarning: Unhandled promise rejections are deprecated. In future versions of Node.js, promise rejections that are not handled will terminate the Node.js process with a non-zero exit code.",
            "context": {"language_or_framework": "Node.js 20 / Express", "environment": "local_development", "recent_changes": "Added async database initialization at server startup."}
        },
        "reference_annotations": {
            "reference_cause": "An async database connection call at server startup failed with ECONNREFUSED, but no .catch() handler or try/catch block captured the rejection.",
            "reference_repair": "Wrap async database initialization in try/catch and handle connection failures gracefully at startup.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "Node.js reported an unhandled promise rejection from a database connection failure (ECONNREFUSED) at startup.",
            "plain_explanation": "An async function called at server startup tried to connect to a PostgreSQL database at 127.0.0.1:5432 but was refused. The async call had no 'try/catch' block or '.catch()' handler, so the error propagated as an unhandled promise rejection. In newer Node.js versions, unhandled rejections crash the process.",
            "error_category": "network",
            "likely_causes": [
                {"description": "The database server (PostgreSQL) is not running locally on port 5432.", "confidence": "high"},
                {"description": "The async initialization code lacks a try/catch or .catch() to handle connection failures gracefully.", "confidence": "high"}
            ],
            "missing_context_questions": [
                "Is your PostgreSQL database service running locally?",
                "Where in your startup code is the database connection initialized, and does it have error handling?"
            ],
            "risk_level": "medium",
            "warnings": [],
            "repair_prompt": "Please inspect server startup code. Node.js reports: \"UnhandledPromiseRejectionWarning: Error: connect ECONNREFUSED 127.0.0.1:5432\". Two things need to happen: (1) Ensure your database is running — check 'pg_isready' or your Docker container status. (2) Add try/catch around the async database init: 'try { await connectDB(); } catch (err) { console.error(\"Database connection failed:\", err.message); process.exit(1); }'. Do not silently swallow database connection errors.",
            "verification_steps": [
                "Verify PostgreSQL is running with 'pg_isready -h 127.0.0.1 -p 5432'.",
                "Add try/catch around the async database connection call at startup.",
                "Restart the server and confirm it either connects successfully or exits with a clear error message."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-run-081",
        "scenario_group": "react-suspense-no-fallback",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic React Suspense error when lazy component has no Suspense boundary."},
        "model_input": {
            "raw_error": "Error: A React component suspended while rendering, but no fallback UI was specified.\n\nAdd a <Suspense fallback=...> component higher in the tree to provide a loading indicator or placeholder to display.\n    at Dashboard (src/app/dashboard/page.tsx)\n\n// code:\nconst HeavyChart = lazy(() => import('./HeavyChart'));",
            "context": {"language_or_framework": "React 18 / Next.js", "environment": "local_development", "recent_changes": "Added a lazily loaded chart component to the dashboard."}
        },
        "reference_annotations": {
            "reference_cause": "React.lazy() was used to lazily import HeavyChart, but no <Suspense> boundary with a fallback was wrapped around it.",
            "reference_repair": "Wrap the lazy component with <Suspense fallback={<LoadingSpinner />}><HeavyChart /></Suspense>.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "React crashed because a lazy-loaded component suspended without a surrounding Suspense boundary.",
            "plain_explanation": "When you use 'React.lazy()' to split code into chunks that load on demand, React 'suspends' rendering while the chunk downloads. React requires a '<Suspense>' component somewhere in the tree above the lazy component to show a fallback UI (like a spinner) during the loading delay. Without it, React throws an error.",
            "error_category": "runtime",
            "likely_causes": [
                {"description": "The lazy-loaded HeavyChart component is rendered without a <Suspense> boundary wrapping it.", "confidence": "high"},
                {"description": "The Suspense boundary exists but is placed below the lazy component rather than above it.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Is there a <Suspense> component anywhere in the Dashboard component tree?",
                "What should the loading state look like while the chart chunk downloads?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect the Dashboard component where HeavyChart is rendered. React reports: \"A React component suspended while rendering, but no fallback UI was specified\". Wrap the HeavyChart usage in a Suspense boundary: '<Suspense fallback={<div>Loading chart...</div>}><HeavyChart /></Suspense>'. Place the Suspense boundary above the lazy component in the JSX tree. Do not remove code splitting if page performance benefits from it.",
            "verification_steps": [
                "Wrap HeavyChart with <Suspense fallback={<p>Loading...</p>}>.</Suspense>",
                "Simulate a slow network in browser DevTools and verify the fallback displays while the chart loads.",
                "Confirm the chart renders correctly after the chunk downloads."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-dpl-082",
        "scenario_group": "github-actions-env-secret-not-set",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic GitHub Actions deployment failure because repository secret is not configured."},
        "model_input": {
            "raw_error": "Run npm run deploy\n  > my-app deploy\n  > vercel --prod\n\nError: The 'VERCEL_TOKEN' environment variable is missing or empty. This is required to authenticate with Vercel.\nProcess exited with code 1",
            "context": {"language_or_framework": "GitHub Actions / Vercel", "environment": "ci_build", "recent_changes": "Added a GitHub Actions deployment workflow."}
        },
        "reference_annotations": {
            "reference_cause": "The GitHub Actions workflow references ${{ secrets.VERCEL_TOKEN }} but the secret has not been added to the repository's Secrets settings.",
            "reference_repair": "Add VERCEL_TOKEN to GitHub repository Settings -> Secrets and variables -> Actions -> Repository secrets.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "GitHub Actions deployment failed because the VERCEL_TOKEN secret was not configured in repository settings.",
            "plain_explanation": "The deployment workflow uses the Vercel CLI, which requires an authentication token via 'VERCEL_TOKEN'. Although the GitHub Actions YAML file references '${{ secrets.VERCEL_TOKEN }}', the secret was never added to the GitHub repository's secret store, so the environment variable passed to the CLI is empty.",
            "error_category": "deployment",
            "likely_causes": [
                {"description": "The 'VERCEL_TOKEN' secret has not been added to GitHub repository Secrets under Settings -> Secrets and variables -> Actions.", "confidence": "high"},
                {"description": "The secret exists but uses a different name than referenced in the workflow YAML file.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Is 'VERCEL_TOKEN' visible in GitHub repository Settings -> Secrets and variables?",
                "How is the secret referenced in your .github/workflows/*.yml file?"
            ],
            "risk_level": "low",
            "warnings": [
                "Vercel tokens grant deployment access; treat them as credentials and never commit them to source code."
            ],
            "repair_prompt": "Please inspect your GitHub Actions workflow file and repository secret settings. Vercel CLI fails with: \"VERCEL_TOKEN environment variable is missing\". In GitHub, navigate to repository Settings -> Secrets and variables -> Actions, and click 'New repository secret'. Name it 'VERCEL_TOKEN' and paste a Vercel token generated from your Vercel account settings. Verify the name in the YAML matches exactly. Do not commit the token to source code.",
            "verification_steps": [
                "Generate a Vercel token at vercel.com/account/tokens.",
                "Add VERCEL_TOKEN as a repository secret in GitHub Settings.",
                "Re-run the failed GitHub Actions workflow and confirm deployment completes."
            ],
            "matched_recipes": []
        }
    },

    # ---------------------------------------------------------------
    # VALIDATION SPLIT (4 records: syn-*-083 through syn-*-086)
    # ---------------------------------------------------------------
    {
        "id": "syn-run-083",
        "scenario_group": "nextjs-image-domain-not-configured",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Next.js Image component domain not allowed error."},
        "model_input": {
            "raw_error": "Error: Invalid src prop (https://images.unsplash.com/photo-abc123.jpg) on `next/image`, hostname \"images.unsplash.com\" is not configured under images in your `next.config.js`\nSee more info: https://nextjs.org/docs/messages/next-image-unconfigured-host",
            "context": {"language_or_framework": "Next.js 14", "environment": "local_development", "recent_changes": "Used next/image component to display images from Unsplash CDN."}
        },
        "reference_annotations": {
            "reference_cause": "Next.js Image optimization requires external hostnames to be explicitly allowlisted in next.config.js before it will proxy and optimize them.",
            "reference_repair": "Add 'images.unsplash.com' to the remotePatterns array in next.config.js.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "next/image rejected the Unsplash URL because 'images.unsplash.com' is not in next.config.js remotePatterns.",
            "plain_explanation": "Next.js's built-in Image component optimizes images on the fly. For security, it only proxies images from domains you explicitly allow in 'next.config.js'. When you use an external URL from 'images.unsplash.com' without listing it in 'remotePatterns', Next.js blocks the request to prevent unauthorized image proxying.",
            "error_category": "configuration",
            "likely_causes": [
                {"description": "The 'images.unsplash.com' hostname is not listed in the 'remotePatterns' or 'domains' array in next.config.js.", "confidence": "high"},
                {"description": "The next.config.js file was not restarted after modification.", "confidence": "low"}
            ],
            "missing_context_questions": [
                "What is currently configured in the 'images' section of next.config.js?",
                "Will your application always use Unsplash, or could multiple image CDN domains be needed?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect next.config.js. Next.js throws: \"hostname 'images.unsplash.com' is not configured under images\". Add the hostname to remotePatterns: 'images: { remotePatterns: [{ protocol: \"https\", hostname: \"images.unsplash.com\" }] }'. Restart the Next.js dev server after modifying next.config.js. Only allowlist domains you trust.",
            "verification_steps": [
                "Add 'images.unsplash.com' to remotePatterns in next.config.js.",
                "Restart the dev server ('npm run dev').",
                "Verify the image renders in browser without the hostname error."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-dat-084",
        "scenario_group": "mongodb-duplicate-key-error-11000",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic MongoDB duplicate key error on unique index."},
        "model_input": {
            "raw_error": "MongoServerError: E11000 duplicate key error collection: myapp.users index: email_1 dup key: { email: \"alice@example.com\" }\n    at Connection.onMessage (node_modules/mongodb/lib/cmap/connection.js:207:26)\n    at src/services/auth.js:24:15",
            "context": {"language_or_framework": "Node.js / MongoDB / Mongoose", "environment": "local_development", "recent_changes": "Added user registration endpoint."}
        },
        "reference_annotations": {
            "reference_cause": "A document with email 'alice@example.com' already exists in the users collection and the email field has a unique index.",
            "reference_repair": "Check for existing users with the same email before inserting, and return an appropriate error message to the client.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "MongoDB rejected user registration because 'alice@example.com' already exists in the users collection.",
            "plain_explanation": "Your MongoDB users collection has a unique index on the 'email' field, meaning each email can only appear once. When you attempted to register a user with 'alice@example.com', MongoDB detected that an existing document already has this email and threw error E11000 to prevent duplicate records.",
            "error_category": "database",
            "likely_causes": [
                {"description": "A user with email 'alice@example.com' already exists in the users collection.", "confidence": "high"},
                {"description": "A retry or idempotent registration call was made twice without deduplication logic.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Is this an expected case (user already registered) or an unexpected duplicate?",
                "Does your registration endpoint check for existing emails before attempting the insert?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect src/services/auth.js around line 24. MongoDB throws: \"E11000 duplicate key error... email: alice@example.com\". Add a pre-check before the insert: query for an existing user with the same email, and if found, return a user-friendly error like 'Email already registered'. Wrap the insert in a try/catch that specifically handles error code 11000 to surface a clean error to the API caller. Do not remove the unique index.",
            "verification_steps": [
                "Add a duplicate email check before inserting a new user.",
                "Verify the API returns a 409 Conflict or descriptive error when registering an existing email.",
                "Test registering the same email twice and confirm the second attempt is rejected gracefully."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-cfg-085",
        "scenario_group": "vite-proxy-target-port-mismatch",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Vite dev server proxy pointing to wrong backend port."},
        "model_input": {
            "raw_error": "[vite] http proxy error: /api/users\nError: connect ECONNREFUSED 127.0.0.1:3000\n  at TCPConnectWrap.afterConnect [as oncomplete] (node:net:1238:16)\n  errno: -111,\n  code: 'ECONNREFUSED',\n  syscall: 'connect',\n  address: '127.0.0.1',\n  port: 3000",
            "context": {"language_or_framework": "Vite / Express", "environment": "local_development", "recent_changes": "Changed backend Express server port from 3000 to 4000."}
        },
        "reference_annotations": {
            "reference_cause": "vite.config.js proxy target still points to port 3000 while the Express backend server was changed to listen on port 4000.",
            "reference_repair": "Update the proxy target in vite.config.js to 'http://localhost:4000'.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "Vite dev proxy failed because it is forwarding API requests to port 3000 while the backend runs on port 4000.",
            "plain_explanation": "Vite's dev server has a proxy configured to forward '/api/' requests to a backend server. The proxy target is set to 'http://localhost:3000', but after changing the Express server port to 4000, the proxy target was not updated. Requests are now refused because nothing is listening on port 3000.",
            "error_category": "configuration",
            "likely_causes": [
                {"description": "The proxy target in vite.config.js was not updated after the backend port changed.", "confidence": "high"},
                {"description": "The backend Express server is not running, causing ECONNREFUSED on the correct port as well.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "What port is your Express server currently listening on?",
                "What is the proxy target set to in vite.config.js?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect vite.config.js and your Express server startup logs. Vite proxy reports: \"ECONNREFUSED 127.0.0.1:3000\". Update the proxy target to match the current backend port: 'server: { proxy: { \"/api\": { target: \"http://localhost:4000\" } } }'. Restart Vite after saving. Also confirm the Express server is running on port 4000.",
            "verification_steps": [
                "Update vite.config.js proxy target to 'http://localhost:4000'.",
                "Restart Vite dev server.",
                "Call an API endpoint from the browser and verify a successful response."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-amb-086",
        "scenario_group": "cryptic-js-heap-out-of-memory",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Node.js JavaScript heap out of memory crash during build."},
        "model_input": {
            "raw_error": "<--- Last few GCs --->\n[12345:0x7f2abc] 214 ms: Scavenge 487.3 (501.0) -> 487.2 (502.0) MB, 2.4 / 0.0 ms\n[12345:0x7f2abc] 219 ms: Scavenge 487.8 (502.0) -> 487.6 (502.0) MB, 1.7 / 0.0 ms\n<--- JS stacktrace --->\nFATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory\n --max-old-space-size=4096 to increase this.",
            "context": {"language_or_framework": "Node.js / Webpack", "environment": "ci_build", "recent_changes": "Increased the number of entry points in the Webpack build."}
        },
        "reference_annotations": {
            "reference_cause": "The Node.js process hit its V8 heap memory limit during a large Webpack build. This typically happens with many large entry points or when analyzing large dependency trees.",
            "reference_repair": "Pass --max-old-space-size=4096 (or higher) to Node.js via NODE_OPTIONS or the build script.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "Node.js crashed during Webpack build with 'JavaScript heap out of memory'.",
            "plain_explanation": "Node.js runs JavaScript in a V8 engine that has a configurable heap memory limit (default around 1.5 GB on 64-bit systems). Compiling a large Webpack bundle with many entry points, dependencies, or source map generation consumed more memory than the limit, causing a fatal crash.",
            "error_category": "unknown",
            "likely_causes": [
                {"description": "The Webpack build processes more entry points or larger dependency trees than the default Node.js heap limit allows.", "confidence": "high"},
                {"description": "Source map generation or a large bundle analyzer plugin is consuming excessive memory.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "How much RAM is available on the build machine or CI runner?",
                "Does the build succeed locally on a machine with more RAM?"
            ],
            "risk_level": "medium",
            "warnings": [],
            "repair_prompt": "Please inspect your build script in package.json and CI configuration. The build crashes with: \"FATAL ERROR: Reached heap limit - JavaScript heap out of memory\". Increase Node.js memory by prefixing the build command with 'NODE_OPTIONS=\"--max-old-space-size=4096\" npm run build' in package.json or as a CI environment variable. Also investigate whether source maps can be disabled for CI builds or if large Webpack chunks can be code-split. Do not increase memory beyond what the machine supports.",
            "verification_steps": [
                "Add NODE_OPTIONS='--max-old-space-size=4096' to the build environment.",
                "Retry the build and verify it completes without heap exhaustion.",
                "Profile Webpack memory usage to identify and split particularly heavy chunks."
            ],
            "matched_recipes": []
        }
    },

    # ---------------------------------------------------------------
    # TEST SPLIT (4 records: syn-*-087 through syn-*-090)
    # ---------------------------------------------------------------
    {
        "id": "syn-run-087",
        "scenario_group": "react-stale-closure-useeffect",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic React stale closure inside useEffect with empty dependency array."},
        "model_input": {
            "raw_error": "// Observed behavior (no thrown error, logic bug):\n// Count always shows 0 in the interval callback even after incrementing.\n\nuseEffect(() => {\n  const interval = setInterval(() => {\n    console.log('count:', count); // always logs 0\n    setCount(count + 1);          // always sets to 1\n  }, 1000);\n  return () => clearInterval(interval);\n}, []); // empty deps",
            "context": {"language_or_framework": "React 18", "code_excerpt": "const [count, setCount] = useState(0);\nuseEffect(() => {\n  const interval = setInterval(() => { setCount(count + 1); }, 1000);\n  return () => clearInterval(interval);\n}, []);", "environment": "local_development"}
        },
        "reference_annotations": {
            "reference_cause": "The empty dependency array causes the effect to capture a stale closure over 'count' (always 0). Each tick sets count to 0+1=1 rather than incrementing.",
            "reference_repair": "Use the functional updater form: 'setCount(prev => prev + 1)' to avoid depending on the stale closure value.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "The counter is stuck at 1 because setInterval captured a stale closure over 'count = 0'.",
            "plain_explanation": "When you pass an empty dependency array '[]' to useEffect, the effect function is created once and captures the value of 'count' at that moment (0). Every time the setInterval callback runs, it reads the same stale '0' and sets count to '0 + 1 = 1'. The actual current count value is never read because the closure was frozen at initialization.",
            "error_category": "runtime",
            "likely_causes": [
                {"description": "The interval callback reads 'count' from a stale closure captured when the effect first ran with the empty dependency array.", "confidence": "high"},
                {"description": "The developer intended to include 'count' in the dependency array but omitted it to avoid the interval resetting on every render.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Does the component need to access other state or props inside the interval?",
                "Is the interval expected to run continuously or until some condition is met?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect the useEffect with setInterval in your component. The counter is stuck at 1 due to a stale closure. Replace 'setCount(count + 1)' with the functional updater form: 'setCount(prev => prev + 1)'. This reads the latest state value inside the setter rather than from the closed-over variable. The empty dependency array can remain since the interval no longer depends on 'count' directly. Do not add 'count' to the dependency array as it would reset the interval on every tick.",
            "verification_steps": [
                "Replace 'setCount(count + 1)' with 'setCount(prev => prev + 1)' in the interval callback.",
                "Open the component in browser and verify the counter increments correctly every second.",
                "Check console.log output to confirm 'count' reflects the latest value."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-cfg-088",
        "scenario_group": "missing-robots-txt-env-specific",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Next.js robots.txt configuration serving wrong environment robots file."},
        "model_input": {
            "raw_error": "Lighthouse SEO audit warning: robots.txt is blocking all search engine crawlers.\n\n// Current public/robots.txt:\nUser-agent: *\nDisallow: /\n\n// Environment: Production (myapp.com)\n// Intended behavior: Allow indexing in production, block in staging.",
            "context": {"language_or_framework": "Next.js", "environment": "production", "recent_changes": "Deployed to production without changing robots.txt from staging configuration."}
        },
        "reference_annotations": {
            "reference_cause": "The staging robots.txt that blocks all crawlers was deployed to production without being replaced with the production version that allows indexing.",
            "reference_repair": "Generate environment-specific robots.txt via Next.js app/robots.ts metadata API or a build script that uses NODE_ENV to write the appropriate file.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "Production site has a robots.txt that blocks all search engine crawlers, preventing indexing.",
            "plain_explanation": "The file 'public/robots.txt' currently contains 'Disallow: /' which instructs all search engine crawlers to avoid indexing the entire site. This configuration is appropriate for staging environments to prevent search engines from indexing test content, but it was accidentally deployed to production where the site should be publicly indexed.",
            "error_category": "configuration",
            "likely_causes": [
                {"description": "The same robots.txt file is used for both staging and production without environment-specific overrides.", "confidence": "high"},
                {"description": "The robots.txt file was not updated during the production deployment process.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Should production allow all crawlers or only specific pages?",
                "Is there a build script or CI step that should generate environment-specific robots.txt?"
            ],
            "risk_level": "high",
            "warnings": [
                "A production site blocked by robots.txt will not be indexed by Google or other search engines. Existing cached pages may also be removed over time."
            ],
            "repair_prompt": "Please update your robots.txt for production. The current file blocks all crawlers: 'Disallow: /'. For production, create a robots.txt that allows crawling: 'User-agent: *\\nDisallow: ' (empty Disallow allows all). Use Next.js's 'app/robots.ts' metadata API to generate environment-specific robots.txt automatically based on process.env.NODE_ENV. Do not deploy staging configuration to production.",
            "verification_steps": [
                "Create app/robots.ts in Next.js to return appropriate robots config per environment.",
                "Deploy to production and verify https://myapp.com/robots.txt shows 'Disallow: ' (empty).",
                "Re-run Lighthouse SEO audit and confirm robots.txt no longer blocks crawlers."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-ath-089",
        "scenario_group": "jwt-verify-wrong-secret",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic JWT signature verification failure due to mismatched signing secret."},
        "model_input": {
            "raw_error": "JsonWebTokenError: invalid signature\n    at /verify (/node_modules/jsonwebtoken/verify.js:89:21)\n    at authMiddleware (src/middleware/auth.js:15:12)\n    at Layer.handle [as handle_request] (node_modules/express/lib/router/layer.js:95:5)",
            "context": {"language_or_framework": "Node.js / Express / JWT", "environment": "staging", "recent_changes": "Rotated the JWT signing secret in the staging environment."}
        },
        "reference_annotations": {
            "reference_cause": "The JWT was signed with the old secret key but is being verified with the new rotated secret, causing the signature check to fail.",
            "reference_repair": "Ensure all services use the same JWT_SECRET for signing and verifying, or implement a key rotation strategy that accepts old tokens during a transition period.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "JWT verification failed because the token was signed with a different secret than the one used for verification.",
            "plain_explanation": "JSON Web Tokens are signed with a secret key when created and must be verified with the same secret key. After you rotated (changed) the JWT signing secret in the staging environment, existing tokens that users already have were signed with the old secret. Verifying them against the new secret fails with 'invalid signature'.",
            "error_category": "authentication",
            "likely_causes": [
                {"description": "The JWT_SECRET environment variable was rotated, invalidating all previously issued tokens.", "confidence": "high"},
                {"description": "Different services (auth service vs API service) are using different JWT_SECRET values.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Was the JWT_SECRET recently changed in the staging environment?",
                "Are multiple services involved in signing vs verifying tokens? Do they all share the same secret?"
            ],
            "risk_level": "high",
            "warnings": [
                "Rotating secrets invalidates all existing sessions; plan user re-authentication or implement graceful key rotation.",
                "Never use the same JWT_SECRET across different environments (development, staging, production)."
            ],
            "repair_prompt": "Please inspect src/middleware/auth.js and the JWT_SECRET environment variable. The error: \"JsonWebTokenError: invalid signature\" occurs because tokens are verified with a different secret than they were signed with. Ensure the same JWT_SECRET is used everywhere. After rotating a secret, existing tokens cannot be verified; implement a re-login flow for users. If this was accidental, restore the previous secret temporarily. Do not use a hardcoded fallback secret in code.",
            "verification_steps": [
                "Verify the JWT_SECRET environment variable matches on all services that sign or verify tokens.",
                "After confirming the secret matches, request a fresh token and verify it successfully passes the middleware.",
                "For production rotations, implement token versioning or use short expiry times to minimize disruption."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-amb-090",
        "scenario_group": "build-output-missing-after-deploy",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic ambiguous production 404s after deployment from missing build output or gitignored dist."},
        "model_input": {
            "raw_error": "Production URL: https://myapp.example.com\nBrowser: 404 Not Found on all pages\n\nDeployment log:\n[15:22:05] Deploy completed successfully.\n[15:22:06] Site live at https://myapp.example.com\n\nLocal check: 'dist/' folder exists locally with correct build files.",
            "context": {"language_or_framework": "Vite / Static Hosting", "environment": "production", "recent_changes": "Deployed static Vite build to hosting via git push."}
        },
        "reference_annotations": {
            "reference_cause": "The 'dist/' build output folder is listed in .gitignore and was never committed, so the hosting platform deployed an empty repository with no static files.",
            "reference_repair": "Either remove dist/ from .gitignore and commit it, or configure the hosting platform to run the build command during deployment.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "Production shows 404 on all pages because the 'dist/' build folder was not deployed (likely ignored by .gitignore).",
            "plain_explanation": "The deployment log reports success but every page returns 404. This happens when the hosting platform deployed the repository content, but the compiled 'dist/' folder was excluded from git via '.gitignore' and therefore never uploaded. The hosting server finds no HTML, JS, or CSS files to serve.",
            "error_category": "unknown",
            "likely_causes": [
                {"description": "'dist/' is listed in .gitignore so it is not included in the deployed repository push.", "confidence": "high"},
                {"description": "The hosting platform was not configured to run a build command, so no build output was generated on the server.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Is 'dist/' listed in your .gitignore file?",
                "Is your hosting platform configured to run a build command (like 'npm run build') after deployment?",
                "What hosting platform are you using (Netlify, GitHub Pages, Cloudflare Pages, Nginx)?"
            ],
            "risk_level": "medium",
            "warnings": [],
            "repair_prompt": "Please inspect your .gitignore and hosting platform configuration. Production returns 404 after a successful deploy. Check whether 'dist/' is in .gitignore. If using a static hosting platform (Netlify, Vercel, Cloudflare Pages), configure a build command ('npm run build') and publish directory ('dist') in the platform settings instead of deploying pre-built files. If using git-based deployments with no build server, remove 'dist/' from .gitignore and commit the build output. Do not deploy empty repositories.",
            "verification_steps": [
                "Check .gitignore for a 'dist' entry.",
                "Configure your hosting platform's build command to 'npm run build' and publish directory to 'dist'.",
                "Redeploy and verify all pages load successfully at the production URL."
            ],
            "matched_recipes": []
        }
    }
]


def main():
    print(f"Total Batch 3 records prepared: {len(RECORDS)}")
    assert len(RECORDS) == 30, f"Expected 30 records, got {len(RECORDS)}"

    train_records = RECORDS[:22]
    val_records   = RECORDS[22:26]
    test_records  = RECORDS[26:]

    assert len(train_records) == 22, f"Expected 22 train records, got {len(train_records)}"
    assert len(val_records)   == 4,  f"Expected 4 val records, got {len(val_records)}"
    assert len(test_records)  == 4,  f"Expected 4 test records, got {len(test_records)}"

    all_ids = [r["id"] for r in RECORDS]
    assert len(all_ids) == len(set(all_ids)), "Duplicate IDs in batch!"

    groups = [r["scenario_group"] for r in RECORDS]
    assert len(groups) == len(set(groups)), "Duplicate scenario groups in batch!"

    train_g = {r["scenario_group"] for r in train_records}
    val_g   = {r["scenario_group"] for r in val_records}
    test_g  = {r["scenario_group"] for r in test_records}
    assert train_g.isdisjoint(val_g),  "Train/Val scenario group overlap!"
    assert train_g.isdisjoint(test_g), "Train/Test scenario group overlap!"
    assert val_g.isdisjoint(test_g),   "Val/Test scenario group overlap!"

    # Check against existing split IDs for cross-batch uniqueness
    for split in ("train", "validation", "test"):
        path = ROOT / "data" / f"{split}.jsonl"
        if path.exists():
            existing_ids = {
                json.loads(line)["id"]
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            }
            for r in RECORDS:
                assert r["id"] not in existing_ids, f"ID {r['id']} already exists in {split}.jsonl!"

    from inference.schema import validate_instance
    from training.validate_data import _strings, SENSITIVE_VALUE, load_valid_recipes

    schema       = json.loads((ROOT / "data" / "schema.json").read_text(encoding="utf-8"))
    valid_recipes = load_valid_recipes(ROOT / "knowledge-base")

    ALLOWED_CATEGORIES = set(schema.get("properties", {}).get("error_category", {}).get("enum", []))

    for r in RECORDS:
        rid = r["id"]
        cat = r["target_report"].get("error_category", "")
        assert cat in ALLOWED_CATEGORIES, f"{rid}: error_category '{cat}' not in schema enum {ALLOWED_CATEGORIES}"
        errors = validate_instance(r["target_report"], schema, f"{rid}.target_report")
        if errors:
            raise ValueError(f"Schema errors in {rid}: {errors}")
        for s in _strings(r):
            if SENSITIVE_VALUE.search(s):
                raise ValueError(f"Secret regex triggered in {rid}: {s[:50]}...")

    print("All 30 Batch 3 records passed schema, category, and secret validation.")

    def append_records(path: Path, new_records: list[dict]):
        with open(path, "a", encoding="utf-8") as f:
            for rec in new_records:
                f.write(json.dumps(rec) + "\n")
        print(f"Appended {len(new_records)} records to {path}")

    append_records(ROOT / "data" / "train.jsonl",      train_records)
    append_records(ROOT / "data" / "validation.jsonl", val_records)
    append_records(ROOT / "data" / "test.jsonl",       test_records)


if __name__ == "__main__":
    main()
