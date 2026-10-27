import * as vscode from 'vscode';
import { unwrapAndValidateResponse } from './response-parser';
import { OopsieReport } from '../types/oopsie';

export async function callModel(prompt: string): Promise<OopsieReport> {
  const config = vscode.workspace.getConfiguration('oopsie');
  const baseUrl = config.get<string>('apiBaseUrl', 'http://127.0.0.1:8000').replace(/\/+$/, '');

  try {
    const response = await fetch(`${baseUrl}/v1/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error_text: prompt }),
    });

    let payload: unknown;
    try {
      payload = await response.json();
    } catch {
      throw new Error(`Model endpoint returned HTTP ${response.status} ${response.statusText} with non-JSON body.`);
    }

    return unwrapAndValidateResponse(payload);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    await vscode.window.showErrorMessage(`OOPSIE: Model call failed — ${message}`);
    throw err;
  }
}
