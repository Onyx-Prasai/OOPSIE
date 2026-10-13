import * as vscode from 'vscode';

export interface Recipe {
  path: string;
  content: string;
}

export async function loadRecipes(extensionUri: vscode.Uri): Promise<Recipe[]> {
  const recipeRoot = vscode.Uri.joinPath(extensionUri, 'out', 'data', 'knowledge-base');
  const recipes: Recipe[] = [];

  async function visit(directory: vscode.Uri): Promise<void> {
    for (const [name, type] of await vscode.workspace.fs.readDirectory(directory)) {
      const entry = vscode.Uri.joinPath(directory, name);
      if (type === vscode.FileType.Directory) {
        await visit(entry);
      } else if (type === vscode.FileType.File && name.endsWith('.md') && name !== '_template.md') {
        recipes.push({
          path: vscode.workspace.asRelativePath(entry),
          content: Buffer.from(await vscode.workspace.fs.readFile(entry)).toString('utf8'),
        });
      }
    }
  }

  await visit(recipeRoot);
  return recipes;
}
