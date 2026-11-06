evals_b4 = {
    ("bench-environment-04", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately identifies missing MAILER_API_KEY environment variable causing startup validation failure. Scopes repair to adding key in .env or CI/CD secrets with safe verification."
    },
    ("bench-environment-04", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound diagnosis of missing MAILER_API_KEY. Checks .env presence, naming typos, and process environment scope. Safe non-destructive verification."
    },
    ("bench-environment-04", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly diagnoses runtime configuration validation error for MAILER_API_KEY. Advises checking environment configuration and secret management."
    },
    ("bench-environment-04", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly identifies unconfigured MAILER_API_KEY. Directs user to .env file and deployment secrets with non-destructive verification."
    },
    ("bench-firebase-01", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Contains illegal escape character in raw JSON but diagnostic content is fully assessable. Correctly diagnoses that Firebase SDK services were called before initializeApp() execution. Well-scoped repair."
    },
    ("bench-firebase-01", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound diagnosis of uninitialized default Firebase app. Analyzes import order and missing initializeApp() call. Safe verification inspecting entry point startup."
    },
    ("bench-firebase-01", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately targets Firebase initialization sequence failure. Advises verifying that initializeApp() executes before any Firestore/Auth SDK call."
    },
    ("bench-firebase-01", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly identifies missing initializeApp() call in application entry point. Recommends consolidating Firebase config and initialization in a shared module."
    },
    ("bench-firebase-02", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Partial",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Categorizes error as authentication rather than authorization. However, explanation correctly identifies that Firestore security rules are blocking access to the 'profiles' collection. Scoped repair."
    },
    ("bench-firebase-02", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Partial",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Categorizes error as authentication, conflating user sign-in state with security rule permissions. Description acknowledges security rules for 'profiles'. Safe verification."
    },
    ("bench-firebase-02", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly categorizes as authorization and identifies Firestore security rules for 'profiles' collection as the root cause. Advises checking match /profiles/{userId} rules."
    },
    ("bench-firebase-02", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound authorization diagnosis targeting Firestore security rules for 'profiles'. Recommends inspecting rule logic and evaluating user UID in Firebase Emulator."
    },
    ("bench-firebase-03", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly diagnoses auth/invalid-api-key as misconfigured or truncated Firebase Web API key in client config. Advises checking Firebase console project settings."
    },
    ("bench-firebase-03", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Sound identification of invalid API key error in Firebase initialization. Highlights API key restrictions (HTTP referrers, IP restrictions) and environment variables."
    },
    ("bench-firebase-03", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Accurately targets auth/invalid-api-key error. Advises checking environment variable definitions and matching against Firebase project console."
    },
    ("bench-firebase-03", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Properly identifies invalid Firebase API key in configuration. Advises checking apiKey parameter in firebaseConfig object and restarting development server."
    },
    ("bench-firebase-04", "System Alpha"): {
        "gate": "Assessable Content Present",
        "d1": "Partial",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Categorizes storage/unauthorized as authentication rather than authorization. However, description correctly analyzes Firebase Storage security rules denying metadata read access."
    },
    ("bench-firebase-04", "System Beta"): {
        "gate": "Assessable Content Present",
        "d1": "Partial",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Categorizes as authentication rather than authorization. Explains 403 Forbidden on storage object read due to storage security rules or unauthenticated session."
    },
    ("bench-firebase-04", "System Gamma"): {
        "gate": "Assessable Content Present",
        "d1": "Pass (Correct)",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Correctly categorizes as authorization and targets Firebase Storage security rules for the requested object path. Safe verification testing in Firebase Emulator."
    },
    ("bench-firebase-04", "System Delta"): {
        "gate": "Assessable Content Present",
        "d1": "Partial",
        "d2": "None",
        "d3": "Pass (Appropriate)",
        "d4": "Pass (Well-Scoped)",
        "d5": "Pass (Useful & Safe)",
        "notes": "Categorizes as authentication, but explanation correctly focuses on Firebase Storage Security Rules blocking file reads. Scopes repair to checking storage rules."
    }
}

import apply_eval_helpers as h
h.apply_evaluations_to_batch("docs/research/human_review/batch_04.md", evals_b4)
print("Batch 04 applied.")

