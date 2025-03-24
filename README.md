# CandBenchmark

**Автор:** Голубенко Андрей

### Установка
```bash
python -m venv .venv1
source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
```

### Запуск
```bash
docker compose up -d --build
```
### Запуск сборщика по hh.ru
python manage.py scrape_hhru
