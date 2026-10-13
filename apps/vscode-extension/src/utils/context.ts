import * as vscode from 'vscode';

export function limitContextLines(text: string): string {
  const maximum = vscode.workspace.getConfiguration('oopsie').get<number>('maxContextLines', 200);
  if (!Number.isSafeInteger(maximum) || maximum < 1) {
    throw new Error('OOPSIE setting "maxContextLines" must be a positive whole number.');
  }

  return text.split(/\r?\n/).slice(-maximum).join('\n');
}
