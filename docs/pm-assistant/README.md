# ЛЗ 13 — ENUWay PM-ассистенті

Бұл бума GitHub дерегінен статус-есеп черновигін жасайтын тегін автоматтандырудың толық дәлел пакетін сақтайды.

## Артефактілер

- `../../scripts/pm_status_assistant.py` — GitHub API, жергілікті модель және қауіпсіз резервтік режим;
- `../../.github/workflows/pm-status-assistant.yml` — апта сайынғы GitHub Actions кестесі;
- `run/source-data.json` — екі спринттің нақты GitHub дерегі;
- `run/generated-status-report.md` — жергілікті модельдің өзгертілмеген жауабы;
- `run/prompt-used.txt` — нақты орындалған промпт;
- `run/run-metrics.json` — нақты орындалу уақыты және модель күйі;
- `verified-status-report.md` — PM қолмен түзеткен есеп;
- `verification-log.csv` — барлық табылған дәлсіздік;
- `quality-and-time.md` — қате үлесі және таза уақыт үнемі;
- `prompt-template.md` — команда активі ретінде промпт шаблоны;
- `team-instruction.md` — іске қосу, тексеру және құпиялылық ережелері;
- `lz13-enuway-pm-assistant-report.docx` — зертханалық жұмыстың толық есебі.

## Қайталанатын іске қосу

```text
python scripts/pm_status_assistant.py --provider ollama --model qwen2.5:0.5b
```

GitHub API-ге қоғамдық репозиторий үшін токенсіз де қол жеткізуге болады. GitHub Actions `GITHUB_TOKEN` қолданады. Токен модель промптына ешқашан енгізілмейді.
