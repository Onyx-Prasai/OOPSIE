# Recipe: Vercel Deployment Command Failure

- **ID**: `kb-vercel-build-001`
- **Category**: `deployment`
- **Frameworks**: `nextjs`, `react`, `vite`
- **Services**: `vercel`
- **Risk Level**: `low`

## Target Error Signatures
- `Error: Command "npm run build" exited with 1`
- `Type error: Route "src/app/api/..." has an invalid export`
- `Build failed because of webpack errors`

## Plain Language Explanation
Vercel tried to build your application for production deployment, but TypeScript type errors, missing imports, or static generation checks failed during `npm run build`.

## Likely Causes
1. TypeScript strict type checks passed during local dev server runtime but failed during production compilation (`tsc --noEmit`).
2. Page route exported an invalid component signature or used client hooks (`useState`, `useEffect`) without `'use client'` directive.
3. ESLint rules triggered build-blocking warnings on Vercel.

## Safe AI Repair Prompt Template
```text
The deployment on Vercel failed during build:
[PASTE_VERCEL_LOG_HERE]

Please:
1. Run `npm run build` locally to reproduce the exact build failure.
2. Fix the TypeScript or export errors without altering working app functionality.
3. Verify that all components using browser state include `'use client'` at top of file.
4. Keep all existing design and business logic unchanged.
```

## Verification Checklist
- [ ] Run `npm run build` locally and confirm exit code 0.
- [ ] Push changes to GitHub to trigger Vercel re-deployment.
