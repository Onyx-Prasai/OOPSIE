# Web demo guide

The React/Vite demo is at `apps/web-demo/`. It accepts a pasted error and sends it to `POST /api/analyze`. The demo displays an error if no inference API is available; it does not fabricate a model report.

Run the app and API separately:

```powershell
npm install
npm run dev
```

See the [demo modes guide](demo-modes-guide.md). By default, the UI uses local rule-based classification and the indexed community knowledge base; it does not require a running inference API. For a separately hosted API, set `VITE_OOPSIE_API_URL` to the absolute `/api/analyze` URL before building and set the API's `OOPSIE_CORS_ORIGINS` to the exact web-demo origin. Configure HTTPS as appropriate; never place private inference credentials in browser variables.

The browser applies best-effort redaction before either local analysis or sending to a configured endpoint. The demo warns users when known secret patterns match. No output should be described as coming from a fine-tuned OOPSIE checkpoint unless the configured service is actually using that checkpoint and its provenance has been verified.

Vercel builds the static demo from the repository root using `npm run build` and serves `apps/web-demo/dist`. A hosted Python inference service is deployed separately.
