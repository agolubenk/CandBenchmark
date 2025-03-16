# hhru/management/commands/scrape_hhru.py
import requests
import time
from django.core.management.base import BaseCommand
from hhru.models import Vacancyhh
from hhru.queries import QUERY_LIST as queries

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
                "text": current_query,  # Подставляем текущий запрос
                "page": 0,
                "per_page": 20,         # Количество вакансий на одной странице
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
                    hh_id = item.get("id")
                    title = item.get("name")
                    description = item.get("snippet", {}).get("responsibility", "")
                    salary = item.get("salary")
                    salary_from = salary.get("from") if salary else None
                    salary_to = salary.get("to") if salary else None

                    # Пропускаем вакансии без заданных salary_from и salary_to
                    if salary_from is None and salary_to is None:
                        continue

                    currency = salary.get("currency") if salary else None
                    area = item.get("area", {}).get("name") if item.get("area") else None

                    # Проверяем, существует ли вакансия с данным hh_id
                    vacancy = Vacancyhh.objects.filter(hh_id=hh_id).first()
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
                        Vacancyhh.objects.create(
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

            self.stdout.write(self.style.WARNING("Ожидание 60 секунд перед следующим запросом..."))
            time.sleep(60)