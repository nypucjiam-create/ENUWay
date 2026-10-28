const HOUR = 60 * 60 * 1000;
const DAY = 24 * HOUR;

const sprintWindows = {
  'Спринт 1': {
    start: '2026-09-16T00:00:00+05:00',
    end: '2026-09-29T23:59:59+05:00',
  },
  'Спринт 2': {
    start: '2026-09-30T00:00:00+05:00',
    end: '2026-10-13T23:59:59+05:00',
  },
};

export function buildWorkItems() {
  return [
    {
      id: 'S1-01',
      sprint: 'Спринт 1',
      title: 'ENUWay жұмыс кеңістігін және GitHub байланыстарын дайындау',
      owner: 'Нурислам',
      inProgressAt: '2026-09-16T21:04:30+05:00',
      doneAt: '2026-09-17T10:40:46+05:00',
      startCommit: '33d5f5f1326118c344bb507b8c64efacb7a44e38',
      doneCommit: '529bc88bbd899b792f53ad6ebb7f44bfa00872b4',
    },
    {
      id: 'S1-02',
      sprint: 'Спринт 1',
      title: 'Пилоттық сұхбат жоспары мен жеткізу моделінің шешімін нақтылау',
      owner: 'Нурай',
      inProgressAt: '2026-09-17T10:40:58+05:00',
      doneAt: '2026-09-17T11:03:57+05:00',
      startCommit: 'b736283de8e6bd08acb7f7136001903bcaf48732',
      doneCommit: 'aca897c5e0c97c4eec0b529bf15c68b599d64a47',
    },
    {
      id: 'S2-01',
      sprint: 'Спринт 2',
      title: 'ЛЗ 4 талаптар пакетін дайындау және әдістемеге сәйкестендіру',
      owner: 'Альфараби',
      inProgressAt: '2026-10-01T12:35:46+05:00',
      doneAt: '2026-10-01T13:14:37+05:00',
      startCommit: 'd80616f521f1fedbb2d8f2bff762f285a441ea42',
      doneCommit: '1b4e8a495ad321bcb75affc988b5089c8bad05c6',
    },
    {
      id: 'S2-02',
      sprint: 'Спринт 2',
      title: 'ЛЗ 5 жеткізу жоспарын дайындау және жаңарту',
      owner: 'Нурай',
      inProgressAt: '2026-10-01T18:21:17+05:00',
      doneAt: '2026-10-01T18:38:11+05:00',
      startCommit: '432a025164c676f1255b9b51cc449e83df4f3bcd',
      doneCommit: '8c949046d7fcf55b56ca323b9f819e8a56410a91',
    },
    {
      id: 'S2-03',
      sprint: 'Спринт 2',
      title: 'ЛЗ 6 Монте Карло болжамын дайындау және әдістемеге сәйкестендіру',
      owner: 'Нурислам',
      inProgressAt: '2026-10-08T15:39:44+05:00',
      doneAt: '2026-10-08T18:29:18+05:00',
      startCommit: 'a315800cd71058fe732a1975c293385a4ffcd3c7',
      doneCommit: 'c28daaeeabf443f5f3565d81019c7939634f85b8',
    },
  ].map((item) => ({
    ...item,
    startUrl: `https://github.com/nypucjiam-create/ENUWay/commit/${item.startCommit}`,
    doneUrl: `https://github.com/nypucjiam-create/ENUWay/commit/${item.doneCommit}`,
    sourceType: 'Git тарихынан ретроспективті реконструкция',
  }));
}

export function validateEvidence(items) {
  const errors = [];
  const ids = new Set();
  for (const item of items) {
    if (ids.has(item.id)) errors.push(`Қайталанған ID: ${item.id}`);
    ids.add(item.id);
    if (!sprintWindows[item.sprint]) errors.push(`Белгісіз спринт: ${item.sprint}`);
    if (new Date(item.doneAt) < new Date(item.inProgressAt)) errors.push(`Теріс cycle time: ${item.id}`);
    if (!/^[0-9a-f]{40}$/.test(item.startCommit) || !/^[0-9a-f]{40}$/.test(item.doneCommit)) {
      errors.push(`Commit идентификаторы қате: ${item.id}`);
    }
  }
  return errors;
}

function percentileInc(values, percentile) {
  const sorted = [...values].sort((a, b) => a - b);
  if (sorted.length === 1) return sorted[0];
  const rank = (sorted.length - 1) * percentile;
  const lower = Math.floor(rank);
  const upper = Math.ceil(rank);
  if (lower === upper) return sorted[lower];
  return sorted[lower] + (sorted[upper] - sorted[lower]) * (rank - lower);
}

export function computeSprintMetrics(items) {
  const metrics = {};
  for (const [sprint, window] of Object.entries(sprintWindows)) {
    const subset = items.filter((item) => item.sprint === sprint);
    const cycleHours = subset.map((item) => (new Date(item.doneAt) - new Date(item.inProgressAt)) / HOUR);
    const windowDays = (new Date(window.end) - new Date(window.start) + 1000) / DAY;
    const meanCycleHours = cycleHours.reduce((sum, value) => sum + value, 0) / cycleHours.length;
    const throughput = subset.length;
    const throughputPerDay = throughput / windowDays;
    const timeWeightedWip = cycleHours.reduce((sum, value) => sum + value, 0) / (windowDays * 24);
    metrics[sprint] = {
      throughput,
      windowDays,
      throughputPerDay,
      meanCycleHours,
      p85CycleHours: percentileInc(cycleHours, 0.85),
      timeWeightedWip,
      littleLawWip: throughputPerDay * (meanCycleHours / 24),
    };
  }
  return metrics;
}

export function buildDailyCfd(items) {
  const rows = [];
  for (const [sprint, window] of Object.entries(sprintWindows)) {
    const subset = items.filter((item) => item.sprint === sprint);
    let cursor = new Date(window.start);
    const end = new Date(window.end);
    while (cursor <= end) {
      const dayEnd = new Date(cursor.getTime() + DAY - 1);
      let backlog = 0;
      let inProgress = 0;
      let done = 0;
      for (const item of subset) {
        const started = new Date(item.inProgressAt);
        const finished = new Date(item.doneAt);
        if (finished <= dayEnd) done += 1;
        else if (started <= dayEnd) inProgress += 1;
        else backlog += 1;
      }
      rows.push({
        sprint,
        date: new Date(cursor.getTime() + 5 * HOUR).toISOString().slice(0, 10),
        backlog,
        inProgress,
        done,
      });
      cursor = new Date(cursor.getTime() + DAY);
    }
  }
  return rows;
}

export function getSprintWindows() {
  return structuredClone(sprintWindows);
}

function csvEscape(value) {
  const text = String(value ?? '');
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function toCsv(headers, rows) {
  return [headers, ...rows]
    .map((row) => row.map(csvEscape).join(','))
    .join('\n') + '\n';
}

export function buildCsvArtifacts(items) {
  const trackerHeaders = [
    'Work item ID', 'Атауы', 'Спринт', 'Жауапты', 'In Progress уақыты', 'Done уақыты',
    'Cycle time сағат', 'Бастау дәлелі', 'Аяқтау дәлелі', 'Дерек түрі',
  ];
  const trackerRows = items.map((item) => [
    item.id,
    item.title,
    item.sprint,
    item.owner,
    item.inProgressAt,
    item.doneAt,
    ((new Date(item.doneAt) - new Date(item.inProgressAt)) / HOUR).toFixed(2),
    item.startUrl,
    item.doneUrl,
    item.sourceType,
  ]);

  const eventHeaders = ['Work item ID', 'Спринт', 'Уақыт', 'Жаңа күй', 'Дәлел', 'Ескерту'];
  const eventRows = items.flatMap((item) => [
    [item.id, item.sprint, item.inProgressAt, 'In Progress', item.startUrl, 'Алғашқы дәлелденген жұмыс коммиті'],
    [item.id, item.sprint, item.doneAt, 'Done', item.doneUrl, 'Нәтижені аяқтаған дәлелденген коммит'],
  ]);

  return {
    trackerCsv: toCsv(trackerHeaders, trackerRows),
    eventCsv: toCsv(eventHeaders, eventRows),
  };
}
