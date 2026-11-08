import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const require = createRequire(import.meta.url);

const serverCjs = path.join(__dirname, 'dist', 'server.cjs');

if (!fs.existsSync(serverCjs)) {
  console.log('[server.js] dist/server.cjs not found, compiling build...');
  const { execSync } = require('node:child_process');
  execSync('npm run build', { stdio: 'inherit' });
}

require(serverCjs);
