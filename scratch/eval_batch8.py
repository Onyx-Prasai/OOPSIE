evals_b8 = {
    ("bench-react-04", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly diagnoses React SSR hydration mismatch. Identifies browser-only APIs (window, localStorage) or timestamp/date differences between server and client. Diagnostic test verification."
    },
    ("bench-react-04", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound identification of hydration mismatch between server-rendered HTML and client DOM. Analyzes browser extensions, dynamic values, and advises incognito testing."
    },
    ("bench-react-04", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately targets hydration error stemming from time-dependent rendering (Date.now()) or browser APIs. Advises deferring client-specific rendering to useEffect."
    },
    ("bench-react-04", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly analyzes server vs client text divergence during hydration. Outlines invalid HTML nesting and non-deterministic state causes with safe browser verification."
    },
    ("bench-supabase-01", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly diagnoses Supabase AuthApiError: Invalid login credentials. Recommends testing with known valid test account and warns against exposing user enumeration details."
    },
    ("bench-supabase-01", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound identification of credential validation failure in Supabase Auth. Recommends checking auth payload formatting and verifying user status in dashboard."
    },
    ("bench-supabase-01", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately targets invalid login credentials. Scopes repair to client submission handling and login error state management without leaking auth secrets."
    },
    ("bench-supabase-01", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly analyzes Supabase AuthApiError. Suggests checking auth provider configuration, email confirmation requirements, and password reset flows."
    },
    ("bench-supabase-02", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly identifies PostgreSQL Row-Level Security (RLS) violation on 'orders' table in Supabase. Advises inspecting RLS policy rules and auth.uid() checks. Safe verification."
    },
    ("bench-supabase-02", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound authorization diagnosis for RLS policy on 'orders'. Recommends verifying user authentication token and checking INSERT policy definitions in Supabase Studio."
    },
    ("bench-supabase-02", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Categorizes as database and accurately explains PostgreSQL Row Level Security policy failure on INSERT into 'orders'. Diagnostic SQL policy inspection."
    },
    ("bench-supabase-02", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly analyzes RLS violation. Advises inspecting pg_policies and adding a scoped INSERT policy for authenticated users rather than disabling RLS."
    },
    ("bench-supabase-03", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly diagnoses missing supabaseKey environment variable during createClient initialization. Scopes repair to .env configuration with safe verification."
    },
    ("bench-supabase-03", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound identification of missing Supabase API key parameter. Advises checking local .env.local vs dashboard API settings and restarting development server."
    },
    ("bench-supabase-03", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately targets missing supabaseKey during Supabase client construction. Directs user to populate environment variables without committing credentials."
    },
    ("bench-supabase-03", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly analyzes 'supabaseKey is required'. Recommends verifying .env file variable names (NEXT_PUBLIC_SUPABASE_ANON_KEY vs SUPABASE_KEY) and client setup."
    },
    ("bench-supabase-04", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly diagnoses Supabase AuthError: OAuth provider callback URL is not allowed. Recommends adding the client redirect URI to Supabase Dashboard > Authentication > URL Configuration."
    },
    ("bench-supabase-04", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound identification of unwhitelisted OAuth callback URL. Advises synchronizing Redirect URLs in Supabase Auth settings with OAuth provider app dashboard."
    },
    ("bench-supabase-04", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately targets disallowed OAuth callback URL. Recommends checking protocol (http vs https), port, and trailing slashes in Supabase 'Site URL' and redirect whitelist."
    },
    ("bench-supabase-04", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly analyzes OAuth provider callback restriction. Scopes repair to adding authorized redirect URI in both provider developer settings and Supabase dashboard."
    }
}

import apply_eval_helpers as h
h.apply_evaluations_to_batch("docs/research/human_review/batch_08.md", evals_b8)
print("Batch 08 applied.")

