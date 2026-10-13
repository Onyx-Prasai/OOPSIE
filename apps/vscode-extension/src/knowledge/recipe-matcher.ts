import * as vscode from 'vscode';
import { loadRecipes, Recipe } from './recipe-loader';

export async function findMatchingRecipe(
  extensionUri: vscode.Uri,
  errorText: string,
): Promise<Recipe | undefined> {
  const normalizedError = errorText.toLocaleLowerCase();
  const recipes = await loadRecipes(extensionUri);

  return recipes
    .map(recipe => ({
      recipe,
      matches: signaturesFor(recipe.content).filter(signature =>
        normalizedError.includes(signature.toLocaleLowerCase()),
      ).length,
    }))
    .filter(result => result.matches > 0)
    .sort((left, right) => right.matches - left.matches)[0]?.recipe;
}

function signaturesFor(recipe: string): string[] {
  const section = recipe.split(/^## Target Error Signatures\s*$/im)[1]?.split(/^## /m)[0] ?? '';
  return [...section.matchAll(/`([^`]+)`/g)]
    .map(match => match[1].trim())
    .filter(Boolean);
}
