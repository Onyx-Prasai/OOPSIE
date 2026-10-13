import classifiers from '../../../rules/classifiers/error-signatures.json';
import redactionRules from '../../../rules/redaction/patterns.json';

interface ClassifierRule {
  category: string;
  framework: string;
  risk: 'low' | 'medium' | 'high';
  signatures: string[];
  explanation: string;
  cause: string;
  focus: string;
}

interface RedactionRule {
  name: string;
  regex: string;
  replacement: string;
  flags?: string;
}

export interface AnalysisReport {
  summary: string;
  plain_explanation: string;
  error_category: string;
  likely_causes: Array<{ description: string; confidence: 'low' | 'medium' | 'high' }>;
  missing_context_questions: string[];
  risk_level: 'low' | 'medium' | 'high';
  warnings: string[];
  repair_prompt: string;
  verification_steps: string[];
  matched_recipes: Array<{ id: string; title: string; path?: string }>;
  detected_framework: string;
}

const classifierRules = classifiers.rules as ClassifierRule[];
const secretRules = redactionRules.rules as RedactionRule[];
const recipes = [
  {
    id: 'kb-react-supabase-001',
    title: 'Missing Supabase Client Package',
    path: 'knowledge-base/react/module-not-found-supabase.md',
    signatures: ["Can't resolve '@supabase/supabase-js'", 'Cannot find module @supabase/supabase-js', '@supabase/ssr'],
    keywords: ['supabase', 'module', 'not', 'found', 'resolve'],
    category: 'dependency',
    framework: 'supabase',
    guidance: 'The recipe recommends checking the package manifest, project root, and import before changing dependencies.',
  },
  {
    id: 'kb-vercel-build-001',
    title: 'Vercel Deployment Command Failure',
    path: 'knowledge-base/vercel/build-command-failed.md',
    signatures: ['npm run build" exited', 'Build failed because of webpack errors'],
    keywords: ['vercel', 'deployment', 'build', 'command', 'failed', 'exited'],
    category: 'deployment',
    framework: 'vercel',
    guidance: 'The recipe recommends reproducing the build locally and checking the first build error before changing hosting settings.',
  },
  {
    id: 'kb-nextjs-env-001',
    title: 'Missing Next.js Environment Variables',
    path: 'knowledge-base/nextjs/missing-env-vars.md',
    signatures: ['Missing environment variable', 'is not defined in process.env'],
    keywords: ['next', 'environment', 'variable', 'missing', 'process.env'],
    category: 'environment_variables',
    framework: 'next',
    guidance: 'The recipe recommends checking variable names and deployment scope without exposing secret values.',
  },
  {
    id: 'kb-supabase-rls-001',
    title: 'Supabase Row-Level Security Permission Denied',
    path: 'knowledge-base/supabase/rls-permission-denied.md',
    signatures: ['new row violates row-level security policy', 'permission denied for table'],
    keywords: ['supabase', 'row-level', 'security', 'policy', 'permission', 'denied'],
    category: 'authorization',
    framework: 'supabase',
    guidance: 'The recipe warns not to disable row-level security globally and to review access policies narrowly.',
  },
];

export function redactInput(text: string): { text: string; detectedSecret: boolean } {
  let cleaned = text;
  let detectedSecret = false;
  for (const rule of secretRules) {
    const flags = `${rule.flags ?? ''}g`;
    const matches = new RegExp(rule.regex, flags).test(cleaned);
    if (!matches) continue;
    detectedSecret = true;
    cleaned = cleaned.replace(new RegExp(rule.regex, flags), rule.replacement);
  }
  return { text: cleaned, detectedSecret };
}

export function analyzeWithRules(errorText: string): AnalysisReport {
  const normalized = errorText.toLowerCase();
  let selected = classifierRules[classifierRules.length - 1];
  let bestScore = 0;
  for (const rule of classifierRules.slice(0, -1)) {
    const score = rule.signatures.reduce(
      (total, signature) => total + (normalized.includes(signature.toLowerCase()) ? signature.length + 1 : 0),
      0,
    );
    if (score > bestScore) {
      selected = rule;
      bestScore = score;
    }
  }
  const matchedRecipes = recipes
    .map(recipe => {
      const signatureMatch = recipe.signatures.some(signature => normalized.includes(signature.toLowerCase()));
      const keywordScore = recipe.keywords.reduce(
        (count, keyword) => count + (normalized.includes(keyword) ? 1 : 0),
        0,
      );
      const frameworkMatch = normalized.includes(recipe.framework);
      const categoryMatch = recipe.category === selected.category;
      return {
        score: (signatureMatch ? 10 : 0) + keywordScore + (frameworkMatch ? 2 : 0) + (categoryMatch ? 2 : 0),
        record: recipe,
      };
    })
    .filter(item => item.score >= 3)
    .sort((left, right) => right.score - left.score)
    .slice(0, 3)
    .map(({ record }) => ({ id: record.id, title: record.title, path: record.path }));
  const warnings = selected.risk === 'high'
    ? ['This issue may affect authentication, authorization, or protected data. Preserve least-privilege controls.']
    : [];
  if (/\b(database|sql|migration|production|prod|payment|billing|charge|refund)\b/i.test(errorText)) {
    warnings.push('Review database, payment, and production impact carefully before applying any change.');
  }
  const questions = [
    'What command or action produced this error, and what happened immediately before it?',
    `Which ${selected.framework} and runtime versions and environment are involved?`,
  ];
  if (selected.category === 'unknown') {
    questions.push('Can you share the surrounding log lines and a minimal reproduction after reviewing them for sensitive data?');
  }
  const recipeGuidance = matchedRecipes.length
    ? recipes.find(recipe => recipe.id === matchedRecipes[0].id)?.guidance
    : undefined;
  return {
    summary: `Likely ${selected.category.replaceAll('_', ' ')} issue${selected.category === 'unknown' ? ' needs more context' : ''}.`,
    plain_explanation: `${selected.explanation} This classification is a rule-based hint, not a confirmed diagnosis.${recipeGuidance ? ` Community recipe guidance: ${recipeGuidance}` : ''}`,
    error_category: selected.category,
    likely_causes: [{ description: selected.cause, confidence: bestScore ? 'medium' : 'low' }],
    missing_context_questions: questions,
    risk_level: selected.risk,
    warnings,
    repair_prompt: `Please inspect the relevant context for this error:\n\n${errorText}\n\nFocus on ${selected.focus}.${recipeGuidance ? ` Consider this non-authoritative community guidance: ${recipeGuidance}` : ''} Identify the likely cause from the code and configuration, then suggest the smallest evidence-based change. Do not expose secrets, weaken security controls, modify unrelated files, execute commands, or deploy. Explain the change and provide verification steps. Do not claim a fix is guaranteed.`,
    verification_steps: [
      'Reproduce the issue in the same environment and inspect the surrounding diagnostic output.',
      'Review the proposed change and its impact before applying it.',
      'Run the relevant tests or build and verify expected behavior in a safe environment.',
    ],
    matched_recipes: matchedRecipes,
    detected_framework: selected.framework,
  };
}
