from django.db import models
from .utils import unify_currency, unify_grade


class Vacancy(models.Model):
    company = models.CharField(max_length=255)
    geo = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255)
    grade = models.CharField(max_length=255)
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    bonus = models.CharField(max_length=255, blank=True)
    bonus_conditions = models.CharField(max_length=255, blank=True)
    currency = models.CharField(max_length=50)
    gross_net = models.CharField(max_length=50)
    work_format = models.CharField(max_length=255)
    date_posted = models.DateField()
    source = models.CharField(max_length=255, blank=True)
    author = models.CharField(max_length=255, blank=True)
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

    def __str__(self):
        # Выводим первые 50 символов промпта
        return self.prompt_text[:50]