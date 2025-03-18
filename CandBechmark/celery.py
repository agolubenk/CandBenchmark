import os
from celery import Celery

# Указываем настройки Django, если переменная не установлена
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CandBechmark.settings')

app = Celery('CandBechmark')

# Загружаем настройки конфигурации из settings.py, используя префикс CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматический поиск задач во всех приложениях Django
app.autodiscover_tasks()

# Пример: настройка периодического задания для celery beat
app.conf.beat_schedule = {
    'run-gemini-worker-every-20-seconds': {
        'task': 'vacancies.tasks.execute_batches',
        'schedule': 20
    },
}

if __name__ == '__main__':
    app.start()