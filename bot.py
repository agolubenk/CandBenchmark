import os
import logging
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

# Импорт моделей: TaskQueue
from vacancies.models import TaskQueue

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: CallbackContext) -> None:
    """
    Команда /start приветствует пользователя и сообщает,
    что для добавления вакансии следует использовать команду /vacancy.
    """
    message = (
        "Добро пожаловать в систему вакансий!\n"
        "Чтобы добавить вакансию с обработкой через Gemini AI, введите"
        "добавьте описание вакансии в любом удобном для Вас виде"
    )
    await update.message.reply_text(message)


@sync_to_async
def save_task(data):
    try:
        task = TaskQueue.objects.create(data=data)
        task.save()
        return "Задача на обработку вакансии успешно добавлена!"
    except Exception as e:
        error_text = f"Ошибка при сохранении задачи на обработку: {e}"
        logger.exception(error_text)
        return error_text

async def process_vacancy(update: Update, context: CallbackContext) -> int:
    """
    Обработка единственного сообщения с вакансиями в формате JSON.
    После разбора данных формируется текст вакансии, которому предшествует промпт.
    Ответ от Gemini AI сохраняется в базе данных в поле description модели Vacancy.
    """
    result = await save_task(update.message.text)
    await update.message.reply_text(result)
    return ConversationHandler.END


def main():
    # Замените YOUR_TELEGRAM_BOT_TOKEN на токен вашего бота
    bot_token = os.environ.get("BOT_TOKEN")

    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_vacancy))

    logger.info("Telegram-бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()
