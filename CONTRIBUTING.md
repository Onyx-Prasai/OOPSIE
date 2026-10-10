# Contributing to OOPSIE 🚀

Thank you for contributing to **OOPSIE** — the open-source AI Error Recovery Copilot for vibe coders!

## How You Can Contribute

### 1. Submit an Error Recovery Recipe (`/knowledge-base/`)
Found a common error in React, Next.js, Supabase, Vercel, Firebase, Docker, or Python?
1. Fork this repository: [https://github.com/Onyx-Prasai/OOPSIE](https://github.com/Onyx-Prasai/OOPSIE)
2. Create a markdown file under `/knowledge-base/<framework>/<error-slug>.md`.
3. Fill out the recipe template:
   - Target Error Signatures
   - Plain Language Explanation
   - Likely Root Causes
   - Safe AI Repair Prompt Template
   - Verification Checklist
4. Open a Pull Request!

### 2. Improve Classification Rules (`/rules/classifiers.json`)
Add regex or keyword patterns to help OOPSIE instantly classify obscure build errors.

### 3. Add Safety & Redaction Patterns (`/rules/secret-redaction-patterns.json`)
Help ensure users never accidentally paste sensitive API tokens or database secrets into public logs.

### 4. Direct Email Support & Inquiries
Reach out to the lead maintainer at **[onyxefforts@gmail.com](mailto:onyxefforts@gmail.com)** for recipe questions or security reports.

## Local Development Setup
```bash
# Clone repository
git clone https://github.com/Onyx-Prasai/OOPSIE.git
cd OOPSIE

# Install dependencies
npm install

# Start local documentation & engine portal
npm run dev
```
