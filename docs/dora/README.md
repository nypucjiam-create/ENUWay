# ЛЗ 10 CI CD және DORA

## Артефактілер

- [GitHub Actions CI](../../.github/workflows/ci.yml)
- [DORA деректерін жинау скрипті](../../scripts/dora.py)
- [DORA бақылау тақтасы](dora-dashboard.svg)
- [Нақты GitHub Actions іске қосылымдары](data/workflow-runs.csv)
- [Есептелген метрикалар](data/dora-metrics.json)
- [Метрика анықтамалары мен жақсарту жоспары](metrics-and-improvements.md)
- [Негізгі тармақ саясаты](branch-policy.md)
- [Релиз жоспары және кері қайтару чек-листі](../ops/release-plan.md)

## Қайта есептеу

```text
python scripts/dora.py --repo nypucjiam-create/ENUWay
```

Public репозиторий үшін токен міндетті емес. API лимиті қажет болса, fine-grained read-only токен `GH_TOKEN` орта айнымалысына беріледі. Токен кодқа немесе файлға жазылмайды.

## Дерек шектеуі

Метрикалар тек ENUWay репозиторийінің `main` тармағындағы аяқталған `CI` іске қосылымдарынан есептеледі. Қысқа оқу тарихы тұрақты трендті дәлелдемейді, сондықтан деңгей «бастапқы бақылау» ретінде беріледі.

