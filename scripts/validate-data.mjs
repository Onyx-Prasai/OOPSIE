import { existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const script = join(root, 'training', 'validate_data.py');
const candidates = [
  join(root, '.venv', 'Scripts', 'python.exe'),
  join(root, '.venv', 'bin', 'python.exe'),
  join(root, '.venv', 'bin', 'python'),
  'python',
  'python3',
];

for (const interpreter of candidates) {
  if (interpreter.includes(root) && !existsSync(interpreter)) continue;
  const result = spawnSync(interpreter, [script, ...process.argv.slice(2)], {
    cwd: root,
    stdio: 'inherit',
  });
  if (result.error?.code === 'ENOENT') continue;
  if (result.error) {
    console.error(`Could not run dataset validation with ${interpreter}: ${result.error.message}`);
    process.exit(2);
  }
  process.exit(result.status ?? 2);
}

console.error('Python was not found. Install Python or create a project .venv and retry.');
process.exit(2);
