import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const src = path.join(root, 'apps', 'web-demo', 'dist');
const dst = path.join(root, 'dist');

if (fs.existsSync(src)) {
  fs.mkdirSync(dst, { recursive: true });
  fs.cpSync(src, dst, { recursive: true, force: true });
  console.log(`Synced web build artifacts: ${src} -> ${dst}`);
}
