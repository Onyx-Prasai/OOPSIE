import React, { useState } from 'react';
import { Sparkles, Terminal, Check, Download, Code, Layers } from 'lucide-react';
import confetti from 'canvas-confetti';

interface ExtensionSimulatorProps {
  theme: 'dark' | 'light';
}

export const ExtensionSimulator: React.FC<ExtensionSimulatorProps> = ({ theme }) => {
  const isDark = theme === 'dark';
  const [activeView, setActiveView] = useState<'vercel' | 'devtools' | 'cursor'>('vercel');
  const [copied, setCopied] = useState<boolean>(false);

  const handleCopyInstallGuide = () => {
    navigator.clipboard.writeText(`git clone https://github.com/Onyx-Prasai/OOPSIE.git\n# Load /extension folder in chrome://extensions Dev Mode`);
    setCopied(true);
    confetti({ particleCount: 35, spread: 40, origin: { y: 0.8 } });
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className={`py-8 px-4 lg:px-8 space-y-8 transition-colors duration-200 ${
      isDark ? 'bg-[#171717] text-white' : 'bg-[#faf9f6] text-[#171717]'
    }`}>
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Title section */}
        <div className={`flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4 ${
          isDark ? 'border-[#2d2d2d]' : 'border-[#e5e5e0]'
        }`}>
          <div>
            <div className="flex items-center gap-2">
              <h2 className={`text-xl font-bold flex items-center gap-2 ${
                isDark ? 'text-white' : 'text-[#171717]'
              }`}>
                <Sparkles className={`w-5 h-5 ${isDark ? 'text-amber-400' : 'text-amber-600'}`} />
                <span>Browser Extension & Copilot Workflow</span>
              </h2>
              <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${
                isDark ? 'bg-[#242424] text-[#a3a3a3] border-[#383838]' : 'bg-[#f4f3ed] text-[#525252] border-[#e5e5e0]'
              }`}>
                Manifest V3
              </span>
            </div>
            <p className={`text-xs mt-1 ${isDark ? 'text-[#a3a3a3]' : 'text-[#525252]'}`}>
              Capture error logs on Vercel, Netlify, Chrome DevTools, or Cursor IDE to format instant recovery prompts.
            </p>
          </div>

          <button
            onClick={handleCopyInstallGuide}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl font-bold text-xs transition border ${
              isDark
                ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 border-amber-400'
                : 'bg-amber-500 hover:bg-amber-600 text-white border-amber-500'
            }`}
          >
            {copied ? <Check className="w-4 h-4" /> : <Download className="w-4 h-4" />}
            <span>{copied ? 'Copied Commands!' : 'Load Unpacked (/extension)'}</span>
          </button>
        </div>

        {/* Simulator tab buttons */}
        <div className={`flex items-center gap-1.5 p-1 rounded-xl border w-fit ${
          isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-[#f4f3ed] border-[#e5e5e0]'
        }`}>
          <button
            onClick={() => setActiveView('vercel')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-bold transition ${
              activeView === 'vercel'
                ? isDark ? 'bg-[#2f2f2f] text-white border border-[#404040]' : 'bg-white text-[#171717] border border-[#d4d4d4] shadow-sm'
                : isDark ? 'text-[#a3a3a3] hover:text-white' : 'text-[#525252] hover:text-[#171717]'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Vercel Deploy Log</span>
          </button>

          <button
            onClick={() => setActiveView('devtools')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-bold transition ${
              activeView === 'devtools'
                ? isDark ? 'bg-[#2f2f2f] text-white border border-[#404040]' : 'bg-white text-[#171717] border border-[#d4d4d4] shadow-sm'
                : isDark ? 'text-[#a3a3a3] hover:text-white' : 'text-[#525252] hover:text-[#171717]'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>Chrome DevTools Panel</span>
          </button>

          <button
            onClick={() => setActiveView('cursor')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-bold transition ${
              activeView === 'cursor'
                ? isDark ? 'bg-[#2f2f2f] text-white border border-[#404040]' : 'bg-white text-[#171717] border border-[#d4d4d4] shadow-sm'
                : isDark ? 'text-[#a3a3a3] hover:text-white' : 'text-[#525252] hover:text-[#171717]'
            }`}
          >
            <Code className="w-3.5 h-3.5" />
            <span>Cursor / Claude Overlay</span>
          </button>
        </div>

        {/* Interactive Mock Window */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          
          {/* Mock Browser Page (2 cols) */}
          <div className="lg:col-span-2 border border-[#2e2e2e] rounded-2xl overflow-hidden shadow-sm bg-[#1c1c1c]">
            
            {/* Mock Window Title Bar */}
            <div className="bg-[#141414] px-4 py-3 border-b border-[#2d2d2d] flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block" />
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" />
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" />
                <span className="text-xs font-mono text-[#a3a3a3] ml-2">
                  {activeView === 'vercel' && 'vercel.com/my-team/vibe-app/deployments/dep_88912'}
                  {activeView === 'devtools' && 'chrome-devtools://devtools/bundled/inspector.html'}
                  {activeView === 'cursor' && 'cursor://workspace/src/app/page.tsx'}
                </span>
              </div>
              <span className="text-[10px] text-amber-400 font-mono font-bold">OOPSIE Active</span>
            </div>

            {/* Window Content */}
            <div className="p-5 font-mono text-xs space-y-3 min-h-[280px] bg-[#141414] text-[#d4d4d4]">
              {activeView === 'vercel' && (
                <div className="space-y-2">
                  <div className="text-[#a3a3a3]">[14:22:01.002] Building Next.js application...</div>
                  <div className="text-rose-400 bg-rose-950/40 p-3 rounded-lg border border-rose-800/40 relative">
                    <div className="font-bold">Failed to compile:</div>
                    <div className="mt-1 bg-rose-900/60 p-1 rounded inline-block text-white select-all">
                      Module not found: Can't resolve '@supabase/supabase-js'
                    </div>
                    <div className="mt-2 text-[#a3a3a3] text-[11px]">
                      Trace: ./src/lib/supabaseClient.ts line 2
                    </div>
                    
                    {/* Context menu overlay simulation */}
                    <div className="absolute right-3 top-3 bg-[#242424] border border-[#383838] rounded-xl p-2 z-10">
                      <div className="flex items-center gap-2 text-amber-400 font-bold px-2 py-1 bg-[#2e2a1f] rounded">
                        <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                        <span>Analyze Error with OOPSIE</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeView === 'devtools' && (
                <div className="space-y-2">
                  <div className="text-amber-400 font-bold">⚠️ [Warning] React hydration mismatch detected</div>
                  <div className="text-rose-400 bg-[#212121] p-3 rounded-lg border border-[#2e2e2e]">
                    <span className="text-[#a3a3a3]">Uncaught Error: </span>
                    <span>NEXT_PUBLIC_SUPABASE_URL is not defined at AuthContext.tsx:14</span>
                  </div>
                  <div className="text-[#a3a3a3]">Call stack: renderWithHooks -&gt; updateFunctionComponent</div>
                </div>
              )}

              {activeView === 'cursor' && (
                <div className="space-y-2">
                  <div className="text-[#a3a3a3]">// Cursor AI Terminal Output</div>
                  <div className="text-rose-400 font-bold">PostgrestError: new row violates row-level security policy for table "projects"</div>
                  <div className="text-[#a3a3a3]">Query: INSERT INTO projects (title, user_id) VALUES ('My App', 'usr_123')</div>
                </div>
              )}
            </div>

          </div>

          {/* Mock OOPSIE Extension Popup Panel (1 col) */}
          <div className={`border rounded-2xl p-5 space-y-4 relative ${
            isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-[#e5e5e0]'
          }`}>
            
            <div className={`flex items-center justify-between border-b pb-3 ${
              isDark ? 'border-[#2d2d2d]' : 'border-[#e5e5e0]'
            }`}>
              <div className="flex items-center gap-2">
                <span className="text-base">⚡</span>
                <div>
                  <h3 className={`text-sm font-bold ${isDark ? 'text-white' : 'text-[#171717]'}`}>OOPSIE Copilot</h3>
                  <p className={`text-[10px] ${isDark ? 'text-[#a3a3a3]' : 'text-[#525252]'}`}>Extension Popup Overlay</p>
                </div>
              </div>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                Connected
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div className={`p-3 rounded-xl border ${
                isDark ? 'bg-[#181818] border-[#2d2d2d]' : 'bg-[#f4f3ed] border-[#e5e5e0]'
              }`}>
                <div className={`font-bold ${isDark ? 'text-amber-400' : 'text-amber-700'}`}>💡 Plain English Explanation:</div>
                <div className={`mt-1 text-[11px] leading-relaxed ${isDark ? 'text-[#e5e5e5]' : 'text-[#171717]'}`}>
                  Supabase client library is missing from project dependencies.
                </div>
              </div>

              <div className={`p-3 rounded-xl border ${
                isDark ? 'bg-[#181818] border-[#2d2d2d]' : 'bg-[#f4f3ed] border-[#e5e5e0]'
              }`}>
                <div className="font-bold text-amber-500">🔍 Probable Cause:</div>
                <div className={`mt-1 text-[11px] ${isDark ? 'text-[#e5e5e5]' : 'text-[#171717]'}`}>
                  Missing `npm install @supabase/supabase-js`.
                </div>
              </div>

              <div className={`p-3 rounded-xl border space-y-1.5 ${
                isDark ? 'bg-[#181818] border-[#2d2d2d]' : 'bg-[#f4f3ed] border-[#e5e5e0]'
              }`}>
                <div className="flex items-center justify-between">
                  <span className={`font-bold ${isDark ? 'text-white' : 'text-[#171717]'}`}>🤖 Repair Prompt:</span>
                  <span className="text-[10px] text-amber-500 font-bold">Safe Diff</span>
                </div>
                <pre className={`text-[10px] p-2 rounded whitespace-pre-wrap font-mono font-semibold ${
                  isDark ? 'text-[#e5e5e5] bg-[#141414]' : 'text-[#171717] bg-white border border-[#e5e5e0]'
                }`}>
{`Inspect package.json and install missing @supabase/supabase-js. Do not change unrelated UI features.`}
                </pre>
              </div>
            </div>

          </div>

        </div>

      </div>
    </section>
  );
};
