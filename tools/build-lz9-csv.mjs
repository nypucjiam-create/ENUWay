import fs from 'node:fs/promises';
import path from 'node:path';
import { buildCsvArtifacts, buildWorkItems, validateEvidence } from './lz9-flow-data.mjs';

const outputDir = path.resolve('docs/process');
const items = buildWorkItems();
const errors = validateEvidence(items);
if (errors.length) throw new Error(errors.join('\n'));

const { trackerCsv, eventCsv } = buildCsvArtifacts(items);
await fs.mkdir(outputDir, { recursive: true });
await fs.writeFile(path.join(outputDir, 'lz9-tracker-export.csv'), trackerCsv, 'utf8');
await fs.writeFile(path.join(outputDir, 'lz9-event-log.csv'), eventCsv, 'utf8');
