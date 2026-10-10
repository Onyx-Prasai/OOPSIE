import React, { useState } from 'react';
import { BookOpen, Search, GitPullRequest, Plus, Copy, Check } from 'lucide-react';
import confetti from 'canvas-confetti';

interface RecipeData {
  id: string;
  title: string;
  framework: string;
  category: string;
  risk: string;
  summary: string;
  signatures: string[];
  repairPrompt: string;
  verification: string[];
}

const COMMUNITY_RECIPES: RecipeData[] = [
  {
    id: 'kb-react-supabase-001',
    title: 'Missing @supabase/supabase-js Package',
    framework: 'React / Next.js',
    category: 'dependency',
    risk: 'low',
    summary: 'Occurs when AI assistants add Supabase query code without adding the npm dependency to package.json.',
    signatures: [
      "Module not found: Can't resolve '@supabase/supabase-js'",
      "Cannot find module '@supabase/supabase-js'"
    ],
    repairPrompt: `My project fails with: "Module not found: Can't resolve '@supabase/supabase-js'". Inspect package.json, install @supabase/supabase-js, and verify client imports. Make minimal changes.`,
    verification: ['Check package.json contains @supabase/supabase-js', 'Restart npm run dev']
  },
  {
    id: 'kb-nextjs-env-001',
    title: 'Missing NEXT_PUBLIC_ Environment Variables',
    framework: 'Next.js',
    category: 'environment_variables',
    risk: 'medium',
    summary: 'Client components fail to load database connection keys missing the NEXT_PUBLIC_ prefix or missing in .env.local.',
    signatures: [
      'Unhandled Runtime Error: NEXT_PUBLIC_ is undefined',
      'TypeError: Cannot read properties of undefined (reading supabaseUrl)'
    ],
    repairPrompt: `My Next.js app fails with missing env variables. Check process.env usage, ensure client variables use NEXT_PUBLIC_, and update .env.example with placeholder names.`,
    verification: ['Verify .env.local exists in root', 'Restart Next.js dev server']
  },
  {
    id: 'kb-vercel-build-001',
    title: 'Vercel Deployment Build Failure',
    framework: 'Vercel / Next.js',
    category: 'deployment',
    risk: 'low',
    summary: 'Production build fails on Vercel due to strict TypeScript compilation errors or client component state directives.',
    signatures: [
      'Error: Command "npm run build" exited with 1',
      'Type error: Property does not exist on type'
    ],
    repairPrompt: `Vercel build failed during 'npm run build'. Run local build to reproduce, fix TypeScript optional chaining, and verify 'use client' directives.`,
    verification: ['Run npm run build locally', 'Push changes to GitHub']
  },
  {
    id: 'kb-supabase-rls-001',
    title: 'Supabase Row Level Security (RLS) Denial',
    framework: 'Supabase',
    category: 'database',
    risk: 'medium',
    summary: 'Database operations fail because table RLS is enabled without explicit permissions for authenticated users.',
    signatures: [
      'new row violates row-level security policy for table',
      'PGRST301: permission denied for schema public'
    ],
    repairPrompt: `Supabase insert failed with RLS violation. Generate SQL statements to create SELECT and INSERT policies for auth.uid() = user_id. Do not disable RLS.`,
    verification: ['Run SQL policies in Supabase SQL Editor', 'Test table insert in UI']
  }
];

interface KnowledgeBaseExplorerProps {
  theme: 'dark' | 'light';
}

export const KnowledgeBaseExplorer: React.FC<KnowledgeBaseExplorerProps> = ({ theme }) => {
  const isDark = theme === 'dark';

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedRecipe, setSelectedRecipe] = useState<RecipeData | null>(null);
  const [isContributeModalOpen, setIsContributeModalOpen] = useState(false);
  const [copiedPrompt, setCopiedPrompt] = useState(false);

  const [newTitle, setNewTitle] = useState('');
  const [newFramework, setNewFramework] = useState('React / Next.js');
  const [newSignature, setNewSignature] = useState('');
  const [newExplanation, setNewExplanation] = useState('');

  const filteredRecipes = COMMUNITY_RECIPES.filter(recipe => {
    const matchesSearch = 
      recipe.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      recipe.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
      recipe.signatures.some(s => s.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesCat = selectedCategory === 'all' || recipe.category === selectedCategory;
    return matchesSearch && matchesCat;
  });

  const handleCopyPrompt = (promptText: string) => {
    navigator.clipboard.writeText(promptText);
    setCopiedPrompt(true);
    confetti({ particleCount: 35, spread: 40, origin: { y: 0.8 } });
    setTimeout(() => setCopiedPrompt(false), 2000);
  };

  const generatedMarkdownRecipe = `# Recipe: ${newTitle || 'Untitled Error Recipe'}

- **Frameworks**: \`${newFramework}\`
- **Category**: \`dependency\`

## Target Error Signature
\`\`\`
${newSignature || 'Paste raw error signature here...'}
\`\`\`

## Plain Language Explanation
${newExplanation || 'Explain what happened in simple terms...'}

## Safe AI Repair Prompt Template
\`\`\`text
My app displays: "${newSignature || 'Error message'}". Inspect dependencies and codebase, apply minimal fixes, and do not redesign UI.
\`\`\`
`;

  return (
    <section className={`py-8 px-4 lg:px-8 space-y-8 transition-colors duration-200 ${
      isDark ? 'bg-[#171717] text-white' : 'bg-[#faf9f6] text-[#171717]'
    }`}>
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Title & header */}
        <div className={`flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4 ${
          isDark ? 'border-[#2d2d2d]' : 'border-[#e5e5e0]'
        }`}>
          <div>
            <h2 className={`text-xl font-bold flex items-center gap-2 ${
              isDark ? 'text-white' : 'text-[#171717]'
            }`}>
              <BookOpen className={`w-5 h-5 ${isDark ? 'text-amber-400' : 'text-amber-600'}`} />
              <span>Community Knowledge Base</span>
            </h2>
            <p className={`text-xs mt-1 ${isDark ? 'text-[#a3a3a3]' : 'text-[#525252]'}`}>
              Open-source error recipes stored in Markdown files under <code className="font-bold">/knowledge-base/</code>.
            </p>
          </div>

          <button
            onClick={() => setIsContributeModalOpen(true)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl font-bold text-xs transition border ${
              isDark
                ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 border-amber-400'
                : 'bg-amber-500 hover:bg-amber-600 text-white border-amber-500'
            }`}
          >
            <Plus className="w-4 h-4" />
            <span>Contribute Recipe</span>
          </button>
        </div>

        {/* Search & filter controls */}
        <div className={`flex flex-col sm:flex-row items-center justify-between gap-3 p-3.5 rounded-2xl border ${
          isDark ? 'bg-[#212121] border-[#2e2e2e]' : 'bg-white border-[#e5e5e0]'
        }`}>
          
          {/* Search bar */}
          <div className="relative w-full sm:w-80">
            <Search className={`w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 ${
              isDark ? 'text-[#a3a3a3]' : 'text-[#737373]'
            }`} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search signatures or keywords..."
              className={`w-full border rounded-xl pl-9 pr-3 py-1.5 text-xs font-medium focus:outline-none ${
                isDark
                  ? 'bg-[#181818] border-[#383838] text-white focus:border-amber-400'
                  : 'bg-[#f4f3ed] border-[#e5e5e0] text-[#171717] focus:border-amber-500'
              }`}
            />
          </div>

          {/* Category filter pills */}
          <div className="flex items-center gap-1.5 flex-wrap text-xs">
            <span className={`font-semibold mr-1 ${isDark ? 'text-[#a3a3a3]' : 'text-[#525252]'}`}>Category:</span>
            {['all', 'dependency', 'environment_variables', 'deployment', 'database'].map(cat => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1 rounded-lg capitalize font-semibold transition border ${
                  selectedCategory === cat
                    ? isDark ? 'bg-[#2f2f2f] text-white border-[#404040]' : 'bg-[#171717] text-white border-[#171717]'
                    : isDark ? 'bg-[#181818] text-[#a3a3a3] border-[#2d2d2d] hover:text-white' : 'bg-[#f4f3ed] text-[#525252] border-[#e5e5e0] hover:text-[#171717]'
                }`}
              >
                {cat.replace('_', ' ')}
              </button>
            ))}
          </div>

        </div>

        {/* Recipe list grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          {filteredRecipes.map(recipe => (
            <div
              key={recipe.id}
              onClick={() => setSelectedRecipe(recipe)}
              className={`border rounded-2xl p-5 space-y-3 cursor-pointer transition group ${
                isDark
                  ? 'bg-[#212121] border-[#2e2e2e] hover:border-[#404040]'
                  : 'bg-white border-[#e5e5e0] hover:border-[#d4d4d4]'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${
                  isDark ? 'bg-[#282828] text-[#a3a3a3] border-[#383838]' : 'bg-[#f4f3ed] text-[#525252] border-[#e5e5e0]'
                }`}>
                  {recipe.framework}
                </span>
                <span className={`text-[10px] font-mono ${isDark ? 'text-[#737373]' : 'text-[#a3a3a3]'}`}>{recipe.id}</span>
              </div>

              <h3 className={`text-base font-bold transition ${
                isDark ? 'text-white group-hover:text-amber-400' : 'text-[#171717] group-hover:text-amber-600'
              }`}>
                {recipe.title}
              </h3>

              <p className={`text-xs leading-relaxed line-clamp-2 ${
                isDark ? 'text-[#a3a3a3]' : 'text-[#525252]'
              }`}>
                {recipe.summary}
              </p>

              <div className={`border rounded-xl p-2.5 font-mono text-[11px] truncate ${
                isDark ? 'bg-[#181818] border-[#2d2d2d] text-rose-400' : 'bg-[#f4f3ed] border-[#e5e5e0] text-rose-600'
              }`}>
                {recipe.signatures[0]}
              </div>

              <div className={`flex items-center justify-between text-xs pt-1 font-bold ${
                isDark ? 'text-amber-400' : 'text-amber-600'
              }`}>
                <span>View Recipe & Prompt Template →</span>
                <span className="text-[10px] font-mono">Markdown</span>
              </div>
            </div>
          ))}
        </div>

        {/* Recipe Details Modal */}
        {selectedRecipe && (
          <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
            <div className={`border rounded-2xl max-w-xl w-full max-h-[85vh] overflow-y-auto p-6 space-y-4 shadow-2xl relative ${
              isDark ? 'bg-[#212121] border-[#2e2e2e] text-white' : 'bg-white border-[#e5e5e0] text-[#171717]'
            }`}>
              
              <div className={`flex items-start justify-between border-b pb-3 ${
                isDark ? 'border-[#2d2d2d]' : 'border-[#e5e5e0]'
              }`}>
                <div>
                  <span className={`text-xs font-mono font-bold ${isDark ? 'text-amber-400' : 'text-amber-600'}`}>{selectedRecipe.id}</span>
                  <h3 className="text-lg font-bold mt-1">{selectedRecipe.title}</h3>
                </div>
                <button
                  onClick={() => setSelectedRecipe(null)}
                  className={`text-xs font-bold px-2.5 py-1 rounded border ${
                    isDark ? 'bg-[#282828] border-[#383838] text-white' : 'bg-[#f4f3ed] border-[#e5e5e0] text-[#171717]'
                  }`}
                >
                  ✕ Close
                </button>
              </div>

              <div className="space-y-3 text-xs">
                <div className="space-y-1">
                  <span className={`font-bold uppercase tracking-wider text-[10px] ${
                    isDark ? 'text-[#a3a3a3]' : 'text-[#737373]'
                  }`}>Target Error Signature:</span>
                  {selectedRecipe.signatures.map((sig, i) => (
                    <pre key={i} className={`border p-2.5 rounded-xl font-mono text-[11px] whitespace-pre-wrap ${
                      isDark ? 'bg-[#181818] border-[#2d2d2d] text-rose-400' : 'bg-[#f4f3ed] border-[#e5e5e0] text-rose-600'
                    }`}>
                      {sig}
                    </pre>
                  ))}
                </div>

                <div className="space-y-1">
                  <span className={`font-bold uppercase tracking-wider text-[10px] ${
                    isDark ? 'text-[#a3a3a3]' : 'text-[#737373]'
                  }`}>Overview:</span>
                  <p className="text-xs leading-relaxed font-medium">{selectedRecipe.summary}</p>
                </div>

                <div className="space-y-2 pt-2">
                  <div className="flex items-center justify-between">
                    <span className={`font-bold uppercase tracking-wider text-[10px] ${
                      isDark ? 'text-amber-400' : 'text-amber-700'
                    }`}>Safe AI Repair Prompt Template:</span>
                    <button
                      onClick={() => handleCopyPrompt(selectedRecipe.repairPrompt)}
                      className={`flex items-center gap-1.5 px-3 py-1 rounded-lg font-bold text-[11px] border ${
                        isDark ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 border-amber-400' : 'bg-amber-500 hover:bg-amber-600 text-white border-amber-500'
                      }`}
                    >
                      {copiedPrompt ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copiedPrompt ? 'Copied!' : 'Copy Prompt'}</span>
                    </button>
                  </div>
                  <pre className={`border p-3 rounded-xl font-mono text-[11px] whitespace-pre-wrap font-semibold ${
                    isDark ? 'bg-[#181818] border-[#2d2d2d] text-[#e5e5e5]' : 'bg-[#f4f3ed] border-[#e5e5e0] text-[#171717]'
                  }`}>
                    {selectedRecipe.repairPrompt}
                  </pre>
                </div>
              </div>

            </div>
          </div>
        )}

        {/* Contribute Recipe Modal */}
        {isContributeModalOpen && (
          <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
            <div className={`border rounded-2xl max-w-xl w-full max-h-[85vh] overflow-y-auto p-6 space-y-4 shadow-2xl ${
              isDark ? 'bg-[#212121] border-[#2e2e2e] text-white' : 'bg-white border-[#e5e5e0] text-[#171717]'
            }`}>
              
              <div className={`flex items-center justify-between border-b pb-3 ${
                isDark ? 'border-[#2d2d2d]' : 'border-[#e5e5e0]'
              }`}>
                <div className="flex items-center gap-2">
                  <GitPullRequest className={`w-4 h-4 ${isDark ? 'text-amber-400' : 'text-amber-600'}`} />
                  <h3 className="text-lg font-bold">Contribute Error Recipe</h3>
                </div>
                <button
                  onClick={() => setIsContributeModalOpen(false)}
                  className={`text-xs font-bold px-2 py-1 rounded border ${
                    isDark ? 'bg-[#282828] border-[#383838] text-white' : 'bg-[#f4f3ed] border-[#e5e5e0] text-[#171717]'
                  }`}
                >
                  ✕ Close
                </button>
              </div>

              <div className="space-y-3 text-xs">
                <div>
                  <label className="block font-bold mb-1">Recipe Title:</label>
                  <input
                    type="text"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    placeholder="e.g., Supabase RLS Permission Denied"
                    className={`w-full border rounded-lg p-2 font-medium ${
                      isDark ? 'bg-[#181818] border-[#383838] text-white' : 'bg-[#f4f3ed] border-[#e5e5e0] text-[#171717]'
                    }`}
                  />
                </div>

                <div>
                  <label className="block font-bold mb-1">Framework / Service:</label>
                  <input
                    type="text"
                    value={newFramework}
                    onChange={(e) => setNewFramework(e.target.value)}
                    placeholder="e.g., React / Next.js / Supabase"
                    className={`w-full border rounded-lg p-2 font-medium ${
                      isDark ? 'bg-[#181818] border-[#383838] text-white' : 'bg-[#f4f3ed] border-[#e5e5e0] text-[#171717]'
                    }`}
                  />
                </div>

                <div>
                  <label className="block font-bold mb-1">Target Error Signature:</label>
                  <textarea
                    value={newSignature}
                    onChange={(e) => setNewSignature(e.target.value)}
                    rows={2}
                    placeholder="Paste error signature..."
                    className={`w-full border rounded-lg p-2 font-mono text-[11px] ${
                      isDark ? 'bg-[#181818] border-[#383838] text-rose-400' : 'bg-[#f4f3ed] border-[#e5e5e0] text-rose-600'
                    }`}
                  />
                </div>

                <div>
                  <label className="block font-bold mb-1">Plain Language Explanation:</label>
                  <textarea
                    value={newExplanation}
                    onChange={(e) => setNewExplanation(e.target.value)}
                    rows={2}
                    placeholder="Explain what happened in simple terms..."
                    className={`w-full border rounded-lg p-2 text-[11px] font-medium ${
                      isDark ? 'bg-[#181818] border-[#383838] text-white' : 'bg-[#f4f3ed] border-[#e5e5e0] text-[#171717]'
                    }`}
                  />
                </div>

                <div>
                  <label className="block font-bold mb-1">Generated Markdown Preview:</label>
                  <pre className={`border p-3 rounded-xl font-mono text-[10px] whitespace-pre-wrap ${
                    isDark ? 'bg-[#181818] border-[#2d2d2d] text-[#d4d4d4]' : 'bg-[#f4f3ed] border-[#e5e5e0] text-[#171717]'
                  }`}>
                    {generatedMarkdownRecipe}
                  </pre>
                </div>

                <div className="pt-2 flex items-center justify-between">
                  <span className="text-[11px] font-mono">Save in <code className="font-bold">knowledge-base/react/my-recipe.md</code></span>
                  <button
                    onClick={() => handleCopyPrompt(generatedMarkdownRecipe)}
                    className={`px-4 py-2 rounded-xl font-bold text-xs border ${
                      isDark ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 border-amber-400' : 'bg-amber-500 hover:bg-amber-600 text-white border-amber-500'
                    }`}
                  >
                    Copy Markdown for PR
                  </button>
                </div>
              </div>

            </div>
          </div>
        )}

      </div>
    </section>
  );
};
