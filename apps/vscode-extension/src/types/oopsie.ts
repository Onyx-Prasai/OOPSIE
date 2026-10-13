export type ErrorCategory =
  | 'dependency'
  | 'configuration'
  | 'environment_variables'
  | 'database'
  | 'authentication'
  | 'authorization'
  | 'network'
  | 'build'
  | 'deployment'
  | 'runtime'
  | 'typescript'
  | 'frontend'
  | 'other'
  | 'unknown';

export interface OopsieReport {
  summary: string;
  plain_explanation: string;
  error_category: ErrorCategory;
  likely_causes: Array<{ description: string; confidence: 'low' | 'medium' | 'high' }>;
  missing_context_questions: string[];
  risk_level: 'low' | 'medium' | 'high';
  warnings: string[];
  repair_prompt: string;
  verification_steps: string[];
  matched_recipes: Array<{ id: string; title: string; path?: string }>;
}

export interface AnalysisContext {
  errorText: string;
  framework?: string;
  filePath?: string;
  selectedCode?: string;
  terminalOutput?: string;
  matchedRecipe?: string;
}
