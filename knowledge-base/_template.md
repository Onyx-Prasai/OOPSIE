# Error Recipe Template

<!-- Copy this file, fill in each section, and submit a PR to knowledge-base/<framework>/<slug>.md -->

- **ID**: `kb-<framework>-<slug>`
- **Category**: `dependency | environment_variables | database | deployment | authentication | network | typescript | build | runtime`
- **Frameworks**: `react, nextjs, supabase, vercel, firebase, npm, general`
- **Risk Level**: `low | medium | high`

## Target Error Signatures

List exact strings or patterns that match this error:

- `Exact error message here`
- `Another variation of the same error`

## Plain English Explanation

What is likely happening in simple, non-technical terms? Distinguish evidence from assumptions.

## Likely Root Causes

1. Most common cause
2. Second most common cause
3. Edge case

## Suggested Repair Steps

Careful, reviewable steps. Do not imply the suggestion is guaranteed:

```bash
# Example only: a person must review commands before running them.
npm install <package>
```

## Repair Prompt for AI

Copy this into Cursor, Claude, or Copilot Chat:

```
My project has this error:

[paste error here]

Please inspect the relevant context, explain the likely cause, and suggest the smallest focused change.
Do not change unrelated files, execute commands, or deploy.
Explain any proposed changes and provide verification steps. Do not claim a fix is guaranteed.
```

## Verification Checklist

- [ ] Review the proposed change and its risks
- [ ] Apply changes only after human review
- [ ] Verify in a safe environment before production use

## Related Recipes

- Link to related recipes if applicable
