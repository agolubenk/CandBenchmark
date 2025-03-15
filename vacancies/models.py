from django.db import models
from .utils import unify_currency, unify_grade
from simple_history.models import HistoricalRecords


class Vacancy(models.Model):
    company = models.CharField(("Компания"),max_length=255)
    geo = models.CharField(("Локация"), max_length=255)
    specialization = models.CharField(("Специализация"), max_length=255)
    grade = models.CharField(("Грейд"), max_length=255)
    salary_min = models.IntegerField(("Min"), null=True, blank=True)
    salary_max = models.IntegerField(("Max"), null=True, blank=True)
    bonus = models.CharField(("Бонус"), max_length=255, blank=True)
    bonus_conditions = models.CharField(("Описание бонуса"), max_length=255, blank=True)
    currency = models.CharField(("Валюта"), max_length=50)
    gross_net = models.CharField(("Gross/Net"), max_length=50)
    work_format = models.CharField(("Формат работы"), max_length=255)
    date_posted = models.DateField(("Дата"))
    source = models.CharField(("Источник"), max_length=255, blank=True)
    author = models.CharField(("Автор"), max_length=255, blank=True)
    description = models.TextField("Описание вакансии", blank=True)

    def save(self, *args, **kwargs):
        # Приведение к единому формату
        self.currency = unify_currency(self.currency)
        self.grade = unify_grade(self.grade)
        super().save(*args, **kwargs)  # Вызов родительского save

    def __str__(self):
        return f"{self.company} ({self.grade} - {self.currency})"


class GeminiResult(models.Model):
    input_text = models.TextField()
    processed_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result from {self.created_at}"


# Новая модель для хранения кастомного промпта для Gemini AI
class GeminiPrompt(models.Model):
    prompt_text = models.TextField("Промпт для Gemini AI")
    updated_at = models.DateTimeField(auto_now=True)

    # Добавляем поле истории изменений
    history = HistoricalRecords()

    def __str__(self):
        # Выводим первые 50 символов промпта
        return self.prompt_text[:50]


class TaskQueue(models.Model):
    data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
