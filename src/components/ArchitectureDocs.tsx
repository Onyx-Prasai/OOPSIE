import React from 'react';
import { Cpu, ShieldCheck, Server } from 'lucide-react';

interface ArchitectureDocsProps {
  theme: 'dark' | 'light';
}

export const ArchitectureDocs: React.FC<ArchitectureDocsProps> = ({ theme }) => {
  const isDark = theme === 'dark';

  const pipelineStages = [
    {
      num: '01',
      title: 'Input Parser & Secret Redactor',
      desc: 'Parses raw terminal text, stack traces, and logs. Redacts JWT tokens, database passwords, and API secret keys prior to LLM evaluation.',
      tag: '/rules/secret-redaction-patterns.json'
    },
    {
      num: '02',
      title: 'Error Classifier & Signature Matcher',
      desc: 'Applies pattern regexes and AI classification rules to categorize error into dependency, env vars, database, deployment, or runtime.',
      tag: '/rules/classifiers.json'
    },
    {
      num: '03',
      title: 'Adaptive Context Collector',
      desc: 'Asks 1-2 targeted questions (e.g. Next.js App Router vs Pages Router, Vercel vs local) to narrow down ambiguous root causes.',
      tag: 'Adaptive Question Generator'
    },
    {
      num: '04',
      title: 'RAG Retrieval Engine',
      desc: 'Queries the open-source community knowledge base (.md recipes) to inject verified recovery instructions into model context.',
      tag: '/knowledge-base/'
    },
    {
      num: '05',
      title: 'Open-Source LLM Generation',
      desc: 'Infers structured JSON response using open-weight models (Qwen-Coder, DeepSeek-Coder, StarCoder) hosted via Ollama, Hugging Face, or vLLM.',
      tag: '/prompts/system-prompt.md'
    },
    {
      num: '06',
      title: 'Safety Layer & Repair Prompt Guard',
      desc: 'Enforces minimal diff guidelines: "Make smallest possible change. Do not redesign UI or alter unrelated features." Generates copyable prompt.',
      tag: '/prompts/response-schema.json'
    }
  ];

  return (
    <section className={`py-8 px-4 lg:px-8 space-y-8 transition-colors duration-200 ${
      isDark ? 'bg-[#171717] text-white' : 'bg-[#faf9f6] text-[#171717]'
    }`}>
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Title */}
        <div className={`border-b pb-4 ${isDark ? 'border-[#2d2d2d]' : 'border-[#e5e5e0]'}`}>
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Cpu className={`w-5 h-5 ${isDark ? 'text-amber-400' : 'text-amber-600'}`} />
            <span>AI Harness Architecture & Pipeline Specification</span>
          </h2>
          <p className={`text-xs mt-1 ${isDark ? 'text-[#a3a3a3]' : 'text-[#525252]'}`}>
            OOPSIE operates as an AI harness: a structured system around an LLM that makes its recovery advice reliable, safe, and repeatable.
          </p>
        </div>

        {/* Pipeline Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {pipelineStages.map((stage) => (
            <div key={stage.num} className={`border rounded-2xl p-5 space-y-3 ${
              isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-[#e5e5e0]'
            }`}>
              <div className="flex items-center justify-between">
                <span className={`text-xl font-mono font-black ${
                  isDark ? 'text-amber-400' : 'text-amber-600'
                }`}>
                  {stage.num}
                </span>
                <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${
                  isDark ? 'bg-[#181818] text-[#a3a3a3] border-[#2d2d2d]' : 'bg-[#f4f3ed] text-[#525252] border-[#e5e5e0]'
                }`}>
                  {stage.tag}
                </span>
              </div>
              <h3 className="text-sm font-bold">{stage.title}</h3>
              <p className={`text-xs leading-relaxed ${isDark ? 'text-[#a3a3a3]' : 'text-[#525252]'}`}>{stage.desc}</p>
            </div>
          ))}
        </div>

        {/* Open Source Models Section */}
        <div className={`border rounded-2xl p-5 space-y-3 ${
          isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-[#e5e5e0]'
        }`}>
          <div className="flex items-center gap-2 text-amber-500 font-bold text-xs">
            <Server className="w-4 h-4 text-amber-500" />
            <span>Supported Open-Source Coding LLMs</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className={`p-3.5 rounded-xl border ${
              isDark ? 'bg-[#181818] border-[#2d2d2d]' : 'bg-[#f4f3ed] border-[#e5e5e0]'
            }`}>
              <div className="font-bold">Qwen2.5-Coder</div>
              <div className={`text-[11px] ${isDark ? 'text-[#a3a3a3]' : 'text-[#525252]'}`}>High precision code syntax analysis and multi-turn repair prompt generation.</div>
              <div className="text-[10px] text-amber-500 font-bold font-mono mt-1">Ollama / vLLM</div>
            </div>

            <div className={`p-3.5 rounded-xl border ${
              isDark ? 'bg-[#181818] border-[#2d2d2d]' : 'bg-[#f4f3ed] border-[#e5e5e0]'
            }`}>
              <div className="font-bold">DeepSeek-Coder</div>
              <div className={`text-[11px] ${isDark ? 'text-[#a3a3a3]' : 'text-[#525252]'}`}>Strong stack trace parsing and root cause reasoning across Next.js and Supabase.</div>
              <div className="text-[10px] text-amber-500 font-bold font-mono mt-1">HF Inference Endpoints</div>
            </div>

            <div className={`p-3.5 rounded-xl border ${
              isDark ? 'bg-[#181818] border-[#2d2d2d]' : 'bg-[#f4f3ed] border-[#e5e5e0]'
            }`}>
              <div className="font-bold">StarCoder2 / Llama3-Code</div>
              <div className={`text-[11px] ${isDark ? 'text-[#a3a3a3]' : 'text-[#525252]'}`}>Efficient open-weight models for local demo execution and offline copilot usage.</div>
              <div className="text-[10px] text-amber-500 font-bold font-mono mt-1">Local / Edge Inference</div>
            </div>
          </div>
        </div>

        {/* Safety & Privacy Policy */}
        <div className={`border rounded-2xl p-5 space-y-3 ${
          isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-[#e5e5e0]'
        }`}>
          <div className="flex items-center gap-2 text-emerald-500 font-bold text-xs">
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
            <span>Safety & Privacy Principles</span>
          </div>

          <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs font-medium">
            <li className={`flex items-start gap-2 p-2.5 rounded-xl border ${
              isDark ? 'bg-[#181818] border-[#2d2d2d] text-[#e5e5e5]' : 'bg-[#f4f3ed]/60 border-[#e5e5e0] text-[#171717]'
            }`}>
              <span className="text-emerald-500 font-bold">✓</span>
              <span>Never auto-execute shell commands or database migrations automatically.</span>
            </li>
            <li className={`flex items-start gap-2 p-2.5 rounded-xl border ${
              isDark ? 'bg-[#181818] border-[#2d2d2d] text-[#e5e5e5]' : 'bg-[#f4f3ed]/60 border-[#e5e5e0] text-[#171717]'
            }`}>
              <span className="text-emerald-500 font-bold">✓</span>
              <span>Redact JWT tokens, passwords, and private API keys before sending to LLMs.</span>
            </li>
            <li className={`flex items-start gap-2 p-2.5 rounded-xl border ${
              isDark ? 'bg-[#181818] border-[#2d2d2d] text-[#e5e5e5]' : 'bg-[#f4f3ed]/60 border-[#e5e5e0] text-[#171717]'
            }`}>
              <span className="text-emerald-500 font-bold">✓</span>
              <span>Enforce minimal diff constraints on all generated repair prompts.</span>
            </li>
            <li className={`flex items-start gap-2 p-2.5 rounded-xl border ${
              isDark ? 'bg-[#181818] border-[#2d2d2d] text-[#e5e5e5]' : 'bg-[#f4f3ed]/60 border-[#e5e5e0] text-[#171717]'
            }`}>
              <span className="text-emerald-500 font-bold">✓</span>
              <span>Flag destructive database operations (e.g. DROP TABLE) as High Risk.</span>
            </li>
          </ul>
        </div>

      </div>
    </section>
  );
};
