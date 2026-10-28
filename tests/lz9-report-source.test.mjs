import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../tools/build_lz9_report.py', import.meta.url), 'utf8');

test('report title does not use the bordered Word Title paragraph style', () => {
  assert.doesNotMatch(source, /doc\.add_paragraph\(style="Title"\)/);
});

test('metrics section starts on a fresh page so its table header is not orphaned', () => {
  assert.match(source, /doc\.add_page_break\(\)\nadd_heading\(doc, "5 Ағын метрикалары"/);
});
