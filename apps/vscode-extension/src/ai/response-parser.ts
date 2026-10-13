import { ErrorCategory, OopsieReport } from '../types/oopsie';

const CATEGORIES: ErrorCategory[] = [
  'dependency', 'configuration', 'environment_variables', 'database', 'authentication',
  'authorization', 'network', 'build', 'deployment', 'runtime', 'typescript', 'frontend',
  'other', 'unknown',
];
const RISKS: OopsieReport['risk_level'][] = ['low', 'medium', 'high'];

export function parseOopsieReport(json: string): OopsieReport {
  let value: unknown;
  try {
    value = JSON.parse(json);
  } catch (error) {
    throw new Error(`The model returned invalid JSON: ${error instanceof Error ? error.message : String(error)}`);
  }

  if (!isRecord(value)) throw new Error('The model response must be a JSON object.');
  const report = value;
  if (
    typeof report.summary !== 'string' ||
    typeof report.plain_explanation !== 'string' ||
    !Array.isArray(report.likely_causes) ||
    !report.likely_causes.every(isCause) ||
    !CATEGORIES.includes(report.error_category as ErrorCategory) ||
    !RISKS.includes(report.risk_level as OopsieReport['risk_level']) ||
    !isStringArray(report.missing_context_questions) ||
    !isStringArray(report.warnings) ||
    typeof report.repair_prompt !== 'string' ||
    !isStringArray(report.verification_steps) ||
    !Array.isArray(report.matched_recipes) ||
    !report.matched_recipes.every(isRecipe)
  ) {
    throw new Error('The model response does not match the OOPSIE report schema.');
  }

  return {
    summary: report.summary,
    plain_explanation: report.plain_explanation,
    likely_causes: report.likely_causes,
    error_category: report.error_category as ErrorCategory,
    risk_level: report.risk_level as OopsieReport['risk_level'],
    missing_context_questions: report.missing_context_questions,
    warnings: report.warnings,
    repair_prompt: report.repair_prompt,
    verification_steps: report.verification_steps,
    matched_recipes: report.matched_recipes,
  };
}

function isRecipe(value: unknown): value is OopsieReport['matched_recipes'][number] {
  if (!isRecord(value)) return false;
  return typeof value.id === 'string' && typeof value.title === 'string' &&
    (value.path === undefined || typeof value.path === 'string');
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every(item => typeof item === 'string');
}

function isCause(value: unknown): value is OopsieReport['likely_causes'][number] {
  if (!isRecord(value)) return false;
  return typeof value.description === 'string' &&
    (value.confidence === 'high' || value.confidence === 'medium' || value.confidence === 'low');
}
