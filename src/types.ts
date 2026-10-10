export type ErrorCategory = 
  | 'dependency' 
  | 'environment_variables' 
  | 'database' 
  | 'deployment' 
  | 'cors' 
  | 'runtime' 
  | 'auth';

export type RiskLevel = 'low' | 'medium' | 'high';

export interface LikelyCause {
  title: string;
  confidence: 'high' | 'medium' | 'low';
  description: string;
}

export interface OopsieReport {
  id: string;
  summary: string;
  plain_english_explanation: string;
  category: ErrorCategory;
  risk_level: RiskLevel;
  likely_causes: LikelyCause[];
  follow_up_questions: string[];
  repair_prompt: string;
  verification_checklist: string[];
  safety_warnings: string[];
  timestamp: string;
}

export interface RecipeItem {
  id: string;
  title: string;
  category: ErrorCategory;
  framework: string;
  risk: RiskLevel;
  signatures: string[];
  summary: string;
  repairPrompt: string;
  verification: string[];
}
