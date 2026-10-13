# Optional VS Code extension

The VS Code extension is an optional future interface, not OOPSIE's main product. Its current scaffold is under `apps/vscode-extension/` and is not required to prepare data, train, evaluate, or run the model API.

The extension sends requests to a user-configured OOPSIE inference API, explains when inference is unavailable, redacts sensitive content before transmission, and must never automatically edit code, execute commands, or deploy applications.

To compile the current scaffold, from its directory run `npm install` and `npm run compile`. Treat the extension and its provider wiring as development scaffolding until documented integration tests and a model-backed workflow exist.
