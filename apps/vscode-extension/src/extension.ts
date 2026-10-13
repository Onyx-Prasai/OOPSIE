import * as vscode from 'vscode';
import { OopsiePanel } from './panels/OopsiePanel';
import { analyzeSelection } from './commands/analyzeError';
import { analyzeTerminal } from './commands/analyzeError';
import { generateRepairPrompt } from './commands/generateRepairPrompt';
import { openHistory } from './commands/openHistory';
import { contributeRecipe } from './commands/contributeRecipe';
import { registerDiagnosticsProvider } from './providers/diagnostics-provider';
import { registerHoverProvider } from './providers/hover-provider';

export function activate(context: vscode.ExtensionContext) {
  const panel = new OopsiePanel(context.extensionUri, context.globalState);
  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider('oopsie.panel', panel),
    registerDiagnosticsProvider(),
    registerHoverProvider(),
  );

  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand('oopsie.analyzeSelection', () =>
      analyzeSelection(panel)
    ),
    vscode.commands.registerCommand('oopsie.analyzeTerminal', () =>
      analyzeTerminal(panel)
    ),
    vscode.commands.registerCommand('oopsie.analyzeDiagnostic', (diagnostic) =>
      analyzeSelection(panel, typeof diagnostic === 'string' ? diagnostic : diagnostic?.message)
    ),
    vscode.commands.registerCommand('oopsie.generateRepairPrompt', () =>
      generateRepairPrompt(panel)
    ),
    vscode.commands.registerCommand('oopsie.openHistory', () =>
      openHistory(panel)
    ),
    vscode.commands.registerCommand('oopsie.contributeRecipe', () =>
      contributeRecipe()
    )
  );
}

export function deactivate() {}
