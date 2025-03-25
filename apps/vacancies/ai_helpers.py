# vacancies/ai_helpers.py (например)

import logging
import json

logger = logging.getLogger(__name__)

def ask_ai_for_vacancy_data(row_text: str) -> dict:
    """
    Пример заглушки, где мы обращаемся к вашему AI (Gemini или ChatGPT).
    row_text - это строка из Excel (объединённые поля?), которую нужно разобрать.
    Возвращаем словарь.
    """
    # Здесь должна быть логика обращения к AI:
    # gemini.configure(api_key=...)
    # response = gemini_model.generate_content(...)
    # parsed = json.loads(response)
    # return parsed

    # Заглушка:
    logger.info("AI called with text: %s", row_text)
    # Представим, что AI вернул JSON. Для примера хардкожу:
    fake_response = {
        "Company": "Test Inc.",
        "Geo": "Minsk",
        "Specialization": "Python Developer",
        "Grade": "Middle+",
        "Salary Min": 1500,
        "Salary Max": 2000,
        "Bonus": "10%",
        "Bonus Conditions": "Performance-based",
        "Currency": "BYN",
        "Gross/Net": "gross",
        "Work Format": "Remote",
        "Date Posted": "2025-01-01",
        "Source": "Excel Import",
        "Author": "AI"
    }
    return fake_response