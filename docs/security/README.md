# ЛЗ 7 ENUWay тәуекелдер және қауіпсіздік

## Артефактілер

- [Қорытынды Word құжаты](lz7-enuway-risk-security.docx)
- [RAID журналы](raid.md) және [CSV нұсқасы](raid-log.csv)
- [STRIDE сипаттамасы](threat-model.md)
- [OWASP Threat Dragon моделі](enuway-auth-threat-model.json)
- [Threat model PNG](enuway-auth-threat-model.png)
- [Сәйкестік чек-листі](compliance-checklist.md)
- [Trivy және gitleaks қорытындысы](scan-summary.md)
- [Сканердің машинамен оқылатын есептері](reports/)

## Бэклогтағы тәуекел шаралары

| Issue | Мера | Иесі | Мерзімі | Сілтеме |
|---|---|---|---|---|
| #31 | ENU аккаунтын тексеру мен сессияны қорғау | Нұрислам | 23.10.2026 | https://github.com/nypucjiam-create/ENUWay/issues/31 |
| #32 | Сапарға қосылуда артық броньды болдырмау | 2-қатысушы | 30.10.2026 | https://github.com/nypucjiam-create/ENUWay/issues/32 |
| #33 | Дербес деректерді сақтау және қолжетімділік бақылауы | 3-қатысушы | 06.11.2026 | https://github.com/nypucjiam-create/ENUWay/issues/33 |

## Негізгі сандар

- 20 тәуекел;
- 4 допущение, 4 орын алған мәселе, 3 тәуелділік;
- бастапқы EMV: 136.40 сағат;
- шаралардан кейінгі қалдық EMV: 29.92 сағат, жоспарлық резерв 30 сағат;
- STRIDE-тің 6 санаты толық қамтылған;
- Trivy: 0 репозиторий finding; gitleaks: 13 commit, 0 verified leak.
