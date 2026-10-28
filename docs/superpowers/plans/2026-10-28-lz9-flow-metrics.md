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

- [ ] Создать лист сводки с throughput, mean, p85, WIP и проверкой Little's Law.
- [ ] Добавить исходный журнал, ежедневный CFD и time in status.
- [ ] Построить нативные диаграммы CFD и сравнения двух спринтов.
- [ ] Пересчитать, проверить формулы, ошибки и визуальный вывод.

### Task 3: Process policy and report

**Files:**
- Create: `docs/process/README.md`
- Create: `docs/process/dor-dod.md`
- Create: `docs/process/retrospective.md`
- Create: `docs/process/lz9-enuway-flow-report.docx`

- [ ] Описать колонки, WIP-лимиты и политики переходов.
- [ ] Записать DoR и DoD в репозитории.
- [ ] Оформить цели, обзоры и ретроспективы двух спринтов.
- [ ] Зафиксировать одно действие: ежедневное обновление статуса карточек владельцем до 18:00, срок 20.10.2026, метрика — доля переходов в день фактического изменения не менее 90%.
- [ ] Создать и визуально проверить итоговый DOCX.

### Task 4: GitHub Projects configuration and publication

**Files:**
- Modify: GitHub Project `ENUWay — MVP Delivery`
- Modify: repository documentation index if needed.

- [ ] Добавить отсутствующий этап ожидания и описания колонок.
- [ ] Зафиксировать WIP-политики в доступной документации проекта.
- [ ] Добавить артефакты в Git, проверить diff и опубликовать.
- [ ] Сверить каждый критерий методички с итоговым пакетом.

