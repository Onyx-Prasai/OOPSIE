import * as vscode from 'vscode';

export function registerHoverProvider(): vscode.Disposable {
  const provider: vscode.HoverProvider = {
    provideHover(document, position): vscode.Hover | undefined {
      const diagnostic = vscode.languages.getDiagnostics(document.uri).find(item =>
        item.range.contains(position),
      );
      if (!diagnostic) return undefined;

      return new vscode.Hover(
        new vscode.MarkdownString(
          `**OOPSIE detected a problem**\n\n${diagnostic.message}\n\nRun **OOPSIE: Explain This Problem** for a plain-English explanation.`,
        ),
        diagnostic.range,
      );
    },
  };

  return vscode.languages.registerHoverProvider(
    [{ language: 'javascript' }, { language: 'javascriptreact' }, { language: 'typescript' }, { language: 'typescriptreact' }],
    provider,
  );
}
