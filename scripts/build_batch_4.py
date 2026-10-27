import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import json
from typing import Any

RECORDS: list[dict[str, Any]] = [
    # ---------------------------------------------------------------
    # TRAIN SPLIT (22 records: syn-*-091 through syn-*-112)
    # ---------------------------------------------------------------
    {
        "id": "syn-run-091",
        "scenario_group": "nextjs-server-action-revalidate-path",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Next.js Server Action mutation not reflected in UI due to missing revalidatePath."},
        "model_input": {
            "raw_error": "// Observed behavior: After form submission the UI does not update. Server action runs successfully (logs confirm DB write). Page still shows old data.\n\n// src/app/actions.ts\n'use server';\nexport async function createPost(formData: FormData) {\n  await db.post.create({ data: { title: formData.get('title') } });\n  // No cache invalidation\n}",
            "context": {"language_or_framework": "Next.js 14 (App Router / Server Actions)", "environment": "local_development", "recent_changes": "Replaced API route with a Server Action for the post creation form."}
        },
        "reference_annotations": {
            "reference_cause": "The Server Action mutates data but does not call revalidatePath() or revalidateTag(), so Next.js serves stale cached page data after the mutation.",
            "reference_repair": "Call 'revalidatePath(\"/posts\")' from next/cache inside the Server Action after the database write.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "Server Action wrote to the database but the page stayed stale because revalidatePath was not called.",
            "plain_explanation": "Next.js App Router aggressively caches page data. When a Server Action mutates data, Next.js does not automatically know which cached pages are now stale. Without calling 'revalidatePath()' or 'revalidateTag()' inside the action, the router continues to serve the old cached data even though the database was updated.",
            "error_category": "runtime",
            "likely_causes": [
                {"description": "The Server Action writes to the database but does not call revalidatePath() to bust the cached page.", "confidence": "high"},
                {"description": "The page uses fetch with caching and no cache tag was provided to invalidate via revalidateTag().", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Does the posts list page use a fetch call with cache settings or 'unstable_cache'?",
                "Should the whole /posts path be revalidated, or only a specific tag?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect src/app/actions.ts. The Server Action writes to the DB but the page shows stale data. Import and call 'revalidatePath' from next/cache after the database write: 'import { revalidatePath } from \"next/cache\"; ... revalidatePath(\"/posts\");'. Optionally use 'redirect(\"/posts\")' from next/navigation to send the user back to the list. Do not call revalidatePath in a try/catch that swallows errors.",
            "verification_steps": [
                "Add 'import { revalidatePath } from \"next/cache\";' at the top of src/app/actions.ts.",
                "Call 'revalidatePath(\"/posts\")' immediately after the successful database write.",
                "Submit the form and verify the new post appears in the list without a manual refresh."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-run-092",
        "scenario_group": "nextjs-parallel-routes-unmatched-slot",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Next.js parallel route slot not rendering due to missing default.tsx."},
        "model_input": {
            "raw_error": "Error: Missing required 'default.js' or 'default.tsx' file for parallel route slot '@modal'.\n\nNext.js requires a default export in the @modal slot to render when the slot does not match the current route.\n    at ParallelRouteError (node_modules/next/dist/client/components/parallel-route-default.js:12:10)",
            "context": {"language_or_framework": "Next.js 14 (App Router / Parallel Routes)", "environment": "local_development", "recent_changes": "Added a @modal parallel route slot to the dashboard layout."}
        },
        "reference_annotations": {
            "reference_cause": "Next.js parallel route slots require a 'default.tsx' file to render when no child route matches, similar to a fallback. The @modal slot was created without one.",
            "reference_repair": "Create 'src/app/dashboard/@modal/default.tsx' that returns null or an empty fragment as the default state.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "Next.js parallel route slot '@modal' is missing a 'default.tsx' fallback file.",
            "plain_explanation": "Parallel routes in Next.js let you render multiple pages simultaneously in the same layout. Each named slot (like '@modal') must have a 'default.tsx' file that Next.js renders when no specific sub-route matches for that slot. Without this file, Next.js throws an error when navigating to routes that don't explicitly render the slot.",
            "error_category": "configuration",
            "likely_causes": [
                {"description": "The @modal slot folder was created without a default.tsx file.", "confidence": "high"},
                {"description": "The default.tsx file exists but does not have a default export.", "confidence": "low"}
            ],
            "missing_context_questions": [
                "Should the modal slot render nothing (null) when not active, or show a placeholder?",
                "Is this a soft or hard navigation scenario for the modal?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please create 'src/app/dashboard/@modal/default.tsx'. Next.js requires a default export in every parallel route slot for non-matching routes. Create the file with: 'export default function ModalDefault() { return null; }'. This tells Next.js to render nothing in the modal slot when no modal route is active. Do not add layout or UI logic to the default file.",
            "verification_steps": [
                "Create 'src/app/dashboard/@modal/default.tsx' with a default export returning null.",
                "Navigate to the dashboard route and verify the layout renders without error.",
                "Trigger a modal route and confirm the slot renders the correct modal content."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-dat-093",
        "scenario_group": "supabase-storage-bucket-access-denied",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Supabase Storage bucket returning 400 storage/unauthorized on upload."},
        "model_input": {
            "raw_error": "StorageApiError: storage/unauthorized\n  statusCode: '403'\n  error: 'Unauthorized'\n  message: 'new row violates row-level security policy'\n\n// Client code:\nconst { error } = await supabase.storage.from('avatars').upload(path, file);",
            "context": {"language_or_framework": "Supabase Storage / Next.js", "environment": "production", "recent_changes": "Created a new 'avatars' storage bucket."}
        },
        "reference_annotations": {
            "reference_cause": "The 'avatars' storage bucket has RLS enabled but no INSERT policy exists for the 'authenticated' role, blocking all uploads.",
            "reference_repair": "Add a storage INSERT policy: 'CREATE POLICY \"user_upload\" ON storage.objects FOR INSERT TO authenticated WITH CHECK (bucket_id = \"avatars\" AND auth.uid()::text = (storage.foldername(name))[1]);'",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "Supabase Storage rejected the avatar upload because no INSERT RLS policy exists for authenticated users.",
            "plain_explanation": "Supabase Storage buckets use Row Level Security by default. When a bucket is created without explicit policies, all operations are blocked for non-service-role clients. The authenticated user needs an INSERT policy on the 'storage.objects' table that permits uploading to the 'avatars' bucket, typically scoped to their own folder (user ID as prefix).",
            "error_category": "authorization",
            "likely_causes": [
                {"description": "The 'avatars' bucket has RLS enabled but no INSERT policy was created for the 'authenticated' role.", "confidence": "high"},
                {"description": "The bucket was created as 'private' and no policies were configured via the Supabase dashboard or migrations.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Is the 'avatars' bucket intended to be public or private?",
                "Should users only be able to upload to a folder named after their own user ID?"
            ],
            "risk_level": "high",
            "warnings": [
                "Do not create an overly permissive policy that allows any authenticated user to overwrite other users' files.",
                "Scope INSERT policies to the user's own folder: check that the file path starts with 'auth.uid()'."
            ],
            "repair_prompt": "Please inspect RLS policies on 'storage.objects' in Supabase SQL Editor. Uploads fail with: \"new row violates row-level security policy\". Create a scoped INSERT policy for authenticated users: 'CREATE POLICY \"authenticated_upload_own_avatar\" ON storage.objects FOR INSERT TO authenticated WITH CHECK (bucket_id = ''avatars'' AND auth.uid()::text = (storage.foldername(name))[1]);'. Also create a SELECT policy if public avatar read access is needed. Do not disable RLS on storage buckets.",
            "verification_steps": [
                "Create the INSERT policy in Supabase SQL Editor or Supabase Dashboard -> Storage -> Policies.",
                "Upload an avatar from a logged-in user and verify no 403 error is returned.",
                "Test that a different authenticated user cannot overwrite the first user's avatar."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-run-094",
        "scenario_group": "react-query-stale-while-revalidate-flicker",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic TanStack Query showing stale data flash before fresh data loads."},
        "model_input": {
            "raw_error": "// Observed: On page load the component briefly flashes old/stale data for ~500ms before showing the fresh API response.\n// No thrown error.\n\nconst { data } = useQuery({\n  queryKey: ['user', userId],\n  queryFn: fetchUser,\n  // staleTime not configured\n});",
            "context": {"language_or_framework": "TanStack Query v5 / React", "environment": "local_development", "recent_changes": "Implemented user profile data fetching with TanStack Query."}
        },
        "reference_annotations": {
            "reference_cause": "TanStack Query defaults to staleTime: 0, immediately marking cached data as stale and triggering a background refetch on every mount, causing the stale-while-revalidate flash.",
            "reference_repair": "Set an appropriate 'staleTime' (e.g. 30000 ms) to prevent unnecessary refetches and reduce the flash of stale content.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "TanStack Query flashes old data on mount because staleTime is 0 (default), triggering an immediate background refetch.",
            "plain_explanation": "TanStack Query caches fetched data and returns it immediately from cache on subsequent mounts (preventing loading spinners). However, with the default 'staleTime: 0', all cached data is considered stale immediately, so Query always fires a background refetch. The brief flash occurs because the component renders stale cached data, then re-renders with fresh data when the refetch completes.",
            "error_category": "runtime",
            "likely_causes": [
                {"description": "staleTime is at its default of 0, causing every cache hit to immediately trigger a background refetch.", "confidence": "high"},
                {"description": "The fetched data is large or the API is slow, making the stale-while-revalidate window more noticeable.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "How frequently does the user data change?",
                "Is the flash visually disruptive, or only a concern when data changes between mounts?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect the useQuery call for the user profile. TanStack Query shows stale data flash due to default staleTime: 0. Set an appropriate staleTime based on how fresh the data needs to be: 'useQuery({ queryKey: [\"user\", userId], queryFn: fetchUser, staleTime: 30 * 1000 })' (30 seconds). For data that rarely changes (user profile), consider 5 minutes. If you need to show a loading state during refetch, use the 'isFetching' flag. Do not set staleTime to Infinity unless the data never changes.",
            "verification_steps": [
                "Add 'staleTime: 30 * 1000' to the useQuery configuration.",
                "Navigate away and return to the user profile and verify no data flash occurs within 30 seconds.",
                "Use React Query DevTools to confirm the query does not refetch immediately on remount."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-bld-095",
        "scenario_group": "eslint-plugin-missing-peer-dep",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic ESLint plugin failing due to missing peer dependency on eslint version."},
        "model_input": {
            "raw_error": "Error [ERR_REQUIRE_ESM]: require() of ES Module node_modules/eslint-plugin-unicorn/index.js not supported.\nInstead change the require of index.js in node_modules/eslint-plugin-unicorn to a dynamic import() which is available in all CommonJS modules.\n\nOr install ESLint 9+ which supports flat config and ESM plugins.",
            "context": {"language_or_framework": "Node.js / ESLint", "environment": "local_development", "recent_changes": "Updated eslint-plugin-unicorn to v55."}
        },
        "reference_annotations": {
            "reference_cause": "eslint-plugin-unicorn v55 is ESM-only and requires ESLint 9 with flat config. The project is using ESLint 8 with a .eslintrc config file.",
            "reference_repair": "Either downgrade eslint-plugin-unicorn to a CommonJS-compatible version (v53 or lower), or upgrade to ESLint 9 and migrate to flat config.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "ESLint crashed because eslint-plugin-unicorn v55 is ESM-only and incompatible with ESLint 8's CommonJS loader.",
            "plain_explanation": "Starting with v55, 'eslint-plugin-unicorn' is published as an ES Module (ESM) only. ESLint 8 uses CommonJS 'require()' to load plugins, which cannot load ESM modules. ESLint 9 introduced 'flat config' format that supports ESM plugins natively. Using the new plugin version with the old ESLint is the root incompatibility.",
            "error_category": "dependency",
            "likely_causes": [
                {"description": "eslint-plugin-unicorn was updated to v55+ which is ESM-only, but the project uses ESLint 8 (CommonJS).", "confidence": "high"},
                {"description": "No explicit peer dependency constraint in package.json prevented the incompatible version from installing.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Which version of ESLint is installed (check package.json)?",
                "Is the ESLint config file .eslintrc.js (legacy) or eslint.config.js (flat config)?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect package.json for eslint and eslint-plugin-unicorn versions. ESLint throws: \"require() of ES Module not supported\". Choose one path: (1) Downgrade eslint-plugin-unicorn to v53 ('npm install eslint-plugin-unicorn@53 --save-dev'); (2) Upgrade ESLint to v9+ and migrate your config from '.eslintrc.js' to 'eslint.config.js' flat format. Do not mix ESLint 8 with ESM-only plugins.",
            "verification_steps": [
                "Downgrade to eslint-plugin-unicorn@53 and run 'npx eslint src/' to verify no ERR_REQUIRE_ESM error.",
                "Alternatively, run 'npm install eslint@latest --save-dev' and migrate to flat config.",
                "Confirm ESLint rules run correctly after the version change."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-dat-096",
        "scenario_group": "drizzle-missing-push-schema-migration",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Drizzle ORM schema column added in code but not migrated to database."},
        "model_input": {
            "raw_error": "LibsqlError: SQLITE_ERROR: table users has no column named bio\n    at mapLibSqlError (node_modules/@libsql/client/src/errors.ts:30:10)\n    at executeMany (node_modules/@libsql/client/src/sqlite3.ts:145:13)\n\n// drizzle/schema.ts has bio: text('bio') on the users table\n// drizzle push was never run after adding the column",
            "context": {"language_or_framework": "Drizzle ORM / SQLite / Turso", "environment": "local_development", "recent_changes": "Added a 'bio' text column to the users table in drizzle/schema.ts."}
        },
        "reference_annotations": {
            "reference_cause": "A new column was added to the Drizzle schema file but 'drizzle-kit push' (or 'drizzle-kit generate' + 'migrate') was not run, so the database does not have the column.",
            "reference_repair": "Run 'npx drizzle-kit push' to synchronize the schema file with the database.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "Drizzle ORM query failed because the 'bio' column was added to schema.ts but never pushed to the actual database.",
            "plain_explanation": "Drizzle ORM's schema definition in TypeScript describes the desired database structure, but changes to this file do not automatically alter the database. You must run 'npx drizzle-kit push' (for prototyping) or generate and apply a migration ('drizzle-kit generate' then 'drizzle-kit migrate') to apply the new column to the actual database.",
            "error_category": "database",
            "likely_causes": [
                {"description": "A new column was added to the Drizzle schema but 'drizzle-kit push' or a migration was not run.", "confidence": "high"},
                {"description": "The migration was run against a different database instance than the one currently in use.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Are you using 'drizzle-kit push' for prototyping or 'drizzle-kit generate' + 'migrate' for production migrations?",
                "Is the database file the same one the application is connecting to?"
            ],
            "risk_level": "low",
            "warnings": [
                "In production, use 'drizzle-kit generate' and 'drizzle-kit migrate' rather than 'drizzle-kit push' to maintain a migration history."
            ],
            "repair_prompt": "Please inspect drizzle/schema.ts and your database. Drizzle ORM throws: \"table users has no column named bio\". Run 'npx drizzle-kit push' to sync your schema changes to the database (development). For production, generate a migration file with 'npx drizzle-kit generate' and apply it with 'npx drizzle-kit migrate'. Do not manually ALTER TABLE as Drizzle-generated migrations keep schema history consistent.",
            "verification_steps": [
                "Run 'npx drizzle-kit push' in the project root.",
                "Inspect the database schema to confirm the 'bio' column exists on the 'users' table.",
                "Retry the query that was failing and verify it executes without the SQLITE_ERROR."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-run-097",
        "scenario_group": "react-hydration-mismatch-date",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic React hydration mismatch from server/client date rendering difference."},
        "model_input": {
            "raw_error": "Error: Hydration failed because the initial UI does not match what was rendered on the server.\n\nWarning: Text content did not match. Server: \"January 17, 2026\" Client: \"January 18, 2026\"\n    at Footer (src/components/Footer.tsx:12:8)",
            "context": {"language_or_framework": "Next.js 14 / React", "environment": "production", "recent_changes": "Added a 'Last updated' date that shows the current date."}
        },
        "reference_annotations": {
            "reference_cause": "A date computed from 'new Date()' produces different values on the server (UTC) and the client (local timezone), causing a React hydration mismatch.",
            "reference_repair": "Use 'suppressHydrationWarning' on the element, or render the date only on the client side using useEffect and useState.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "React hydration failed because the server rendered a date string in UTC while the browser rendered it in the local timezone.",
            "plain_explanation": "Next.js server-side rendering uses UTC time, but the user's browser renders using their local timezone. When 'new Date().toLocaleDateString()' is called, it returns a different date near timezone boundaries. React compares the server-rendered HTML with what React would render in the browser, and the mismatch causes a hydration error.",
            "error_category": "runtime",
            "likely_causes": [
                {"description": "A date is rendered using new Date() or toLocaleDateString() which produces timezone-dependent output.", "confidence": "high"},
                {"description": "The user's local timezone is behind UTC, causing the date to appear one day behind near midnight.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Does the footer need to show the exact current date, or a static publication/update date?",
                "Should the date be rendered server-side or browser-side only?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect src/components/Footer.tsx line 12. React fails: \"Text content did not match... Server: 'January 17, 2026' Client: 'January 18, 2026'\". To fix: (1) Render the date only on the client side using useEffect: 'const [date, setDate] = useState(\"\"); useEffect(() => setDate(new Date().toLocaleDateString()), []);'; (2) Or add 'suppressHydrationWarning' to the span if the mismatch is acceptable: '<span suppressHydrationWarning>{new Date().toLocaleDateString()}</span>'. Do not hardcode dates.",
            "verification_steps": [
                "Wrap the date display in useEffect to render it client-side only.",
                "Test from a timezone offset from UTC and verify no hydration error in console.",
                "Confirm the footer date displays correctly in the browser."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-dep-098",
        "scenario_group": "npm-overrides-breaking-peer-resolution",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic npm overrides causing downstream peer dependency conflicts."},
        "model_input": {
            "raw_error": "npm warn ERESOLVE overriding peer dependency\nnpm warn peer react@\"^18.0.0\" from react-dom@18.3.1\nnpm warn node_modules/react-dom\nnpm warn   react-dom@\"18.3.1\" from the root project\n\nnpm error code ERESOLVE\nnpm error ERESOLVE could not resolve\nnpm error While resolving: some-library@2.1.0\nnpm error Found: react@19.0.0\nnpm error Could not resolve dependency: peer react@\"^18.0.0\" from some-library@2.1.0",
            "context": {"language_or_framework": "Node.js / npm", "environment": "local_development", "recent_changes": "Upgraded React to v19."}
        },
        "reference_annotations": {
            "reference_cause": "After upgrading to React 19, a library (some-library) still declares a peer dependency on React 18. npm cannot resolve compatible versions.",
            "reference_repair": "Check if some-library has a React 19 compatible release; if not, add an npm override: '\"overrides\": { \"react\": \"19.0.0\", \"react-dom\": \"19.0.0\" }' in package.json to force resolution.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "npm cannot resolve dependencies because a library requires React 18 but the project uses React 19.",
            "plain_explanation": "After upgrading to React 19, 'some-library' still declares 'react@^18.0.0' as a peer dependency. npm's default resolution refuses to install packages with conflicting peer requirements. The library either has not released a React 19 compatible version yet, or the peer requirement is overly conservative.",
            "error_category": "dependency",
            "likely_causes": [
                {"description": "The third-party library's peer dependency declaration has not been updated to include React 19.", "confidence": "high"},
                {"description": "The library uses React 18-specific internal APIs that are removed or changed in React 19.", "confidence": "low"}
            ],
            "missing_context_questions": [
                "Has 'some-library' released a version that declares React 19 as a supported peer?",
                "Is the functionality you rely on from some-library likely to actually break with React 19?"
            ],
            "risk_level": "medium",
            "warnings": [
                "Using npm overrides to force a React version may cause runtime errors if the library uses React 18-specific internals.",
                "Test thoroughly after applying the override to confirm the library behaves correctly."
            ],
            "repair_prompt": "Please inspect package.json. npm cannot resolve React 19 peer dependencies for some-library. First, check if a React 19 compatible version of some-library is available ('npm info some-library peerDependencies'). If not, add an override to force resolution: '\"overrides\": { \"react\": \"19.0.0\", \"react-dom\": \"19.0.0\" }' in package.json. As a fallback, use '--legacy-peer-deps' during install. Do not downgrade React to 18 unless the library is critical and has no React 19 path.",
            "verification_steps": [
                "Check the library's GitHub or npm changelog for React 19 support.",
                "Add the overrides block to package.json and run 'npm install'.",
                "Run the application and verify the library functionality works correctly with React 19."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-run-099",
        "scenario_group": "tailwind-jit-purge-missing-content-glob",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Tailwind CSS JIT styles not appearing because content glob misses app directory."},
        "model_input": {
            "raw_error": "// Observed: Tailwind utility classes applied in src/app/**/*.tsx are not generated in the CSS output.\n// No build error thrown.\n\n// tailwind.config.js\ncontent: [\n  './src/pages/**/*.{js,ts,jsx,tsx}',\n  './src/components/**/*.{js,ts,jsx,tsx}',\n  // Missing: src/app/**\n],",
            "context": {"language_or_framework": "Next.js / Tailwind CSS v3", "environment": "local_development", "recent_changes": "Migrated from Pages Router to App Router but did not update tailwind.config.js content paths."}
        },
        "reference_annotations": {
            "reference_cause": "The Tailwind content array still lists 'pages/' and 'components/' but the App Router files live in 'app/', so Tailwind's JIT scanner never sees the new files and does not generate their utility classes.",
            "reference_repair": "Add './src/app/**/*.{js,ts,jsx,tsx}' to the content array in tailwind.config.js.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "Tailwind CSS classes from 'src/app/' are missing from the CSS bundle because the content glob was not updated for the App Router.",
            "plain_explanation": "Tailwind CSS v3 uses JIT (Just-In-Time) compilation. It scans your source files using the paths in the 'content' array of 'tailwind.config.js' and only generates CSS for classes it finds there. After migrating to the Next.js App Router, component files moved to 'src/app/', but the content array still only points to 'src/pages/' and 'src/components/', so Tailwind never scans the new app files.",
            "error_category": "configuration",
            "likely_causes": [
                {"description": "The 'content' array in tailwind.config.js was not updated after the Pages Router to App Router migration.", "confidence": "high"},
                {"description": "New feature files were added to a directory not covered by the existing content globs.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Are components split between src/components/ and src/app/ directories?",
                "Does the project have additional feature folders not covered by the current content paths?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect tailwind.config.js. Tailwind utility classes from App Router files are not appearing in the CSS output. Add 'src/app/**' to the content array: 'content: [\"./src/pages/**/*.{js,ts,jsx,tsx,mdx}\", \"./src/components/**/*.{js,ts,jsx,tsx,mdx}\", \"./src/app/**/*.{js,ts,jsx,tsx,mdx}\"]'. Restart the dev server after saving. Do not add node_modules or test directories to the content array.",
            "verification_steps": [
                "Add './src/app/**/*.{js,ts,jsx,tsx,mdx}' to the content array in tailwind.config.js.",
                "Restart the Next.js dev server.",
                "Inspect an App Router component in the browser and verify its Tailwind classes are applied."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-run-100",
        "scenario_group": "node-cron-memory-leak-no-clearInterval",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Node.js scheduled job creating new intervals without clearing old ones on hot-reload."},
        "model_input": {
            "raw_error": "// Observed: After Next.js HMR reload, logs show the cron job firing 2x, then 4x, then 8x per interval.\n// Process memory grows steadily over time in development.\n// No thrown error.\n\n// src/lib/scheduler.ts\nsetInterval(async () => {\n  await cleanupExpiredSessions();\n}, 60_000);",
            "context": {"language_or_framework": "Next.js (App Router) / Node.js", "environment": "local_development", "recent_changes": "Added a session cleanup scheduled job."}
        },
        "reference_annotations": {
            "reference_cause": "The module-level setInterval is re-executed on every Hot Module Replacement (HMR) reload in development, accumulating multiple concurrent intervals without clearing previous ones.",
            "reference_repair": "Use a global singleton pattern or store the interval ID and clear it before re-registering: 'if (globalThis._cleanupInterval) clearInterval(globalThis._cleanupInterval); globalThis._cleanupInterval = setInterval(...);'",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "Session cleanup job fires multiple times per interval because HMR re-runs the setInterval call without clearing the previous interval.",
            "plain_explanation": "During Next.js development with Hot Module Replacement (HMR), modules can be re-evaluated when files change. Each re-evaluation of 'src/lib/scheduler.ts' calls 'setInterval()' again, creating an additional concurrent interval. The old intervals are never cleared, so after several HMR cycles you have many intervals all running the same job simultaneously.",
            "error_category": "runtime",
            "likely_causes": [
                {"description": "The setInterval call is at module scope and the module is re-evaluated on every HMR event.", "confidence": "high"},
                {"description": "No teardown or cleanup code is registered to clear the interval before module re-evaluation.", "confidence": "high"}
            ],
            "missing_context_questions": [
                "Does the scheduler need to run in both development and production, or only production?",
                "Is there an existing pattern for singleton initialization in the project?"
            ],
            "risk_level": "medium",
            "warnings": [
                "Duplicate cron jobs can run the same operation multiple times, leading to data corruption or excessive API calls."
            ],
            "repair_prompt": "Please inspect src/lib/scheduler.ts. The cleanup job multiplies on HMR reloads. Use a global singleton pattern to prevent duplicate intervals: 'declare global { var _cleanupInterval: NodeJS.Timeout | undefined; } if (globalThis._cleanupInterval) clearInterval(globalThis._cleanupInterval); globalThis._cleanupInterval = setInterval(async () => { await cleanupExpiredSessions(); }, 60_000);'. Alternatively, only start the scheduler on the first invocation using a guard flag. Do not run scheduled jobs in edge functions.",
            "verification_steps": [
                "Apply the globalThis singleton pattern to the scheduler.",
                "Save a file multiple times to trigger HMR and verify the job fires only once per interval.",
                "Monitor process memory to confirm it no longer grows continuously during development."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-bld-101",
        "scenario_group": "webpack-circular-dependency-undefined-import",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Webpack circular dependency causing undefined import at runtime."},
        "model_input": {
            "raw_error": "TypeError: Cannot read properties of undefined (reading 'createLogger')\n    at src/services/api.js:3:18\n    at Module.<anonymous> (src/services/api.js:1:1)\n\n// Circular: src/services/api.js -> src/utils/logger.js -> src/services/api.js",
            "context": {"language_or_framework": "Webpack / Node.js / React", "environment": "local_development", "recent_changes": "Added logging to the API service module."}
        },
        "reference_annotations": {
            "reference_cause": "A circular dependency between api.js and logger.js causes one module to be incompletely initialized when the other imports it, resulting in an undefined value.",
            "reference_repair": "Break the cycle by moving shared logic to a third module that neither api.js nor logger.js imports, or use lazy initialization.",
            "difficulty": "hard"
        },
        "target_report": {
            "summary": "api.js receives 'undefined' for the logger import because a circular module dependency prevents complete initialization.",
            "plain_explanation": "JavaScript module systems evaluate modules in a specific order. When module A imports module B, and module B imports module A, the bundler must break the cycle somewhere. At that break point, one module receives an incomplete (undefined) version of the other because it has not finished evaluating yet. This is why 'createLogger' is undefined when api.js first tries to use it.",
            "error_category": "build",
            "likely_causes": [
                {"description": "src/services/api.js and src/utils/logger.js import each other, creating a circular dependency.", "confidence": "high"},
                {"description": "A new import was added to logger.js that pulls in something from the services layer, completing a cycle that was previously absent.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Why does logger.js need to import from api.js?",
                "Can the shared functionality be moved to a separate utility module without any API or logging dependencies?"
            ],
            "risk_level": "medium",
            "warnings": [
                "Circular dependencies often indicate architectural issues; avoid patching with lazy imports without understanding the root cause."
            ],
            "repair_prompt": "Please inspect src/services/api.js and src/utils/logger.js. The error: \"Cannot read properties of undefined: createLogger\" is caused by a circular import. Break the cycle by: (1) creating a 'src/utils/config.js' or 'src/utils/constants.js' that holds any shared data both files need, (2) removing the api.js import from logger.js. If logger must call API functions, pass them as parameters (dependency injection) instead of importing. Run 'npx madge --circular src/' to detect all cycles.",
            "verification_steps": [
                "Run 'npx madge --circular src/' to identify all circular dependencies.",
                "Refactor to remove the api.js -> logger.js -> api.js cycle.",
                "Restart the app and confirm 'createLogger' is no longer undefined."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-ath-102",
        "scenario_group": "oauth-redirect-uri-mismatch",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic OAuth redirect_uri mismatch error in production."},
        "model_input": {
            "raw_error": "OAuthCallbackError: redirect_uri_mismatch\nThe redirect URI in the Authorization Request did not match a registered redirect URI.\n\nProvider: Google OAuth\nRequested redirect: https://myapp.com/api/auth/callback/google\nRegistered in Google Console: http://localhost:3000/api/auth/callback/google",
            "context": {"language_or_framework": "Next.js / Auth.js (NextAuth) / Google OAuth", "environment": "production", "recent_changes": "Deployed the application to production."}
        },
        "reference_annotations": {
            "reference_cause": "The Google OAuth client only has the localhost redirect URI registered. The production domain was never added to the authorized redirect URIs in Google Cloud Console.",
            "reference_repair": "Add 'https://myapp.com/api/auth/callback/google' to the OAuth 2.0 client's authorized redirect URIs in Google Cloud Console.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "Google OAuth login failed because the production redirect URI is not registered in the Google Cloud Console.",
            "plain_explanation": "OAuth providers require that the 'redirect_uri' sent during login exactly match one of the URIs pre-registered in the developer console. The OAuth client was configured only for 'http://localhost:3000' during development and was never updated with the production domain, so Google rejects the production login attempt.",
            "error_category": "authentication",
            "likely_causes": [
                {"description": "The production domain was not added to the authorized redirect URIs in Google Cloud Console.", "confidence": "high"},
                {"description": "NEXTAUTH_URL environment variable is not set to the production domain, causing Auth.js to build an incorrect redirect URI.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Is NEXTAUTH_URL set to 'https://myapp.com' in your production environment variables?",
                "Have you added the production callback URL to the Google Cloud Console OAuth 2.0 client?"
            ],
            "risk_level": "high",
            "warnings": [
                "Never share your OAuth client secret between development and production environments; use separate OAuth app configurations."
            ],
            "repair_prompt": "Please update your Google OAuth configuration. The login fails with: \"redirect_uri_mismatch: https://myapp.com/api/auth/callback/google\". In Google Cloud Console -> APIs & Services -> Credentials -> your OAuth 2.0 Client, add 'https://myapp.com/api/auth/callback/google' to Authorized redirect URIs. Also ensure the production environment has 'NEXTAUTH_URL=https://myapp.com' set. For extra safety, create a separate Google OAuth app for production vs. development.",
            "verification_steps": [
                "Add the production redirect URI to Google Cloud Console OAuth 2.0 client settings.",
                "Set NEXTAUTH_URL=https://myapp.com in production environment variables.",
                "Attempt Google login in production and confirm successful callback and session creation."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-cfg-103",
        "scenario_group": "docker-compose-env-file-not-loaded",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Docker Compose service not reading .env file for environment variables."},
        "model_input": {
            "raw_error": "Error: connect ECONNREFUSED database:5432\n    at TCPConnectWrap.afterConnect\n\n// docker-compose.yml defines DATABASE_URL using ${POSTGRES_PASSWORD}\n// .env file exists in the same directory\n// But the container starts with POSTGRES_PASSWORD set to an empty string",
            "context": {"language_or_framework": "Docker Compose / PostgreSQL", "environment": "local_development", "recent_changes": "Added Docker Compose setup with a PostgreSQL service."}
        },
        "reference_annotations": {
            "reference_cause": "Docker Compose loads a .env file from the current working directory by default, but the compose command was run from a different directory or the file was named differently (e.g. .env.local).",
            "reference_repair": "Run 'docker compose --env-file .env up' explicitly, or ensure the terminal working directory matches where the .env file is located.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "Docker Compose did not load environment variables because the .env file was not found in the working directory.",
            "plain_explanation": "Docker Compose automatically reads a '.env' file from the directory where the 'docker compose' command is executed. If the command is run from a parent directory, a subdirectory, or if the file is named '.env.local' instead of '.env', the variables are not loaded and interpolated values like '${POSTGRES_PASSWORD}' become empty strings.",
            "error_category": "configuration",
            "likely_causes": [
                {"description": "The docker compose command was run from a directory other than where the .env file is located.", "confidence": "high"},
                {"description": "The environment file is named .env.local or .env.development instead of .env.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "From which directory are you running 'docker compose up'?",
                "What is the exact name of your environment file?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect your Docker Compose setup. The container receives an empty POSTGRES_PASSWORD because the .env file is not being loaded. Run 'docker compose' from the directory containing both docker-compose.yml and .env, or explicitly specify the env file: 'docker compose --env-file .env up'. Verify variable substitution works with 'docker compose config' which prints the resolved compose file. Do not hardcode secrets in docker-compose.yml.",
            "verification_steps": [
                "Run 'docker compose config' and verify ${POSTGRES_PASSWORD} is resolved to the expected value.",
                "If unresolved, run from the directory containing .env or use '--env-file .env'.",
                "Restart containers and verify the database connection succeeds."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-run-104",
        "scenario_group": "zustand-persist-hydration-mismatch",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Zustand persist middleware causing Next.js hydration mismatch on first render."},
        "model_input": {
            "raw_error": "Error: Hydration failed because the initial UI does not match what was rendered on the server.\nWarning: Prop 'className' did not match. Server: 'theme-light' Client: 'theme-dark'\n    at ThemeWrapper (src/components/ThemeWrapper.tsx:9:5)",
            "context": {"language_or_framework": "Next.js / Zustand", "environment": "production", "recent_changes": "Added Zustand persist middleware with localStorage to store user theme preference."}
        },
        "reference_annotations": {
            "reference_cause": "Zustand persist reads from localStorage during client hydration, but server-side rendering has no localStorage access so the server renders the default value while the client renders the persisted value.",
            "reference_repair": "Use Zustand's built-in 'skipHydration' option and manually call 'useStore.persist.rehydrate()' inside a useEffect to delay localStorage reads until after hydration.",
            "difficulty": "hard"
        },
        "target_report": {
            "summary": "Zustand persist causes a hydration mismatch because localStorage is unavailable on the server but provides a different value on the client.",
            "plain_explanation": "Zustand's persist middleware saves and restores state from localStorage. During server-side rendering, localStorage does not exist, so the store initializes with the default value (e.g. 'light' theme). When the page hydrates in the browser, Zustand reads the persisted 'dark' theme from localStorage. React detects that the rendered HTML ('theme-light') differs from what client hydration produces ('theme-dark') and throws a hydration error.",
            "error_category": "runtime",
            "likely_causes": [
                {"description": "Zustand persist middleware restores state from localStorage during client hydration, differing from the server-rendered default value.", "confidence": "high"},
                {"description": "The component renders different classNames based on persisted store values without waiting for hydration to complete.", "confidence": "high"}
            ],
            "missing_context_questions": [
                "Does the theme need to be applied before first paint, or can a brief flash of the default theme be tolerated?",
                "Is the theme stored in a cookie that could be read server-side to eliminate the mismatch?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect src/components/ThemeWrapper.tsx and the Zustand store. Hydration fails because the server renders 'theme-light' but client rehydrates 'theme-dark' from localStorage. Use Zustand's skipHydration option: 'persist(storeConfig, { name: \"theme\", skipHydration: true })'. Then in a client component, call 'useThemeStore.persist.rehydrate()' inside a useEffect. This delays localStorage reads until after React hydration. Alternatively, store the theme in a cookie and read it server-side for consistent SSR.",
            "verification_steps": [
                "Add 'skipHydration: true' to the Zustand persist config.",
                "Call 'useThemeStore.persist.rehydrate()' inside a useEffect in a client component.",
                "Test with a persisted 'dark' theme: load the page and verify no hydration error appears in console."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-dpl-105",
        "scenario_group": "vercel-function-size-limit-exceeded",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Vercel deployment failing due to serverless function exceeding 250 MB compressed size limit."},
        "model_input": {
            "raw_error": "Error: The Serverless Function \"api/process\" is 312.4 MB which exceeds the maximum size of 250 MB.\n\nLearn More: https://vercel.com/docs/functions/serverless-functions/runtimes#size",
            "context": {"language_or_framework": "Next.js / Vercel", "environment": "production", "recent_changes": "Added PDF parsing functionality using pdfjs-dist inside an API route."}
        },
        "reference_annotations": {
            "reference_cause": "The 'pdfjs-dist' library and its native canvas bindings are bundled into the serverless function, exceeding Vercel's 250 MB limit.",
            "reference_repair": "Use the lightweight pdfjs-dist/legacy/build/pdf.js entry point, exclude canvas bindings with webpack externals, or move PDF processing to a background job or external service.",
            "difficulty": "hard"
        },
        "target_report": {
            "summary": "Vercel deployment failed because the 'api/process' function bundled pdfjs-dist and its native bindings, exceeding the 250 MB size limit.",
            "plain_explanation": "Vercel Serverless Functions have a 250 MB compressed size limit. The 'pdfjs-dist' library includes large WASM files and optional canvas bindings. When bundled naively into a Next.js API route, it pushes the function size over the limit.",
            "error_category": "deployment",
            "likely_causes": [
                {"description": "pdfjs-dist includes heavy WASM and canvas dependencies that are bundled into the API route.", "confidence": "high"},
                {"description": "Other large dependencies (ML models, data files) may also contribute to the oversized bundle.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Does PDF processing need to happen in a Vercel function, or can it be offloaded to a queue or external service?",
                "Are there other large libraries imported by the same API route?"
            ],
            "risk_level": "high",
            "warnings": [
                "Vercel Fluid Compute functions have higher limits but still have constraints; consider moving heavy processing to Vercel Queue or a dedicated worker.",
                "Do not include native binaries or large WASM files in serverless functions."
            ],
            "repair_prompt": "Please inspect the api/process route and its imports. Vercel throws: \"Serverless Function is 312.4 MB which exceeds 250 MB\". Reduce the bundle size by: (1) Using Next.js serverComponentsExternalPackages in next.config.js to exclude pdfjs-dist from bundling; (2) Replacing pdfjs-dist with a lighter PDF library or a managed PDF API; (3) Moving PDF processing to a background job using Vercel Queue or a separate microservice. Run 'npx @next/bundle-analyzer' to identify large contributors. Do not raise the Vercel function size limit as it is a hard constraint.",
            "verification_steps": [
                "Add pdfjs-dist to serverComponentsExternalPackages in next.config.js.",
                "Run a local build and check bundle sizes with Next.js bundle analyzer.",
                "Deploy and verify the function size is below 250 MB in Vercel deployment logs."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-run-106",
        "scenario_group": "fetch-no-cors-opaque-response",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic fetch no-cors mode returning opaque response with no readable body."},
        "model_input": {
            "raw_error": "// Observed: fetch completes but response body is always empty/null.\n// Response: type: 'opaque', status: 0, body: null\n\nconst res = await fetch('https://api.third-party.com/data', { mode: 'no-cors' });\nconst data = await res.json(); // throws: SyntaxError: Unexpected end of JSON input",
            "context": {"language_or_framework": "React (browser)", "environment": "local_development", "recent_changes": "Attempted to call a third-party API directly from the browser to bypass a CORS error."}
        },
        "reference_annotations": {
            "reference_cause": "Using mode: 'no-cors' produces an opaque response whose body cannot be read in JavaScript. It is not a CORS solution — it just silences the error while making the response unreadable.",
            "reference_repair": "Remove mode: 'no-cors' and proxy the API call through your own backend, or use a third-party proxy if the API supports it.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "mode: 'no-cors' produces an opaque response with no readable body, making it impossible to parse the API JSON.",
            "plain_explanation": "The 'no-cors' fetch mode is not a CORS workaround. It silences the browser CORS error, but as a security measure, the browser gives you an 'opaque' response — you can confirm the request went out but cannot read the status code, headers, or body. The correct fix for CORS is to proxy the request through your own backend, where there is no same-origin restriction.",
            "error_category": "network",
            "likely_causes": [
                {"description": "mode: 'no-cors' was added to silence a CORS error, without understanding that it makes the response unreadable.", "confidence": "high"},
                {"description": "The third-party API does not send CORS headers, so direct browser requests are blocked.", "confidence": "high"}
            ],
            "missing_context_questions": [
                "Do you have control over the third-party API to add CORS headers?",
                "Can a backend route in your application proxy this request to the third-party API?"
            ],
            "risk_level": "low",
            "warnings": [
                "Never use mode: 'no-cors' expecting to read the response; it is intended only for fire-and-forget requests like analytics beacons."
            ],
            "repair_prompt": "Please inspect the fetch call to 'https://api.third-party.com/data'. Using mode: 'no-cors' is incorrect here. Remove the no-cors mode and instead create a server-side proxy route in your backend (e.g. Next.js API route at '/api/proxy/data') that fetches from the third-party API using node-fetch or the built-in fetch. Your frontend then calls '/api/proxy/data' on your own domain, avoiding CORS entirely. Do not use mode: 'no-cors' to read response data.",
            "verification_steps": [
                "Create a proxy API route in your backend that fetches from the third-party API.",
                "Update the frontend fetch call to use your proxy endpoint instead of the third-party URL.",
                "Verify the response body is readable and contains the expected JSON data."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-dat-107",
        "scenario_group": "supabase-realtime-channel-not-subscribed",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Supabase Realtime subscription not receiving events due to missing .subscribe() call."},
        "model_input": {
            "raw_error": "// Observed: Real-time messages are never received in the React component.\n// No console errors, subscription appears set up.\n\nconst channel = supabase.channel('messages')\n  .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'messages' }, (payload) => {\n    setMessages(prev => [...prev, payload.new]);\n  });\n// Missing: .subscribe()",
            "context": {"language_or_framework": "Supabase Realtime / React", "environment": "local_development", "recent_changes": "Added real-time message updates to a chat component."}
        },
        "reference_annotations": {
            "reference_cause": "The Supabase Realtime channel listener was configured but .subscribe() was never called, so the subscription was never activated.",
            "reference_repair": "Chain .subscribe() after the .on() call: 'supabase.channel(\"messages\").on(...).subscribe();'",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "Supabase Realtime never fires because .subscribe() was not called to activate the channel subscription.",
            "plain_explanation": "Supabase Realtime uses a channel-based pub/sub system. Calling '.channel()' and '.on()' configures what to listen for, but does not activate the subscription. The '.subscribe()' method must be called to open the WebSocket connection and start receiving events.",
            "error_category": "runtime",
            "likely_causes": [
                {"description": "The .subscribe() call was accidentally omitted when setting up the channel.", "confidence": "high"},
                {"description": "The channel was set up in one place and subscribe() was expected to be called elsewhere but was missed.", "confidence": "low"}
            ],
            "missing_context_questions": [
                "Is the channel setup code inside a useEffect hook?",
                "Is there cleanup code that calls channel.unsubscribe() when the component unmounts?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect the Realtime channel setup in your chat component. Messages are not received because .subscribe() was not called. Update the channel setup: 'const channel = supabase.channel(\"messages\").on(\"postgres_changes\", { event: \"INSERT\", schema: \"public\", table: \"messages\" }, (payload) => { setMessages(prev => [...prev, payload.new]); }).subscribe();'. Also add cleanup in useEffect's return function: 'return () => { supabase.removeChannel(channel); };'. Do not create subscriptions outside of useEffect.",
            "verification_steps": [
                "Chain .subscribe() to the end of the channel configuration.",
                "Add useEffect cleanup: 'return () => supabase.removeChannel(channel);'.",
                "Insert a message via Supabase Dashboard and verify it appears in the component in real time."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-run-108",
        "scenario_group": "react-context-rerender-performance",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic React context causing excessive re-renders on all consumers."},
        "model_input": {
            "raw_error": "// Observed: React DevTools Profiler shows every component re-rendering on any state change,\n// even components that only use a small part of the context.\n// No thrown error, but UI is sluggish with > 200 components in the tree.\n\nconst AppContext = createContext({ user, theme, cart, notifications, settings });",
            "context": {"language_or_framework": "React 18", "environment": "local_development", "recent_changes": "Moved all global state into a single AppContext provider."}
        },
        "reference_annotations": {
            "reference_cause": "A single large context causes all consumers to re-render whenever any part of the context value changes, even if the consumer only uses an unrelated slice.",
            "reference_repair": "Split the monolithic context into smaller focused contexts (UserContext, ThemeContext, CartContext) so consumers only re-render when their relevant data changes.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "All React components re-render on every state change because a single large context holds all global state.",
            "plain_explanation": "React Context re-renders every consumer component whenever the context value changes. When all global state (user, theme, cart, notifications, settings) is in one context object, a cart update causes user profile components to re-render, and a notification triggers cart components to re-render — even though the relevant data didn't change for those components.",
            "error_category": "runtime",
            "likely_causes": [
                {"description": "A monolithic AppContext combines unrelated state slices, causing all consumers to re-render on any change.", "confidence": "high"},
                {"description": "The context value object is recreated on every parent render, triggering reference equality failures even when data is unchanged.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "How many components consume the AppContext?",
                "Are there independent slices of state that could be split into separate contexts?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect AppContext and its consumers. React Profiler shows excessive re-renders because all state is in one context. Split into focused contexts: 'UserContext', 'CartContext', 'ThemeContext', etc. Each component then subscribes only to the context it needs. Also wrap context values in useMemo to prevent unnecessary reference changes: 'const userValue = useMemo(() => ({ user, setUser }), [user]);'. For complex global state, consider Zustand or Jotai which provide selector-based subscriptions.",
            "verification_steps": [
                "Split AppContext into smaller, focused context providers.",
                "Verify each consuming component only re-renders when its specific context slice changes.",
                "Use React DevTools Profiler to confirm render counts decrease significantly."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-bld-109",
        "scenario_group": "next-config-missing-transpile-packages",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Next.js failing to compile ESM-only npm package without transpilePackages."},
        "model_input": {
            "raw_error": "SyntaxError: Cannot use import statement in a module\n    at node_modules/some-esm-library/index.js:1:1\n\nError occurred prerendering page \"/\". Read more: https://nextjs.org/docs/messages/prerender-error\nExport encountered errors on following paths:\n  /: /",
            "context": {"language_or_framework": "Next.js 14", "environment": "production", "recent_changes": "Added 'some-esm-library' which is an ESM-only npm package."}
        },
        "reference_annotations": {
            "reference_cause": "Next.js's Node.js runtime uses CommonJS by default; ESM-only packages cannot be required() without being transpiled. The transpilePackages config option tells Next.js to run the package through its Babel/SWC compiler.",
            "reference_repair": "Add the package to 'transpilePackages' in next.config.js: 'transpilePackages: [\"some-esm-library\"]'",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "Next.js failed to import an ESM-only package because it was not added to transpilePackages in next.config.js.",
            "plain_explanation": "Some npm packages ship as pure ES Modules (using 'export' and 'import' syntax). Next.js's server runtime needs to use CommonJS 'require()' for external packages by default. When it tries to load an ESM-only package, it fails with a SyntaxError. Adding the package to 'transpilePackages' tells Next.js to process it through its SWC/Babel compiler, converting it to CJS-compatible code.",
            "error_category": "build",
            "likely_causes": [
                {"description": "An ESM-only npm package was imported without adding it to next.config.js transpilePackages.", "confidence": "high"},
                {"description": "The package recently switched from CJS to ESM-only in a major version update.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "What version of the library was previously working, and which version introduced the ESM-only change?",
                "Does the library provide a CommonJS build alternative?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect next.config.js. Next.js throws: \"Cannot use import statement in a module\" for 'some-esm-library'. Add the package to the transpilePackages option: 'const nextConfig = { transpilePackages: [\"some-esm-library\"] };'. Restart the dev server and rebuild. If the package has many sub-packages, add them individually. Do not add all node_modules to transpilePackages as this severely slows builds.",
            "verification_steps": [
                "Add 'some-esm-library' to transpilePackages in next.config.js.",
                "Restart Next.js dev server.",
                "Navigate to the affected page and verify it renders without the SyntaxError."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-run-110",
        "scenario_group": "async-await-missing-in-array-map",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic async function in array.map returning array of Promises instead of resolved values."},
        "model_input": {
            "raw_error": "// Observed: 'processedItems' is an array of Promise objects, not resolved values.\n// console.log(processedItems) -> [Promise {pending}, Promise {pending}, ...]\n\nconst processedItems = items.map(async (item) => {\n  const result = await processItem(item);\n  return result;\n});\n\n// Later:\nconsole.log(processedItems[0].name); // undefined",
            "context": {"language_or_framework": "JavaScript / Node.js", "environment": "local_development", "recent_changes": "Added async processing to a batch operation using Array.map."}
        },
        "reference_annotations": {
            "reference_cause": "Array.map does not await async callbacks; each callback returns a Promise immediately, so the map result is an array of unresolved Promises.",
            "reference_repair": "Wrap with Promise.all: 'const processedItems = await Promise.all(items.map(async (item) => processItem(item)));'",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "Array.map with an async callback returns an array of Promises, not resolved values; Promise.all is needed.",
            "plain_explanation": "JavaScript's Array.map is synchronous. When the callback is an async function, map returns immediately with an array of Promise objects — one per item. The Promises are still pending. To wait for all of them to resolve, you must wrap the map call with 'await Promise.all(...)'.",
            "error_category": "runtime",
            "likely_causes": [
                {"description": "Array.map was used with an async callback without wrapping in Promise.all.", "confidence": "high"},
                {"description": "The calling function or code path does not await the result of the map.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Should items be processed in parallel (Promise.all) or sequentially (for...of with await)?",
                "What is the acceptable level of concurrency for processItem?"
            ],
            "risk_level": "low",
            "warnings": [
                "Promise.all runs all promises concurrently; if processItem has side effects or hits rate limits, consider processing items sequentially with a for...of loop and await inside."
            ],
            "repair_prompt": "Please update the batch processing code. 'items.map(async ...)' returns an array of Promises, not resolved values. Wrap with Promise.all: 'const processedItems = await Promise.all(items.map(async (item) => processItem(item)));'. If sequential processing is needed (to avoid overwhelming a database or API), use: 'const processedItems = []; for (const item of items) { processedItems.push(await processItem(item)); }'.",
            "verification_steps": [
                "Replace 'items.map(async ...)' with 'await Promise.all(items.map(async ...))'.",
                "Log processedItems[0] and verify it shows the resolved value, not a Promise object.",
                "Run a test with a small item array and confirm all results are correctly resolved."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-dpl-111",
        "scenario_group": "railway-nixpacks-build-command-override",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Railway.app Nixpacks build failing due to wrong start command detection."},
        "model_input": {
            "raw_error": "=== Nixpacks build output ===\nDetected: Node.js\nBuild: npm install && npm run build\nStart: npm start\n\n=== Runtime error ===\nsh: 1: next: not found\nError: Cannot find module '/app/.next/server/app/page.js'",
            "context": {"language_or_framework": "Next.js / Railway.app", "environment": "production", "recent_changes": "Deployed a Next.js application to Railway for the first time."}
        },
        "reference_annotations": {
            "reference_cause": "Nixpacks detected 'npm start' as the start command, but the Next.js build output requires 'next start' to serve from the .next directory. The 'next' binary was not found because it is not globally installed.",
            "reference_repair": "Add a 'start' script to package.json: '\"start\": \"next start\"', or configure the Railway start command override to 'npx next start'.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "Railway deployment crashed because 'npm start' could not find the 'next' binary to serve the compiled .next output.",
            "plain_explanation": "Nixpacks automatically uses 'npm start' as the start command. However, a Next.js app needs 'next start' to serve the server-side rendered output from the '.next' directory. If the 'start' script in package.json is missing or not configured to run 'next start', the server cannot start.",
            "error_category": "deployment",
            "likely_causes": [
                {"description": "The 'start' script in package.json is absent or set to something other than 'next start'.", "confidence": "high"},
                {"description": "The project was bootstrapped from a template that does not include a 'start' script.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Does package.json have a 'start' script defined?",
                "Is this a Next.js standalone output build requiring a different start command?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect package.json scripts. Railway/Nixpacks fails: \"sh: next: not found\". Add or update the 'start' script: '\"start\": \"next start\"'. Alternatively, configure Railway to use a custom start command in the Railway dashboard (Settings -> Deploy -> Start Command: 'npx next start'). Do not use 'node server.js' unless you have a custom Next.js server file.",
            "verification_steps": [
                "Add '\"start\": \"next start\"' to package.json scripts.",
                "Push the change and verify Railway rebuilds and starts the application.",
                "Check Railway logs to confirm the server starts on the expected port."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-run-112",
        "scenario_group": "formdata-file-upload-content-type-missing",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic file upload FormData boundary stripped when manually setting Content-Type header."},
        "model_input": {
            "raw_error": "// API server logs: 'Error: Multipart: Boundary not found'\n// Browser console: No error thrown.\n\nconst formData = new FormData();\nformData.append('file', selectedFile);\n\nawait fetch('/api/upload', {\n  method: 'POST',\n  headers: { 'Content-Type': 'multipart/form-data' }, // manually set\n  body: formData,\n});",
            "context": {"language_or_framework": "React / Express (multer)", "environment": "local_development", "recent_changes": "Added a file upload endpoint using multer on Express."}
        },
        "reference_annotations": {
            "reference_cause": "Manually setting 'Content-Type: multipart/form-data' overwrites the browser's auto-generated header that includes the multipart boundary string. Without the boundary, the server cannot parse the form data.",
            "reference_repair": "Remove the 'Content-Type' header from the fetch options and let the browser set it automatically with the correct boundary.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "File upload failed because manually setting Content-Type overwrote the browser's multipart boundary in the header.",
            "plain_explanation": "When you send a FormData object with fetch, the browser automatically sets the 'Content-Type' header to 'multipart/form-data; boundary=----WebKitFormBoundary...'. The boundary is a unique string the server uses to separate the different parts of the upload. By manually setting 'Content-Type: multipart/form-data' (without a boundary), you overwrite the browser's auto-generated header and the server cannot parse the multipart body.",
            "error_category": "network",
            "likely_causes": [
                {"description": "Content-Type: multipart/form-data was manually added to fetch headers, stripping the required boundary parameter.", "confidence": "high"},
                {"description": "A generic request interceptor (Axios defaults, a middleware) is overriding the Content-Type header for all POST requests.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Is there an Axios interceptor or fetch wrapper that automatically adds a Content-Type header to all requests?",
                "Are you using Axios instead of fetch? Axios has a separate fix for FormData uploads."
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect the fetch call in the file upload handler. Express/multer throws: \"Boundary not found\". Remove the 'Content-Type' header from the fetch options entirely: 'await fetch(\"/api/upload\", { method: \"POST\", body: formData });'. The browser will automatically set the correct multipart Content-Type with boundary. If using Axios, delete the Content-Type from default headers for this request: 'axios.post(\"/api/upload\", formData, { headers: { \"Content-Type\": undefined } })'.",
            "verification_steps": [
                "Remove the 'Content-Type' header from the fetch options.",
                "Upload a file and verify the request headers in browser DevTools show the boundary parameter.",
                "Confirm the Express/multer endpoint receives and processes the file successfully."
            ],
            "matched_recipes": []
        }
    },

    # ---------------------------------------------------------------
    # VALIDATION SPLIT (4 records: syn-*-113 through syn-*-116)
    # ---------------------------------------------------------------
    {
        "id": "syn-cfg-113",
        "scenario_group": "prisma-schema-provider-mismatch",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Prisma schema datasource provider set to sqlite while DATABASE_URL points to PostgreSQL."},
        "model_input": {
            "raw_error": "Error: Datasource provider 'sqlite' does not match the URL scheme 'postgresql://'\n\n  --> schema.prisma:5\n    |\n  4 |   provider = \"sqlite\"\n  5 |   url      = env(\"DATABASE_URL\")\n    |",
            "context": {"language_or_framework": "Prisma / PostgreSQL", "environment": "local_development", "recent_changes": "Migrated from SQLite to PostgreSQL and updated DATABASE_URL but forgot to update schema.prisma."}
        },
        "reference_annotations": {
            "reference_cause": "schema.prisma still declares 'provider = \"sqlite\"' while DATABASE_URL has been changed to a PostgreSQL connection string.",
            "reference_repair": "Update the datasource block in schema.prisma: change 'provider = \"sqlite\"' to 'provider = \"postgresql\"'.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "Prisma rejected the database connection because schema.prisma specifies 'sqlite' but DATABASE_URL points to PostgreSQL.",
            "plain_explanation": "Prisma's schema.prisma file must declare the correct database provider. The 'provider' field tells Prisma which database engine to use, and it must match the URL format in DATABASE_URL. After switching to PostgreSQL, the DATABASE_URL was updated but the 'provider' field in the datasource block was left as 'sqlite', creating a contradiction.",
            "error_category": "configuration",
            "likely_causes": [
                {"description": "The DATABASE_URL was updated to PostgreSQL but schema.prisma provider was not changed from 'sqlite'.", "confidence": "high"},
                {"description": "A template schema.prisma with a sqlite default was used without customizing it.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Are there existing Prisma migration files that need to be regenerated for PostgreSQL?",
                "Is this a new project, or are there existing SQLite migrations that need to be handled?"
            ],
            "risk_level": "low",
            "warnings": [
                "After changing the provider, run 'npx prisma migrate dev' to regenerate migrations for PostgreSQL syntax; SQLite migrations are not compatible."
            ],
            "repair_prompt": "Please inspect schema.prisma. Prisma throws: \"provider 'sqlite' does not match URL scheme 'postgresql://'\". Update the datasource block: 'datasource db { provider = \"postgresql\" url = env(\"DATABASE_URL\") }'. Then run 'npx prisma generate' to regenerate the client. For a migration-based project, also run 'npx prisma migrate dev --name switch-to-postgres'. Do not mix SQLite migration files with a PostgreSQL datasource.",
            "verification_steps": [
                "Change provider from 'sqlite' to 'postgresql' in schema.prisma.",
                "Run 'npx prisma generate'.",
                "Run 'npx prisma db push' (dev) or 'npx prisma migrate dev' and verify the schema is applied."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-run-114",
        "scenario_group": "uncontrolled-to-controlled-input-warning",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic React warning about switching from uncontrolled to controlled input."},
        "model_input": {
            "raw_error": "Warning: A component is changing an uncontrolled input to be controlled. This is likely caused by the value changing from undefined to a defined value, which should not happen. Decide between using a controlled or uncontrolled input element for the lifetime of the component.\n    at input\n    at SearchForm (src/components/SearchForm.tsx:15:7)",
            "context": {"language_or_framework": "React 18 / TypeScript", "environment": "local_development", "recent_changes": "Added a controlled search input using fetched user preferences as the initial value."}
        },
        "reference_annotations": {
            "reference_cause": "The input's 'value' prop is initially 'undefined' (when user preferences haven't loaded yet), then becomes a string once data loads. React treats an input as uncontrolled when value is undefined.",
            "reference_repair": "Initialize the state with an empty string: 'const [query, setQuery] = useState(\"\")' so the input is always controlled from the first render.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "React warns because the search input's value prop starts as undefined and transitions to a string when data loads.",
            "plain_explanation": "React treats form inputs as either 'controlled' (value prop is a string) or 'uncontrolled' (value prop is undefined/absent) — and the mode must not change during a component's lifetime. When 'user.defaultSearchQuery' is undefined before data loads, the input is uncontrolled. When data arrives and the value becomes a string, React detects the switch and issues a warning.",
            "error_category": "runtime",
            "likely_causes": [
                {"description": "The initial state is set to undefined or a possibly-undefined value from async-loaded data.", "confidence": "high"},
                {"description": "A state variable is declared as 'const [query, setQuery] = useState(user?.defaultQuery)' where 'user' is initially undefined.", "confidence": "high"}
            ],
            "missing_context_questions": [
                "What is the initial value of the state variable used as the input value?",
                "Should the search input be pre-filled from user preferences or start empty?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect the input element in src/components/SearchForm.tsx. React warns: \"changing an uncontrolled input to be controlled\". Ensure the initial state is always a string: 'const [query, setQuery] = useState(\"\");' rather than using possibly-undefined data directly. If you want to pre-fill from loaded data, use a useEffect: 'useEffect(() => { if (user?.defaultQuery) setQuery(user.defaultQuery); }, [user]);'. Never use undefined as a controlled input value.",
            "verification_steps": [
                "Change the useState initializer to '' (empty string).",
                "Verify the React warning no longer appears in the browser console.",
                "Confirm the input is pre-filled from user data once it loads using the useEffect approach."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-bld-115",
        "scenario_group": "vite-env-prefix-not-exposed-client",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Vite env variable undefined in client code due to missing VITE_ prefix."},
        "model_input": {
            "raw_error": "// .env:\nANALYTICS_ID=analytics_site_42\n\n// src/api/client.ts:\nconsole.log(import.meta.env.ANALYTICS_ID); // undefined\nconsole.log(import.meta.env.VITE_ANALYTICS_ID); // undefined\n\n// No thrown error, but API calls fail silently with 'undefined' in the URL.",
            "context": {"language_or_framework": "Vite / React", "environment": "local_development", "recent_changes": "Added an analytics site ID to the .env file for use in the frontend."}
        },
        "reference_annotations": {
            "reference_cause": "Vite only exposes environment variables prefixed with 'VITE_' to the client-side bundle. Variables without this prefix are server-only and not accessible in the browser.",
            "reference_repair": "Rename the variable to 'VITE_ANALYTICS_ID=analytics_site_42' in the .env file and access it as 'import.meta.env.VITE_ANALYTICS_ID'.",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "The analytics ID variable is undefined in the browser because Vite only exposes variables prefixed with 'VITE_' to client-side code.",
            "plain_explanation": "Vite has a deliberate security feature: environment variables defined in '.env' are NOT exposed to the browser unless they start with 'VITE_'. This prevents accidentally leaking server-side configuration to the client bundle. Variables without the prefix are only accessible in vite.config.js and other build-time scripts.",
            "error_category": "configuration",
            "likely_causes": [
                {"description": "The environment variable is named 'ANALYTICS_ID' without the 'VITE_' prefix, making it inaccessible in the browser.", "confidence": "high"},
                {"description": "The variable was defined correctly in .env but the dev server was not restarted after the change.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Should this variable be exposed in client-side browser code? If it is a secret backend credential, it should not be prefixed with VITE_.",
                "Was the dev server restarted after adding the .env variable?"
            ],
            "risk_level": "high",
            "warnings": [
                "CRITICAL: Only prefix an environment variable with 'VITE_' if it is safe to expose publicly in the browser. If the variable is sensitive or has elevated privileges, it must remain server-only and be called via a backend proxy."
            ],
            "repair_prompt": "Please inspect .env and src/api/client.ts. 'import.meta.env.ANALYTICS_ID' is undefined because Vite requires the 'VITE_' prefix for client-side variables. IF the variable is safe to expose publicly: rename in .env to 'VITE_ANALYTICS_ID=analytics_site_42' and access it as 'import.meta.env.VITE_ANALYTICS_ID'. IF the value is sensitive: keep it without the prefix and create a backend proxy route that handles the request server-side. Restart the dev server after any .env changes.",
            "verification_steps": [
                "Rename the variable to VITE_ANALYTICS_ID in .env.",
                "Restart the Vite dev server.",
                "Log 'import.meta.env.VITE_ANALYTICS_ID' and verify it prints the expected value."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-dat-116",
        "scenario_group": "sequelize-association-not-defined-before-use",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic Sequelize eager loading failing because .associate() method was never called."},
        "model_input": {
            "raw_error": "EagerLoadingError [SequelizeEagerLoadingError]: Post is not associated to User!\n    at Model.getAssociatedModelInstance (node_modules/sequelize/lib/model.js:714:13)\n\n// Query:\nawait User.findAll({ include: [{ model: Post }] });\n\n// models/post.js has: User.hasMany(Post) in associate()\n// But models/index.js never calls Post.associate()",
            "context": {"language_or_framework": "Sequelize / Node.js", "environment": "local_development", "recent_changes": "Added Post model and attempted to include it in User queries."}
        },
        "reference_annotations": {
            "reference_cause": "The Post model defines its associations inside an 'associate()' function, but models/index.js does not call this function, so Sequelize never registers the User-Post relationship.",
            "reference_repair": "In models/index.js, iterate over all models and call their associate method: 'Object.values(db).forEach(model => { if (model.associate) model.associate(db); });'",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "Sequelize eager loading failed because the User-Post association was never activated by calling Post.associate().",
            "plain_explanation": "In Sequelize, defining an association in a model file's 'associate()' method is a convention, not automatic. The association (e.g. 'User.hasMany(Post)') is only registered with Sequelize when 'associate()' is actually called. If 'models/index.js' loads the models but never calls their 'associate()' methods, Sequelize is unaware of any relationships.",
            "error_category": "database",
            "likely_causes": [
                {"description": "models/index.js loads model files but does not call model.associate() for any of them.", "confidence": "high"},
                {"description": "The new Post model was added but the models/index.js bootstrapping code was not updated to include it.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Does models/index.js have code that iterates models and calls their associate methods?",
                "Was the Post model file added to the models directory that index.js scans?"
            ],
            "risk_level": "low",
            "warnings": [],
            "repair_prompt": "Please inspect models/index.js. Sequelize throws: \"Post is not associated to User!\". After loading all model files, add a second pass that calls associate methods: 'Object.values(db).forEach(model => { if (typeof model.associate === \"function\") { model.associate(db); } });'. Ensure this runs after all models are imported. Do not hardcode association calls per model; use the loop pattern for maintainability.",
            "verification_steps": [
                "Add the associate() loop to models/index.js.",
                "Restart the server and run 'User.findAll({ include: [Post] })'.",
                "Verify the query returns users with their associated posts without EagerLoadingError."
            ],
            "matched_recipes": []
        }
    },

    # ---------------------------------------------------------------
    # TEST SPLIT (4 records: syn-*-117 through syn-*-120)
    # ---------------------------------------------------------------
    {
        "id": "syn-cfg-117",
        "scenario_group": "gitignore-env-file-committed",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic .env file with secrets accidentally committed to git repository."},
        "model_input": {
            "raw_error": "GitHub Secret Scanning Alert:\n[HIGH] Secret detected in commit abc1234\nFile: .env\nSecret type: PostgreSQL Connection URI\nLocation: commit diff includes active database credentials on line 4\n\nGitHub has blocked push and notified the repository owner.",
            "context": {"language_or_framework": "Git / Node.js", "environment": "production", "recent_changes": "Committed all project files including .env to the git repository."}
        },
        "reference_annotations": {
            "reference_cause": "The .env file containing production secrets was not listed in .gitignore and was committed to the repository.",
            "reference_repair": "Add .env to .gitignore, remove it from git history using 'git rm --cached .env', rotate all exposed secrets immediately, and push the fix.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "A production .env file containing database credentials was committed to git and detected by GitHub secret scanning.",
            "plain_explanation": "The '.env' file was added to version control. This file contained production database credentials. GitHub's secret scanning detected and blocked the push, but the secrets may have been exposed in the commit history or if the repository is public.",
            "error_category": "authentication",
            "likely_causes": [
                {"description": "The .env file was not listed in .gitignore, allowing 'git add .' to include it.", "confidence": "high"},
                {"description": "A developer was unaware that .env files must never be committed to version control.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Is this a public or private repository?",
                "How long has the commit containing secrets been in the repository history?"
            ],
            "risk_level": "high",
            "warnings": [
                "CRITICAL: Rotate the exposed DATABASE_URL password immediately, even if the repository is private — treat exposed credentials as compromised.",
                "Removing a file from git history requires a force push which rewrites history; coordinate with the team before doing so."
            ],
            "repair_prompt": "URGENT: Take these steps immediately: (1) Rotate the database password and any other secrets in the .env file — the old credentials should be considered compromised; (2) Add '.env' and '.env.*' to .gitignore; (3) Remove .env from git tracking: 'git rm --cached .env && git commit -m \"Remove .env from tracking\"'; (4) To fully remove secrets from history: 'git filter-repo --path .env --invert-paths' (requires git-filter-repo); (5) Push changes. Create a '.env.example' file with dummy values as documentation. Do not use 'git push --force' without team coordination.",
            "verification_steps": [
                "Verify the new database password is in use and the old one is revoked.",
                "Confirm .env is in .gitignore: 'git check-ignore -v .env'.",
                "Run 'git log --all --full-history -- .env' to verify the file is removed from history."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-run-118",
        "scenario_group": "event-listener-not-removed-memory-leak",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic React useEffect adding event listener without cleanup, causing memory leak."},
        "model_input": {
            "raw_error": "// Observed: After navigating between pages multiple times, keyboard shortcuts fire 2x, 4x, 8x.\n// React DevTools: component unmounted but event listeners still attached to window.\n// Chrome DevTools Memory: growing heap after each navigation.\n\nuseEffect(() => {\n  window.addEventListener('keydown', handleKeyboardShortcut);\n  // Missing cleanup\n}, []);",
            "context": {"language_or_framework": "React 18 / Next.js", "environment": "local_development", "recent_changes": "Added global keyboard shortcut handling to the main layout component."}
        },
        "reference_annotations": {
            "reference_cause": "The useEffect adds a global event listener but returns no cleanup function, so the listener persists after the component unmounts and accumulates on each remount.",
            "reference_repair": "Return a cleanup function from useEffect: 'return () => window.removeEventListener(\"keydown\", handleKeyboardShortcut);'",
            "difficulty": "easy"
        },
        "target_report": {
            "summary": "Global keyboard event listener accumulates on each mount because useEffect has no cleanup to remove it on unmount.",
            "plain_explanation": "React's useEffect allows you to subscribe to browser events. When a component unmounts (e.g. on navigation), React runs the cleanup function returned from useEffect — if you return one. Without it, 'window.addEventListener' adds a new listener every time the component mounts but the old ones are never removed. After several navigations, multiple identical listeners are registered and the shortcut fires multiple times per keypress.",
            "error_category": "runtime",
            "likely_causes": [
                {"description": "useEffect adds a window event listener without returning a cleanup function to remove it.", "confidence": "high"},
                {"description": "The component is used in multiple places or remounts frequently (e.g. route changes), causing listener accumulation.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Is the component that adds the listener a layout component that mounts/unmounts on each route change?",
                "Is 'handleKeyboardShortcut' declared inside or outside the component?"
            ],
            "risk_level": "medium",
            "warnings": [
                "Memory leaks from accumulating event listeners can degrade performance over time in long browser sessions."
            ],
            "repair_prompt": "Please inspect the useEffect in the keyboard shortcut component. The shortcut fires multiple times due to accumulated listeners. Add a cleanup return: 'useEffect(() => { window.addEventListener(\"keydown\", handleKeyboardShortcut); return () => window.removeEventListener(\"keydown\", handleKeyboardShortcut); }, [handleKeyboardShortcut]);'. Also wrap 'handleKeyboardShortcut' in useCallback to keep a stable reference so the cleanup correctly removes the same function. Do not add global listeners outside useEffect.",
            "verification_steps": [
                "Add the return () => window.removeEventListener cleanup to the useEffect.",
                "Navigate between pages several times and verify the shortcut fires exactly once per keypress.",
                "Check Chrome DevTools Memory tab to confirm heap size stabilizes across navigations."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-dpl-119",
        "scenario_group": "aws-s3-cors-preflight-blocked",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic browser direct-to-S3 upload blocked by missing S3 CORS configuration."},
        "model_input": {
            "raw_error": "Access to XMLHttpRequest at 'https://my-bucket.s3.amazonaws.com/uploads/file.pdf' from origin 'https://myapp.com' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource.",
            "context": {"language_or_framework": "React / AWS S3 (direct browser upload via presigned URL)", "environment": "production", "recent_changes": "Implemented direct S3 uploads from the browser using presigned URLs."}
        },
        "reference_annotations": {
            "reference_cause": "The S3 bucket does not have a CORS policy configured to allow cross-origin PUT requests from the application domain.",
            "reference_repair": "Add a CORS configuration to the S3 bucket via AWS Console or CLI that allows the app origin, PUT/GET methods, and required headers.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "Direct S3 browser uploads are blocked because the S3 bucket has no CORS configuration for the application domain.",
            "plain_explanation": "When your React app uploads files directly to S3 from the browser using presigned URLs, the browser first sends a CORS preflight OPTIONS request to S3. S3 responds only with CORS headers if the bucket has an explicit CORS policy that allows the request's origin. Without this policy, S3 does not include 'Access-Control-Allow-Origin' in the response and the browser blocks the upload.",
            "error_category": "network",
            "likely_causes": [
                {"description": "The S3 bucket has no CORS configuration set, so it does not respond to cross-origin requests.", "confidence": "high"},
                {"description": "CORS is configured but the allowed origin does not match the production domain.", "confidence": "medium"}
            ],
            "missing_context_questions": [
                "Is the S3 bucket CORS policy configured in the AWS Console or via Terraform/CDK?",
                "Which HTTP methods do you need to allow (PUT for uploads, GET for downloads)?"
            ],
            "risk_level": "low",
            "warnings": [
                "Avoid using a wildcard '*' for AllowedOrigins in production S3 CORS; specify exact allowed origins."
            ],
            "repair_prompt": "Please configure CORS on your S3 bucket. Browser uploads fail: \"No 'Access-Control-Allow-Origin' header is present\". Add the following CORS policy to the S3 bucket via AWS Console -> S3 -> Bucket -> Permissions -> CORS: '[{\"AllowedHeaders\":[\"*\"],\"AllowedMethods\":[\"PUT\",\"GET\"],\"AllowedOrigins\":[\"https://myapp.com\"],\"ExposeHeaders\":[\"ETag\"],\"MaxAgeSeconds\":3000}]'. Replace 'https://myapp.com' with your actual domain. Do not use '*' for AllowedOrigins in production.",
            "verification_steps": [
                "Apply the CORS configuration to the S3 bucket.",
                "Attempt a direct browser upload and verify the OPTIONS preflight returns 200 with Access-Control-Allow-Origin.",
                "Confirm a file uploads successfully and is accessible at the expected S3 URL."
            ],
            "matched_recipes": []
        }
    },
    {
        "id": "syn-amb-120",
        "scenario_group": "dependency-version-lock-drift",
        "provenance": {"source_type": "synthetic", "license": "Apache-2.0"},
        "review": {"status": "unreviewed", "fix_tested": False, "review_notes": "Synthetic inconsistency between package.json and package-lock.json causing CI installs to differ from local."},
        "model_input": {
            "raw_error": "// CI: Tests pass\n// Local: Tests fail with: TypeError: someLibrary.newMethod is not a function\n\n// Local package-lock.json: some-library@2.3.0\n// CI uses: npm install (no lock file committed) -> some-library@2.4.0\n// package.json: \"some-library\": \"^2.3.0\"",
            "context": {"language_or_framework": "Node.js / npm", "environment": "ci_build", "recent_changes": "CI was recently re-configured to use a clean npm install without a committed lock file."}
        },
        "reference_annotations": {
            "reference_cause": "package-lock.json is not committed to version control, so CI installs the latest compatible version (2.4.0) while locally the developer has 2.3.0. The API changed between these versions.",
            "reference_repair": "Commit package-lock.json to version control and use 'npm ci' in CI pipelines to enforce exact lock file installs.",
            "difficulty": "medium"
        },
        "target_report": {
            "summary": "Tests behave differently in CI and locally because package-lock.json is not committed, causing CI to install a newer package version.",
            "plain_explanation": "The caret ('^') in '\"some-library\": \"^2.3.0\"' allows npm to install any compatible minor or patch version up to (but not including) 3.0.0. Without 'package-lock.json' committed to git, each CI run reinstalls from scratch and may pick up a newer version (2.4.0) that changed an API. The local developer still has 2.3.0 pinned in their own lock file.",
            "error_category": "dependency",
            "likely_causes": [
                {"description": "package-lock.json is not committed to version control, allowing CI to install a different version than what developers have locally.", "confidence": "high"},
                {"description": "CI uses 'npm install' instead of 'npm ci', which would enforce the lock file.", "confidence": "high"}
            ],
            "missing_context_questions": [
                "Is package-lock.json in .gitignore?",
                "Does the CI pipeline use 'npm install' or 'npm ci'?"
            ],
            "risk_level": "medium",
            "warnings": [
                "Always commit package-lock.json (npm) or pnpm-lock.yaml (pnpm) or yarn.lock (yarn) to ensure reproducible installs."
            ],
            "repair_prompt": "Please inspect .gitignore and CI workflow configuration. Tests differ between CI and local because package-lock.json is not committed, allowing version drift. Take these steps: (1) Remove package-lock.json from .gitignore if it is listed there; (2) Commit the current package-lock.json; (3) Change CI from 'npm install' to 'npm ci' which installs exactly from the lock file. If the API difference between 2.3.0 and 2.4.0 is causing test failures, pin the version in package.json to '2.3.0' (no caret) until you can update the usage.",
            "verification_steps": [
                "Commit package-lock.json to the repository.",
                "Update CI workflow to use 'npm ci' instead of 'npm install'.",
                "Run CI and confirm the same version (2.3.0) is installed as locally."
            ],
            "matched_recipes": []
        }
    }
]


def main():
    print(f"Total Batch 4 records prepared: {len(RECORDS)}")
    assert len(RECORDS) == 30, f"Expected 30 records, got {len(RECORDS)}"

    train_records = RECORDS[:22]
    val_records   = RECORDS[22:26]
    test_records  = RECORDS[26:]

    assert len(train_records) == 22
    assert len(val_records)   == 4
    assert len(test_records)  == 4

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

    from inference.schema import validate_instance
    from inference.safety import redact_secrets
    from training.validate_data import _strings, SENSITIVE_VALUE, load_valid_recipes

    schema        = json.loads((ROOT / "data" / "schema.json").read_text(encoding="utf-8"))
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
            red, count = redact_secrets(s)
            if count and red != s:
                raise ValueError(f"Secret redaction triggered in {rid}: {red[:50]}...")

    print("All 30 Batch 4 records passed schema, category, and secret validation.")

    batch_ids = {r["id"] for r in RECORDS}

    def write_split(path, new_records):
        existing = []
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                if row["id"] not in batch_ids:
                    existing.append(row)
        combined = existing + new_records
        with open(path, "w", encoding="utf-8") as f:
            for rec in combined:
                f.write(json.dumps(rec) + "\n")
        print(f"Updated {path}: {len(existing)} existing + {len(new_records)} Batch 4 = {len(combined)} total")

    write_split(ROOT / "data" / "train.jsonl",      train_records)
    write_split(ROOT / "data" / "validation.jsonl", val_records)
    write_split(ROOT / "data" / "test.jsonl",       test_records)


if __name__ == "__main__":
    main()
