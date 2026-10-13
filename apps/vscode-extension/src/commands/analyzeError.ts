import * as vscode from 'vscode';
import { OopsiePanel } from '../panels/OopsiePanel';
import { callModel } from '../ai/model-client';
import { sanitizeSecrets } from '../safety/redact';
import { findMatchingRecipe } from '../knowledge/recipe-matcher';
import { limitContextLines } from '../utils/context';

export async function analyzeSelection(panel: OopsiePanel, text?: string): Promise<void> {
  const editor = vscode.window.activeTextEditor;
  const errorText = text ?? editor?.document.getText(editor.selection) ?? '';

  if (!errorText.trim()) {
    vscode.window.showWarningMessage('OOPSIE: Select an error or paste one to analyze.');
    return;
  }

  panel.showLoading();

  let limitedError: string;
  let limitedCode: string | undefined;
  try {
    limitedError = limitContextLines(errorText);
    limitedCode = editor ? limitContextLines(editor.document.getText(editor.selection)) : undefined;
  } catch (error) {
    await vscode.window.showErrorMessage(error instanceof Error ? error.message : String(error));
    return;
  }
  const sanitizedError = sanitizeSecrets(limitedError);
  const sanitizedCode = limitedCode === undefined ? undefined : sanitizeSecrets(limitedCode).text;
  const recipe = await findMatchingRecipe(panel.extensionUri, sanitizedError.text);
  const analysisInput = buildErrorInput(sanitizedError.text, sanitizedCode, recipe?.content);
  const report = await callModel(analysisInput);
  await panel.saveAnalysis(sanitizedError.text, report);
  panel.showReport(report);
}

export async function analyzeTerminal(panel: OopsiePanel): Promise<void> {
  const input = await vscode.window.showInputBox({
    prompt: 'Paste your terminal output or error log here',
    placeHolder: 'npm error, build failure, stack trace...',
    ignoreFocusOut: true,
  });

  if (!input) return;

  panel.showLoading();
  let limitedInput: string;
  try {
    limitedInput = limitContextLines(input);
  } catch (error) {
    await vscode.window.showErrorMessage(error instanceof Error ? error.message : String(error));
    return;
  }
  const sanitizedInput = sanitizeSecrets(limitedInput);
  const recipe = await findMatchingRecipe(panel.extensionUri, sanitizedInput.text);
  const analysisInput = buildErrorInput(sanitizedInput.text, undefined, recipe?.content);
  const report = await callModel(analysisInput);
  await panel.saveAnalysis(sanitizedInput.text, report);
  panel.showReport(report);
}

function buildErrorInput(
  errorText: string,
  selectedCode?: string,
  matchedRecipe?: string,
): string {
  return [
    errorText,
    selectedCode ? `Selected code:\n${selectedCode}` : '',
    matchedRecipe ? `Relevant community recipe:\n${matchedRecipe}` : '',
  ].filter(Boolean).join('\n\n');
}
