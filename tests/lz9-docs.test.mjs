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

test('live board configuration is recorded with the final column order and native limits', () => {
  const text = read('docs/process/board-configuration.md');
  assert.match(text, /Backlog → Ready → In Progress → Waiting → Review → Done/);
  for (const limit of ['Ready — 6', 'In Progress — 6', 'Waiting — 2', 'Review — 3']) {
    assert.match(text, new RegExp(limit));
  }
  assert.match(text, /github\.com\/users\/nypucjiam-create\/projects\/3/);
});

test('methodology checklist maps every required evidence category and keeps the data limitation explicit', () => {
  const text = read('docs/process/methodology-checklist.md');
  for (const requirement of ['DoR', 'DoD', 'throughput', 'p85', 'Little’s Law', 'CFD', 'ретроспектива']) {
    assert.match(text, new RegExp(requirement, 'i'));
  }
  assert.match(text, /тарихи Done қозғалысы жоқ/);
});
