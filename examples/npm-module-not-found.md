# Example: npm Module Not Found

## Error

```
Module not found: Error: Can't resolve '@supabase/supabase-js' in '/app/src'
```

## What Happened

The AI assistant wrote code that uses Supabase but never ran `npm install @supabase/supabase-js`. The package is imported in the code but doesn't exist in `node_modules`.

## OOPSIE Report

**Category:** dependency  
**Risk Level:** low

**Likely Cause:** Package imported but not installed.

**Repair Prompt Generated:**
```
My project has this error:

Module not found: Error: Can't resolve '@supabase/supabase-js'

Please identify the root cause and make the smallest possible fix.
Do not change unrelated files or redesign anything.
Explain every file you change.
```

**Fix:**
```bash
npm install @supabase/supabase-js
```

**Verification:**
- Restart dev server
- Confirm `package.json` includes `@supabase/supabase-js`
- Reload the page
