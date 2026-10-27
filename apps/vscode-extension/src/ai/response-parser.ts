import { ErrorCategory, OopsieReport } from '../types/oopsie';

const CATEGORIES: ErrorCategory[] = [
  'dependency',
  'configuration',
  'environment_variables',
  'database',
  'authentication',
  'authorization',
  'network',
  'build',
  'deployment',
  'runtime',
  'typescript',
  'frontend',
  'other',
  'unknown',
];

const RISKS: OopsieReport['risk_level'][] = ['low', 'medium', 'high'];

export class OopsieServiceError extends Error {
  readonly code: string;
  readonly requestId?: string;

  constructor(code: string, message: string, requestId?: string) {
    super(`Inference service error [${code}]: ${message}`);
    this.name = 'OopsieServiceError';
    this.code = code;
    this.requestId = requestId;
  }
}

/**
 * Validates a report object against the strict OOPSIE schema.
 */
export function validateOopsieReport(report: unknown): OopsieReport {
  if (!isRecord(report)) {
    throw new Error('The model response must be a JSON object.');
  }

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

/**
 * Unwraps and validates an inference service API response.
 *
 * Supported formats:
 * 1. Standard success envelope: { status: 'success', data: report, metadata: {...} }
 * 2. Standard error envelope: { status: 'error', error: { code, message }, ... }
 * 3. Legacy direct report: { summary, plain_explanation, ... } (validated strictly)
 */
export function unwrapAndValidateResponse(payload: unknown): OopsieReport {
  let value = payload;
  if (typeof value === 'string') {
    try {
      value = JSON.parse(value);
    } catch (error) {
      throw new Error(`The model returned invalid JSON: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  if (!isRecord(value)) {
    throw new Error('The model response must be a JSON object.');
  }

  // 1. Error envelope handling
  if (value.status === 'error') {
    const errorObj = isRecord(value.error) ? value.error : {};
    const code = typeof errorObj.code === 'string' ? errorObj.code : 'UNKNOWN_ERROR';
    const message = typeof errorObj.message === 'string' ? errorObj.message : 'An unspecified service error occurred.';
    const requestId = typeof value.request_id === 'string' ? value.request_id : undefined;
    throw new OopsieServiceError(code, message, requestId);
  }

  // 2. Success envelope handling
  if (value.status === 'success') {
    if (!('data' in value) || !isRecord(value.data)) {
      throw new Error("Malformed success envelope: missing or invalid 'data' property.");
    }
    return validateOopsieReport(value.data);
  }

  // 3. Supported legacy direct raw-report (for backwards compatibility with direct mock fixtures)
  if (!('status' in value) && typeof value.summary === 'string') {
    return validateOopsieReport(value);
  }

  throw new Error("Unrecognized response envelope: missing 'status' indicator ('success' | 'error').");
}

/**
 * Legacy entry point: parses JSON string and unwraps if enveloped.
 */
export function parseOopsieReport(json: string): OopsieReport {
  return unwrapAndValidateResponse(json);
}

function isRecipe(value: unknown): value is OopsieReport['matched_recipes'][number] {
  if (!isRecord(value)) return false;
  return (
    typeof value.id === 'string' &&
    typeof value.title === 'string' &&
    (value.path === undefined || typeof value.path === 'string')
  );
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every(item => typeof item === 'string');
}

function isCause(value: unknown): value is OopsieReport['likely_causes'][number] {
  if (!isRecord(value)) return false;
  return (
    typeof value.description === 'string' &&
    (value.confidence === 'high' || value.confidence === 'medium' || value.confidence === 'low')
  );
}
