import React from 'react';
import { Terminal, Sparkles, Code2 } from 'lucide-react';

interface HeroProps {
  onStartEngine: () => void;
  onExploreExtension: () => void;
  onViewContributing: () => void;
  theme: 'dark' | 'light';
}

export const Hero: React.FC<HeroProps> = ({
  onStartEngine,
  onExploreExtension,
  onViewContributing,
  theme
}) => {
  const isDark = theme === 'dark';

  return (
    <div className={`relative pt-10 pb-12 px-4 lg:px-8 border-b transition-colors duration-200 ${
      isDark
        ? 'bg-[#171717] border-[#2d2d2d] text-white'
        : 'bg-[#fffdf0] border-yellow-200 text-slate-900'
    }`}>
      <div className="max-w-4xl mx-auto text-center space-y-6">
        
        {/* Pill badge */}
        <div className={`inline-flex items-center gap-2 px-3.5 py-1 rounded-full text-xs font-semibold border ${
          isDark
            ? 'bg-[#242424] border-[#383838] text-[#d4d4d4]'
            : 'bg-amber-100 border-amber-300 text-amber-900 shadow-sm'
        }`}>
          <Sparkles className={`w-3.5 h-3.5 ${isDark ? 'text-amber-400' : 'text-amber-600'}`} />
          <span>Open-Source AI Error Recovery Copilot for Vibe Coders</span>
        </div>

        {/* Headline */}
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-tight">
          Paste chaos.{' '}
          <span className={isDark ? 'text-amber-400' : 'text-amber-600 font-black'}>
            Get clarity.
          </span>
        </h1>

        {/* Subtitle */}
        <p className={`text-base sm:text-lg max-w-2xl mx-auto leading-relaxed ${
          isDark ? 'text-[#a3a3a3]' : 'text-slate-700 font-medium'
        }`}>
          When your app breaks on Vercel, Supabase, Next.js, or local terminal, <strong className={isDark ? 'text-white font-bold' : 'text-slate-900 font-bold'}>OOPSIE</strong> explains the technical failure in plain English, identifies root causes, redacts secrets, and generates a copy-ready AI repair prompt.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
          <button
            onClick={onStartEngine}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold text-sm transition shadow-lg ${
              isDark
                ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 border border-amber-400'
                : 'bg-amber-400 hover:bg-amber-300 text-slate-950 shadow-amber-300/50'
            }`}
          >
            <Terminal className="w-4 h-4" />
            <span>Try Live Error Engine</span>
          </button>

          <button
            onClick={onExploreExtension}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-sm border transition ${
              isDark
                ? 'bg-[#242424] hover:bg-[#2c2c2c] text-white border-[#383838]'
                : 'bg-white hover:bg-yellow-50 text-slate-900 border-amber-300 shadow-sm'
            }`}
          >
            <Sparkles className={`w-4 h-4 ${isDark ? 'text-amber-400' : 'text-amber-600'}`} />
            <span>Browser Extension Specs</span>
          </button>

          <button
            onClick={onViewContributing}
            className={`flex items-center gap-2 px-5 py-3 rounded-xl font-semibold text-sm border transition ${
              isDark
                ? 'bg-[#242424] hover:bg-[#2c2c2c] text-[#a3a3a3] border-[#383838]'
                : 'bg-yellow-100 hover:bg-yellow-200 text-amber-950 border-amber-300'
            }`}
          >
            <Code2 className={`w-4 h-4 ${isDark ? 'text-[#a3a3a3]' : 'text-amber-700'}`} />
            <span>Contribute Error Recipes</span>
          </button>
        </div>

        {/* Minimal Stats Ticker */}
        <div className="pt-6 grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-3xl mx-auto text-left">
          <div className={`p-3.5 rounded-xl border ${
            isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-amber-200 shadow-sm'
          }`}>
            <div className={`text-xl font-extrabold ${isDark ? 'text-white' : 'text-slate-900'}`}>100%</div>
            <div className={`text-xs ${isDark ? 'text-[#a3a3a3]' : 'text-slate-600 font-medium'}`}>Open Source & Local LLM</div>
          </div>
          <div className={`p-3.5 rounded-xl border ${
            isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-amber-200 shadow-sm'
          }`}>
            <div className="text-xl font-extrabold text-emerald-500">Zero</div>
            <div className={`text-xs ${isDark ? 'text-[#a3a3a3]' : 'text-slate-600 font-medium'}`}>Secret / Key Leaks</div>
          </div>
          <div className={`p-3.5 rounded-xl border ${
            isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-amber-200 shadow-sm'
          }`}>
            <div className="text-xl font-extrabold text-amber-500">6 Stage</div>
            <div className={`text-xs ${isDark ? 'text-[#a3a3a3]' : 'text-slate-600 font-medium'}`}>AI Safety Pipeline</div>
          </div>
          <div className={`p-3.5 rounded-xl border ${
            isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-amber-200 shadow-sm'
          }`}>
            <div className="text-xl font-extrabold text-sky-500">Cursor & Claude</div>
            <div className={`text-xs ${isDark ? 'text-[#a3a3a3]' : 'text-slate-600 font-medium'}`}>Repair Prompt Format</div>
          </div>
        </div>

      </div>
    </div>
  );
};
