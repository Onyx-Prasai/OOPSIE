# Example: Vercel Missing Environment Variable

## Error

```
TypeError: Cannot read properties of undefined (reading 'from')
  at getUser (/var/task/.next/server/app/api/user/route.js:12:34)
```

## What Happened

The application appears to expect a Supabase URL while handling this request. The log alone does not establish whether the value is missing in Vercel or whether another configuration or initialization issue is involved.

## OOPSIE Report

**Category:** environment_variables  
**Risk Level:** medium

**Likely Cause:** A required environment value may be unavailable to the deployed process.

**Missing context:**
- Which variable name does the code read at the indicated call site?
- Is the deployment using the expected Vercel environment (preview or production)?
- Does the deployed value exist without sharing its contents?

**Suggested repair prompt:** Ask a coding assistant to inspect the code and deployment environment-variable names, confirm the expected variables exist without printing their values, and propose the smallest correction. Do not expose secrets or change production settings without review.

**Verification:** Verify the variable name and deployment scope in Vercel settings without revealing its value, then test a preview deployment and inspect sanitized logs.
