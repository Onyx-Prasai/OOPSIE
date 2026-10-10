# OOPSIE System Architecture

OOPSIE is an open-source AI Error Recovery Copilot designed to transform raw terminal crashes, build logs, and console traces into safe, executable repair plans.

```mermaid
graph TD
    A[User Error Input / Screenshot / Console] --> B[Input Parser & Secret Redactor]
    B --> C[Rule-Based & AI Classifier]
    C --> D[Adaptive Context Collector]
    D --> E[RAG Engine - Community Knowledge Base]
    E --> F[Open-Source LLM Serving Pipeline]
    F --> G[Safety & Secret Checker]
    G --> H[Structured OOPSIE Report UI]
    H --> I[Copy Repair Prompt to AI Assistant]
```

## Core Components
1. **Input Parser (`/rules/secret-redaction-patterns.json`)**: Redacts credentials (JWTs, DB passwords, API keys) prior to prompt evaluation.
2. **Error Classifier (`/rules/classifiers.json`)**: Categorizes errors into dependency, env vars, database, build, deployment, or runtime.
3. **Knowledge Base RAG (`/knowledge-base/`)**: Matches error signatures against community-curated markdown recipes.
4. **Open-Source LLM Inference**: Formats prompts using Hugging Face endpoints, Ollama, or vLLM running open-weight coding models (Qwen-Coder, DeepSeek-Coder, StarCoder).
5. **Safety Guardrails**: Prevents destructive schema drops or unauthenticated exposures.
