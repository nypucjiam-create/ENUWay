# ЛЗ 6 есептеу ортасы

## Құрылым

- `lz6-monte-carlo.ipynb` — орындалған негізгі notebook;
- `data/throughput.csv` — 26 толық аптаның throughput деректері;
- `data/source-issues.csv` — дерекке кірген 106 жабылған issue;
- `data/source.json` — тікелей сілтеме, кезең, қаралған күн және шектеулер;
- `forecast-summary.csv` — P50, P70, P85 және P95 нәтижелері;
- `figures/` — notebook қайта жасайтын үш график.

## Қайта іске қосу

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r notebooks/lz6/requirements.txt
jupyter lab
```

Jupyter ішінде `notebooks/lz6/lz6-monte-carlo.ipynb` файлын ашып, **Restart Kernel and
Run All Cells** таңдаңыз. Notebook репозиторий түбірінен де, өзінің бумасынан да іске қосылады.
Тұрақты `seed=20261008` бірдей кесте мен графиктерді қайта береді.
