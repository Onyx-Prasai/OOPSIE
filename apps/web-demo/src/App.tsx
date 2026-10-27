import { useState, useRef, type FormEvent } from 'react';
import { analyzeWithRules, redactInput } from './ruleAnalysis';
import {
  analyzeErrorWithApi,
  getApiEndpointUrl,
  OopsieApiError,
  type OopsieReport,
  type OopsieApiMetadata,
} from './api/oopsieClient';

export function App() {
  const [errorText, setErrorText] = useState('');
  const [report, setReport] = useState<OopsieReport | null>(null);
  const [metadata, setMetadata] = useState<OopsieApiMetadata | null>(null);
  const [sourceMode, setSourceMode] = useState<'model' | 'rule_demo' | null>(null);
  const [modelIdentity, setModelIdentity] = useState<{
    modelVersion?: string;
    formatterVersion?: string;
    requestId?: string;
  } | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [errorCode, setErrorCode] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [secretDetected, setSecretDetected] = useState(false);
  const [showMetadata, setShowMetadata] = useState(false);

  const abortControllerRef = useRef<AbortController | null>(null);
  const configuredEndpoint = getApiEndpointUrl();
  const isModelMode = Boolean(configuredEndpoint);

  async function analyzeError(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!errorText.trim() || busy) return;

    setBusy(true);
    setReport(null);
    setMetadata(null);
    setSourceMode(null);
    setModelIdentity(null);
    setMessage('');
    setErrorCode(null);

    const { text: cleanedError, detectedSecret } = redactInput(errorText);
    setSecretDetected(detectedSecret);

    if (isModelMode) {
      // 1. Live Model Mode (Strictly calls backend /v1/analyze, NO silent mock fallback)
      const controller = new AbortController();
      abortControllerRef.current = controller;

      try {
        const envelope = await analyzeErrorWithApi(cleanedError, {
          signal: controller.signal,
          systemPromptVersion: 'system_prompt_v2_enum_guided',
        });

        const reportData = { ...envelope.data };
        if (detectedSecret) {
          reportData.warnings = [
            'Secret-like text was detected and recognized patterns were redacted in the browser before submission; review manually because redaction is not guaranteed.',
            ...reportData.warnings,
          ];
        }

        setReport(reportData);
        setMetadata(envelope.metadata);
        setModelIdentity({
          modelVersion: envelope.model_version,
          formatterVersion: envelope.formatter_version,
          requestId: envelope.request_id,
        });
        setSourceMode('model');
      } catch (err: unknown) {
        if (err instanceof OopsieApiError) {
          setErrorCode(err.code);
          setMessage(err.message);
        } else {
          const msg = err instanceof Error ? err.message : String(err);
          setErrorCode('UNEXPECTED_ERROR');
          setMessage(`An unexpected error occurred while analyzing the error: ${msg}`);
        }
      } finally {
        setBusy(false);
        abortControllerRef.current = null;
      }
    } else {
      // 2. Offline Demo Mode (Explicitly uses local rule-based classifier + knowledge-base)
      try {
        const ruleReport = analyzeWithRules(cleanedError);
        if (detectedSecret) {
          ruleReport.warnings = [
            'Secret-like text was detected and recognized patterns were redacted before analysis; review manually because redaction is not guaranteed.',
            ...ruleReport.warnings,
          ];
        }

        setReport(ruleReport);
        setSourceMode('rule_demo');
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        setErrorCode('RULE_ANALYSIS_ERROR');
        setMessage(`Rule-based analysis failed: ${msg}`);
      } finally {
        setBusy(false);
      }
    }
  }

  function handleCancelRequest() {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setBusy(false);
      setMessage(
        'Request cancelled in browser. Note: cancelling the browser connection does not stop background GPU computation on the backend once admitted.'
      );
      setErrorCode('REQUEST_ABORTED');
    }
  }

  async function copyPrompt() {
    if (!report) return;
    try {
      await navigator.clipboard.writeText(report.repair_prompt);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setMessage(`Could not copy the prompt: ${msg}`);
    }
  }

  return (
    <div className="min-h-screen bg-[#101114] text-slate-100">
      <header className="border-b border-white/10">
        <nav className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4" aria-label="Main navigation">
          <a className="text-xl font-black tracking-tight text-amber-300" href="#home">
            OOPSIE
          </a>
          <div className="flex flex-wrap gap-4 text-sm text-slate-300">
            <a className="hover:text-amber-300" href="#demo">Demo</a>
            <a className="hover:text-amber-300" href="#model">Model</a>
            <a className="hover:text-amber-300" href="#dataset">Dataset</a>
            <a className="hover:text-amber-300" href="#community">Community</a>
            <a className="hover:text-amber-300" href="https://github.com/Onyx-Prasai/OOPSIE" target="_blank" rel="noreferrer">
              GitHub
            </a>
          </div>
        </nav>
      </header>

      <main id="home">
        <section className="mx-auto max-w-5xl px-5 py-20 text-center sm:py-28">
          <p className="mb-5 text-sm font-bold uppercase tracking-[0.2em] text-amber-300">
            Open-source AI error recovery model
          </p>
          <h1 className="text-4xl font-black leading-tight sm:text-6xl">
            When your AI-built app breaks, <span className="text-amber-300">get clarity.</span>
          </h1>
          <p className="mx-auto mt-6 max-w-3xl text-lg leading-8 text-slate-300">
            Vibe coders can get stuck when generated apps fail. OOPSIE is being built to explain coding errors,
            stack traces, and deployment logs—and prepare a focused repair prompt for the AI coding tool you use.
          </p>
          <a className="mt-8 inline-flex rounded-xl bg-amber-300 px-6 py-3 font-bold text-slate-950 hover:bg-amber-200" href="#demo">
            Try the demo
          </a>
          <p className="mx-auto mt-5 max-w-2xl text-sm text-slate-400">
            OOPSIE offers suggestions, not guaranteed fixes. It does not automatically edit code, execute commands,
            or deploy applications.
          </p>
        </section>

        <section id="demo" className="border-y border-white/10 bg-white/[0.03] px-5 py-16">
          <div className="mx-auto max-w-4xl">
            {/* Operational Mode Transparency Banner */}
            <div
              className={`mb-6 rounded-xl border p-4 text-sm ${
                !isModelMode
                  ? 'border-amber-300/30 bg-amber-300/10 text-amber-100'
                  : metadata?.engine_mode === 'mock'
                  ? 'border-amber-400/40 bg-amber-950/20 text-amber-200'
                  : metadata?.engine_mode === 'real_model'
                  ? 'border-emerald-400/40 bg-emerald-950/20 text-emerald-200'
                  : 'border-blue-400/40 bg-blue-950/20 text-blue-200'
              }`}
              role="status"
            >
              {isModelMode ? (
                <div>
                  <div className="flex items-center gap-2 font-bold">
                    {metadata?.engine_mode === 'mock' ? (
                      <>
                        <span className="inline-block h-2.5 w-2.5 rounded-full bg-amber-400"></span>
                        <span className="text-amber-300">Local Mock Server Mode (Simulated Fixtures)</span>
                      </>
                    ) : metadata?.engine_mode === 'real_model' ? (
                      <>
                        <span className="inline-block h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                        <span className="text-emerald-300">Live GPU Inference Mode (Experimental Model)</span>
                      </>
                    ) : (
                      <>
                        <span className="inline-block h-2.5 w-2.5 rounded-full bg-blue-400"></span>
                        <span className="text-blue-300">Inference Service Configured</span>
                      </>
                    )}
                  </div>
                  <p className="mt-1 text-xs text-slate-300">
                    Connected to inference endpoint <code className="rounded bg-black/40 px-1 py-0.5 text-slate-200">{configuredEndpoint}</code>.
                    {metadata?.engine_mode === 'mock'
                      ? ' Backend is running with OOPSIE_USE_MOCK_ENGINE=1: responses are static test fixtures, not real AI evaluations.'
                      : metadata?.engine_mode === 'real_model'
                      ? ' Requests are processed by fine-tuned Gemma 4 12B IT pilot model running on a GPU backend.'
                      : ' Engine mode (mock vs. real GPU) will be identified from service metadata upon evaluation.'}
                  </p>
                </div>
              ) : (
                <div>
                  <div className="font-bold text-amber-300">Offline Demo Mode (Rule-Based Classification)</div>
                  <p className="mt-1 text-xs text-slate-300">
                    No backend inference endpoint is configured (<code className="rounded bg-black/40 px-1 py-0.5">VITE_OOPSIE_API_URL</code> is unset).
                    Running in-browser rule classification and community knowledge-base retrieval.
                  </p>
                </div>
              )}
            </div>

            <div className="mb-6">
              <p className="text-sm font-bold uppercase tracking-widest text-amber-300">Interactive demo</p>
              <h2 className="mt-2 text-3xl font-bold">Paste an error. Get an OOPSIE analysis.</h2>
              <p className="mt-3 text-slate-300 text-sm">
                <strong>Privacy Notice:</strong> Never submit credentials, private API keys, passwords, or sensitive production secrets.
                Recognized patterns are redacted in your browser before analysis or submission as a best-effort defense-in-depth measure, but manual review is always required.
              </p>
            </div>

            <form className="space-y-4" onSubmit={analyzeError}>
              <label className="sr-only" htmlFor="error-input">
                Error message or log
              </label>
              <textarea
                id="error-input"
                className="min-h-48 w-full rounded-xl border border-white/15 bg-[#17191e] p-4 font-mono text-sm text-slate-100 outline-none focus:border-amber-300"
                placeholder="Paste an error message, stack trace, build log, or deployment output…"
                value={errorText}
                onChange={event => {
                  setErrorText(event.target.value);
                  setSecretDetected(redactInput(event.target.value).detectedSecret);
                }}
                disabled={busy}
                required
              />

              {secretDetected && (
                <p className="rounded-lg border border-rose-400/30 bg-rose-950/30 p-3 text-sm text-rose-200" role="alert">
                  Potential secret pattern detected. Recognized secret values will be redacted prior to submission, but redaction is not guaranteed. Please review text carefully before submission.
                </p>
              )}

              <div className="flex flex-wrap items-center gap-3">
                <button
                  className="rounded-xl bg-amber-300 px-5 py-3 font-bold text-slate-950 disabled:cursor-not-allowed disabled:opacity-50 hover:bg-amber-200 transition-colors"
                  type="submit"
                  disabled={busy || !errorText.trim()}
                >
                  {busy ? 'Running analysis…' : 'Analyze error'}
                </button>

                {busy && isModelMode && (
                  <button
                    type="button"
                    onClick={handleCancelRequest}
                    className="rounded-xl border border-white/20 px-4 py-3 text-sm font-semibold text-slate-300 hover:bg-white/10"
                  >
                    Cancel request
                  </button>
                )}

                {busy && (
                  <span className="flex items-center gap-2 text-sm text-slate-400">
                    <span className="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-amber-300 border-t-transparent"></span>
                    Evaluating error with {isModelMode ? 'live model' : 'rule classifier'}…
                  </span>
                )}
              </div>
            </form>

            {/* Error Message Envelope Rendering */}
            {message && (
              <div className="mt-5 rounded-xl border border-rose-400/30 bg-rose-950/40 p-5 text-sm text-rose-200" role="alert">
                <div className="flex items-center gap-2 font-bold text-rose-300">
                  <span>Inference Failure</span>
                  {errorCode && (
                    <span className="rounded bg-rose-900/60 px-2 py-0.5 font-mono text-xs text-rose-200">
                      [{errorCode}]
                    </span>
                  )}
                </div>
                <p className="mt-2 leading-relaxed">{message}</p>
              </div>
            )}

            {/* Validated Analysis Report Output */}
            {report && (
              <article className="mt-8 space-y-6 rounded-2xl border border-white/10 bg-[#17191e] p-5 sm:p-7" aria-live="polite">
                {/* Mock Engine Warning Banner */}
                {metadata?.engine_mode === 'mock' && (
                  <div className="rounded-xl border border-amber-400/40 bg-amber-950/40 p-4 text-amber-200 text-sm" role="alert">
                    <div className="font-bold flex items-center gap-2 text-amber-300">
                      <span>⚠️ Mock demo — sample response, not AI diagnosis</span>
                    </div>
                    <p className="mt-1 text-xs text-amber-200/90 leading-relaxed">
                      This response is a static/sample test fixture returned by the local mock engine (<code>OOPSIE_USE_MOCK_ENGINE=1</code>).
                      It does not correspond to the submitted error and was not evaluated by an AI model.
                      Live model inference requires a running GPU backend with loaded weights.
                    </p>
                  </div>
                )}

                {/* Mode and Provenance Badge */}
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/10 pb-4">
                  <div className="flex items-center gap-2">
                    {sourceMode === 'model' ? (
                      metadata?.engine_mode === 'mock' ? (
                        <span className="rounded-full border border-amber-500/50 bg-amber-500/10 px-3 py-1 text-xs font-bold text-amber-400 uppercase tracking-wide">
                          Mock Test Fixture (Sample Response)
                        </span>
                      ) : (
                        <span className="rounded-full border border-emerald-400/50 bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-300 uppercase tracking-wide">
                          Live GPU Model Output (Experimental)
                        </span>
                      )
                    ) : (
                      <span className="rounded-full border border-slate-600 bg-slate-800 px-3 py-1 text-xs font-bold text-slate-300 uppercase tracking-wide">
                        Offline Rule-Based Analysis
                      </span>
                    )}
                    <span className="text-xs text-slate-400">
                      Category: <strong className="text-slate-200">{report.error_category}</strong>
                    </span>
                  </div>

                  <span
                    className={`rounded px-2.5 py-0.5 text-xs font-bold uppercase tracking-wider ${
                      report.risk_level === 'high'
                        ? 'border border-rose-400/30 bg-rose-950/50 text-rose-300'
                        : report.risk_level === 'medium'
                        ? 'border border-amber-400/30 bg-amber-950/50 text-amber-300'
                        : 'border border-emerald-400/30 bg-emerald-950/50 text-emerald-300'
                    }`}
                  >
                    {report.risk_level} Risk
                  </span>
                </div>

                <div>
                  <h3 className="text-2xl font-bold">{report.summary}</h3>
                  <p className="mt-3 leading-7 text-slate-300 whitespace-pre-wrap">{report.plain_explanation}</p>
                </div>

                <ReportList
                  title="Likely causes"
                  items={report.likely_causes.map(cause => `${cause.description} (${cause.confidence} confidence)`)}
                />

                <ReportList title="Questions to clarify" items={report.missing_context_questions} />

                {report.warnings.length > 0 && (
                  <section className="rounded-xl border border-amber-400/30 bg-amber-950/20 p-4">
                    <h4 className="font-bold text-amber-300">Safety warnings</h4>
                    <ul className="mt-2 list-disc space-y-1.5 pl-5 text-sm text-amber-200">
                      {report.warnings.map((warning, idx) => (
                        <li key={idx}>{warning}</li>
                      ))}
                    </ul>
                  </section>
                )}

                <section>
                  <h4 className="font-bold text-amber-200">Suggested repair prompt</h4>
                  <p className="mt-1 text-xs text-slate-400">
                    Copy and review this prompt before pasting it into your AI coding tool:
                  </p>
                  <pre className="mt-2 whitespace-pre-wrap break-words rounded-lg bg-black/40 p-4 font-mono text-sm text-slate-200 border border-white/10 select-all">
                    {report.repair_prompt}
                  </pre>
                  <button
                    className="mt-3 rounded-lg border border-amber-300/40 px-4 py-2 text-sm font-semibold hover:bg-amber-300/10 transition-colors"
                    onClick={copyPrompt}
                    type="button"
                  >
                    {copied ? 'Copied to clipboard!' : 'Copy repair prompt'}
                  </button>
                </section>

                <ReportList title="Verify after applying changes" items={report.verification_steps} />

                <ReportList
                  title="Community knowledge-base context"
                  items={
                    report.matched_recipes && report.matched_recipes.length
                      ? report.matched_recipes.map(recipe => `${recipe.title} (${recipe.path ?? recipe.id})`)
                      : ['No closely matching community recipe was found.']
                  }
                />

                {/* Technical Metadata Section */}
                <div className="border-t border-white/10 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowMetadata(!showMetadata)}
                    className="text-xs font-semibold text-slate-400 hover:text-slate-200 flex items-center gap-1.5"
                  >
                    <span>{showMetadata ? 'Hide technical metadata' : 'Show technical metadata'}</span>
                    <span>{showMetadata ? '▲' : '▼'}</span>
                  </button>

                  {showMetadata && (
                    <div className="mt-3 rounded-lg bg-black/30 p-3 font-mono text-xs text-slate-300 space-y-1 border border-white/5">
                      <div>
                        Execution Mode:{' '}
                        {sourceMode === 'model'
                          ? metadata?.engine_mode === 'mock'
                            ? 'Local Mock Engine (Simulated Fixture, No GPU)'
                            : 'Real GPU Inference Engine (Gemma 4 12B IT)'
                          : 'Client-side Rule Classifier (No Model)'}
                      </div>
                      {modelIdentity?.modelVersion && <div>Model Version: {modelIdentity.modelVersion}</div>}
                      {modelIdentity?.formatterVersion && <div>Formatter: {modelIdentity.formatterVersion}</div>}
                      {metadata?.system_prompt_version && <div>System Prompt: {metadata.system_prompt_version}</div>}
                      {modelIdentity?.requestId && <div>Request ID: {modelIdentity.requestId}</div>}
                      {metadata?.prompt_tokens !== undefined && (
                        <div>
                          {metadata?.engine_mode === 'mock' ? 'Simulated Tokens: ' : 'Measured Tokens: '}
                          {metadata.prompt_tokens} prompt / {metadata.generated_tokens} generated
                          {metadata?.engine_mode === 'mock' && ' (Fixture default)'}
                        </div>
                      )}
                      {metadata?.duration_ms !== undefined && (
                        <div>
                          {metadata?.engine_mode === 'mock' ? 'Simulated Mock Latency: ' : 'Measured GPU Latency: '}
                          {metadata.duration_ms} ms
                          {metadata?.engine_mode === 'mock' && ' (Non-GPU overhead)'}
                        </div>
                      )}
                      {metadata?.budget_hit !== undefined && <div>Hit Token Budget: {String(metadata.budget_hit)}</div>}
                    </div>
                  )}
                </div>

                <p className="border-t border-white/10 pt-4 text-xs text-slate-400">
                  <strong>Disclaimer:</strong> OOPSIE provides diagnostic suggestions based on observed error logs, not guaranteed fixes.
                  It does not execute shell commands, edit code, or deploy applications. Review and test all proposed changes in an isolated development environment.
                </p>
              </article>
            )}
          </div>
        </section>

        <section id="model" className="mx-auto grid max-w-6xl gap-5 px-5 py-16 md:grid-cols-2">
          <InfoCard
            title="The model"
            text="OOPSIE is fine-tuned from Google Gemma 4 12B IT using Low-Rank Adaptation (LoRA). The pilot adapter (oopsie-pilot-gemma4-12b-lora-c44) is designed to generate strict JSON conforming to data/schema.json with schema-derived enum guidance."
          />
          <InfoCard
            title="The dataset"
            text="An open, anonymized error-recovery dataset teaches the model to separate observed facts from likely causes, ask for missing context, identify security risks, and suggest focused repair prompts."
          />
          <InfoCard
            title="Retrieval-augmented recipes"
            text="Community-reviewed recipes in the knowledge base can be retrieved as supporting context. Recipes are helpful references, not guaranteed or authoritative fixes."
          />
          <InfoCard
            title="Safety first"
            text="The service redacts common secrets before model processing. OOPSIE does not execute commands, modify code, or deploy. Database, authentication, payment, and production changes need careful human review."
          />
        </section>

        <section id="dataset" className="border-y border-white/10 bg-white/[0.03] px-5 py-14 text-center">
          <h2 className="text-3xl font-bold">Build a better error-recovery dataset</h2>
          <p className="mx-auto mt-4 max-w-2xl leading-7 text-slate-300">
            Contributors add synthetic or permissioned, anonymized JSONL examples and separate evaluation cases.
            Never submit credentials, private logs, or identifying user information.
          </p>
          <a
            className="mt-5 inline-block font-semibold text-amber-300 underline"
            href="https://github.com/Onyx-Prasai/OOPSIE/blob/main/docs/dataset-guide.md"
            target="_blank"
            rel="noreferrer"
          >
            Read the dataset guide
          </a>
        </section>

        <section id="community" className="mx-auto max-w-5xl px-5 py-16 text-center">
          <p className="text-sm font-bold uppercase tracking-widest text-amber-300">Community-powered</p>
          <h2 className="mt-3 text-3xl font-bold">Help make error recovery more useful.</h2>
          <p className="mx-auto mt-4 max-w-2xl leading-7 text-slate-300">
            Add verified framework recipes, anonymized examples, benchmark cases, prompt improvements, documentation, and translations.
          </p>
          <div className="mt-7 flex flex-wrap justify-center gap-3">
            <a
              className="rounded-xl bg-amber-300 px-5 py-3 font-bold text-slate-950"
              href="https://github.com/Onyx-Prasai/OOPSIE/blob/main/CONTRIBUTING.md"
              target="_blank"
              rel="noreferrer"
            >
              Contribute
            </a>
            <a
              className="rounded-xl border border-white/20 px-5 py-3 font-semibold"
              href="https://github.com/Onyx-Prasai/OOPSIE/blob/main/ROADMAP.md"
              target="_blank"
              rel="noreferrer"
            >
              View roadmap
            </a>
          </div>
          <div className="mt-6 flex flex-wrap justify-center gap-x-5 gap-y-2 text-sm text-amber-300">
            <a className="underline" href="https://github.com/Onyx-Prasai/OOPSIE/blob/main/inference/model-card.md">Model card</a>
            <a className="underline" href="https://github.com/Onyx-Prasai/OOPSIE/blob/main/docs/evaluation-guide.md">Evaluation guide</a>
            <a className="underline" href="https://github.com/Onyx-Prasai/OOPSIE/blob/main/docs/safety-guide.md">Safety guide</a>
          </div>
        </section>
      </main>

      <footer className="border-t border-white/10 px-5 py-7 text-center text-sm text-slate-400">
        OOPSIE is open source under Apache-2.0. Model, data, and dependency licenses may differ.
      </footer>
    </div>
  );
}

export default App;

function ReportList({ title, items }: { title: string; items: string[] }) {
  return (
    <section>
      <h4 className="font-bold text-amber-200">{title}</h4>
      {items.length ? (
        <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-300">
          {items.map((item, index) => (
            <li key={`${index}-${item}`}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="mt-2 text-sm text-slate-400">None identified.</p>
      )}
    </section>
  );
}

function InfoCard({ title, text }: { title: string; text: string }) {
  return (
    <article className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
      <h3 className="text-xl font-bold text-amber-200">{title}</h3>
      <p className="mt-3 leading-7 text-slate-300">{text}</p>
    </article>
  );
}
