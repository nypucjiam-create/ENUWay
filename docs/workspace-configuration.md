# GitHub жұмыс кеңістігінің конфигурациясы

- Репозиторий: https://github.com/nypucjiam-create/ENUWay
- GitHub Project: https://github.com/users/nypucjiam-create/projects/3

## Task түрлері

- `Research` — белгісіздікті азайтатын зерттеу немесе spike;
- `Feature` — пайдаланушыға көрінетін функция;
- `Bug` — күтілетін мінез-құлықтан ауытқу;
- `Documentation` — құжаттама және келісім;
- `Risk` — тәуекелді бақылау немесе mitigation.

## Status

1. `Backlog`
2. `Ready`
3. `In progress`
4. `Review`
5. `Done`

`Blocked` жеке өріс арқылы белгіленеді, себебі blocked жұмыс өзінің ағымдағы кезеңін сақтауы керек.

## Custom fields

| Өріс | Мәндер |
|---|---|
| Type | Research, Feature, Bug, Documentation, Risk |
| Priority | P0, P1, P2, P3 |
| Iteration | екі апталық итерациялар |
| Area | Product, UX, Frontend, Backend, QA, PM |
| Estimate | 1, 2, 3, 5, 8 |
| Risk | Low, Medium, High |
| Blocked | Yes/No |

## Көріністер

- **Delivery board:** Status бойынша топталған негізгі Kanban тақтасы;
- **Prioritized backlog:** Priority және Estimate көрсетілген кесте;
- **Current iteration:** ағымдағы итерацияға сүзілген тақта;
- **Risks:** Type = Risk немесе Risk = High элементтері;
- **My work:** assignee бойынша сүзілген жеке жұмыс.

## WIP лимиттері

- `In progress` — ең көбі 3 тапсырма;
- `Review` — ең көбі 2 тапсырма.

## Automation

- жаңа issue → `Backlog`;
- PR ашылғанда байланысты issue → `Review`;
- PR `main` тармағына біріктірілгенде байланысты issue → `Done`;
- жабылған issue → `Done`.

## Қолжетімділік

Репозиторийге барлық команда мүшелері collaborator ретінде, оқытушы read/triage деңгейінде шақырылады. Нақты шақырулар олардың GitHub пайдаланушы аттары алынғаннан кейін орындалады.
