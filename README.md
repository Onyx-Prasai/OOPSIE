# OOPSIE — AI Error Recovery Copilot

> **Tagline:** Paste chaos. Get clarity.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![GitHub](https://img.shields.io/badge/GitHub-Onyx--Prasai%2FOOPSIE-purple.svg)](https://github.com/Onyx-Prasai/OOPSIE)

**OOPSIE** is an open-source AI Error Recovery Copilot built specifically for vibe coders, non-traditional builders, and developers working with AI assistants like Cursor, Claude, ChatGPT, Lovable, Bolt, and Replit.

When your application breaks with scary terminal output, build logs, or database permission failures, OOPSIE translates technical errors into plain English, identifies likely root causes, assesses risk, and generates a copy-ready AI repair prompt.

---

## Key Features

- **Plain English Explanations**: Converts complex stack traces into understandable explanations.
- **Root Cause Analysis**: Ranks probable causes with clear confidence levels.
- **Risk & Safety Shield**: Identifies potential dangers (e.g., dropping DB tables, leaking API secrets) before running fixes.
- **Safe AI Repair Prompts**: Produces guarded instructions for AI coding assistants that enforce minimal changes.
- **Open Source Knowledge Base**: Community-maintained error recipes across React, Next.js, Supabase, Vercel, Firebase, and npm.
- **Browser & DevTools Extension**: Inspect errors directly on Vercel build logs, Netlify, and Chrome DevTools.

---

## Repository Structure

```
/
├── knowledge-base/            # Community Error Recovery Recipes (.md)
│   ├── react/
│   ├── nextjs/
│   ├── supabase/
│   ├── vercel/
│   ├── firebase/
│   └── npm/
├── prompts/                   # System Prompts & JSON Response Schemas
├── rules/                     # Error Classifiers & Secret Redaction Patterns
├── extension/                 # Manifest V3 Browser Extension Scaffold
├── docs/                      # Architecture, Extension Specs, & LLM Guides
├── vercel.json                # Production Vercel deployment config
└── CONTRIBUTING.md            # Community Contribution Guidelines
```

---

## How to Contribute

We welcome open-source contributions!

1. **Add an Error Recipe**: Check [`knowledge-base/`](knowledge-base/) and submit a new Markdown recipe for a framework error you solved.
2. **Improve Error Classification**: Add regex signatures to [`rules/classifiers.json`](rules/classifiers.json).
3. **Enhance Extension**: Expand [`extension/`](extension/) content scripts for Vercel, GitHub Actions, or Cursor.

- **GitHub Repository**: [https://github.com/Onyx-Prasai/OOPSIE](https://github.com/Onyx-Prasai/OOPSIE)

Read the full [Contribution Guide](CONTRIBUTING.md) to get started.

---

## License

Released under the [MIT License](LICENSE).
