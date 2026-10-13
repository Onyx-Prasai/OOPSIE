import * as vscode from 'vscode';

export async function contributeRecipe(): Promise<void> {
  const title = encodeURIComponent('New Error Recipe');
  const body = encodeURIComponent([
    '## Framework',
    '',
    '## Error signature',
    '',
    '## Explanation and safe repair steps',
    '',
    'Please do not include secrets, access tokens, or private project data.',
  ].join('\n'));
  const issueUrl = vscode.Uri.parse(
    `https://github.com/Onyx-Prasai/OOPSIE/issues/new?title=${title}&body=${body}&labels=recipe`,
  );
  await vscode.env.openExternal(issueUrl);
}
