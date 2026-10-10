import React, { useState } from 'react';
import { GitPullRequest, Code, FolderTree, Shield, Terminal, Copy, Check } from 'lucide-react';
import confetti from 'canvas-confetti';

interface ContributorHubProps {
  theme: 'dark' | 'light';
}

export const ContributorHub: React.FC<ContributorHubProps> = ({ theme }) => {
  const isDark = theme === 'dark';
  const [copiedCommand, setCopiedCommand] = useState<string | null>(null);

  const handleCopy = (cmd: string) => {
    navigator.clipboard.writeText(cmd);
    setCopiedCommand(cmd);
    confetti({ particleCount: 35, spread: 40, origin: { y: 0.8 } });
    setTimeout(() => setCopiedCommand(null), 2000);
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
            <div className="flex items-center gap-2">
              <h2 className={`text-xl font-bold flex items-center gap-2 ${
                isDark ? 'text-white' : 'text-slate-900'
              }`}>
                <GitPullRequest className={`w-5 h-5 ${isDark ? 'text-amber-400' : 'text-amber-600'}`} />
                <span>Open Source Contributor Hub</span>
              </h2>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-600 border border-emerald-500/30">
                PRs Welcome
              </span>
            </div>
            <p className={`text-xs mt-1 ${isDark ? 'text-[#a3a3a3]' : 'text-slate-600 font-medium'}`}>
              OOPSIE is built by the community for vibe coders worldwide. Here is how you can contribute error recipes, rules, or extension capabilities!
            </p>
          </div>
        </div>


        {/* Contribution categories grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          
          {/* Box 1: Knowledge Base Recipes */}
          <div className={`border rounded-2xl p-5 space-y-3 shadow-sm ${
            isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-amber-200'
          }`}>
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold border ${
              isDark ? 'bg-[#282828] border-[#383838] text-amber-400' : 'bg-amber-100 border-amber-300 text-amber-900'
            }`}>
              <Code className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-bold">1. Submit Error Recipes</h3>
            <p className={`text-xs leading-relaxed ${isDark ? 'text-[#a3a3a3]' : 'text-slate-600 font-medium'}`}>
              Add a Markdown recipe for a framework error you solved in <code className="font-bold">/knowledge-base/&lt;framework&gt;/&lt;slug&gt;.md</code>.
            </p>
            <div className={`p-2 rounded-xl border text-[11px] font-mono font-bold ${
              isDark ? 'bg-[#181818] border-[#2d2d2d] text-amber-400' : 'bg-[#fffbeb] border-amber-200 text-amber-900'
            }`}>
              Path: <span className="underline">knowledge-base/react/my-error.md</span>
            </div>
          </div>

          {/* Box 2: Error Classifiers */}
          <div className={`border rounded-2xl p-5 space-y-3 shadow-sm ${
            isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-amber-200'
          }`}>
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold border ${
              isDark ? 'bg-[#282828] border-[#383838] text-amber-400' : 'bg-amber-100 border-amber-300 text-amber-900'
            }`}>
              <Terminal className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-bold">2. Update Classifier Rules</h3>
            <p className={`text-xs leading-relaxed ${isDark ? 'text-[#a3a3a3]' : 'text-slate-600 font-medium'}`}>
              Add signatures or regex patterns to <code className="font-bold">/rules/classifiers.json</code> so OOPSIE recognizes obscure logs.
            </p>
            <div className={`p-2 rounded-xl border text-[11px] font-mono font-bold ${
              isDark ? 'bg-[#181818] border-[#2d2d2d] text-amber-400' : 'bg-[#fffbeb] border-amber-200 text-amber-900'
            }`}>
              Path: <span className="underline">rules/classifiers.json</span>
            </div>
          </div>

          {/* Box 3: Safety Guardrails */}
          <div className={`border rounded-2xl p-5 space-y-3 shadow-sm ${
            isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-amber-200'
          }`}>
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold border ${
              isDark ? 'bg-[#282828] border-[#383838] text-emerald-400' : 'bg-emerald-100 border-emerald-300 text-emerald-900'
            }`}>
              <Shield className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-bold">3. Secret & Redaction Filters</h3>
            <p className={`text-xs leading-relaxed ${isDark ? 'text-[#a3a3a3]' : 'text-slate-600 font-medium'}`}>
              Help prevent credential leaks by adding patterns to <code className="font-bold">/rules/secret-redaction-patterns.json</code>.
            </p>
            <div className={`p-2 rounded-xl border text-[11px] font-mono font-bold ${
              isDark ? 'bg-[#181818] border-[#2d2d2d] text-emerald-400' : 'bg-[#fffbeb] border-amber-200 text-emerald-800'
            }`}>
              Path: <span className="underline">rules/secret-redaction-patterns.json</span>
            </div>
          </div>

        </div>

        {/* Directory Structure Map */}
        <div className={`border rounded-2xl p-5 space-y-3 shadow-sm ${
          isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-amber-200'
        }`}>
          <div className={`flex items-center gap-2 font-bold text-xs ${
            isDark ? 'text-amber-400' : 'text-amber-800'
          }`}>
            <FolderTree className="w-4 h-4" />
            <span>OOPSIE Open Source Repository Layout</span>
          </div>

          <div className={`border rounded-xl p-4 font-mono text-xs leading-relaxed whitespace-pre overflow-x-auto font-semibold ${
            isDark 
              ? 'bg-[#181818] border-[#2d2d2d] text-[#e5e5e5]' 
              : 'bg-[#fffbeb] border-amber-200 text-slate-900'
          }`}>
{`/oopsie-web                 # Documentation Hub & Live Recovery Engine (Vite + React + Tailwind)
/knowledge-base             # Community error recovery recipes
  /react                    # React & component state error recipes
  /nextjs                   # Next.js App Router & env variable recipes
  /supabase                 # Supabase RLS & auth recipes
  /vercel                   # Vercel deployment crash recipes
/prompts                    # System prompts & JSON output schemas
/rules                      # Error classifiers & secret redactor patterns
/extension                  # Manifest V3 browser extension scaffold
/docs                       # Architecture specs & open-source model guides
vercel.json                 # Production Vercel deployment config
CONTRIBUTING.md             # Community contribution guide`}
          </div>
        </div>

        {/* Step-by-step Git Quickstart */}
        <div className={`border rounded-2xl p-5 space-y-4 ${
          isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-amber-200'
        }`}>
          <h3 className="text-sm font-bold">
            🚀 Step-by-step Contribution Workflow
          </h3>

          <div className="space-y-2.5 text-xs">
            
            <div className={`p-3 border rounded-xl flex items-center justify-between gap-4 ${
              isDark ? 'bg-[#181818] border-[#2d2d2d]' : 'bg-yellow-50/70 border-amber-200'
            }`}>
              <div>
                <span className={`font-bold ${isDark ? 'text-amber-400' : 'text-amber-800'}`}>Step 1: Clone repo & install dependencies</span>
                <pre className={`text-[11px] font-mono mt-1 font-semibold ${isDark ? 'text-white' : 'text-slate-900'}`}>git clone https://github.com/Onyx-Prasai/OOPSIE.git && npm install</pre>
              </div>
              <button
                onClick={() => handleCopy("git clone https://github.com/Onyx-Prasai/OOPSIE.git && npm install")}
                className={`px-3 py-1.5 rounded-lg font-bold text-[11px] border shrink-0 ${
                  isDark
                    ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 border-amber-400'
                    : 'bg-amber-400 hover:bg-amber-300 text-slate-950 border-amber-300 shadow-sm'
                }`}
              >
                {copiedCommand === "git clone https://github.com/Onyx-Prasai/OOPSIE.git && npm install" ? 'Copied!' : 'Copy'}
              </button>
            </div>

            <div className={`p-3 border rounded-xl flex items-center justify-between gap-4 ${
              isDark ? 'bg-[#181818] border-[#2d2d2d]' : 'bg-yellow-50/70 border-amber-200'
            }`}>
              <div>
                <span className={`font-bold ${isDark ? 'text-amber-400' : 'text-amber-800'}`}>Step 2: Create a feature branch</span>
                <pre className={`text-[11px] font-mono mt-1 font-semibold ${isDark ? 'text-white' : 'text-slate-900'}`}>git checkout -b recipe/supabase-rls-fix</pre>
              </div>
              <button
                onClick={() => handleCopy("git checkout -b recipe/supabase-rls-fix")}
                className={`px-3 py-1.5 rounded-lg font-bold text-[11px] border shrink-0 ${
                  isDark
                    ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 border-amber-400'
                    : 'bg-amber-400 hover:bg-amber-300 text-slate-950 border-amber-300 shadow-sm'
                }`}
              >
                {copiedCommand === "git checkout -b recipe/supabase-rls-fix" ? 'Copied!' : 'Copy'}
              </button>
            </div>

            <div className={`p-3 border rounded-xl flex items-center justify-between gap-4 ${
              isDark ? 'bg-[#181818] border-[#2d2d2d]' : 'bg-yellow-50/70 border-amber-200'
            }`}>
              <div>
                <span className={`font-bold ${isDark ? 'text-amber-400' : 'text-amber-800'}`}>Step 3: Run local dev portal & push PR</span>
                <pre className={`text-[11px] font-mono mt-1 font-semibold ${isDark ? 'text-white' : 'text-slate-900'}`}>npm run dev && git push origin recipe/supabase-rls-fix</pre>
              </div>
              <button
                onClick={() => handleCopy("npm run dev && git push origin recipe/supabase-rls-fix")}
                className={`px-3 py-1.5 rounded-lg font-bold text-[11px] border shrink-0 ${
                  isDark
                    ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 border-amber-400'
                    : 'bg-amber-400 hover:bg-amber-300 text-slate-950 border-amber-300 shadow-sm'
                }`}
              >
                {copiedCommand === "npm run dev && git push origin recipe/supabase-rls-fix" ? 'Copied!' : 'Copy'}
              </button>
            </div>

          </div>
        </div>

      </div>
    </section>
  );
};
