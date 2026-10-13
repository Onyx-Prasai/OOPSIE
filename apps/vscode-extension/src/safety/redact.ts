import * as vscode from 'vscode';

// Patterns for secrets that should never be sent to an AI model
const REDACTION_PATTERNS: Array<{ name: string; regex: RegExp; replacement: string }> = [
  { name: 'JWT',            regex: /eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+/g,  replacement: '[REDACTED_JWT]' },
  { name: 'AWS Key',        regex: /AKIA[0-9A-Z]{16}/g,                                      replacement: '[REDACTED_AWS_KEY]' },
  { name: 'GitHub Token',   regex: /ghp_[a-zA-Z0-9]{36}/g,                                   replacement: '[REDACTED_GH_TOKEN]' },
  { name: 'Generic Secret', regex: /(secret|password|api_key|apikey|token)=["']?[^\s"']+/gi, replacement: '$1=[REDACTED]' },
  { name: 'Private Key',    regex: /-----BEGIN (RSA |EC )?PRIVATE KEY-----[\s\S]+?-----END/g, replacement: '[REDACTED_PRIVATE_KEY]' },
];

export function redactSecrets(input: string): string {
  let result = input;
  for (const pattern of REDACTION_PATTERNS) {
    result = result.replace(pattern.regex, pattern.replacement);
  }
  return result;
}

export function countRedactions(original: string): number {
  let count = 0;
  for (const pattern of REDACTION_PATTERNS) {
    const matches = original.match(pattern.regex);
    if (matches) count += matches.length;
  }
  return count;
}

export function sanitizeSecrets(input: string): { text: string; count: number } {
  const enabled = vscode.workspace.getConfiguration('oopsie').get<boolean>('redactSecrets', true);
  if (!enabled) return { text: input, count: 0 };
  return { text: redactSecrets(input), count: countRedactions(input) };
}
