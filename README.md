# CandBenchmark

## Установка
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

## Запуск

### Redis + Celery
```bash
docker compose up -d
```

#### Django
```bash
python manage.py runserver
```

