import * as vscode from 'vscode';
import { OopsieReport } from '../types/oopsie';
import { AnalysisHistoryItem, addHistoryItem } from '../utils/storage';

type PanelMessage =
  | { type: 'loading' }
  | { type: 'report'; report: OopsieReport }
  | { type: 'prompt'; prompt: string };

export class OopsiePanel implements vscode.WebviewViewProvider {
  private view?: vscode.WebviewView;

  constructor(
    readonly extensionUri: vscode.Uri,
    private readonly globalState: vscode.Memento,
  ) {}

  resolveWebviewView(view: vscode.WebviewView): void {
    this.view = view;
    view.webview.options = { enableScripts: true };
    view.webview.html = this.renderHtml(view.webview);
    view.webview.onDidReceiveMessage(async (message: { type?: string }) => {
      if (message.type === 'fixed') {
        await vscode.window.showInformationMessage('OOPSIE: Thanks for the feedback!');
      } else if (message.type === 'notFixed') {
        await vscode.window.showInformationMessage('OOPSIE: Your feedback will help improve future recipes.');
      }
    });
  }

  showLoading(): void {
    this.postMessage({ type: 'loading' });
  }

  showReport(report: OopsieReport): void {
    this.postMessage({ type: 'report', report });
  }

  showRepairPromptCopied(prompt: string): void {
    this.postMessage({ type: 'prompt', prompt });
  }

  async saveAnalysis(errorText: string, report: OopsieReport): Promise<void> {
    await addHistoryItem(this.globalState, { errorText, report, createdAt: Date.now() });
  }

  async getHistory(): Promise<AnalysisHistoryItem[]> {
    const stored = this.globalState.get<AnalysisHistoryItem[]>('oopsie.analysisHistory', []);
    return Array.isArray(stored) ? stored : [];
  }

  private postMessage(message: PanelMessage): void {
    if (this.view) {
      void this.view.webview.postMessage(message);
    } else {
      void vscode.commands.executeCommand('oopsie.panel.focus');
      setTimeout(() => {
        if (this.view) void this.view.webview.postMessage(message);
      }, 100);
    }
  }

  private renderHtml(webview: vscode.Webview): string {
    const nonce = getNonce();
    const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(this.extensionUri, 'media', 'styles', 'panel.css'));
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource}; script-src 'nonce-${nonce}';">
  <link href="${styleUri}" rel="stylesheet">
  <title>OOPSIE Error Recovery</title>
</head>
<body>
  <main>
    <h1>OOPSIE</h1>
    <p id="status">Select an error and run <strong>OOPSIE: Explain Selected Error</strong>, or paste a log with <strong>OOPSIE: Analyze Terminal Output</strong>.</p>
    <section id="result" hidden>
      <h2>What happened</h2><p id="explanation"></p>
      <h2>Likely causes</h2><ul id="causes"></ul>
      <h2>Risk</h2><p id="risk"></p><ul id="risk-notes"></ul>
      <h2>Repair prompt</h2><pre id="prompt"></pre>
      <button id="copy">Copy repair prompt</button>
      <h2>Check after fixing</h2><ul id="checklist"></ul>
      <p>Did this fix it?</p>
      <button data-feedback="fixed">Yes</button>
      <button data-feedback="notFixed">No</button>
    </section>
  </main>
  <script nonce="${nonce}">
    const vscode = acquireVsCodeApi();
    const status = document.getElementById('status');
    const result = document.getElementById('result');
    let repairPrompt = '';
    const fillList = (id, values) => {
      const list = document.getElementById(id);
      list.replaceChildren(...values.map(value => {
        const item = document.createElement('li');
        item.textContent = value;
        return item;
      }));
    };
    window.addEventListener('message', event => {
      const message = event.data;
      if (message.type === 'loading') {
        status.textContent = 'Analyzing your error…';
        result.hidden = true;
      } else if (message.type === 'report') {
        const report = message.report;
        status.textContent = report.summary;
        document.getElementById('explanation').textContent = report.plain_explanation;
        document.getElementById('risk').textContent = report.risk_level;
        document.getElementById('prompt').textContent = report.repair_prompt;
        repairPrompt = report.repair_prompt;
        fillList('causes', report.likely_causes.map(cause => cause.description + ' (' + cause.confidence + ')'));
        fillList('risk-notes', report.warnings);
        fillList('checklist', report.verification_steps);
        result.hidden = false;
      } else if (message.type === 'prompt') {
        repairPrompt = message.prompt;
        status.textContent = 'Repair prompt copied to clipboard.';
      }
    });
    document.getElementById('copy').addEventListener('click', async () => {
      await navigator.clipboard.writeText(repairPrompt);
    });
    document.querySelectorAll('[data-feedback]').forEach(button => {
      button.addEventListener('click', () => vscode.postMessage({ type: button.dataset.feedback }));
    });
  </script>
</body>
</html>`;
  }
}

function getNonce(): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  return Array.from({ length: 32 }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
}
