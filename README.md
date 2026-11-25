# Ауыз су сапасын скринингтеу

№10 нұсқаға арналған гибридті оқу жобасы. Сараптамалық тексерулер мен машиналық оқыту моделін біріктіріп, Kaggle Water Potability дерегіндегі `Potability` класын болжайды.

> Бұл жүйе оқу мақсатындағы скрининг қана. Accuracy-ді арттырғанда Potable precision 0.809-дан 0.647-ге төмендеді. Ол су ішуге қауіпсіз деген сертификат бермейді және зертханалық талдауды алмастырмайды.

## Дайын нәтиже

- Оқытылған Random Forest артефактісі: `models/model.joblib`.
- Таңдалған threshold: 0.5517; test accuracy: 0.669; Potable precision: 0.647; recall: 0.336; F1: 0.442; Average Precision: 0.6075.
- Салыстырылған CV Average Precision: Logistic Regression 0.391254, Random Forest 0.574162, HistGradientBoosting 0.562963.
- Толық әдіс пен нәтижелер `report.docx` есебінде берілген.

Python және scikit-learn нұсқасына қарай қайта оқытқандағы мәндер аздап өзгеруі мүмкін. Артефакт Python 3.14.3 және scikit-learn 1.9.1 ортасында жасалды.

## Деректер

[Kaggle Water Potability](https://www.kaggle.com/datasets/adityakadiwal/water-potability). Деректер файлын репозиторийге қоспаймыз. CSV файлын Kaggle бетінен жүктеп, ноутбукқа енгізіңіз. Нақты Kaggle лицензиясын қолданар/таратар алдында тексеріңіз.

## Орнату және іске қосу

Жоба түбірінде үш пәрмен:

1. `pip install -r requirements.txt`
2. `uvicorn api.main:app --reload`
3. Басқа терминалда `streamlit run app/ui.py`

API құжаттамасы: http://127.0.0.1:8000/docs

API `models/model.joblib` файлын оқиды. GitHub-та модель көлемін басқару үшін ол мәтіндік бөліктерге бөлінген; Алғашқы `/predict` немесе `/explain` сұрауында API жетіспейтін `model.joblib` файлын автоматты жинайды. Жергілікті ZIP ішінде файл дайын тұр. Модельді қайта оқыту үшін `notebooks/water_hybrid_v10.ipynb` файлын Colab-та ашып, Kaggle CSV таңдаңыз; экспортталған модельді `models/model.joblib` жолына көшіріңіз. Test жиыны threshold таңдауына қатыспайды.

## Жоба құрылымы

- `notebooks/water_hybrid_v10.ipynb` — EDA, 3 алгоритм, 5-fold CV, threshold таңдау, қате және permutation importance талдауы.
- `src/rules.py`, `src/decision.py` — кіріс тексеруі, ережелер және гибрид шешім.
- `api/main.py` — `/health`, `/predict`, `/explain` және SQLite журнал.
- `app/ui.py` — API-ға сұраныс жасайтын Streamlit интерфейсі.
- `tests/` — ережелерге 15, API-ға 6, барлығы 21 тест.
- `models/model.joblib`, `models/metrics.json`, `models/importance.json` — модель және бағалау нәтижелері. GitHub көшірмесінде модель бөліктерін жинайтын `scripts/restore_model.py` бар.
- `report.docx` — жобаның есебі.

## Тестілеу

`pytest -q`

## Сақтық және шектеулер

pH, хлорамин және лайлылық шектері қосымша тексеру сигналы. Олар әмбебап норматив емес. Kaggle дерегінде микробиологиялық талдау мен барлық ластағыштар жоқ. Су қауіпсіздігін жергілікті ереже және зертханалық талдау анықтайды.

GitHub-қа Kaggle token, `.env`, деректердің жеке көшірмесі немесе SQLite шешім журналы қосылмайды.