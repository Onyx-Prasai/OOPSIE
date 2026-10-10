import React, { useState } from 'react';
import { SAMPLE_ERRORS } from '../data/sampleErrors';
import type { SampleError } from '../data/sampleErrors';
import type { OopsieReport, RiskLevel } from '../types';
import { 
  Terminal, Sparkles, Copy, Check, AlertTriangle, ShieldAlert, 
  HelpCircle, RefreshCw, CheckCircle2, ThumbsUp, ThumbsDown
} from 'lucide-react';
import confetti from 'canvas-confetti';

interface InteractivePlaygroundProps {
  theme: 'dark' | 'light';
}

export const InteractivePlayground: React.FC<InteractivePlaygroundProps> = ({ theme }) => {
  const isDark = theme === 'dark';

  const [inputText, setInputText] = useState<string>(SAMPLE_ERRORS[0].rawLog);
  const [selectedFramework, setSelectedFramework] = useState<string>('auto');
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [pipelineStep, setPipelineStep] = useState<number>(0);
  const [report, setReport] = useState<OopsieReport | null>(SAMPLE_ERRORS[0].report);
  const [copied, setCopied] = useState<boolean>(false);
  const [feedback, setFeedback] = useState<'fixed' | 'not_fixed' | null>(null);

  const pipelineNames = [
    "1. Redacting Credentials & API Keys...",
    "2. Classifying Error Signature...",
    "3. Searching RAG Knowledge Base Recipes...",
    "4. Querying Open-Source LLM Model...",
    "5. Enforcing Safety & Minimal Diff Rules...",
    "6. Recovery Report Generated!"
  ];

  const handleSelectSample = (sample: SampleError) => {
    setInputText(sample.rawLog);
    setReport(sample.report);
    setFeedback(null);
  };

  const handleRunAnalysis = () => {
    if (!inputText.trim()) return;
    setIsAnalyzing(true);
    setPipelineStep(0);
    setFeedback(null);

    let step = 0;
    const interval = setInterval(() => {
      step++;
      setPipelineStep(step);
      if (step >= 5) {
        clearInterval(interval);
        setIsAnalyzing(false);

        const textLower = inputText.toLowerCase();
        let matchedSample = SAMPLE_ERRORS.find(s => textLower.includes(s.category.toLowerCase()) || textLower.includes(s.framework.toLowerCase()));
        
        if (textLower.includes("supabase")) {
          matchedSample = SAMPLE_ERRORS[0];
        } else if (textLower.includes("next_public") || textLower.includes("env")) {
          matchedSample = SAMPLE_ERRORS[1];
        } else if (textLower.includes("vercel") || textLower.includes("build")) {
          matchedSample = SAMPLE_ERRORS[2];
        } else if (textLower.includes("rls") || textLower.includes("security policy")) {
          matchedSample = SAMPLE_ERRORS[3];
        }

        if (matchedSample) {
          setReport(matchedSample.report);
        } else {
          setReport({
            id: `custom-${Date.now()}`,
            summary: "Detected custom application runtime failure",
            plain_english_explanation: "Your code encountered an unexpected error during execution. An imported function or service configuration returned an error state.",
            category: 'runtime',
            risk_level: 'medium',
            likely_causes: [
              {
                title: "Uncaught exception or invalid configuration",
                confidence: 'medium',
                description: "The parameter passed to the function or service was undefined or invalid."
              }
            ],
            follow_up_questions: [
              "Is this error happening locally or in deployment?",
              "Which specific file or line triggered this error?"
            ],
            repair_prompt: `My app encountered the following error:\n"${inputText.trim().substring(0, 200)}..."\n\nPlease inspect the error context, verify imports and configuration, and fix the issue. Make the smallest possible change and do not alter unrelated features or UI.`,
            verification_checklist: [
              "Run local build or dev server",
              "Check browser/terminal console for clear logs"
            ],
            safety_warnings: [
              "Verify secret keys are stored in environment variables, not code."
            ],
            timestamp: new Date().toISOString()
          });
        }
      }
    }, 400);
  };

  const handleCopyPrompt = () => {
    if (!report) return;
    navigator.clipboard.writeText(report.repair_prompt);
    setCopied(true);
    confetti({ particleCount: 35, spread: 40, origin: { y: 0.8 } });
    setTimeout(() => setCopied(false), 2000);
  };

  const getRiskBadge = (risk: RiskLevel) => {
    switch (risk) {
      case 'low':
        return (
          <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${
            isDark ? 'bg-[#1b261f] text-emerald-400 border-emerald-800' : 'bg-emerald-50 text-emerald-700 border-emerald-300'
          }`}>
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> Low Risk (Setup / Config)
          </span>
        );
      case 'medium':
        return (
          <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${
            isDark ? 'bg-[#292218] text-amber-400 border-amber-800' : 'bg-amber-50 text-amber-800 border-amber-300'
          }`}>
            <AlertTriangle className="w-3.5 h-3.5 text-amber-500" /> Medium Risk (Secrets / Permissions)
          </span>
        );
      case 'high':
        return (
          <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${
            isDark ? 'bg-[#2b1a1a] text-rose-400 border-rose-800' : 'bg-rose-50 text-rose-800 border-rose-300'
          }`}>
            <ShieldAlert className="w-3.5 h-3.5 text-rose-500" /> High Risk (Data / DB Action)
          </span>
        );
    }
  };

  return (
    <section className={`py-8 px-4 lg:px-8 space-y-8 transition-colors duration-200 ${
      isDark ? 'bg-[#171717] text-white' : 'bg-[#fffdf0] text-slate-900'
    }`}>
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header section */}
        <div className={`flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4 ${
          isDark ? 'border-[#2d2d2d]' : 'border-yellow-200'
        }`}>
          <div>
            <h2 className={`text-xl font-bold flex items-center gap-2 ${
              isDark ? 'text-white' : 'text-slate-900'
            }`}>
              <Terminal className={`w-5 h-5 ${isDark ? 'text-amber-400' : 'text-amber-600'}`} />
              <span>Error Recovery Engine</span>
            </h2>
            <p className={`text-xs mt-1 ${isDark ? 'text-[#a3a3a3]' : 'text-slate-600 font-medium'}`}>
              Paste any stack trace, build log, or console output below to simulate OOPSIE’s recovery pipeline.
            </p>
          </div>

          {/* Quick sample error buttons */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className={`text-xs font-semibold mr-1 ${isDark ? 'text-[#a3a3a3]' : 'text-amber-950'}`}>Samples:</span>
            {SAMPLE_ERRORS.map((s) => (
              <button
                key={s.id}
                onClick={() => handleSelectSample(s)}
                className={`text-xs px-2.5 py-1 rounded-lg font-semibold border transition ${
                  isDark
                    ? 'bg-[#242424] hover:bg-[#2c2c2c] text-white border-[#383838]'
                    : 'bg-white hover:bg-yellow-50 text-slate-900 border-amber-300 shadow-sm'
                }`}
              >
                {s.title}
              </button>
            ))}
          </div>
        </div>

        {/* Main input & selector card */}
        <div className={`border rounded-2xl p-5 space-y-4 shadow-sm ${
          isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-amber-200'
        }`}>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <label className={`text-xs font-bold uppercase tracking-wider flex items-center gap-2 ${
              isDark ? 'text-[#d4d4d4]' : 'text-slate-700'
            }`}>
              <span>Paste Error / Stack Trace / Build Log</span>
              <span className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold border ${
                isDark ? 'bg-[#2a2a2a] text-[#a3a3a3] border-[#383838]' : 'bg-amber-100 text-amber-900 border-amber-300'
              }`}>
                Auto Secret Redactor Active
              </span>
            </label>

            <div className="flex items-center gap-2">
              <span className={`text-xs font-semibold ${isDark ? 'text-[#a3a3a3]' : 'text-slate-600'}`}>Framework:</span>
              <select
                value={selectedFramework}
                onChange={(e) => setSelectedFramework(e.target.value)}
                className={`border rounded-lg text-xs font-semibold px-3 py-1.5 focus:outline-none ${
                  isDark
                    ? 'bg-[#181818] border-[#383838] text-white focus:border-amber-400'
                    : 'bg-yellow-50 border-amber-300 text-slate-900 focus:border-amber-500'
                }`}
              >
                <option value="auto">⚡ Auto-Detect</option>
                <option value="react">React / Next.js</option>
                <option value="supabase">Supabase</option>
                <option value="vercel">Vercel</option>
                <option value="firebase">Firebase</option>
                <option value="node">Node.js / npm</option>
                <option value="python">Python / FastAPI</option>
              </select>
            </div>
          </div>

          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            rows={5}
            placeholder="Paste your error message, build log, or terminal output here..."
            className={`w-full border rounded-xl p-4 font-mono text-xs focus:outline-none transition resize-y ${
              isDark
                ? 'bg-[#181818] border-[#2e2e2e] text-[#f5f5f5] focus:border-amber-400'
                : 'bg-[#fffbeb] border-amber-200 text-slate-900 focus:border-amber-500'
            }`}
          />

          <div className="flex items-center justify-between">
            <span className={`text-xs font-mono ${isDark ? 'text-[#a3a3a3]' : 'text-slate-600 font-medium'}`}>
              {inputText.length} characters parsed
            </span>

            <button
              onClick={handleRunAnalysis}
              disabled={isAnalyzing || !inputText.trim()}
              className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-xs transition border disabled:opacity-50 ${
                isDark
                  ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 border-amber-400'
                  : 'bg-amber-400 hover:bg-amber-300 text-slate-950 border-amber-300 shadow-md shadow-amber-300/50'
              }`}
            >
              {isAnalyzing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Processing Pipeline...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Analyze Chaos & Generate Report</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* AI Pipeline Loading Indicator */}
        {isAnalyzing && (
          <div className={`border rounded-2xl p-6 text-center space-y-3 animate-pulse ${
            isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-amber-300 shadow-sm'
          }`}>
            <div className="flex justify-center items-center gap-2">
              <RefreshCw className={`w-5 h-5 animate-spin ${isDark ? 'text-amber-400' : 'text-amber-600'}`} />
              <h3 className={`text-base font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>Processing OOPSIE Recovery Pipeline</h3>
            </div>
            <div className={`text-xs font-mono font-semibold ${isDark ? 'text-[#a3a3a3]' : 'text-amber-900'}`}>
              {pipelineNames[pipelineStep] || "Formatting report..."}
            </div>
            <div className={`w-full h-2 rounded-full overflow-hidden max-w-xs mx-auto mt-2 ${
              isDark ? 'bg-[#181818]' : 'bg-amber-100'
            }`}>
              <div
                className="h-full bg-amber-500 transition-all duration-300"
                style={{ width: `${((pipelineStep + 1) / 6) * 100}%` }}
              />
            </div>
          </div>
        )}

        {/* OOPSIE Report Display */}
        {report && !isAnalyzing && (
          <div className="space-y-6">
            <div className={`flex items-center justify-between border-b pb-3 ${
              isDark ? 'border-[#2d2d2d]' : 'border-yellow-200'
            }`}>
              <h3 className={`text-lg font-bold flex items-center gap-2 ${
                isDark ? 'text-white' : 'text-slate-900'
              }`}>
                <span>⚡ OOPSIE Recovery Report</span>
                <span className={`text-xs font-mono font-normal ${isDark ? 'text-[#a3a3a3]' : 'text-slate-500'}`}>
                  [{report.id}]
                </span>
              </h3>

              {getRiskBadge(report.risk_level)}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              
              {/* Card 1: Plain English Explanation */}
              <div className={`border rounded-2xl p-5 space-y-3 shadow-sm ${
                isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-amber-200'
              }`}>
                <h4 className={`text-xs font-bold uppercase tracking-wider ${
                  isDark ? 'text-amber-400' : 'text-amber-800'
                }`}>
                  💡 What Happened (In Plain English)
                </h4>
                <p className={`text-sm leading-relaxed font-medium ${
                  isDark ? 'text-[#e5e5e5]' : 'text-slate-800'
                }`}>
                  {report.plain_english_explanation}
                </p>
                <div className={`p-2.5 rounded-xl border text-xs font-mono font-bold ${
                  isDark ? 'bg-[#181818] border-[#2d2d2d] text-[#d4d4d4]' : 'bg-yellow-50 border-amber-200 text-slate-900'
                }`}>
                  Category: <strong className={isDark ? 'text-amber-400 uppercase' : 'text-amber-700 uppercase'}>{report.category}</strong>
                </div>
              </div>

              {/* Card 2: Likely Causes */}
              <div className={`border rounded-2xl p-5 space-y-3 shadow-sm ${
                isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-amber-200'
              }`}>
                <h4 className={`text-xs font-bold uppercase tracking-wider ${
                  isDark ? 'text-amber-400' : 'text-amber-800'
                }`}>
                  🔍 Likely Root Cause
                </h4>
                <div className="space-y-2">
                  {report.likely_causes.map((cause, idx) => (
                    <div key={idx} className={`p-3 rounded-xl border space-y-1 ${
                      isDark ? 'bg-[#181818] border-[#2d2d2d]' : 'bg-yellow-50/60 border-amber-200'
                    }`}>
                      <div className={`flex items-center justify-between text-xs font-bold ${
                        isDark ? 'text-white' : 'text-slate-900'
                      }`}>
                        <span>{cause.title}</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded font-mono ${
                          isDark ? 'bg-[#282828] text-[#a3a3a3]' : 'bg-amber-200 text-amber-950 font-bold'
                        }`}>
                          {cause.confidence} confidence
                        </span>
                      </div>
                      <p className={`text-xs leading-relaxed ${isDark ? 'text-[#a3a3a3]' : 'text-slate-600 font-medium'}`}>{cause.description}</p>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* Safety Warnings Banner if any */}
            {report.safety_warnings.length > 0 && (
              <div className={`border rounded-2xl p-4 flex items-start gap-3 ${
                isDark ? 'bg-[#292218] border-amber-800' : 'bg-amber-50 border-amber-300'
              }`}>
                <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                <div>
                  <h5 className="text-xs font-bold text-amber-500 uppercase tracking-wider">Safety Advisory</h5>
                  <ul className={`text-xs list-disc list-inside mt-1 space-y-0.5 font-medium ${
                    isDark ? 'text-amber-200' : 'text-amber-900'
                  }`}>
                    {report.safety_warnings.map((w, i) => (
                      <li key={i}>{w}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Card 3: AI Repair Prompt Card */}
            <div className={`border rounded-2xl p-6 space-y-4 shadow-sm ${
              isDark ? 'bg-[#212121] border-[#333333]' : 'bg-white border-amber-200'
            }`}>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <h4 className={`text-sm font-bold flex items-center gap-2 ${
                    isDark ? 'text-white' : 'text-slate-900'
                  }`}>
                    <Sparkles className={`w-4 h-4 ${isDark ? 'text-amber-400' : 'text-amber-600'}`} />
                    <span>Copy-Ready AI Repair Prompt</span>
                  </h4>
                  <p className={`text-xs ${isDark ? 'text-[#a3a3a3]' : 'text-slate-600 font-medium'}`}>
                    Paste this exact prompt into Cursor, Claude, ChatGPT, Lovable, or Replit.
                  </p>
                </div>

                <button
                  onClick={handleCopyPrompt}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl font-bold text-xs transition border ${
                    isDark
                      ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 border-amber-400'
                      : 'bg-amber-400 hover:bg-amber-300 text-slate-950 border-amber-300 shadow-md shadow-amber-300/50'
                  }`}
                >
                  {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  <span>{copied ? 'Copied Prompt!' : 'Copy Repair Prompt'}</span>
                </button>
              </div>

              {/* CHEESY LIGHT CODE BOX: Warm light background #fffbeb with dark text #171717! */}
              <div className={`border rounded-xl p-4 text-xs font-mono leading-relaxed whitespace-pre-wrap select-all font-semibold ${
                isDark 
                  ? 'bg-[#181818] border-[#2e2e2e] text-[#f5f5f5]' 
                  : 'bg-[#fffbeb] border-amber-200 text-slate-900'
              }`}>
                {report.repair_prompt}
              </div>
            </div>

            {/* Card 4: Verification Checklist & Context Questions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              
              <div className={`border rounded-2xl p-5 space-y-3 shadow-sm ${
                isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-amber-200'
              }`}>
                <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-500 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  <span>Verification Checklist After Fix</span>
                </h4>
                <ul className="space-y-2 text-xs font-medium">
                  {report.verification_checklist.map((item, i) => (
                    <li key={i} className={`flex items-center gap-2 p-2 rounded-lg border ${
                      isDark ? 'bg-[#181818] border-[#2d2d2d] text-[#e5e5e5]' : 'bg-emerald-50/50 border-emerald-200 text-slate-800'
                    }`}>
                      <span className="text-emerald-500 font-bold">✓</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className={`border rounded-2xl p-5 space-y-3 shadow-sm ${
                isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-amber-200'
              }`}>
                <h4 className="text-xs font-bold uppercase tracking-wider text-sky-500 flex items-center gap-2">
                  <HelpCircle className="w-4 h-4 text-sky-500" />
                  <span>Adaptive Context Questions</span>
                </h4>
                <ul className="space-y-2 text-xs font-medium">
                  {report.follow_up_questions.map((q, i) => (
                    <li key={i} className={`flex items-start gap-2 p-2 rounded-lg border ${
                      isDark ? 'bg-[#181818] border-[#2d2d2d] text-[#e5e5e5]' : 'bg-sky-50/50 border-sky-200 text-slate-800'
                    }`}>
                      <span className="text-sky-500 font-bold">?</span>
                      <span>{q}</span>
                    </li>
                  ))}
                </ul>
              </div>

            </div>

            {/* Feedback section */}
            <div className={`border rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left ${
              isDark ? 'bg-[#181818] border-[#2e2e2e]' : 'bg-white border-amber-200 shadow-sm'
            }`}>
              <div>
                <div className={`text-xs font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>Did this OOPSIE report fix your error?</div>
                <div className={`text-xs ${isDark ? 'text-[#a3a3a3]' : 'text-slate-600 font-medium'}`}>Your feedback tunes our open-source error recipes.</div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setFeedback('fixed')}
                  className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-bold transition border ${
                    feedback === 'fixed'
                      ? 'bg-emerald-600 text-white border-emerald-600'
                      : isDark
                        ? 'bg-[#242424] hover:bg-[#2c2c2c] text-white border-[#383838]'
                        : 'bg-yellow-100 hover:bg-yellow-200 text-amber-950 border border-amber-300'
                  }`}
                >
                  <ThumbsUp className="w-3.5 h-3.5" />
                  <span>Fixed It</span>
                </button>

                <button
                  onClick={() => setFeedback('not_fixed')}
                  className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-bold transition border ${
                    feedback === 'not_fixed'
                      ? 'bg-rose-600 text-white border-rose-600'
                      : isDark
                        ? 'bg-[#242424] hover:bg-[#2c2c2c] text-white border-[#383838]'
                        : 'bg-yellow-100 hover:bg-yellow-200 text-amber-950 border border-amber-300'
                  }`}
                >
                  <ThumbsDown className="w-3.5 h-3.5" />
                  <span>Needs Context</span>
                </button>
              </div>
            </div>

          </div>
        )}

      </div>
    </section>
  );
};
