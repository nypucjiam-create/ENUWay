import fs from 'node:fs/promises';
import path from 'node:path';
import { SpreadsheetFile, Workbook } from '@oai/artifact-tool';
import { buildDailyCfd, buildWorkItems, computeSprintMetrics } from '../lz9-flow-data.mjs';

const outputPath = path.resolve('docs/process/lz9-flow-metrics.xlsx');
const previewDir = path.resolve('docs/process/.qa');
const font = 'Arial';
const navy = '#1F4E78';
const blue = '#5B9BD5';
const pale = '#DDEBF7';
const green = '#70AD47';
const amber = '#ED7D31';
const gray = '#D9E1F2';
const items = buildWorkItems();
const metrics = computeSprintMetrics(items);
const cfdRows = buildDailyCfd(items);

function localDate(iso) {
  const [datePart, timePart] = iso.slice(0, 19).split('T');
  const [year, month, day] = datePart.split('-').map(Number);
  const [hour, minute, second] = timePart.split(':').map(Number);
  return new Date(Date.UTC(year, month - 1, day, hour, minute, second));
}

function styleTitle(sheet, range) {
  sheet.getRange(range).format = {
    font: { name: font, size: 16, bold: true, color: '#000000' },
    verticalAlignment: 'center',
  };
}

function styleHeader(sheet, range) {
  sheet.getRange(range).format = {
    fill: navy,
    font: { name: font, size: 10, bold: true, color: '#FFFFFF' },
    horizontalAlignment: 'center',
    verticalAlignment: 'center',
    wrapText: true,
    borders: { preset: 'all', style: 'thin', color: '#FFFFFF' },
  };
}

function styleBody(sheet, range) {
  sheet.getRange(range).format = {
    font: { name: font, size: 10, color: '#222222' },
    verticalAlignment: 'center',
  };
}

const workbook = Workbook.create();
const summary = workbook.worksheets.add('Шолу');
const work = workbook.worksheets.add('Жұмыс элементтері');
const cfd = workbook.worksheets.add('CFD');
const statusTime = workbook.worksheets.add('Күй уақыты');
const source = workbook.worksheets.add('Дереккөз');

for (const sheet of [summary, work, cfd, statusTime, source]) {
  sheet.showGridLines = false;
}

summary.tabColor = navy;
summary.getRange('A2:H2').merge();
summary.getRange('A2').values = [['ENUWay ағын метрикалары және екі спринтті салыстыру']];
styleTitle(summary, 'A2:H2');
summary.getRange('A3:H3').merge();
summary.getRange('A3').values = [['Дерек: 16.09–13.10.2026 Git тарихынан ретроспективті реконструкция. GitHub Projects-та Done карточкалары болмаған.']];
summary.getRange('A3:H3').format = { font: { name: font, size: 10, italic: true, color: '#595959' }, wrapText: true };
summary.getRange('A5:D5').values = [['Метрика', 'Спринт 1', 'Спринт 2', 'Өзгеріс']];
styleHeader(summary, 'A5:D5');
summary.getRange('A6:A11').values = [
  ['Throughput, элемент'],
  ['Орташа cycle time, сағ'],
  ['p85 cycle time, сағ'],
  ['Throughput, элемент/күн'],
  ['Орташа WIP'],
  ["Little's Law бойынша WIP"],
];
summary.getRange('B6').formulas = [["=COUNTIFS('Жұмыс элементтері'!$C$5:$C$9,B$4)"]];
summary.getRange('B6:C6').fillRight();
summary.getRange('B7').formulas = [["=AVERAGEIFS('Жұмыс элементтері'!$G$5:$G$9,'Жұмыс элементтері'!$C$5:$C$9,B$4)"]];
summary.getRange('B7:C7').fillRight();
summary.getRange('B8').formulas = [["=SMALL('Жұмыс элементтері'!$G$5:$G$6,1)+(SMALL('Жұмыс элементтері'!$G$5:$G$6,2)-SMALL('Жұмыс элементтері'!$G$5:$G$6,1))*0.85", "=SMALL('Жұмыс элементтері'!$G$7:$G$9,2)+(SMALL('Жұмыс элементтері'!$G$7:$G$9,3)-SMALL('Жұмыс элементтері'!$G$7:$G$9,2))*0.7"]];
summary.getRange('B9:C9').formulas = [['=B6/14', '=C6/14']];
summary.getRange('B10:C10').formulas = [["=SUMIFS('Жұмыс элементтері'!$G$5:$G$9,'Жұмыс элементтері'!$C$5:$C$9,B$4)/(14*24)", "=SUMIFS('Жұмыс элементтері'!$G$5:$G$9,'Жұмыс элементтері'!$C$5:$C$9,C$4)/(14*24)"]];
summary.getRange('B11:C11').formulas = [['=B9*(B7/24)', '=C9*(C7/24)']];
summary.getRange('D6:D11').formulas = [
  ['=C6-B6'], ['=C7-B7'], ['=C8-B8'], ['=C9-B9'], ['=C10-B10'], ['=C11-B11'],
];
summary.getRange('B4:C4').values = [['Спринт 1', 'Спринт 2']];
summary.getRange('B4:C4').format = { font: { name: font, size: 9, bold: true, color: navy }, horizontalAlignment: 'center' };
styleBody(summary, 'A6:D11');
summary.getRange('A6:D11').format.borders = { preset: 'all', style: 'thin', color: '#D9D9D9' };
summary.getRange('B6:D6').format.numberFormat = '0';
summary.getRange('B7:D11').format.numberFormat = '0.00';
summary.getRange('A13:H13').merge();
summary.getRange('A13').values = [['Қорытынды: Спринт 2-де throughput 2-ден 3 элементке өсті, ал cycle time қысқарды. CFD-де негізгі күту Backlog кезеңінде көрінеді. Дегенмен нәтиже тарихи Git деректерін реконструкциялауға негізделген, сондықтан процесс тәртібін емес, орындалған жұмыс дәлелін көрсетеді.']];
summary.getRange('A13:H13').format = { font: { name: font, size: 10, bold: true, color: '#000000' }, wrapText: true };

const comparisonData = summary.getRange('F5:H8');
comparisonData.values = [
  ['Метрика', 'Спринт 1', 'Спринт 2'],
  ['Throughput', metrics['Спринт 1'].throughput, metrics['Спринт 2'].throughput],
  ['Орташа cycle time', metrics['Спринт 1'].meanCycleHours, metrics['Спринт 2'].meanCycleHours],
  ['p85 cycle time', metrics['Спринт 1'].p85CycleHours, metrics['Спринт 2'].p85CycleHours],
];
styleHeader(summary, 'F5:H5');
styleBody(summary, 'F6:H8');
const compareChart = summary.charts.add('bar', comparisonData);
compareChart.title = 'Екі спринт метрикалары';
compareChart.titleTextStyle.typeface = font;
compareChart.legend = { position: 'top', textStyle: { typeface: font } };
compareChart.xAxis = { axisType: 'textAxis', textStyle: { typeface: font, fontSize: 10 } };
compareChart.yAxis = { numberFormatCode: '0.00', numberFormatSourceLinked: false, textStyle: { typeface: font } };
compareChart.setPosition('A15', 'H31');
compareChart.series.items[0].fill = blue;
compareChart.series.items[1].fill = green;

work.getRange('A2:J2').merge();
work.getRange('A2').values = [['Реконструкцияланған жұмыс элементтері']];
styleTitle(work, 'A2:J2');
work.getRange('A4:J4').values = [[
  'ID', 'Атауы', 'Спринт', 'Жауапты', 'In Progress', 'Done', 'Cycle time, сағ', 'Бастау дәлелі', 'Аяқтау дәлелі', 'Дерек түрі',
]];
styleHeader(work, 'A4:J4');
const workRows = items.map((item) => {
  const cycleHours = (new Date(item.doneAt) - new Date(item.inProgressAt)) / (60 * 60 * 1000);
  return [
    item.id, item.title, item.sprint, item.owner, localDate(item.inProgressAt), localDate(item.doneAt), cycleHours,
    item.startUrl, item.doneUrl, item.sourceType,
  ];
});
work.getRange('A5:J9').values = workRows;
styleBody(work, 'A5:J9');
work.getRange('A4:J9').format.borders = { preset: 'all', style: 'thin', color: '#D9D9D9' };
work.getRange('E5:F9').format.numberFormat = 'yyyy-mm-dd hh:mm';
work.getRange('G5:G9').format.numberFormat = '0.00';
work.freezePanes.freezeRows(4);

cfd.getRange('A2:F2').merge();
cfd.getRange('A2').values = [['Кумулятивті ағын диаграммасы']];
styleTitle(cfd, 'A2:F2');
cfd.getRange('A4:D4').values = [['Күні', 'Backlog', 'In Progress', 'Done']];
styleHeader(cfd, 'A4:D4');
const sprint1Cfd = cfdRows.filter((row) => row.sprint === 'Спринт 1');
const sprint2Cfd = cfdRows.filter((row) => row.sprint === 'Спринт 2');
cfd.getRange('A5:D18').values = sprint1Cfd.map((row) => [localDate(`${row.date}T00:00:00+05:00`), row.backlog, row.inProgress, row.done]);
styleBody(cfd, 'A5:D18');
cfd.getRange('A4:D18').format.borders = { preset: 'all', style: 'thin', color: '#D9D9D9' };
cfd.getRange('A5:A18').format.numberFormat = 'yyyy-mm-dd';
cfd.getRange('A21:D21').values = [['Күні', 'Backlog', 'In Progress', 'Done']];
styleHeader(cfd, 'A21:D21');
cfd.getRange('A22:D35').values = sprint2Cfd.map((row) => [localDate(`${row.date}T00:00:00+05:00`), row.backlog, row.inProgress, row.done]);
styleBody(cfd, 'A22:D35');
cfd.getRange('A21:D35').format.borders = { preset: 'all', style: 'thin', color: '#D9D9D9' };
cfd.getRange('A22:A35').format.numberFormat = 'yyyy-mm-dd';
cfd.getRange('A20:D20').merge();
cfd.getRange('A20').values = [['Спринт 2 CFD деректері']];
cfd.getRange('A20:D20').format = { font: { name: font, size: 11, bold: true, color: '#000000' } };
cfd.freezePanes.freezeRows(4);
const firstCfdChart = cfd.charts.add('line', cfd.getRange('A4:D18'));
firstCfdChart.title = 'Спринт 1 CFD';
firstCfdChart.titleTextStyle.typeface = font;
firstCfdChart.legend = { position: 'top', textStyle: { typeface: font } };
firstCfdChart.xAxis = { axisType: 'textAxis', textStyle: { typeface: font, fontSize: 9 } };
firstCfdChart.yAxis = { numberFormatCode: '0', numberFormatSourceLinked: false, textStyle: { typeface: font } };
firstCfdChart.setPosition('G4', 'N18');
const secondCfdChart = cfd.charts.add('line', cfd.getRange('A21:D35'));
secondCfdChart.title = 'Спринт 2 CFD';
secondCfdChart.titleTextStyle.typeface = font;
secondCfdChart.legend = { position: 'top', textStyle: { typeface: font } };
secondCfdChart.xAxis = { axisType: 'textAxis', textStyle: { typeface: font, fontSize: 9 } };
secondCfdChart.yAxis = { numberFormatCode: '0', numberFormatSourceLinked: false, textStyle: { typeface: font } };
secondCfdChart.setPosition('G20', 'N34');
for (const chart of [firstCfdChart, secondCfdChart]) {
  chart.series.items[0].line = { fill: gray, style: 'solid', width: 2 };
  chart.series.items[1].line = { fill: amber, style: 'solid', width: 2 };
  chart.series.items[2].line = { fill: green, style: 'solid', width: 2 };
}

statusTime.getRange('A2:G2').merge();
statusTime.getRange('A2').values = [['Күйлердегі уақыт']];
styleTitle(statusTime, 'A2:G2');
statusTime.getRange('A4:G4').values = [['ID', 'Спринт', 'Backlog, сағ', 'Ready, сағ', 'In Progress, сағ', 'Review, сағ', 'Түсіндірме']];
styleHeader(statusTime, 'A4:G4');
statusTime.getRange('A5:G9').values = items.map((item) => [item.id, item.sprint, 'n.a.', 'n.a.', null, 'n.a.', 'Тек In Progress және Done уақыты Git коммиттерімен дәлелденген']);
for (let row = 5; row <= 9; row += 1) statusTime.getRange(`E${row}`).formulas = [[`='Жұмыс элементтері'!G${row}`]];
styleBody(statusTime, 'A5:G9');
statusTime.getRange('A4:G9').format.borders = { preset: 'all', style: 'thin', color: '#D9D9D9' };
statusTime.getRange('C5:F9').format.numberFormat = '0.00';

source.getRange('A2:F2').merge();
source.getRange('A2').values = [['Дереккөз және шектеулер']];
styleTitle(source, 'A2:F2');
source.getRange('A4:B8').values = [
  ['Параметр', 'Мәні'],
  ['Репозиторий', 'https://github.com/nypucjiam-create/ENUWay'],
  ['GitHub Project', 'https://github.com/users/nypucjiam-create/projects/3'],
  ['Ағымдағы тақта күйі', 'Backlog 8, Ready 1, In Progress 0, Review 1, Done 0'],
  ['Әдіс', '16.09–13.10.2026 аралығындағы immutable Git commit тарихы бойынша ретроспективті реконструкция'],
];
styleHeader(source, 'A4:B4');
styleBody(source, 'A5:B8');
source.getRange('A4:B8').format.borders = { preset: 'all', style: 'thin', color: '#D9D9D9' };
source.getRange('A10:B13').values = [
  ['Шектеу', 'Түсіндірме'],
  ['Board transition тарихы жоқ', 'Карточкалар нақты жұмыс күні қозғалғанын дәлелдеу мүмкін емес'],
  ['Ready және Review уақыты жоқ', 'Бұл күйлерге уақыт ойдан қосылмайды және n.a. деп көрсетіледі'],
  ['CFD түсіндірмесі', 'Backlog басталуы спринт шекарасы ретінде қабылданды; In Progress және Done ғана commit-пен дәлелденген'],
];
styleHeader(source, 'A10:B10');
styleBody(source, 'A11:B13');
source.getRange('A10:B13').format.borders = { preset: 'all', style: 'thin', color: '#D9D9D9' };

for (const [sheet, widths] of [
  [summary, [34, 16, 16, 16, 3, 24, 16, 16]],
  [work, [11, 44, 14, 14, 20, 20, 16, 40, 40, 32]],
  [cfd, [14, 14, 12, 14, 12, 3, 12, 12, 12, 12, 12, 12, 12, 12]],
  [statusTime, [11, 14, 14, 14, 18, 14, 52]],
  [source, [30, 95]],
]) {
  widths.forEach((width, index) => {
    sheet.getRangeByIndexes(0, index, Math.max(40, sheet.getUsedRange()?.rowCount ?? 40), 1).format.columnWidth = width;
  });
  sheet.getUsedRange().format.font.name = font;
  sheet.getUsedRange().format.verticalAlignment = 'center';
  sheet.getUsedRange().format.wrapText = true;
  sheet.getUsedRange().format.autofitRows();
}

workbook.recalculate();
await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.mkdir(previewDir, { recursive: true });
for (const sheetName of ['Шолу', 'Жұмыс элементтері', 'CFD', 'Күй уақыты', 'Дереккөз']) {
  const preview = await workbook.render({ sheetName, autoCrop: 'all', scale: 1, format: 'png' });
  await fs.writeFile(path.join(previewDir, `${sheetName}.png`), new Uint8Array(await preview.arrayBuffer()));
}
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

const keyCheck = await workbook.inspect({
  kind: 'table', range: 'Шолу!A4:D13', include: 'values,formulas', tableMaxRows: 20, tableMaxCols: 8,
});
console.log(keyCheck.ndjson);
const errors = await workbook.inspect({
  kind: 'match', searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',
  options: { useRegex: true, maxResults: 100 }, summary: 'final formula error scan',
});
console.log(errors.ndjson);
