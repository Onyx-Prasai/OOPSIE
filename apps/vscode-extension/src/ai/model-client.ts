import * as vscode from 'vscode';
import { parseOopsieReport } from './response-parser';
import { OopsieReport } from '../types/oopsie';

export async function callModel(prompt: string): Promise<OopsieReport> {
  const config = vscode.workspace.getConfiguration('oopsie');
  const baseUrl = config.get<string>('apiBaseUrl', 'http://127.0.0.1:8000').replace(/\/+$/, '');

  try {
    const response = await fetch(`${baseUrl}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error_text: prompt }),
    });
    const data = await readJson(response);
    return parseOopsieReport(JSON.stringify(data));
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    await vscode.window.showErrorMessage(`OOPSIE: Model call failed — ${message}`);
    throw err;
  }
}

async function readJson(response: Response): Promise<unknown> {
  if (!response.ok) {
    throw new Error(`Model endpoint returned HTTP ${response.status} ${response.statusText}.`);
  }
  return response.json() as Promise<unknown>;
}
