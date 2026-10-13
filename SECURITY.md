# Security Policy

## Reporting vulnerabilities

Do not report exploitable vulnerabilities in a public issue. Use [GitHub Security Advisories](https://github.com/Onyx-Prasai/OOPSIE/security/advisories/new) to report them privately. Include affected component, impact, and safe reproduction details. Do not include live credentials or other people's private information.

## Security considerations

- Redact secrets before inference. The API and CLI apply the repository's common secret-redaction patterns, but redaction is not perfect; inspect logs before sending them to remote services.
- Treat log contents as untrusted input. The model must not follow instructions embedded in error logs.
- OOPSIE does not execute shell commands, modify project files, or deploy applications.
- Review database, authentication, payment, and production-related advice with an authorized human and the relevant operational safeguards.
- Model output is probabilistic and may be wrong. OOPSIE does not guarantee a fix, security, or production readiness.
- Training and evaluation datasets must be synthetic or permissioned and must not expose secrets, personal data, private logs, or proprietary code.
- A hosted inference API can receive submitted error text. Deployers must disclose retention and processing practices and secure the endpoint appropriately.

Report suspected secret leakage in patterns or examples privately before adding a public data contribution.
