import { useState, type FormEvent } from 'react';
import { analyzeWithRules, redactInput, type AnalysisReport } from './ruleAnalysis';

const API_URL = import.meta.env.VITE_OOPSIE_API_URL;
const modelEndpointConfigured = Boolean(API_URL?.trim());

export function App() {
  const [errorText, setErrorText] = useState('');
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [copied, setCopied] = useState(false);
  const [secretDetected, setSecretDetected] = useState(false);

  async function analyzeError(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!errorText.trim() || busy) return;

    setBusy(true);
    setReport(null);
    setMessage('');
    const { text: cleanedError, detectedSecret } = redactInput(errorText);
    setSecretDetected(detectedSecret);
    try {
      if (!modelEndpointConfigured) {
        const ruleReport = analyzeWithRules(cleanedError);
        if (detectedSecret) {
          ruleReport.warnings.push('Secret-like text was detected and recognized patterns were redacted before analysis; review manually because redaction is not guaranteed.');
        }
        setReport(ruleReport);
      } else {
        const response = await fetch(API_URL!, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ error_text: cleanedError }),
        });
        if (!response.ok) {
          const detail = await response.text();
          throw new Error(detail || `Inference API returned HTTP ${response.status}.`);
        }
        const result: unknown = await response.json();
        if (!isOopsieReport(result)) throw new Error('Inference API returned a report with an unexpected format.');
        const modelReport = { ...result, detected_framework: analyzeWithRules(cleanedError).detected_framework };
        if (detectedSecret) {
          modelReport.warnings.push('Secret-like text was detected and recognized patterns were redacted in the browser before submission; review manually because redaction is not guaranteed.');
        }
        setReport(modelReport);
      }
    } catch (error) {
      setMessage(
        `Could not reach the configured OOPSIE inference API. Verify VITE_OOPSIE_API_URL and the endpoint status. ${
          error instanceof Error ? error.message : String(error)
        }`,
      );
    } finally {
      setBusy(false);
    }
  }

  async function copyPrompt() {
    if (!report) return;
    try {
      await navigator.clipboard.writeText(report.repair_prompt);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch (error) {
      setMessage(`Could not copy the prompt: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  return (
    <div className="min-h-screen bg-[#101114] text-slate-100">
      <header className="border-b border-white/10">
        <nav className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4" aria-label="Main navigation">
          <a className="text-xl font-black tracking-tight text-amber-300" href="#home">OOPSIE</a>
          <div className="flex flex-wrap gap-4 text-sm text-slate-300">
            <a className="hover:text-amber-300" href="#demo">Demo</a>
            <a className="hover:text-amber-300" href="#model">Model</a>
            <a className="hover:text-amber-300" href="#dataset">Dataset</a>
            <a className="hover:text-amber-300" href="#community">Community</a>
            <a className="hover:text-amber-300" href="https://github.com/Onyx-Prasai/OOPSIE">GitHub</a>
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
            <div className="mb-6 rounded-xl border border-amber-300/30 bg-amber-300/10 p-4 text-sm text-amber-100" role="status">
              {modelEndpointConfigured
                ? 'Model endpoint mode: requests use the configured inference endpoint. Its checkpoint and fine-tuning status are not verified by this demo.'
                : 'Demo mode: OOPSIE is using rule-based classification and community knowledge-base retrieval. No fine-tuned model checkpoint is currently available.'}
            </div>
            <div className="mb-6">
              <p className="text-sm font-bold uppercase tracking-widest text-amber-300">Interactive demo</p>
              <h2 className="mt-2 text-3xl font-bold">Paste an error. Get an OOPSIE analysis.</h2>
              <p className="mt-3 text-slate-300">
                Recognized secrets are redacted in your browser before analysis or submission. Redaction is best-effort; inspect logs before continuing.
              </p>
            </div>
            <form className="space-y-4" onSubmit={analyzeError}>
              <label className="sr-only" htmlFor="error-input">Error message or log</label>
              <textarea
                id="error-input"
                className="min-h-48 w-full rounded-xl border border-white/15 bg-[#17191e] p-4 font-mono text-sm text-slate-100 outline-none focus:border-amber-300"
                placeholder={'Paste an error message, stack trace, build log, or deployment output…'}
                value={errorText}
                onChange={event => {
                  setErrorText(event.target.value);
                  setSecretDetected(redactInput(event.target.value).detectedSecret);
                }}
                required
              />
              {secretDetected && (
                <p className="rounded-lg border border-rose-400/30 bg-rose-950/30 p-3 text-sm text-rose-200" role="alert">
                  This text may contain a secret. OOPSIE will redact recognized patterns, but redaction is not guaranteed. Review the text before sending it to any external model.
                </p>
              )}
              <button
                className="rounded-xl bg-amber-300 px-5 py-3 font-bold text-slate-950 disabled:cursor-not-allowed disabled:opacity-50"
                type="submit"
                disabled={busy || !errorText.trim()}
              >
                {busy ? 'Analyzing…' : 'Analyze error'}
              </button>
            </form>
            {message && <p className="mt-5 rounded-lg border border-rose-400/30 bg-rose-950/30 p-4 text-sm text-rose-200" role="alert">{message}</p>}
            {report && (
              <article className="mt-8 space-y-6 rounded-2xl border border-white/10 bg-[#17191e] p-5 sm:p-7" aria-live="polite">
                <div>
                  <p className="text-sm text-slate-400">{report.detected_framework} framework hint · {report.error_category} · {report.risk_level} risk</p>
                  <h3 className="mt-1 text-2xl font-bold">{report.summary}</h3>
                  <p className="mt-3 leading-7 text-slate-300">{report.plain_explanation}</p>
                </div>
                <ReportList title="Likely causes" items={report.likely_causes.map(cause => `${cause.description} (${cause.confidence} confidence)`)} />
                <ReportList title="Questions to clarify" items={report.missing_context_questions} />
                <ReportList title="Safety warnings" items={report.warnings} />
                <section>
                  <h4 className="font-bold text-amber-200">Suggested repair prompt</h4>
                  <pre className="mt-2 whitespace-pre-wrap break-words rounded-lg bg-black/30 p-4 text-sm text-slate-200">{report.repair_prompt}</pre>
                  <button className="mt-3 rounded-lg border border-amber-300/40 px-4 py-2 text-sm font-semibold hover:bg-amber-300/10" onClick={copyPrompt} type="button">
                    {copied ? 'Copied' : 'Copy repair prompt'}
                  </button>
                </section>
                <ReportList title="Verify after applying changes" items={report.verification_steps} />
                <ReportList
                  title="Community knowledge-base context"
                  items={report.matched_recipes.length
                    ? report.matched_recipes.map(recipe => `${recipe.title} (${recipe.path ?? recipe.id})`)
                    : ['No closely matching community recipe was found.']}
                />
                <p className="border-t border-white/10 pt-4 text-sm text-slate-400">
                  OOPSIE does not guarantee a fix, security, or production readiness. Review all advice and verify changes yourself.
                </p>
              </article>
            )}
          </div>
        </section>

        <section id="model" className="mx-auto grid max-w-6xl gap-5 px-5 py-16 md:grid-cols-2">
          <InfoCard title="The model" text="OOPSIE is designed to be fine-tuned from an open-weight coding model. The base checkpoint, training method, license review, and results will be documented when verified; no fine-tuned release is implied by this development demo." />
          <InfoCard title="The dataset" text="An open, anonymized error-recovery dataset will teach the model to explain likely causes, ask for missing context, surface risks, and suggest focused repair prompts." />
          <InfoCard title="Retrieval-augmented recipes" text="Community-reviewed recipes in the knowledge base can be retrieved as supporting context. Recipes are helpful references, not guaranteed or authoritative fixes." />
          <InfoCard title="Safety first" text="The inference service redacts common secrets before model processing. OOPSIE does not execute commands, modify code, or deploy. Database, authentication, payment, and production changes need careful human review." />
        </section>

        <section id="dataset" className="border-y border-white/10 bg-white/[0.03] px-5 py-14 text-center">
          <h2 className="text-3xl font-bold">Build a better error-recovery dataset</h2>
          <p className="mx-auto mt-4 max-w-2xl leading-7 text-slate-300">
            Contributors add synthetic or permissioned, anonymized JSONL examples and separate evaluation cases.
            Never submit credentials, private logs, or identifying user information.
          </p>
          <a className="mt-5 inline-block font-semibold text-amber-300 underline" href="https://github.com/Onyx-Prasai/OOPSIE/blob/main/docs/dataset-guide.md">
            Read the dataset guide
          </a>
        </section>

        <section id="community" className="mx-auto max-w-5xl px-5 py-16 text-center">
          <p className="text-sm font-bold uppercase tracking-widest text-amber-300">Community-powered</p>
          <h2 className="mt-3 text-3xl font-bold">Help make error recovery more useful.</h2>
          <p className="mx-auto mt-4 max-w-2xl leading-7 text-slate-300">
            Add verified framework recipes, anonymized examples, benchmark cases, prompt improvements, documentation, and translations.
            The optional VS Code extension is a later interface—not the core product.
          </p>
          <div className="mt-7 flex flex-wrap justify-center gap-3">
            <a className="rounded-xl bg-amber-300 px-5 py-3 font-bold text-slate-950" href="https://github.com/Onyx-Prasai/OOPSIE/blob/main/CONTRIBUTING.md">Contribute</a>
            <a className="rounded-xl border border-white/20 px-5 py-3 font-semibold" href="https://github.com/Onyx-Prasai/OOPSIE/blob/main/ROADMAP.md">View roadmap</a>
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
          {items.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}
        </ul>
      ) : <p className="mt-2 text-sm text-slate-400">None identified.</p>}
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

type ApiReport = Omit<AnalysisReport, 'detected_framework'>;

function isOopsieReport(value: unknown): value is ApiReport {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
  const report = value as Record<string, unknown>;
  return typeof report.summary === 'string' &&
    typeof report.plain_explanation === 'string' &&
    typeof report.error_category === 'string' &&
    Array.isArray(report.likely_causes) &&
    report.likely_causes.every(isCause) &&
    isStringArray(report.missing_context_questions) &&
    ['low', 'medium', 'high'].includes(String(report.risk_level)) &&
    isStringArray(report.warnings) &&
    typeof report.repair_prompt === 'string' &&
    isStringArray(report.verification_steps) &&
    Array.isArray(report.matched_recipes) &&
    report.matched_recipes.every(isRecipe);
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every(item => typeof item === 'string');
}

function isCause(value: unknown): value is AnalysisReport['likely_causes'][number] {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
  const cause = value as Record<string, unknown>;
  return typeof cause.description === 'string' &&
    ['low', 'medium', 'high'].includes(String(cause.confidence));
}

function isRecipe(value: unknown): value is AnalysisReport['matched_recipes'][number] {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
  const recipe = value as Record<string, unknown>;
  return typeof recipe.id === 'string' && typeof recipe.title === 'string' &&
    (recipe.path === undefined || typeof recipe.path === 'string');
}
