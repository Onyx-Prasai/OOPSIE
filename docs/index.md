# OOPSIE: Open-source AI error recovery

## The problem

Vibe coders often build with AI assistants and get stuck when the app breaks. Stack traces, build output, and deployment logs are technical, noisy, and difficult to turn into a useful follow-up request.

## The solution

OOPSIE is an open-source AI error-recovery model project. Given an error or log, it aims to explain the issue in plain language, list likely causes, ask for missing context, surface risk warnings, and prepare a safe, focused repair prompt with verification steps.

OOPSIE is advisory. It does not automatically edit code, run commands, or deploy apps, and it does not guarantee fixes, security, or production readiness.

## The model

The project plans to fine-tune a suitable open-weight coding model. The base model, its license, training method, and results must be recorded in the [model guide](model-guide.md) and [model card](../inference/model-card.md) once verified. Until then, treat model training and release as work in progress.

## The dataset

The initial open synthetic dataset contains 100 examples across train, validation, and test splits. Read the [dataset guide](dataset-guide.md) before contributing JSONL examples. Never submit credentials, personal information, private logs, or proprietary code.

## The demo

The [web demo](demo-modes-guide.md) defaults to clearly labeled rule-based classification and community recipe retrieval. A configured inference endpoint is a separate mode; its fine-tuning and checkpoint status are not asserted.

## The community

Contributors can add verified error recipes and evaluation examples, improve prompts, help the web demo, and update documentation and translations. Relevant community recipes are retrieved as context to help inform an answer; they are not guaranteed to be correct.

Read the [architecture](architecture.md) and [benchmark guide](benchmark-guide.md). The separate 40-case benchmark has not been run against a fine-tuned checkpoint, and no results are available. Start with [CONTRIBUTING.md](../CONTRIBUTING.md), see the [four-phase roadmap](../ROADMAP.md), and review the [safety guide](safety-guide.md).
