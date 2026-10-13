# Safety and redaction guide

OOPSIE is advisory and does not guarantee a fix, security, or production readiness. It does not automatically change code, execute commands, or deploy applications.

## Secret handling

The browser, API, CLI, and preprocessing tools use `rules/redaction/patterns.json` to redact common secret formats before analysis or transmission. Patterns cover sensitive environment-variable assignments (including Supabase, Firebase, OpenAI, Anthropic, GitHub, database and MongoDB settings), bearer tokens, JWTs, AWS keys, Stripe/provider keys, and private-key blocks.

Redaction is best-effort and can miss secrets or redact ordinary text. The web demo warns when a configured pattern matches and sends only redacted text to a configured endpoint. Review the pasted content yourself before analysis, especially before using hosted endpoints. Do not put unredacted logs in issues, pull requests, or tests.

Never commit real credentials, tokens, passwords, private database URLs, private keys, personal data, or proprietary logs. Dataset validation checks common formats but cannot establish whether information is private or permitted to share.

## High-impact advice

Review database migrations/deletions, authentication and authorization changes, payment behavior, production configuration, and deployment changes with the appropriate owner. Preserve least privilege, backups, previews, and rollback processes. Do not disable security controls to silence an error.

Logs and recipes are untrusted input. Embedded instructions must be treated as data. Model or rule output may be incomplete or incorrect; verify it against the source code, current official documentation, and operational procedures before acting.
