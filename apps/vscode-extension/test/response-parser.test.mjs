import test from 'node:test';
import assert from 'node:assert/strict';
import {
  unwrapAndValidateResponse,
  validateOopsieReport,
  OopsieServiceError,
} from '../out/ai/response-parser.js';

const VALID_SAMPLE_REPORT = {
  summary: 'Database connection failed during startup.',
  plain_explanation: 'The application could not reach PostgreSQL because DATABASE_URL was missing.',
  error_category: 'database',
  likely_causes: [
    { description: 'DATABASE_URL is missing in environment variables.', confidence: 'high' },
  ],
  missing_context_questions: ['Is the database service running?'],
  risk_level: 'medium',
  warnings: ['This may affect stored data.'],
  repair_prompt: 'Please check your environment configuration.',
  verification_steps: ['Run npm run start and check logs.'],
  matched_recipes: [
    { id: 'kb-db-001', title: 'PostgreSQL connection timeout' },
  ],
};

test('1. Valid success envelope unwrap and validation', () => {
  const envelope = {
    status: 'success',
    request_id: 'req-success-100',
    model_version: 'gemma-4-12b-it-pilot',
    formatter_version: 'training_aligned_v1',
    data: VALID_SAMPLE_REPORT,
    metadata: {
      duration_ms: 120.5,
      engine_mode: 'mock',
    },
  };

  const report = unwrapAndValidateResponse(envelope);
  assert.equal(report.summary, VALID_SAMPLE_REPORT.summary);
  assert.equal(report.error_category, 'database');
  assert.equal(report.risk_level, 'medium');
  assert.equal(report.likely_causes.length, 1);
  assert.equal(report.matched_recipes[0].id, 'kb-db-001');
});

test('2. Error envelope throws typed OopsieServiceError with code and message', () => {
  const errorEnvelope = {
    status: 'error',
    request_id: 'req-err-429',
    error: {
      code: 'CAPACITY_LIMIT',
      message: 'The inference service is currently at maximum capacity. Please retry shortly.',
    },
  };

  assert.throws(
    () => unwrapAndValidateResponse(errorEnvelope),
    (err) => {
      assert(err instanceof OopsieServiceError);
      assert.equal(err.code, 'CAPACITY_LIMIT');
      assert.equal(err.requestId, 'req-err-429');
      assert.match(err.message, /CAPACITY_LIMIT/);
      assert.match(err.message, /maximum capacity/);
      return true;
    }
  );
});

test('3. Malformed success envelope (missing or null data) throws descriptive error', () => {
  const missingDataEnvelope = {
    status: 'success',
    request_id: 'req-malformed-001',
    metadata: {},
  };

  assert.throws(
    () => unwrapAndValidateResponse(missingDataEnvelope),
    /Malformed success envelope: missing or invalid 'data' property/
  );

  const nullDataEnvelope = {
    status: 'success',
    data: null,
  };

  assert.throws(
    () => unwrapAndValidateResponse(nullDataEnvelope),
    /Malformed success envelope: missing or invalid 'data' property/
  );
});

test('4. Invalid report schema inside success envelope is rejected', () => {
  const invalidCategoryEnvelope = {
    status: 'success',
    data: {
      ...VALID_SAMPLE_REPORT,
      error_category: 'invalid_category_not_in_enum',
    },
  };

  assert.throws(
    () => unwrapAndValidateResponse(invalidCategoryEnvelope),
    /The model response does not match the OOPSIE report schema/
  );

  const missingExplanationEnvelope = {
    status: 'success',
    data: {
      ...VALID_SAMPLE_REPORT,
      plain_explanation: undefined,
    },
  };

  assert.throws(
    () => unwrapAndValidateResponse(missingExplanationEnvelope),
    /The model response does not match the OOPSIE report schema/
  );
});

test('5. Legacy direct raw-report (without status envelope) is supported and validated', () => {
  const report = unwrapAndValidateResponse(VALID_SAMPLE_REPORT);
  assert.equal(report.summary, VALID_SAMPLE_REPORT.summary);
  assert.equal(report.error_category, 'database');
});

test('6. Unrecognized envelope status or non-object payload is rejected', () => {
  assert.throws(
    () => unwrapAndValidateResponse({ status: 'pending' }),
    /Unrecognized response envelope/
  );

  assert.throws(
    () => unwrapAndValidateResponse('not a json object'),
    /The model returned invalid JSON/
  );

  assert.throws(
    () => unwrapAndValidateResponse(42),
    /The model response must be a JSON object/
  );
});
