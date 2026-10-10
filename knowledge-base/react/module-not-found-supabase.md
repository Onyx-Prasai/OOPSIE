# Recipe: Missing Supabase Client Package

- **ID**: `kb-react-supabase-001`
- **Category**: `dependency`
- **Frameworks**: `react`, `nextjs`
- **Services**: `supabase`
- **Risk Level**: `low`

## Target Error Signatures
- `Module not found: Can't resolve '@supabase/supabase-js'`
- `Cannot find module '@supabase/supabase-js'`
- `Error: Cannot find module '@supabase/ssr'`

## Plain Language Explanation
Your application code is importing Supabase functions (e.g. `createClient`), but the Supabase JavaScript library is not installed in your project's `node_modules` directory.

## Likely Causes
1. An AI coding tool added Supabase code snippet into your components without running `npm install @supabase/supabase-js`.
2. The dependency was installed in a parent directory or inside a subfolder rather than the project root.
3. The `package.json` file was edited manually without running the package manager installation step.

## Safe AI Repair Prompt Template
```text
My project fails with the following error:
"Module not found: Can't resolve '@supabase/supabase-js'"

Please inspect package.json and project dependencies.
Install the missing package "@supabase/supabase-js" (or "@supabase/ssr" if server components are used).
Do NOT modify database schemas, environment variables, or unrelated UI components.
After fixing, list the exact commands run and files changed.
```

## Verification Checklist
- [ ] Check `package.json` contains `"@supabase/supabase-js"` under dependencies.
- [ ] Restart local development server (`npm run dev`).
- [ ] Verify Supabase client initializes without console module errors.
