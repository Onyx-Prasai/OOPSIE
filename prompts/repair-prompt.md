# Safe repair prompt instructions

Generate a copy-ready prompt for a human to give to Cursor, Claude Code, ChatGPT, Lovable, Bolt, Replit, or another coding assistant.

The prompt should state the observed error and relevant known context, ask the coding assistant to inspect the relevant files before changing anything, and request the smallest focused repair. It must prohibit unrelated redesigns, secret disclosure, automatic deployment, and destructive operations without explicit human review. Ask for a concise explanation of changed files and concrete verification steps. Phrase the result as a suggestion, never a guaranteed fix.
