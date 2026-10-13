# Inference API

Run the API from the repository root with `uvicorn inference.api.main:app --host 127.0.0.1 --port 8000` after installing `.[api]` and setting `OOPSIE_MODEL_PATH` to a compatible local model or merged checkpoint directory. The `POST /api/analyze` request is `{"error_text":"..."}`; successful responses conform to `data/schema.json`.

The API is intended for local development. If deploying it remotely, add authentication, quotas, HTTPS, abuse protections, and documented input retention. Do not expose an unauthenticated model endpoint by default.
