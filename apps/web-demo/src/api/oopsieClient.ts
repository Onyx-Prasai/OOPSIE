/**
 * OOPSIE Inference API Client Adapter
 * 
 * Communicates with the FastAPI inference service adhering strictly to the
 * outer envelope contract:
 * - Success: { status: 'success', request_id, model_version, formatter_version, data, metadata }
 * - Error: { status: 'error', request_id, error: { code, message } }
 * 
 * Safety & Integrity:
 * - Never silently falls back to mock or rule-based data on API failure.
 * - Never automatically retries failed generations.
 * - Renders all model output as untrusted text.
 */

export interface LikelyCause {
  description: string;
  confidence: 'low' | 'medium' | 'high';
}

export interface MatchedRecipe {
  id: string;
  title: string;
  path?: string;
}

export interface OopsieReport {
  summary: string;
  plain_explanation: string;
  error_category: string;
  likely_causes: LikelyCause[];
  missing_context_questions: string[];
  risk_level: 'low' | 'medium' | 'high';
  warnings: string[];
  repair_prompt: string;
  verification_steps: string[];
  matched_recipes: MatchedRecipe[];
}

export interface OopsieApiMetadata {
  prompt_tokens?: number;
  generated_tokens?: number;
  budget_hit?: boolean;
  duration_ms?: number;
  system_prompt_version?: string;
  engine_mode?: 'mock' | 'real_model' | string;
}

export interface OopsieSuccessEnvelope {
  status: 'success';
  request_id: string;
  model_version: string;
  formatter_version: string;
  data: OopsieReport;
  metadata: OopsieApiMetadata;
}

export interface OopsieErrorDetail {
  code: string;
  message: string;
}

export interface OopsieErrorEnvelope {
  status: 'error';
  request_id?: string;
  error: OopsieErrorDetail;
}

export class OopsieApiError extends Error {
  readonly code: string;
  readonly status: number;
  readonly requestId?: string;

  constructor(message: string, code: string, status: number, requestId?: string) {
    super(message);
    this.name = 'OopsieApiError';
    this.code = code;
    this.status = status;
    this.requestId = requestId;
  }
}

/**
 * Resolves the effective backend endpoint.
 * - If VITE_OOPSIE_API_URL is set, uses it (normalizing to append /v1/analyze if given a base host).
 * - Otherwise defaults to empty/undefined (allowing client to use local rule demo or dev proxy).
 */
export function getApiEndpointUrl(): string | undefined {
  const envUrl = import.meta.env.VITE_OOPSIE_API_URL;
  if (!envUrl || typeof envUrl !== 'string') return undefined;
  const trimmed = envUrl.trim();
  if (!trimmed) return undefined;

  // If user passed base URL like http://127.0.0.1:8000, normalize to /v1/analyze
  if (!trimmed.endsWith('/analyze') && !trimmed.endsWith('/analyze/')) {
    return trimmed.replace(/\/+$/, '') + '/v1/analyze';
  }
  return trimmed;
}

export interface AnalyzeOptions {
  context?: Record<string, unknown>;
  systemPromptVersion?: 'system_prompt_v2_enum_guided' | 'system_prompt_v1';
  signal?: AbortSignal;
}

/**
 * Validates the structure of the data report inside the success envelope.
 */
export function isValidOopsieReport(data: unknown): data is OopsieReport {
  if (!data || typeof data !== 'object' || Array.isArray(data)) return false;
  const r = data as Record<string, unknown>;
  return (
    typeof r.summary === 'string' &&
    typeof r.plain_explanation === 'string' &&
    typeof r.error_category === 'string' &&
    Array.isArray(r.likely_causes) &&
    r.likely_causes.every(
      c =>
        c &&
        typeof c === 'object' &&
        typeof (c as Record<string, unknown>).description === 'string' &&
        ['low', 'medium', 'high'].includes(String((c as Record<string, unknown>).confidence))
    ) &&
    Array.isArray(r.missing_context_questions) &&
    r.missing_context_questions.every(q => typeof q === 'string') &&
    ['low', 'medium', 'high'].includes(String(r.risk_level)) &&
    Array.isArray(r.warnings) &&
    r.warnings.every(w => typeof w === 'string') &&
    typeof r.repair_prompt === 'string' &&
    Array.isArray(r.verification_steps) &&
    r.verification_steps.every(s => typeof s === 'string') &&
    Array.isArray(r.matched_recipes)
  );
}

/**
 * Maps known OOPSIE error codes to clear, actionable developer guidance.
 */
export function mapErrorCodeToUserMessage(code: string, rawMessage: string): string {
  switch (code) {
    case 'CAPACITY_LIMIT':
      return `Service Busy (HTTP 429): The GPU inference service is currently at maximum capacity (single-worker admission active). Please wait for the current generation to finish and try again.`;
    case 'MODEL_UNAVAILABLE':
      return `Model Unavailable (HTTP 503): The inference model or adapter weights are not loaded into memory. Ensure the backend is initialized.`;
    case 'INVALID_INPUT':
      return `Invalid Request (HTTP 400): ${rawMessage}`;
    case 'PARSE_ERROR':
      return `JSON Parse Rejection (HTTP 422): The model output could not be strictly parsed as valid JSON. Incomplete or malformed responses are rejected for safety.`;
    case 'SCHEMA_ERROR':
      return `Schema Conformance Failure (HTTP 422): The model output failed strict JSON schema validation. ${rawMessage}`;
    case 'OUTPUT_BUDGET_EXCEEDED':
      return `Token Budget Exceeded (HTTP 422): The generation hit the maximum token budget before completing. Incomplete outputs are rejected for safety.`;
    case 'GENERATION_ERROR':
      return `Generation Error (HTTP 500): An error occurred during tensor operations on the inference engine.`;
    case 'NETWORK_ERROR':
      return rawMessage;
    default:
      return `${code}: ${rawMessage}`;
  }
}

/**
 * Calls the OOPSIE /v1/analyze inference API endpoint.
 * Rejects with OopsieApiError on any envelope or HTTP error.
 */
export async function analyzeErrorWithApi(
  errorText: string,
  options?: AnalyzeOptions
): Promise<OopsieSuccessEnvelope> {
  const endpoint = getApiEndpointUrl();
  if (!endpoint) {
    throw new OopsieApiError(
      'No inference API endpoint is configured (VITE_OOPSIE_API_URL is unset).',
      'ENDPOINT_UNCONFIGURED',
      0
    );
  }

  const payload: Record<string, unknown> = {
    error_text: errorText,
  };
  if (options?.context) {
    payload.context = options.context;
  }
  if (options?.systemPromptVersion) {
    payload.system_prompt_version = options.systemPromptVersion;
  }

  let response: Response;
  try {
    response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: options?.signal,
    });
  } catch (err: unknown) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new OopsieApiError(
        'The request was cancelled by the browser. Note: cancelling in the browser does not stop ongoing GPU inference on the backend.',
        'REQUEST_ABORTED',
        0
      );
    }
    const message = err instanceof Error ? err.message : String(err);
    throw new OopsieApiError(
      `Could not reach the OOPSIE inference service at ${endpoint}. Please verify that the backend is running and reachable. (${message})`,
      'NETWORK_ERROR',
      0
    );
  }

  let body: unknown;
  try {
    body = await response.json();
  } catch {
    const rawText = await response.text().catch(() => '');
    throw new OopsieApiError(
      `Inference service returned a non-JSON response (HTTP ${response.status}): ${rawText.slice(0, 200)}`,
      'INVALID_RESPONSE',
      response.status
    );
  }

  // Handle standard error envelope
  if (!response.ok || (body && typeof body === 'object' && (body as Record<string, unknown>).status === 'error')) {
    const errObj = body as Partial<OopsieErrorEnvelope>;
    const code = errObj.error?.code || `HTTP_${response.status}`;
    const rawMsg = errObj.error?.message || `Inference API returned HTTP ${response.status}.`;
    const userMsg = mapErrorCodeToUserMessage(code, rawMsg);
    throw new OopsieApiError(userMsg, code, response.status, errObj.request_id);
  }

  // Handle success envelope
  const successObj = body as Partial<OopsieSuccessEnvelope>;
  if (successObj.status !== 'success' || !successObj.data) {
    throw new OopsieApiError(
      'Inference API returned a response missing status="success" or data.',
      'INVALID_RESPONSE_FORMAT',
      response.status
    );
  }

  if (!isValidOopsieReport(successObj.data)) {
    throw new OopsieApiError(
      'Inference API returned a report that failed frontend client schema validation.',
      'CLIENT_VALIDATION_ERROR',
      response.status,
      successObj.request_id
    );
  }

  return successObj as OopsieSuccessEnvelope;
}
