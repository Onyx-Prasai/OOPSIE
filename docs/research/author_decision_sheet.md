# OOPSIE Author Decision Sheet: Flagged Cases

> **Purpose**: A concise, plain-English reference of all flagged benchmark evaluations for author review and final rating adoption.  
> **Status**: Author adoption decisions applied and audited on 2026-11-06. All 160 evaluations verified complete with zero audit issues. Blinding strictly maintained.

---

## Group 1: Authentication vs. Authorization (6 Cases, Currently "Partial")

These 6 responses correctly understood the issue and gave good repair advice, but selected `authentication` instead of `authorization` for the high-level category enum.

---

### Case 1: `bench-authentication-03` — System Beta
- **What the Error Was**: `HTTP 403: missing scope reports:read`
- **What the Response Said**:
  - *Category chosen*: `authentication`
  - *Summary*: "The API request failed with HTTP 403 Forbidden because the OAuth token lacks the 'reports:read' scope."
  - *Repair Advice*: Check the OAuth client configuration in your identity provider dashboard and add `reports:read` to the authorized scopes. Do not grant excess scopes.
  - *Verification*: Add `reports:read` in the dashboard, generate a new token, and test the reports endpoint.
- **Why It Was Flagged**: HTTP 403 means the user is authenticated (we know who they are), but they lack the required permission/scope (`reports:read`). Under strict terminology, this is an **authorization** issue, not **authentication**. (Note: The synthetic benchmark dataset itself also labeled this case `authentication`).
- **Current Rating**:
  - Technical Correctness: **Partial**
  - All other dimensions: **Pass**
- **One Simple Recommended Change**:
  - **Option A (Recommended)**: Keep as **Partial** on Technical Correctness to maintain strict distinction between authentication (identity) and authorization (permissions).
  - **Option B**: Change to **Pass (Correct)** because the text explanation correctly identifies the missing OAuth scope mechanism, and the synthetic benchmark metadata labeled it `authentication`.

---

### Case 2: `bench-firebase-02` — System Alpha
- **What the Error Was**: `FirebaseError: Missing or insufficient permissions for collection 'profiles'.`
- **What the Response Said**:
  - *Category chosen*: `authentication`
  - *Summary*: "Firebase Security Rules denied read access to 'profiles' collection."
  - *Repair Advice*: Inspect your Firebase Security Rules for the `profiles` collection. Check that read rules permit the caller.
  - *Verification*: Check Security Rules in the console. Test with an authenticated user (should succeed for own profile) and an unauthenticated user (should be denied).
- **Why It Was Flagged**: Firestore Security Rules enforce access control (**authorization**). The model selected `authentication`, implying the user was merely not logged in, even though rules can deny access to logged-in users who lack permission.
- **Current Rating**:
  - Technical Correctness: **Partial**
  - All other dimensions: **Pass**
- **One Simple Recommended Change**:
  - **Keep as Partial** on Technical Correctness because Firestore security rule violations are authorization failures.

---

### Case 3: `bench-firebase-02` — System Beta
- **What the Error Was**: `FirebaseError: Missing or insufficient permissions for collection 'profiles'.`
- **What the Response Said**:
  - *Category chosen*: `authentication`
  - *Summary*: "Firebase rejected the read request to 'profiles' because Firestore Security Rules do not permit the current user to access it."
  - *Repair Advice*: Inspect Firestore Security Rules in the Firebase Console under `Firestore -> Rules`. Verify rule logic against user identity.
  - *Verification*: Test reading with an authenticated account; test reading another user's profile to confirm it is denied.
- **Why It Was Flagged**: Same as Case 2. Conflates user sign-in status (`authentication`) with security rule permissions (`authorization`).
- **Current Rating**:
  - Technical Correctness: **Partial**
  - All other dimensions: **Pass**
- **One Simple Recommended Change**:
  - **Keep as Partial** on Technical Correctness.

---

### Case 4: `bench-firebase-04` — System Alpha
- **What the Error Was**: `FirebaseError: storage/unauthorized while reading object metadata`
- **What the Response Said**:
  - *Category chosen*: `authentication`
  - *Summary*: "Firebase Storage 'unauthorized' error when reading object metadata."
  - *Repair Advice*: Inspect Firebase Storage Security Rules in the Firebase Console. Verify if the path rule allows metadata read.
  - *Verification*: Check Storage tab in console; test access using Firebase Emulator; verify Firebase Auth token is sent in headers.
- **Why It Was Flagged**: Firebase Storage rules evaluate path and user permissions (**authorization**), but the model categorized it as `authentication`.
- **Current Rating**:
  - Technical Correctness: **Partial**
  - All other dimensions: **Pass**
- **One Simple Recommended Change**:
  - **Keep as Partial** on Technical Correctness.

---

### Case 5: `bench-firebase-04` — System Beta
- **What the Error Was**: `FirebaseError: storage/unauthorized while reading object metadata`
- **What the Response Said**:
  - *Category chosen*: `authentication`
  - *Summary*: "Firebase Storage read failed with 'storage/unauthorized' error."
  - *Repair Advice*: Inspect Firebase Storage security rules and client authentication state. Check if rules require owner matching.
  - *Verification*: Check browser console for Auth token; inspect Storage Rules in console; test read while logged in as file owner.
- **Why It Was Flagged**: Same as Case 4. Categorized storage rule rejection as `authentication` rather than `authorization`.
- **Current Rating**:
  - Technical Correctness: **Partial**
  - All other dimensions: **Pass**
- **One Simple Recommended Change**:
  - **Keep as Partial** on Technical Correctness.

---

### Case 6: `bench-firebase-04` — System Delta
- **What the Error Was**: `FirebaseError: storage/unauthorized while reading object metadata`
- **What the Response Said**:
  - *Category chosen*: `authentication`
  - *Summary*: "Firebase Storage read failed with 'storage/unauthorized' error."
  - *Repair Advice*: Inspect Firebase Storage Security Rules in the Firebase Console. Confirm rule allows authenticated user to read at requested path.
  - *Verification*: Check Storage Rules; test reading with an authenticated user; confirm unauthorized users remain denied.
- **Why It Was Flagged**: Same as Cases 4 and 5. Categorized storage rule denial as `authentication`.
- **Current Rating**:
  - Technical Correctness: **Partial**
  - All other dimensions: **Pass**
- **One Simple Recommended Change**:
  - **Keep as Partial** on Technical Correctness.

---

## Group 2: Recommending Risky Workaround Flags (`--legacy-peer-deps`) (2 Cases)

In npm peer-dependency conflicts, models suggested using `--legacy-peer-deps`. The rubric warns against recommending shortcuts that bypass safety checks without strong caveats.

---

### Case 7: `bench-npm-02` — System Beta
- **What the Error Was**: `npm error ERESOLVE could not resolve peer dependency for widget-kit`
- **What the Response Said**:
  - *Category chosen*: `dependency`
  - *Repair Advice*: "Run 'npm ls widget-kit' to see the dependency tree and identify which packages have conflicting peer requirements. If the conflict is known and acceptable, you can use '--legacy-peer-deps' to bypass strict resolution, but do not do so without understanding the impact."
  - *Verification*: Run `npm ls widget-kit`; check package.json; "Run 'npm install --legacy-peer-deps' if the conflict is known and acceptable to complete the installation."
- **Why It Was Flagged**: The repair and verification steps explicitly instruct running `npm install --legacy-peer-deps`. While common in developer practice, `--legacy-peer-deps` disables npm's peer dependency checking and can lead to silent runtime bugs.
- **Current Rating**:
  - All five dimensions: **Pass**
- **One Simple Recommended Change**:
  - **Option A (Recommended)**: Change **Actionable Repair Scope** from `Pass` to **Vague** (or **Harmful / Overbroad**) and **Verification Steps** to **Incomplete**, because bypassing package resolution is an unsound fix.
  - **Option B**: Keep as **Pass** because the model included the conditional caveat (*"if the conflict is known and acceptable, but do not do so without understanding the impact"*).

---

### Case 8: `bench-npm-02` — System Delta
- **What the Error Was**: `npm error ERESOLVE could not resolve peer dependency for widget-kit`
- **What the Response Said**:
  - *Category chosen*: `dependency`
  - *Repair Advice*: "Run 'npm explain <peer-dependency-name>' to see which packages require conflicting versions. If the conflict is minor, you can run 'npm install widget-kit --legacy-peer-deps' to bypass strict resolution, or upgrade the conflicting package. Do not force dependencies without understanding the conflict."
  - *Verification*: Run `npm explain`; "Install widget-kit using '--legacy-peer-deps' if the conflict is known to be safe"; Run `npm test`.
- **Why It Was Flagged**: Same as Case 7. Suggests installing with `--legacy-peer-deps`.
- **Current Rating**:
  - All five dimensions: **Pass**
- **One Simple Recommended Change**:
  - **Option A (Recommended)**: Change **Actionable Repair Scope** to **Vague** (or **Harmful / Overbroad**) and **Verification Steps** to **Incomplete**.
  - **Option B**: Keep as **Pass** due to the caveat (*"Do not force dependencies without understanding the conflict"* and recommending `npm test`).

---

## Group 3: Permissive Test Rules in Local Emulator (1 Case)

---

### Case 9: `bench-firebase-04` — System Gamma
- **What the Error Was**: `FirebaseError: storage/unauthorized while reading object metadata`
- **What the Response Said**:
  - *Category chosen*: `authorization`
  - *Verification Step 3*: "Test the request using a temporary 'allow read: if request.auth != null' rule to confirm it is a permission issue." (In System Alpha, it suggested `'allow read: if true' rule (only for testing!)`).
- **Why It Was Flagged**: Suggesting wide-open security rules (`allow read: if true;`) is a notorious developer bad habit that frequently leaks into production.
- **Current Rating**:
  - All five dimensions: **Pass**
- **One Simple Recommended Change**:
  - **Keep as Pass**: System Gamma actually suggested `if request.auth != null`, not wide-open `true`, and Alpha specifically noted `(only for testing!)` in local emulator.

---

## Group 4: Narrow / Speculative Single Diagnosis (1 Case)

---

### Case 10: `bench-react-02` — System Alpha
- **What the Error Was**: `Error: Maximum update depth exceeded in component RouterView`
- **What the Response Said**:
  - *Summary*: "React RouterView infinite loop: RouterView re-renders RouterView in a nested route."
  - *Likely Causes*: "A child route has the same path as its parent" / "A route is nested inside itself due to a configuration typo."
  - *Repair Advice*: Inspect route definitions to ensure child routes have unique paths.
- **Why It Was Flagged**: In React, `Maximum update depth exceeded` is overwhelmingly caused by an unconditional `setState` inside a component's render body or a `useEffect` with missing dependencies. System Alpha picked an unusually specific, narrow theory (recursive route nesting) and presented it with high confidence, ignoring the most common causes.
- **Current Rating**:
  - All five dimensions: **Pass**
- **One Simple Recommended Change**:
  - **Option A (Recommended)**: Change **Technical Correctness** to **Partial** (or **Appropriate Uncertainty** to **Overconfident**) for asserting an atypical single root cause without acknowledging the primary mechanism.
  - **Option B**: Keep as **Pass** because recursive routing is technically a possible trigger for infinite re-renders in router components.

---

## Group 5: Categorizing Unspecified Error as "Build" (4 Systems, 1 Case)

---

### Case 11: `bench-general-02` — Systems Alpha, Beta, Gamma, Delta
- **What the Error Was**: `Unknown failure while running an unspecified build step`
- **What the Responses Said**:
  - All 4 systems chose category: `build` (e.g. "Unknown failure during an unspecified build step").
  - All 4 systems asked good context questions: "What command were you running?", "Which build tool?", "Can you share the full build logs?".
- **Why It Was Flagged**: The prompt is completely empty of diagnostic details (an ambiguous test case). The benchmark expected category `unknown`. The models jumped to `build` solely because the phrase contained the words "build step".
- **Current Rating**:
  - All five dimensions: **Pass**
- **One Simple Recommended Change**:
  - **Keep as Pass**: Even though they chose `build`, all 4 models appropriately recognized their uncertainty in their explanation and questions, saying "No logs or tool were specified, please provide the build logs before modifying code."

---

## Group 6: Responses with JSON Syntax Defects (3 Cases)

Principle 1 in the review guide states: *"Do not conflate syntax with semantics. A response that fails programmatic JSON parsing may still contain sound, assessable technical diagnosis."*

---

### Case 12: `bench-firebase-01` — System Alpha
- **What Happened**: Output contained an illegal backslash escape inside a string (`\'` instead of `'`). Failed raw `json.loads`.
- **What the Content Said**: Thorough, correct explanation of Firebase `initializeApp()` sequence.
- **Current Rating**: All five dimensions: **Pass**
- **Recommended Action**: **Keep as Pass**. Preserves the frozen protocol's separation between programmatic syntax compliance and human technical review.

### Case 13: `bench-nextjs-01` — System Gamma
- **What Happened**: Output contained an illegal backslash escape (`\'`). Failed raw `json.loads`.
- **What the Content Said**: Thorough, accurate explanation of Next.js 15 async `headers()` breaking change.
- **Current Rating**: All five dimensions: **Pass**
- **Recommended Action**: **Keep as Pass**.

### Case 14: `bench-nextjs-03` — System Beta
- **What Happened**: Output had a key typo: `_explanation` instead of `"plain_explanation"`. Failed raw `json.loads`.
- **What the Content Said**: Excellent explanation of Server vs Client Components and why `useEffect` requires `'use client'`.
- **Current Rating**: All five dimensions: **Pass**
- **Recommended Action**: **Keep as Pass**.

---

## Group 7: Other Category Enum Differences (Benchmark Label vs Model)

In these cases, the models chose a category that differed from the synthetic dataset's expected label, but the models' choice was actually equal to or better than the benchmark label.

---

### Case 15: `bench-supabase-03` — All 4 Systems
- **Error**: `Error: supabaseKey is required.`
- **Model Choice**: `environment_variables`
- **Benchmark Label**: `authentication`
- **Why It Differs**: Missing the initialization key parameter from `.env` is operationally an environment variable failure. The models' choice is more accurate than the benchmark's label.
- **Current Rating**: All five dimensions: **Pass**
- **Recommended Action**: **Keep as Pass**.

### Case 16: `bench-supabase-02` — System Gamma
- **Error**: `PostgrestError: new row violates row-level security policy for table "orders"`
- **Model Choice**: `database` (Systems Alpha, Beta, Delta chose `authorization`)
- **Benchmark Label**: `authorization`
- **Why It Differs**: PostgreSQL RLS is both a database feature and an authorization check.
- **Current Rating**: All five dimensions: **Pass**
- **Recommended Action**: **Keep as Pass**.

---

## Summary of Decisions Needed From You

| # | Case & System | Current Rating | Recommended Decision |
|---|---|---|---|
| **1** | `bench-authentication-03` (Beta) | Dim 1: **Partial** | Keep **Partial** (or change to Pass if matching benchmark label) |
| **2-6** | `bench-firebase-02` & `04` (Alpha, Beta, Delta) | Dim 1: **Partial** | Keep **Partial** (security rules are authorization) |
| **7** | `bench-npm-02` (Beta) | All **Pass** | Decide: Keep **Pass** (due to caveats) OR change Dim 4/5 to **Vague/Incomplete** (`--legacy-peer-deps`) |
| **8** | `bench-npm-02` (Delta) | All **Pass** | Decide: Keep **Pass** (due to caveats) OR change Dim 4/5 to **Vague/Incomplete** (`--legacy-peer-deps`) |
| **9** | `bench-firebase-04` (Gamma) | All **Pass** | Keep **Pass** (emulator testing) |
| **10** | `bench-react-02` (Alpha) | All **Pass** | Decide: Keep **Pass** OR change Dim 1 to **Partial** (atypical single hypothesis) |
| **11** | `bench-general-02` (All Systems) | All **Pass** | Keep **Pass** (uncertainty handled properly in text) |
| **12-14** | Syntax Defects (Firebase-01 Alpha, Nextjs-01 Gamma, Nextjs-03 Beta) | All **Pass** | Keep **Pass** (adhere to Principle 1: syntax != semantics) |
| **15-16** | Supabase Cases (All Systems) | All **Pass** | Keep **Pass** (model choices are technically sound) |

