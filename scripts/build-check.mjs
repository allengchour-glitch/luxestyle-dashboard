#!/usr/bin/env node
// Build-/Validierungslauf fuer das statische Dashboard.
// Kein Bundler noetig - geprueft wird, was sonst erst live auffaellt:
// Script-Bloecke in index.html, deren JS-Syntax, Tag-Balance und die Netlify-Functions.
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { join, dirname } from 'node:path';
import vm from 'node:vm';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const errors = [];
const ok = (msg) => console.log('  OK   ' + msg);
const fail = (msg) => { errors.push(msg); console.log('  FAIL ' + msg); };

console.log('index.html');
const html = readFileSync(join(ROOT, 'index.html'), 'utf8');

// Nur Inline-Bloecke - Bloecke mit src= haben keinen Body zum Pruefen.
const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
if (blocks.length === 3) ok('3 Script-Bloecke gefunden');
else fail(`erwartet 3 Script-Bloecke (Theme-Init, Content-Tab, Haupt-Skript), gefunden ${blocks.length}`);

blocks.forEach((code, i) => {
  try {
    new vm.Script(code, { filename: `index.html#script[${i}]` });
    ok(`Script-Block ${i} syntaktisch valide (${code.length} Zeichen)`);
  } catch (e) {
    fail(`Script-Block ${i}: ${e.message}`);
  }
});

const open = (html.match(/<div\b/g) || []).length;
const close = (html.match(/<\/div>/g) || []).length;
if (open === close) ok(`div-Balance ${open}/${close}`);
else fail(`div-Balance unausgeglichen: ${open} <div> vs. ${close} </div>`);

console.log('netlify/functions');
const fnDir = join(ROOT, 'netlify', 'functions');
for (const file of readdirSync(fnDir).filter((f) => f.endsWith('.js'))) {
  try {
    execFileSync(process.execPath, ['--check', join(fnDir, file)], { stdio: 'pipe' });
    ok(`${file} syntaktisch valide`);
  } catch (e) {
    fail(`${file}: ${String(e.stderr || e.message).trim().split('\n').slice(0, 3).join(' | ')}`);
  }
}

console.log('');
if (errors.length) {
  console.error(`Build fehlgeschlagen - ${errors.length} Problem(e).`);
  process.exit(1);
}
console.log('Build ok - statische Dateien sind deploy-bereit.');
