import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

function read(relativePath) {
  return fs.readFileSync(new URL(`../${relativePath}`, import.meta.url), 'utf8');
}

test('process policy defines six real stages and methodology WIP limits', () => {
  const text = read('docs/process/README.md');
  for (const stage of ['Backlog', 'Ready', 'In Progress', 'Waiting', 'Review', 'Done']) assert.match(text, new RegExp(stage));
  assert.match(text, /әр адамға 2/);
  assert.match(text, /Review.*3/);
});

test('DoR and DoD are explicit and DoD contains all four methodology gates', () => {
  const text = read('docs/process/dor-dod.md');
  for (const gate of ['тест', 'екінші', 'стенд', 'құжаттама']) assert.match(text.toLowerCase(), new RegExp(gate));
});

test('retrospective contains exactly one measurable action with owner deadline and metric', () => {
  const text = read('docs/process/retrospective.md');
  assert.equal((text.match(/^## Қабылданған әрекет$/gm) ?? []).length, 1);
  assert.match(text, /Альфараби/);
  assert.match(text, /13\.10\.2026/);
  assert.match(text, /кемінде 3/);
});
