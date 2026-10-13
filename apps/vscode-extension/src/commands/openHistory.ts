import * as vscode from 'vscode';
import { OopsiePanel } from '../panels/OopsiePanel';

export async function openHistory(panel: OopsiePanel): Promise<void> {
  const history = await panel.getHistory();
  if (history.length === 0) {
    await vscode.window.showInformationMessage('OOPSIE: No error analyses have been saved yet.');
    return;
  }

  const selected = await vscode.window.showQuickPick(
    history.map((item, index) => ({
      label: item.report.summary,
      description: new Date(item.createdAt).toLocaleString(),
      index,
    })),
    { placeHolder: 'Select an OOPSIE analysis to view' },
  );

  if (selected) panel.showReport(history[selected.index].report);
}
