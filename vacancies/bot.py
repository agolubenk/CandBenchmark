import os
import json
import logging
from datetime import datetime
import requests
from asgiref.sync import sync_to_async

# Настраиваем окружение Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CandBechmark.settings")
import django

django.setup()

# Импортируем необходимые классы из python-telegram-bot
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    CallbackContext,
)

# Импорт моделей: Vacancy и GeminiPrompt
from vacancies.models import Vacancy, GeminiPrompt

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Определяем единое состояние диалога
VACANCY = 1


async def start(update: Update, context: CallbackContext) -> None:
    """
    Команда /start приветствует пользователя и сообщает,
    что для добавления вакансии следует использовать команду /vacancy.
    """
    message = (
        "Добро пожаловать в систему вакансий!\n"
        "Чтобы добавить вакансию с обработкой через Gemini AI, введите команду /vacancy."
    )
    await update.message.reply_text(message)


async def ask_vacancy(update: Update, context: CallbackContext) -> int:
    """
    При вызове команды /vacancy бот отправляет инструкцию,
    как надо отправлять вакансию одним сообщением в формате JSON.
    Пример JSON приведён ниже.
    """
    sample = {
        "company": "ПримерКомпания",
        "geo": "Москва",
        "specialization": "Информационные технологии",
        "grade": "Senior",
        "salary_min": "100000",
        "salary_max": "150000",
        "bonus": "10%",
        "bonus_conditions": "При выполнении KPI",
        "currency": "RUB",
        "gross_net": "Gross",
        "work_format": "Удалённая",
        "date_posted": "2025-03-13",
        "source": "hh.ru",
        "author": "HR Department",
        "description": "Дополнительная информация о вакансии",
        # Опционально можно передать кастомный промпт для Gemini AI:
        # "prompt": "Сгенерируйте подробное описание вакансии с фокусом на технические навыки."
    }
    instructions = (
        "Отправьте вакансию в формате JSON одним сообщением.\n\n"
        "Пример формата:\n"
        f"{json.dumps(sample, indent=2, ensure_ascii=False)}"
    )
    await update.message.reply_text(instructions)
    return VACANCY


def call_gemini_ai(input_text: str, prompt: str) -> str:
    """
    Отправляет запрос к Gemini AI API, передавая объединённый промпт.
    Ожидается, что API принимает JSON с ключом 'prompt' и возвращает JSON с ключом 'result'.
    """
    gemini_api_url = os.environ.get("GEMINI_API_URL", "http://example.com/gemini")
    full_prompt = f"{prompt}\n\n{input_text}"
    try:
        response = requests.post(gemini_api_url, json={"prompt": full_prompt})
        if response.status_code == 200:
            result = response.json().get("result", "")
            return result
        else:
            return f"Ошибка Gemini AI: {response.status_code}"
    except Exception as e:
        logger.exception("Ошибка при вызове Gemini AI:")
        return f"Ошибка при вызове Gemini AI: {e}"


@sync_to_async
def get_prompt():
    return GeminiPrompt.objects.first()


@sync_to_async
def save_vacancy(company, geo, specialization, grade,
                 salary_min, salary_max, bonus, bonus_conditions,
                 currency, gross_net, work_format, date_posted, source,
                 author, gemini_response):
    try:
        vacancy = Vacancy.objects.create(
            company=company,
            geo=geo,
            specialization=specialization,
            grade=grade,
            salary_min=salary_min,
            salary_max=salary_max,
            bonus=bonus,
            bonus_conditions=bonus_conditions,
            currency=currency,
            gross_net=gross_net,
            work_format=work_format,
            date_posted=date_posted,
            source=source,
            author=author,
            description=gemini_response  # Ответ от Gemini AI сохраняется в поле description
        )
        vacancy.save()
        return "Вакансия успешно сохранена с обработанным описанием!"
    except Exception as e:
        logger.exception("Ошибка при сохранении вакансии:")
        return f"Ошибка при сохранении вакансии: {e}"

async def process_vacancy(update: Update, context: CallbackContext) -> int:
    """
    Обработка единственного сообщения с вакансиями в формате JSON.
    После разбора данных формируется текст вакансии, которому предшествует промпт.
    Ответ от Gemini AI сохраняется в базе данных в поле description модели Vacancy.
    """
    text = update.message.text
    try:
        data = json.loads(text)
    except Exception as e:
        await update.message.reply_text(f"Ошибка при разборе JSON: {e}")
        return VACANCY

    # Извлечение данных вакансии
    company = data.get("company", "")
    geo = data.get("geo", "")
    specialization = data.get("specialization", "")
    grade = data.get("grade", "")
    salary_min = int(data.get("salary_min", 0)) if data.get("salary_min") else None
    salary_max = int(data.get("salary_max", 0)) if data.get("salary_max") else None
    bonus = data.get("bonus", "")
    bonus_conditions = data.get("bonus_conditions", "")
    currency = data.get("currency", "")
    gross_net = data.get("gross_net", "")
    work_format = data.get("work_format", "")
    date_posted_str = data.get("date_posted", "")
    try:
        date_posted = datetime.strptime(date_posted_str,
                                        "%Y-%m-%d").date() if date_posted_str else datetime.today().date()
    except Exception:
        date_posted = datetime.today().date()
    source = data.get("source", "")
    author = data.get("author", "")
    vacancy_description = data.get("description", "")

    # Формирование текстового представления вакансии для передачи в Gemini AI
    vacancy_text = (
        f"Компания: {company}\n"
        f"Локация: {geo}\n"
        f"Специализация: {specialization}\n"
        f"Грейд: {grade}\n"
        f"ЗП от: {salary_min}\n"
        f"ЗП до: {salary_max}\n"
        f"Бонус: {bonus}\n"
        f"Условия бонуса: {bonus_conditions}\n"
        f"Валюта: {currency}\n"
        f"Тип оплаты (Gross/Net): {gross_net}\n"
        f"Формат работы: {work_format}\n"
        f"Дата публикации: {date_posted}\n"
        f"Источник: {source}\n"
        f"Автор: {author}\n"
        f"Дополнительно: {vacancy_description}"
    )

    # Определяем промпт: либо из JSON, либо дефолтный из модели GeminiPrompt, либо статичная строка
    prompt_text = data.get("prompt", None)
    if not prompt_text:
        gemini_prompt_instance = await get_prompt()
        if gemini_prompt_instance:
            prompt_text = gemini_prompt_instance.prompt_text
        else:
            prompt_text = "Проанализируйте данную вакансию и сгенерируйте подробное описание для её публикации."

    # Вызов Gemini AI
    gemini_response = call_gemini_ai(vacancy_text, prompt_text)

    # Сохранение вакансии в базу данных с полученным ответом
    result = await save_vacancy(company, geo, specialization, grade,
                                salary_min, salary_max, bonus, bonus_conditions,
                                currency, gross_net, work_format, date_posted, source,
                                author, gemini_response)
    await update.message.reply_text(result)
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END


def main():
    # Замените YOUR_TELEGRAM_BOT_TOKEN на токен вашего бота
    bot_token = "YOUR_TELEGRAM_BOT_TOKEN"

    application = Application.builder().token(bot_token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("vacancy", ask_vacancy)],
        states={
            VACANCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_vacancy)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    logger.info("Telegram-бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()