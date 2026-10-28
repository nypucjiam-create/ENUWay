import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../tools/lz9-artifact/build-workbook.mjs', import.meta.url), 'utf8');

test('summary formulas reference the populated work-item rows 5 through 9', () => {
  assert.match(source, /\$C\$5:\$C\$9/);
  assert.match(source, /\$G\$5:\$G\$9/);
  assert.doesNotMatch(source, /\$C\$2:\$C\$6/);
});

test('cycle hours are written from validated evidence rather than unsupported date arithmetic', () => {
  assert.match(source, /cycleHours/);
  assert.doesNotMatch(source, /\=\(F\$\{row\}-E\$\{row\}\)\*24/);
});

test('workbook preserves Kazakhstan wall-clock timestamps and uses titled CFD tables', () => {
  assert.match(source, /Date\.UTC/);
  assert.match(source, /Спринт 2 CFD деректері/);
  assert.doesNotMatch(source, /cfd\.getRange\('B19:E32'\)/);
});
