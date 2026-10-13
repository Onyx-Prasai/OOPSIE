import * as vscode from 'vscode';
import { OopsiePanel } from '../panels/OopsiePanel';
import { buildRepairPrompt } from '../ai/prompt-builder';
import { sanitizeSecrets } from '../safety/redact';
import { limitContextLines } from '../utils/context';

export async function generateRepairPrompt(panel: OopsiePanel): Promise<void> {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showWarningMessage('OOPSIE: Open a file and select an error first.');
    return;
  }

  const selectedText = editor.document.getText(editor.selection);
  if (!selectedText.trim()) {
    vscode.window.showWarningMessage('OOPSIE: Select an error or code snippet before generating a repair prompt.');
    return;
  }
  let limitedSelection: string;
  try {
    limitedSelection = limitContextLines(selectedText);
  } catch (error) {
    await vscode.window.showErrorMessage(error instanceof Error ? error.message : String(error));
    return;
  }
  const sanitized = sanitizeSecrets(limitedSelection);

  const prompt = buildRepairPrompt({
    errorText: sanitized.text,
    filePath: editor.document.fileName,
    selectedCode: sanitized.text,
    framework: detectFramework(editor.document.fileName),
  });

  await vscode.env.clipboard.writeText(prompt);
  panel.showRepairPromptCopied(prompt);
  vscode.window.showInformationMessage('OOPSIE: Repair prompt copied to clipboard!');
}

function detectFramework(filePath: string): string {
  if (filePath.includes('next')) return 'Next.js';
  if (filePath.includes('supabase')) return 'Supabase';
  if (filePath.includes('firebase')) return 'Firebase';
  return 'React';
}
