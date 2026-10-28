# ENUWay ЛЗ 9 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Выполнить ЛЗ 9 по методичке на казахском языке без вымышленных метрик, используя ретроспективную реконструкцию по истории Git и фактическому состоянию GitHub Projects.

**Architecture:** Источником фактов служат Git-коммиты ENUWay и текущее состояние GitHub Projects. Сначала формируется проверяемый журнал событий, затем Excel рассчитывает throughput, cycle time, p85, WIP, time in status, Little's Law и CFD. Word-отчёт объясняет метод, ограничения и одно измеримое ретроспективное изменение.

**Tech Stack:** Git, GitHub Projects, CSV, Excel XLSX, Word DOCX, JavaScript artifact-tool, Python python-docx.

**Spec:** Скриншоты ЛЗ 9 и разделы методички о настройке процесса, двух спринтах, метриках и ретроспективе.

## Global Constraints

- Весь сдаваемый текст — на казахском языке.
- Нельзя выдавать реконструированные даты за прямой экспорт GitHub Projects.
- Метрики считаются формулами из сохранённого журнала событий.
- Ретроспектива содержит ровно одно измеримое действие, владельца и срок.
- DoD включает тесты, проверку вторым участником, доступный стенд и обновлённую документацию.

## Review Focus

- Нет завершённых карточек в текущем GitHub Projects: это явно отражается в источнике и ограничениях.
- Даты начала и завершения подтверждаются коммитами, а не подбираются под желаемый результат.
- Среднее и p85 cycle time считаются отдельно для каждого спринта.
- CFD строится по ежедневным накопленным состояниям без отрицательных значений.
- Little's Law сверяется с тем же временным окном и единицами измерения.

---

### Task 1: Evidence dataset

**Files:**
- Create: `docs/process/lz9-tracker-export.csv`
- Create: `docs/process/lz9-event-log.csv`

- [x] Собрать коммиты за 16.09–13.10.2026 и связать их с фактическими результатами ENUWay.
- [x] Зафиксировать источник каждой даты и статус реконструкции.
- [x] Проверить отсутствие будущих дат, отрицательных интервалов и дубликатов идентификаторов.

### Task 2: Metrics workbook

**Files:**
- Create: `docs/process/lz9-flow-metrics.xlsx`

- [x] Создать лист сводки с throughput, mean, p85, WIP и проверкой Little's Law.
- [x] Добавить исходный журнал, ежедневный CFD и time in status.
- [x] Построить нативные диаграммы CFD и сравнения двух спринтов.
- [x] Пересчитать, проверить формулы, ошибки и визуальный вывод.

### Task 3: Process policy and report

**Files:**
- Create: `docs/process/README.md`
- Create: `docs/process/dor-dod.md`
- Create: `docs/process/retrospective.md`
- Create: `docs/process/lz9-enuway-flow-report.docx`

- [x] Описать колонки, WIP-лимиты и политики переходов.
- [x] Записать DoR и DoD в репозитории.
- [x] Оформить цели, обзоры и ретроспективы двух спринтов.
- [x] Зафиксировать одно действие: разделить работу Спринта 2 минимум на три отдельно принимаемых результата с отдельными финальными commit; владелец — Альфараби, срок — 13.10.2026, метрика — не менее трёх завершённых элементов с доказательствами start/finish.
- [x] Создать и визуально проверить итоговый DOCX.

### Task 4: GitHub Projects configuration and publication

**Files:**
- Modify: GitHub Project `ENUWay — MVP Delivery`
- Modify: repository documentation index if needed.

- [x] Добавить отсутствующий этап ожидания и описания колонок.
- [x] Зафиксировать WIP-политики в доступной документации проекта.
- [ ] Добавить артефакты в Git, проверить diff и опубликовать.
- [ ] Сверить каждый критерий методички с итоговым пакетом.

