import React from 'react';
import { GitPullRequest } from 'lucide-react';

interface FooterProps {
  theme: 'dark' | 'light';
}

export const Footer: React.FC<FooterProps> = ({ theme }) => {
  const isDark = theme === 'dark';

  return (
    <footer className={`border-t py-8 px-4 lg:px-8 text-xs transition-colors duration-200 ${
      isDark
        ? 'bg-[#171717] border-[#2d2d2d] text-[#a3a3a3]'
        : 'bg-[#fffdf0] border-yellow-200 text-slate-600'
    }`}>
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
        
        <div>
          <div className={`flex items-center justify-center sm:justify-start gap-2 font-bold text-sm ${
            isDark ? 'text-white' : 'text-slate-900'
          }`}>
            <span>⚡ OOPSIE</span>
            <span className={`font-normal text-xs ${isDark ? 'text-[#737373]' : 'text-[#737373]'}`}>| Paste chaos. Get clarity.</span>
          </div>
          <p className="mt-1 font-medium">
            Open-Source AI Error Recovery Copilot for Vibe Coders. Released under MIT License.
          </p>
        </div>

        <div className="flex items-center flex-wrap justify-center sm:justify-end gap-4 font-semibold">
          {/* GitHub Repository Link */}
          <a
            href="https://github.com/Onyx-Prasai/OOPSIE"
            target="_blank"
            rel="noreferrer"
            className={`flex items-center gap-1.5 transition ${
              isDark ? 'text-[#a3a3a3] hover:text-white' : 'text-slate-700 hover:text-amber-800'
            }`}
          >
            <GitPullRequest className="w-3.5 h-3.5 text-amber-500" />
            <span>GitHub Repository</span>
          </a>
        </div>

      </div>
    </footer>
  );
};
