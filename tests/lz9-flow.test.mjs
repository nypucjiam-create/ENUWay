import test from 'node:test';
import assert from 'node:assert/strict';
import {
  buildWorkItems,
  computeSprintMetrics,
  buildDailyCfd,
  buildCsvArtifacts,
  validateEvidence,
} from '../tools/lz9-flow-data.mjs';

test('evidence contains two factual sprint windows and five unique work items', () => {
  const items = buildWorkItems();
  assert.equal(items.length, 5);
  assert.deepEqual([...new Set(items.map((item) => item.sprint))], ['Спринт 1', 'Спринт 2']);
  assert.equal(new Set(items.map((item) => item.id)).size, items.length);
  assert.deepEqual(validateEvidence(items), []);
});

test('metrics calculate throughput and percentile from evidence instead of hardcoded summary', () => {
  const metrics = computeSprintMetrics(buildWorkItems());
  assert.equal(metrics['Спринт 1'].throughput, 2);
  assert.equal(metrics['Спринт 2'].throughput, 3);
  assert.ok(metrics['Спринт 1'].meanCycleHours > metrics['Спринт 2'].meanCycleHours);
  assert.ok(metrics['Спринт 1'].p85CycleHours > 0);
  assert.ok(metrics['Спринт 2'].p85CycleHours > 0);
});

test('daily CFD is monotonic for Done and conserves total items', () => {
  const items = buildWorkItems();
  const rows = buildDailyCfd(items);
  for (const sprint of ['Спринт 1', 'Спринт 2']) {
    const sprintRows = rows.filter((row) => row.sprint === sprint);
    for (let index = 1; index < sprintRows.length; index += 1) {
      assert.ok(sprintRows[index].done >= sprintRows[index - 1].done);
    }
    for (const row of sprintRows) {
      assert.equal(row.backlog + row.inProgress + row.done, items.filter((item) => item.sprint === sprint).length);
    }
  }
  assert.equal(rows.find((row) => row.sprint === 'Спринт 1').date, '2026-09-16');
  assert.equal(rows.filter((row) => row.sprint === 'Спринт 1').at(-1).date, '2026-09-29');
  assert.equal(rows.find((row) => row.sprint === 'Спринт 2').date, '2026-09-30');
  assert.equal(rows.filter((row) => row.sprint === 'Спринт 2').at(-1).date, '2026-10-13');
});

test('CSV artifacts disclose reconstruction source and include transition evidence', () => {
  const { trackerCsv, eventCsv } = buildCsvArtifacts(buildWorkItems());
  assert.match(trackerCsv, /Git тарихынан ретроспективті реконструкция/);
  assert.match(trackerCsv, /S2-03/);
  assert.match(eventCsv, /In Progress/);
  assert.match(eventCsv, /Done/);
});
