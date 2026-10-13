# Web demo modes

The web demo provides two clearly distinguished modes.

## Rule + Knowledge Base mode

This is the default when `VITE_OOPSIE_API_URL` is not configured. It uses the repository's deterministic classifier signatures, browser-side secret-redaction patterns, and indexed community recipes. It can provide a useful starting point, but its classification and explanation are rule-based and limited to the matching rules. It is **not** a fine-tuned model.

The demo displays this banner:

> Demo mode: OOPSIE is using rule-based classification and community knowledge-base retrieval. No fine-tuned model checkpoint is currently available.

When no recipe is a close match, the demo says so explicitly.

## Model endpoint mode

Set `VITE_OOPSIE_API_URL` to an `/api/analyze` endpoint at build time to enable this mode. The endpoint's model identity, checkpoint provenance, and fine-tuning status are not verified by the web app. An unavailable or invalid endpoint results in a visible error; the app does not fall back to a success-shaped mock response.

The browser redacts recognized secret patterns before either local analysis or sending input to an endpoint. Redaction is best-effort. A visible warning appears when a recognized secret-like pattern is detected. Review logs yourself before using any hosted service.

Both modes are advisory: neither edits files, runs commands, deploys applications, nor guarantees a fix. Review suggestions and verify changes in a safe environment.
