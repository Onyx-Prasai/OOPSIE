import * as vscode from 'vscode';

let channel: vscode.OutputChannel | undefined;

export function getOutputChannel(): vscode.OutputChannel {
  channel ??= vscode.window.createOutputChannel('OOPSIE');
  return channel;
}
