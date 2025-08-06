# CandBenchmark

**Авторы:** Голубенко Андрей | Корнеев Валентин

### Установка
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
```

### Запуск
```bash
docker compose up -d --build
```
### Запуск сборщика по hh.ru
python manage.py scrape_hhru
