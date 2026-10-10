# Recipe: Missing Environment Variables in Next.js / Vercel

- **ID**: `kb-nextjs-env-001`
- **Category**: `environment_variables`
- **Frameworks**: `nextjs`, `react`
- **Services**: `vercel`, `supabase`, `custom_api`
- **Risk Level**: `medium`

## Target Error Signatures
- `Error: invalid api key`
- `Unhandled Runtime Error: Error: NEXT_PUBLIC_` is undefined
- `TypeError: Cannot read properties of undefined (reading 'supabaseUrl')`
- `Vercel Deployment Error: Environment Variable NEXT_PUBLIC_... missing`

## Plain Language Explanation
Your code is trying to access configuration keys or database connection URLs (such as `process.env.NEXT_PUBLIC_SUPABASE_URL`) that have not been defined in `.env.local` or in your Vercel project environment settings.

## Likely Causes
1. The `.env.local` file was not created in the project root folder.
2. The environment variable name in `.env.local` differs from what the code expects (e.g., missing `NEXT_PUBLIC_` prefix for client-side access).
3. Environment variables were added locally but not pushed to Vercel/Netlify deployment configuration.

## Safety Warning
> [!CAUTION]
> Never commit real secrets, API secret keys, or database service role keys to Git repository files or paste them into public prompt windows.

## Safe AI Repair Prompt Template
```text
My Next.js project is encountering missing environment variable errors:
[PASTE_ERROR_LINE_HERE]

Please:
1. Inspect where environment variables are defined (e.g. env configuration or lib files).
2. Create or update `.env.example` with placeholder names for required variables.
3. Ensure client-side variables correctly use the `NEXT_PUBLIC_` prefix if accessed in browser components.
4. Do NOT output or expose any live secret keys in code or commits.
5. Provide a summary of required environment variables for `.env.local`.
```

## Verification Checklist
- [ ] Ensure `.env.local` exists in the root directory.
- [ ] Confirm variable names match `.env.example` placeholders.
- [ ] Restart Next.js dev server (`npm run dev`) so environment variables reload.
- [ ] Add the variables to Vercel project settings if deploying.
