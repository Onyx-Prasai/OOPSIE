import React from 'react';
import { Terminal, BookOpen, GitPullRequest, Cpu, Sparkles, ExternalLink, Sun, Moon } from 'lucide-react';

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  theme: 'dark' | 'light';
  toggleTheme: () => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab, theme, toggleTheme }) => {
  const isDark = theme === 'dark';

  const navItems = [
    { id: 'playground', label: 'Live Engine', icon: Terminal },
    { id: 'extension', label: 'Extension Specs', icon: Sparkles },
    { id: 'recipes', label: 'Recipe Catalog', icon: BookOpen },
    { id: 'contribute', label: 'Contributor Hub', icon: GitPullRequest },
    { id: 'docs', label: 'Architecture Specs', icon: Cpu },
  ];

  return (
    <header className={`sticky top-0 z-50 border-b transition-colors duration-200 px-4 lg:px-8 py-3.5 ${
      isDark
        ? 'bg-[#171717]/95 backdrop-blur-md border-[#2d2d2d] text-white'
        : 'bg-[#fffdf0]/95 backdrop-blur-md border-yellow-200 text-slate-900 shadow-sm'
    }`}>
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Brand logo & title */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('playground')}>
          <div className={`w-9 h-9 rounded-xl flex items-center justify-center font-bold text-lg shadow-md transition ${
            isDark 
              ? 'bg-[#282828] border border-[#383838] text-amber-400' 
              : 'bg-gradient-to-tr from-amber-400 to-amber-500 text-slate-950 shadow-amber-300/50'
          }`}>
            ⚡
          </div>
          <div>
            <h1 className={`text-xl font-extrabold tracking-tight ${
              isDark ? 'text-white' : 'text-slate-900'
            }`}>
              OOPSIE
            </h1>
            <p className={`text-xs font-medium ${isDark ? 'text-[#a3a3a3]' : 'text-slate-600'}`}>
              Paste chaos. Get clarity.
            </p>
          </div>
        </div>

        {/* Navigation links */}
        <nav className={`flex items-center flex-wrap justify-center gap-1 p-1 rounded-xl border ${
          isDark
            ? 'bg-[#212121] border-[#2e2e2e]'
            : 'bg-yellow-100/80 border-yellow-300'
        }`}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  isActive
                    ? isDark
                      ? 'bg-[#2f2f2f] text-white border border-[#404040]'
                      : 'bg-amber-400 text-slate-950 font-bold shadow-md shadow-amber-300/50'
                    : isDark
                      ? 'text-[#a3a3a3] hover:text-white hover:bg-[#282828]'
                      : 'text-amber-900 hover:text-slate-950 hover:bg-yellow-200/60'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${
                  isActive 
                    ? isDark ? 'text-amber-400' : 'text-slate-950' 
                    : isDark ? 'text-[#737373]' : 'text-amber-700'
                }`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Actions: Theme Toggle, Email, GitHub */}
        <div className="flex items-center gap-2 text-xs">
          
          {/* Light / Dark Mode Toggle */}
          <button
            onClick={toggleTheme}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-semibold border transition ${
              isDark
                ? 'bg-[#242424] hover:bg-[#2c2c2c] text-white border-[#383838]'
                : 'bg-amber-200 hover:bg-amber-300 text-amber-950 border-amber-400'
            }`}
          >
            {isDark ? <Sun className="w-3.5 h-3.5 text-amber-400" /> : <Moon className="w-3.5 h-3.5 text-slate-800" />}
            <span>{isDark ? 'Light Mode ☀️' : 'Dark Mode 🌙'}</span>
          </button>


          {/* Exact GitHub repository link */}
          <a
            href="https://github.com/Onyx-Prasai/OOPSIE"
            target="_blank"
            rel="noreferrer"
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-semibold border transition ${
              isDark
                ? 'bg-[#242424] hover:bg-[#2c2c2c] text-[#a3a3a3] hover:text-white border-[#383838]'
                : 'bg-white hover:bg-yellow-50 text-slate-800 border-amber-300'
            }`}
          >
            <GitPullRequest className="w-3.5 h-3.5 text-amber-500" />
            <span>GitHub</span>
            <ExternalLink className="w-3 h-3 text-[#737373]" />
          </a>
        </div>

      </div>
    </header>
  );
};
