import { cp, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const extensionRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const repositoryRoot = path.resolve(extensionRoot, '..', '..');
const dataRoot = path.join(extensionRoot, 'out', 'data');

await mkdir(dataRoot, { recursive: true });
await cp(
  path.join(repositoryRoot, 'knowledge-base'),
  path.join(dataRoot, 'knowledge-base'),
  { recursive: true },
);
