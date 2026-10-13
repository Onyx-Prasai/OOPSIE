import * as vscode from 'vscode';

export async function requestTerminalLog(): Promise<string | undefined> {
  return vscode.window.showInputBox({
    prompt: 'Paste your terminal output or error log here',
    placeHolder: 'npm error, build failure, stack trace...',
    ignoreFocusOut: true,
  });
}
