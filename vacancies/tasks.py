import datetime
import json

from celery import shared_task
import logging
import requests

import google.generativeai as genai

from CandBechmark import settings
from .models import Vacancy, GeminiPrompt, TaskQueue
from .utils import unify_currency, unify_grade

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


@shared_task
def execute_batches():
    batch_size = 10
    tasks = TaskQueue.objects.all()[:batch_size]

    if tasks:
        batch = [task.data for task in tasks]
        gemini_worker.delay(batch)
        TaskQueue.objects.filter(id__in=[task.id for task in tasks]).delete()


@shared_task
def process_hhru_data(vacancy_text):
    """
    Задача для обработки данных, полученных из скрапера HH.ru
    """
    try:
        TaskQueue.objects.create(data=vacancy_text)
        logger.info("Данные вакансии с HH.ru успешно добавлены в очередь")
    except Exception as e:
        logger.exception("Ошибка при добавлении данных HH.ru в очередь: %s", e)
    return "Данные HH.ru добавлены в очередь"


@shared_task
def gemini_worker(tasks):
    gemini_prompt_obj = GeminiPrompt.objects.first()

    if gemini_prompt_obj:
        prompt_template = gemini_prompt_obj.prompt_text
    else:
        prompt_template = (
            "Проанализируй следующий текст о вакансии и верни результат в виде JSON-объекта с указанными ключами. "
            "JSON должен содержать следующие поля:\n"
            "- 'Company': название компании.\n"
            "- 'Geo': местоположение компании или вакансии.\n"
            "- 'Specialization': специализация или направление работы.\n"
            "- 'Grade': уровень должности.\n"
            "- 'Salary Min': минимальная зарплата.\n"
            "- 'Salary Max': максимальная зарплата.\n"
            "- 'Bonus': размер бонуса.\n"
            "- 'Bonus Conditions': условия предоставления бонуса.\n"
            "- 'Currency': валюта расчёта.\n"
            "- 'Gross/Net': информация о типе оплаты (до вычета/после вычета налогов).\n"
            "- 'Work Format': формат работы (удаленная, офис и др.).\n"
            "- 'Date Posted': дата публикации вакансии.\n"
            "- 'Source': источник вакансии.\n"
            "- 'Author': автор публикации вакансии.\n\n"
            "Не добавляй никаких дополнительных полей или комментариев. Верни только валидный JSON-объект.\n\n"
            "Текст: "
        )

    genai.configure(api_key=settings.GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    for i, task in enumerate(tasks):
        try:
            prompt = prompt_template + task
            response = model.generate_content(prompt)
            gemini_response = response.text

            if gemini_response.startswith("```json"):
                gemini_response = gemini_response.replace("```json", "", 1).strip()
            if gemini_response.endswith("```"):
                gemini_response = gemini_response.rstrip("```").strip()
            if not gemini_response.startswith("{"):
                idx = gemini_response.find("{")
                if idx != -1:
                    gemini_response = gemini_response[idx:].strip()

            vac_data = json.loads(gemini_response)

            currency_clean = unify_currency(vac_data.get('Currency') or '')
            grade_clean = unify_grade(vac_data.get('Grade') or '')

            date_posted = vac_data.get('Date Posted')

            try:
                if isinstance(date_posted, int) or date_posted.is_digit():
                    if isinstance(date_posted, str):
                        date_posted = int(date_posted)
                    date_posted = datetime.datetime.fromordinal(
                        datetime.datetime(1900, 1, 1).toordinal() + date_posted - 2
                    )
            except Exception:
                date_posted = None

            if not date_posted:
                date_posted = datetime.date.today()

            Vacancy.objects.create(
                company=vac_data.get('Company') or '',
                geo=vac_data.get('Geo') or '',
                specialization=vac_data.get('Specialization') or '',
                grade=grade_clean,
                salary_min=vac_data.get('Salary Min'),
                salary_max=vac_data.get('Salary Max'),
                bonus=vac_data.get('Bonus') or '',
                bonus_conditions=vac_data.get('Bonus Conditions') or '',
                currency=currency_clean,
                gross_net=vac_data.get('Gross/Net') or '',
                work_format=vac_data.get('Work Format') or '',
                date_posted=date_posted,
                source=vac_data.get('Source') or 'Excel Import',
                author=vac_data.get('Author') or '',
                description=task
            )

        except json.JSONDecodeError as e:
            logger.error(f"JSON ошибка в строке {i + 1}: {e}. Ответ AI: {gemini_response}")
        except Exception as e:
            logger.exception(f"Ошибка обработки строки {i + 1}: {e}")

    return 'Gemini Worker отработал'
