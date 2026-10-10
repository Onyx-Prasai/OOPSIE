# Recipe: Supabase Row Level Security (RLS) Permission Denied

- **ID**: `kb-supabase-rls-001`
- **Category**: `database`
- **Frameworks**: `react`, `nextjs`
- **Services**: `supabase`
- **Risk Level**: `medium`

## Target Error Signatures
- `new row violates row-level security policy for table`
- `PGRST301: permission denied for schema public`
- `42501: RLS policy violated`

## Plain Language Explanation
Supabase database table protection (Row Level Security) blocked your query. The table exists, but no permission policy allows your current user (or anonymous public client) to read, insert, or update rows.

## Likely Causes
1. Table was created in Supabase with RLS enabled, but 0 access policies were created.
2. User is attempting an operation (e.g. `INSERT` into `profiles`) while unauthenticated.
3. The RLS policy requires `auth.uid() = user_id`, but the query did not include the current authenticated user's ID.

## Safety Warning
> [!WARNING]
> Do NOT disable RLS globally in production! Create specific SELECT/INSERT policies instead.

## Safe AI Repair Prompt Template
```text
Supabase database query failed with Row Level Security policy violation:
[PASTE_ERROR_HERE]

Please:
1. Provide the SQL commands to add appropriate RLS policies for table [TABLE_NAME].
2. Create standard policies for SELECT/INSERT based on authenticated user ID (`auth.uid()`).
3. Explain clearly how to run these SQL statements in the Supabase SQL Editor.
4. Do NOT turn off RLS globally.
```

## Verification Checklist
- [ ] Run RLS policy query in Supabase SQL Editor.
- [ ] Test table insert or fetch in application UI.
