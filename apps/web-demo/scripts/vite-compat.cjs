#!/usr/bin/env node
require('./patch-node-styleText.cjs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const viteDir = path.dirname(require.resolve('vite/package.json'));
const binUrl = pathToFileURL(path.join(viteDir, 'bin', 'vite.js')).href;
import(binUrl);
