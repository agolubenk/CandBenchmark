from celery import shared_task
import logging
import requests
from .models import Vacancy

logger = logging.getLogger(__name__)


@shared_task
def fetch_vacancies():
    """
    Задача для периодического опроса внешнего источника (например, hh.ru)
    для получения вакансий. Здесь можно реализовать логику запроса к API,
    обработки данных и сохранения новых вакансий в базе данных.
    """
    logger.info("Запущена задача получения вакансий")
    # Пример: получаем данные с фиктивного API
    try:
        # Здесь должна быть логика запроса к API hh.ru. Для демонстрации:
        response = requests.get('https://api.example.com/vacancies')  # замените URL на реальный
        if response.status_code == 200:
            data = response.json()
            # Обработка данных и сохранение вакансий (пример псевдокода)
            for item in data.get('results', []):
                # Допустим, у вас в API есть поля company, specialization и т.д.
                Vacancy.objects.update_or_create(
                    company=item.get('company'),
                    specialization=item.get('specialization'),
                    defaults={
                        'grade': item.get('grade'),
                        'salary_min': item.get('salary_min'),
                        'salary_max': item.get('salary_max'),
                        'bonus': item.get('bonus'),
                        'bonus_conditions': item.get('bonus_conditions'),
                        'currency': item.get('currency'),
                        'gross_net': item.get('gross_net'),
                        'work_format': item.get('work_format'),
                        'date_posted': item.get('date_posted'),
                        'source': item.get('source'),
                        'author': item.get('author'),
                    }
                )
            logger.info("Вакансии успешно обновлены")
        else:
            logger.error("Ошибка при получении данных: %s", response.status_code)
    except Exception as e:
        logger.exception("Исключение при выполнении задачи fetch_vacancies: %s", e)
    return "Задача fetch_vacancies выполнена"


@shared_task
def process_vacancy_nlp(vacancy_id):
    """
    Задача обработки вакансии с использованием NLP-сервиса.
    Допустим, мы анализируем текст бонуса для извлечения дополнительных данных.
    """
    try:
        vacancy = Vacancy.objects.get(id=vacancy_id)
        # Здесь можно вызвать реальный NLP-сервис, например:
        # result = call_nlp_service(vacancy.some_text_field)
        # Для демонстрации используем фиктивный анализ:
        result = analyze_text(vacancy.bonus if vacancy.bonus else "Нет данных")

        # Обновляем некоторые поля вакансии на основе данных из NLP-сервиса
        vacancy.specialization = result.get("specialization", vacancy.specialization)
        vacancy.grade = result.get("grade", vacancy.grade)
        vacancy.save()
        return f"NLP-обработка вакансии {vacancy_id} выполнена"
    except Vacancy.DoesNotExist:
        return f"Вакансия с id {vacancy_id} не найдена"
    except Exception as e:
        logger.exception("Ошибка в задаче process_vacancy_nlp: %s", e)
        return f"Ошибка при обработке вакансии {vacancy_id}"


def analyze_text(text):
    """
    Функция-заглушка для демонстрации вызова NLP-сервиса.
    На практике здесь может быть вызов внешнего API с использованием библиотеки requests.
    """
    # Пример фиктивного анализа текста
    return {
        "specialization": "Разработка ПО",
        "grade": "Middle",
        "salary_range": "1500-2500"
    }