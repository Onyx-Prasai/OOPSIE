import type { OopsieReport } from '../types';

export interface SampleError {
  id: string;
  title: string;
  framework: string;
  category: string;
  rawLog: string;
  report: OopsieReport;
}

export const SAMPLE_ERRORS: SampleError[] = [
  {
    id: 'sample-supabase-1',
    title: "Supabase Module Not Found",
    framework: "React / Next.js",
    category: "Dependency",
    rawLog: `Module not found: Can't resolve '@supabase/supabase-js'
  > 3 | import { createClient } from '@supabase/supabase-js'
      | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  Import trace for requested module:
  ./src/lib/supabaseClient.ts`,
    report: {
      id: 'rep-supabase-1',
      summary: "Missing '@supabase/supabase-js' library in node_modules",
      plain_english_explanation: "Your project code is trying to use Supabase database tools, but the required Supabase library is missing from your project's installed packages.",
      category: 'dependency',
      risk_level: 'low',
      likely_causes: [
        {
          title: "AI added Supabase code without installing package",
          confidence: 'high',
          description: "An AI assistant generated Supabase client code into lib/supabaseClient.ts, but forgot to execute `npm install @supabase/supabase-js`."
        },
        {
          title: "Wrong directory installation",
          confidence: 'medium',
          description: "The package was installed in a parent directory or nested subfolder instead of the project root."
        }
      ],
      follow_up_questions: [
        "Are you using Next.js App Router (which may also need `@supabase/ssr`)?",
        "Did you run npm install inside the root project directory?"
      ],
      repair_prompt: `My project displays: "Module not found: Can't resolve '@supabase/supabase-js'". Inspect the project's package manager and existing Supabase setup in ./src/lib/supabaseClient.ts. Install the correct @supabase/supabase-js package, verify the import path, and make the smallest possible change. Do not redesign the UI or modify unrelated features. After the fix, tell me which file(s) changed and how I can verify it works.`,
      verification_checklist: [
        "Check that '@supabase/supabase-js' is listed in package.json dependencies",
        "Restart local development server (npm run dev)",
        "Confirm console no longer logs module resolution failures"
      ],
      safety_warnings: [
        "This is a package setup issue. No database or user data is at risk."
      ],
      timestamp: new Date().toISOString()
    }
  },
  {
    id: 'sample-nextjs-env-1',
    title: "Next.js Missing ENV Variable",
    framework: "Next.js",
    category: "Environment Variables",
    rawLog: `Unhandled Runtime Error: Error: NEXT_PUBLIC_SUPABASE_URL is not defined
  at getSupabaseClient (lib/supabase.ts:12:11)
  at AuthProvider (context/AuthContext.tsx:24:18)
  at renderWithHooks (react-dom.development.js:16305:18)`,
    report: {
      id: 'rep-env-1',
      summary: "Environment variable NEXT_PUBLIC_SUPABASE_URL is missing or undefined",
      plain_english_explanation: "Your code is trying to connect to Supabase, but it cannot find your database URL. The environment variable needed to connect has not been set up in `.env.local`.",
      category: 'environment_variables',
      risk_level: 'medium',
      likely_causes: [
        {
          title: "Missing .env.local file in project root",
          confidence: 'high',
          description: "No `.env.local` file exists in your project root, or the variable name inside `.env.local` is misspelled."
        },
        {
          title: "Missing NEXT_PUBLIC_ prefix for client side",
          confidence: 'medium',
          description: "The variable was named `SUPABASE_URL` instead of `NEXT_PUBLIC_SUPABASE_URL`, preventing browser components from accessing it."
        }
      ],
      follow_up_questions: [
        "Is this happening locally on your computer or on Vercel deployment?",
        "Do you have a `.env.local` file in your root folder?"
      ],
      repair_prompt: `My Next.js project throws "NEXT_PUBLIC_SUPABASE_URL is not defined". Inspect lib/supabase.ts and AuthContext.tsx. Verify how environment variables are accessed. Create or update .env.example with placeholder names for NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY. Ensure client components use the NEXT_PUBLIC_ prefix properly. Do NOT paste or commit actual secret keys. Tell me what keys I need to put in .env.local.`,
      verification_checklist: [
        "Ensure .env.local exists in your project root folder",
        "Restart your dev server (npm run dev) so Next.js reloads environment variables",
        "Verify your app loads without runtime env crashes"
      ],
      safety_warnings: [
        "Never paste live secret API keys or service keys directly in code files or git commits."
      ],
      timestamp: new Date().toISOString()
    }
  },
  {
    id: 'sample-vercel-build-1',
    title: "Vercel Build Command Failure",
    framework: "Vercel / Next.js",
    category: "Deployment",
    rawLog: `[14:22:01.002] Running "npm run build"
[14:22:04.110] Failed to compile.
[14:22:04.111] ./src/app/dashboard/page.tsx:18:24
[14:22:04.111] Type error: Property 'user_metadata' does not exist on type 'User | null'.
[14:22:04.180] Error: Command "npm run build" exited with 1`,
    report: {
      id: 'rep-vercel-1',
      summary: "TypeScript type failure during production build execution",
      plain_english_explanation: "Vercel tried to build your app for deployment, but TypeScript found a potential bug where code accesses `user_metadata` on an object that could be null.",
      category: 'deployment',
      risk_level: 'low',
      likely_causes: [
        {
          title: "Missing null-check on optional user object",
          confidence: 'high',
          description: "The user variable might be null before authentication completes. `user?.user_metadata` optional chaining or conditional guard is required."
        }
      ],
      follow_up_questions: [
        "Did `npm run dev` work locally because TypeScript strict checks only run during build?",
        "Is this page using client state or server component auth?"
      ],
      repair_prompt: `My Vercel deployment failed during 'npm run build' with error: "Type error: Property 'user_metadata' does not exist on type 'User | null'" at ./src/app/dashboard/page.tsx:18:24. Add appropriate optional chaining (e.g. user?.user_metadata) or early return null-guard before accessing properties. Keep all UI and styling intact. Run local build checks to verify fix.`,
      verification_checklist: [
        "Run `npm run build` locally in your terminal to verify exit code 0",
        "Git push changes to trigger automated Vercel re-deployment"
      ],
      safety_warnings: [
        "Pure build compilation fix. Safe to deploy once local build passes."
      ],
      timestamp: new Date().toISOString()
    }
  },
  {
    id: 'sample-supabase-rls-1',
    title: "Supabase Row-Level Security Violation",
    framework: "Supabase / PostgreSQL",
    category: "Database",
    rawLog: `PostgrestError: new row violates row-level security policy for table "projects"
  code: "42501"
  details: "Failing row contains (id: 4a2b, title: New App, user_id: 8812)"
  hint: null`,
    report: {
      id: 'rep-rls-1',
      summary: "Database operation blocked by Supabase Row-Level Security (RLS)",
      plain_english_explanation: "Your application tried to save data into the 'projects' database table, but Supabase blocked it because no permission policy allows this insert operation.",
      category: 'database',
      risk_level: 'medium',
      likely_causes: [
        {
          title: "Table has RLS enabled but 0 access policies defined",
          confidence: 'high',
          description: "The table was created in Supabase with RLS turned on, but no policy was created to grant INSERT access to authenticated users."
        }
      ],
      follow_up_questions: [
        "Are users logged in when making this insert request?",
        "Did you create the table via Supabase Dashboard UI or migration script?"
      ],
      repair_prompt: `My Supabase insert failed with: "new row violates row-level security policy for table 'projects'". Provide the SQL statements to create standard RLS policies for table 'projects' enabling logged-in users (auth.uid() = user_id) to SELECT and INSERT rows. Do NOT turn off RLS globally. Tell me step-by-step how to run this in the Supabase SQL Editor.`,
      verification_checklist: [
        "Run the generated SQL RLS policy in Supabase SQL Editor",
        "Retry the form submission in your app UI"
      ],
      safety_warnings: [
        "Do NOT disable RLS globally in production databases. Always use explicit policies."
      ],
      timestamp: new Date().toISOString()
    }
  }
];
