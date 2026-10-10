import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { InteractivePlayground } from './components/InteractivePlayground';
import { ExtensionSimulator } from './components/ExtensionSimulator';
import { KnowledgeBaseExplorer } from './components/KnowledgeBaseExplorer';
import { ContributorHub } from './components/ContributorHub';
import { ArchitectureDocs } from './components/ArchitectureDocs';
import { Footer } from './components/Footer';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('playground');
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    const saved = localStorage.getItem('oopsie-theme');
    return (saved === 'light' || saved === 'dark') ? saved : 'dark';
  });

  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
    localStorage.setItem('oopsie-theme', nextTheme);
  };

  useEffect(() => {
    if (theme === 'light') {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
    } else {
      document.documentElement.classList.remove('light');
      document.documentElement.classList.add('dark');
    }
  }, [theme]);

  const isDark = theme === 'dark';

  return (
    <div className={`min-h-screen font-sans selection:bg-amber-500 selection:text-white flex flex-col transition-colors duration-200 ${
      isDark ? 'bg-[#171717] text-white' : 'bg-[#faf9f6] text-[#171717]'
    }`}>
      {/* Top sticky navigation header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        theme={theme}
        toggleTheme={toggleTheme}
      />

      {/* Main hero section */}
      <Hero
        onStartEngine={() => setActiveTab('playground')}
        onExploreExtension={() => setActiveTab('extension')}
        onViewContributing={() => setActiveTab('contribute')}
        theme={theme}
      />

      {/* Tab content area */}
      <main className="flex-1">
        {activeTab === 'playground' && <InteractivePlayground theme={theme} />}
        {activeTab === 'extension' && <ExtensionSimulator theme={theme} />}
        {activeTab === 'recipes' && <KnowledgeBaseExplorer theme={theme} />}
        {activeTab === 'contribute' && <ContributorHub theme={theme} />}
        {activeTab === 'docs' && <ArchitectureDocs theme={theme} />}
      </main>

      {/* Footer */}
      <Footer theme={theme} />
    </div>
  );
}

export default App;
