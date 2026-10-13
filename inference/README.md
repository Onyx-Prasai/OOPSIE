# Inference

The local API and CLI load a merged model directory selected with `OOPSIE_MODEL_PATH`. A fine-tuned checkpoint is not included in the repository; point this setting at a compatible local base-model or merged-checkpoint directory after reviewing its license.

Install the optional API dependencies and start the service bound to localhost:

```powershell
python -m pip install -e ".[api]"
$env:OOPSIE_MODEL_PATH = "C:\models\oopsie"
uvicorn inference.api.main:app --host 127.0.0.1 --port 8000
```

The service provides `GET /health` and `POST /api/analyze`. It redacts common secrets, retrieves matching community recipes, generates structured output, validates against `data/schema.json`, and adds deterministic safety warnings. Invalid model output returns an error rather than a success-shaped fallback. The default web demo does not require this service; it uses an explicitly labeled browser-side rule/knowledge-base mode. To select this endpoint mode, set `VITE_OOPSIE_API_URL` at web-demo build time. For a web demo hosted on another origin, set `OOPSIE_CORS_ORIGINS` to a comma-separated allowlist of exact origins; the default is no cross-origin access.

Use the CLI in another terminal:

```powershell
python -m inference.cli --file error.log
Get-Content error.log | python -m inference.cli
```

OOPSIE never executes commands, edits code, or deploys apps. Avoid exposing the API publicly without appropriate authentication, rate limits, input controls, HTTPS, and a clear data-retention policy. See [the safety guide](../docs/safety-guide.md).
