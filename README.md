# CandBenchmark

## Установка
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

## Запуск

### Redis
```bash
docker compose up -d
```

### Celery

#### Worker
```bash
celery -A CandBechmark worker --loglevel=info
```

#### Beat
```bash
celery -A CandBechmark beat --loglevel=info
```

#### Django
```bash
python manage.py runserver
```