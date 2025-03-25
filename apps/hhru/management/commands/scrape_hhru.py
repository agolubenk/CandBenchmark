# hhru/management/commands/scrape_hhru.py
import requests
import time
import random
from django.core.management.base import BaseCommand
from apps.hhru.models import VacancyHH
from apps.hhru.queries import QUERY_LIST as queries
from apps.vacancies.tasks import process_hhru_data


class Command(BaseCommand):
    help = "Собирает вакансии с hh.ru API для разных поисковых запросов каждые 60 секунд"

    def handle(self, *args, **kwargs):
        query_count = len(queries)
        current_index = 0

        self.stdout.write(self.style.SUCCESS("Запуск периодического сбора вакансий."))

        while True:
            # Выбираем текущий поисковый запрос из списка
            current_query = queries[current_index]
            self.stdout.write(self.style.WARNING(f"Старт сбора для запроса: {current_query}"))

            url = "https://api.hh.ru/vacancies"
            params = {
                "text": current_query, 
                "only_with_salary": True,
                "page": 0,
                "per_page": 20,  # Количество вакансий на одной странице
            }
            headers = {"User-Agent": "MA/v1.0 (agolubenkoby@gmail.com)"}

            total_fetched_current = 0
            # Обходим страницы для текущего запроса
            while True:
                self.stdout.write(f"Получаем страницу {params['page']} для запроса '{current_query}'")
                response = requests.get(url, params=params, headers=headers)
                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(f"Ошибка запроса: {response.status_code}"))
                    break

                data = response.json()
                items = data.get("items", [])
                if not items:
                    self.stdout.write(self.style.WARNING("Нет вакансий на этой странице."))
                    break

                for item in items:
                    try:
                        hh_id = item.get("id")

                        # Получаем детальную информацию о вакансии
                        vacancy_url = f"https://api.hh.ru/vacancies/{hh_id}"
                        vacancy_response = requests.get(vacancy_url, headers=headers)

                        if vacancy_response.status_code == 200:
                            vacancy_detail = vacancy_response.json()

                            # Извлекаем информацию о зарплате из детальной информации
                            salary_detail = vacancy_detail.get('salary')
                            salary_from_detail = salary_detail.get("from") if salary_detail else None
                            salary_to_detail = salary_detail.get("to") if salary_detail else None

                            # Если в детальной информации не указана зарплата, пропускаем вакансию
                            if salary_from_detail is None and salary_to_detail is None:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"Вакансия {hh_id} пропущена, так как не указана зарплата."
                                    )
                                )
                                continue

                            # Формируем текст вакансии для обработки через Celery
                            vacancy_text = (
                                f"Вакансия с HH.ru\n"
                                f"Компания: {vacancy_detail.get('employer', {}).get('name', '')}\n"
                                f"Название позиции: {vacancy_detail.get('name', '')}\n"
                                f"Описание: {vacancy_detail.get('description', '')}\n"
                                f"Требования: {vacancy_detail.get('snippet', {}).get('requirement', '')}\n"
                                f"Обязанности: {vacancy_detail.get('snippet', {}).get('responsibility', '')}\n"
                                f"Зарплата: {str(vacancy_detail.get('salary', {}))}\n"
                                f"Город: {vacancy_detail.get('area', {}).get('name', '')}\n"
                                f"Опыт: {vacancy_detail.get('experience', {}).get('name', '')}\n"
                                f"Тип занятости: {vacancy_detail.get('employment', {}).get('name', '')}\n"
                                f"Дата публикации: {vacancy_detail.get('published_at', '')}"
                            )

                            # Отправляем данные вакансии в очередь Celery
                            process_hhru_data.delay(vacancy_text)
                            self.stdout.write(self.style.SUCCESS(f"Вакансия {hh_id} отправлена в очередь"))
                        else:
                            self.stdout.write(self.style.ERROR(
                                f"Не удалось получить детали вакансии {hh_id}, код ответа: {vacancy_response.status_code}"
                            ))
                            continue

                        # Используем детальную информацию для сохранения в базу
                        title = vacancy_detail.get("name", "")
                        description = vacancy_detail.get("description", "")
                        salary = vacancy_detail.get("salary")
                        salary_from = salary.get("from") if salary else None
                        salary_to = salary.get("to") if salary else None

                        # Двойная проверка, на случай если данные отличаются (хоть ранее мы уже проверили)
                        if salary_from is None and salary_to is None:
                            continue

                        currency = salary.get("currency") if salary else None
                        area = vacancy_detail.get("area", {}).get("name", "")

                        # Проверяем, существует ли вакансия с данным hh_id
                        vacancy = VacancyHH.objects.filter(hh_id=hh_id).first()
                        if vacancy:
                            vacancy.title = title
                            vacancy.description = description
                            vacancy.salary_from = salary_from
                            vacancy.salary_to = salary_to
                            vacancy.currency = currency
                            vacancy.area = area
                            vacancy.save()
                            self.stdout.write(f"Обновлена вакансия: {title}")
                        else:
                            VacancyHH.objects.create(
                                hh_id=hh_id,
                                title=title,
                                description=description,
                                salary_from=salary_from,
                                salary_to=salary_to,
                                currency=currency,
                                area=area,
                            )
                            self.stdout.write(self.style.SUCCESS(f"Добавлена вакансия: {title}"))
                        total_fetched_current += 1

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Ошибка при обработке вакансии {hh_id}: {str(e)}"))
                        continue

                    time.sleep(0.2)

                # Завершаем цикл, если достигнута последняя страница
                if params["page"] + 1 >= data.get("pages", 0):
                    break
                params["page"] += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Сбор для запроса '{current_query}' завершён. Всего вакансий загружено: {total_fetched_current}"
                )
            )

            # Циклический переход к следующему запросу
            current_index = (current_index + 1) % query_count

            sleep_time = random.randint(60, 198)
            self.stdout.write(self.style.WARNING(f"Ожидание {sleep_time} секунд перед следующим запросом..."))
            time.sleep(sleep_time)