import * as vscode from 'vscode';

export function registerDiagnosticsProvider(): vscode.Disposable {
  const provider: vscode.CodeActionProvider = {
    provideCodeActions(
      _document: vscode.TextDocument,
      _range: vscode.Range | vscode.Selection,
      context: vscode.CodeActionContext,
    ): vscode.CodeAction[] {
      return context.diagnostics.map(diagnostic => {
        const action = new vscode.CodeAction(
          'Explain this problem with OOPSIE',
          vscode.CodeActionKind.QuickFix,
        );
        action.command = {
          command: 'oopsie.analyzeDiagnostic',
          title: 'Explain this problem with OOPSIE',
          arguments: [diagnostic.message],
        };
        return action;
      });
    },
  };

  return vscode.languages.registerCodeActionsProvider(
    { scheme: 'file' },
    provider,
    { providedCodeActionKinds: [vscode.CodeActionKind.QuickFix] },
  );
}
