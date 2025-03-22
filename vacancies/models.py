from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .utils import unify_currency, unify_grade
from simple_history.models import HistoricalRecords
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Vacancy(models.Model):
    company = models.CharField("Компания", max_length=255)
    geo = models.CharField("Локация", max_length=255, db_index=True)
    specialization = models.CharField("Специализация", max_length=255, db_index=True)
    grade = models.CharField("Грейд", max_length=255, db_index=True)
    salary_min = models.IntegerField(
        "Min",
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    salary_max = models.IntegerField(
        "Max",
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    bonus = models.CharField("Бонус", max_length=255, blank=True)
    bonus_conditions = models.CharField("Описание бонуса", max_length=255, blank=True)
    currency = models.CharField("Валюта", max_length=50)
    gross_net = models.CharField("Gross/Net", max_length=50)
    work_format = models.CharField("Формат работы", max_length=255)
    date_posted = models.DateField("Дата", db_index=True)
    source = models.CharField("Источник", max_length=255, blank=True)
    author = models.CharField("Автор", max_length=255, blank=True)
    description = models.TextField("Описание вакансии", blank=True)
    last_edited_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='edited_vacancies',
        verbose_name='Последний редактор'
    )
    last_edited_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата последнего редактирования'
    )

    def clean(self):
        if self.salary_min and self.salary_max and self.salary_min > self.salary_max:
            raise ValidationError("Минимальная зарплата не может быть больше максимальной")

    def save(self, *args, **kwargs):
        self.clean()
        # Приведение к единому формату
        self.currency = unify_currency(self.currency)
        self.grade = unify_grade(self.grade)
        super().save(*args, **kwargs)  # Вызов родительского save

    def __str__(self):
        return f"{self.company} ({self.grade} - {self.currency})"

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['-date_posted']


class GeminiResult(models.Model):
    input_text = models.TextField()
    processed_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result from {self.created_at}"

    class Meta:
        verbose_name = "Результат обработки AI с сайта"
        verbose_name_plural = "Результаты обработки AI с сайта"

# Новая модель для хранения кастомного промпта для Gemini AI
class GeminiPrompt(models.Model):
    prompt_text = models.TextField("Промпт для Gemini AI")
    updated_at = models.DateTimeField(auto_now=True)

    # Добавляем поле истории изменений
    history = HistoricalRecords()

    def __str__(self):
        # Выводим первые 50 символов промпта
        return self.prompt_text[:50]

    class Meta:
        verbose_name = "Промпт для AI"
        verbose_name_plural = "Промпт для AI"

class TaskQueue(models.Model):
    class Priority(models.IntegerChoices):
        LOW = 50, 'Low'
        MEDIUM = 25, 'Medium'
        HIGH = 5, 'High'
        CRITICAL = 0, 'Critical'

    data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    priority = models.IntegerField(choices=Priority.choices, default=Priority.LOW, null=False, blank=True)

    @classmethod
    def create(cls, data, priority=Priority.LOW):
        cls.objects.create(data=data, priority=priority)


class ExchangeRate(models.Model):
    currency = models.CharField('Валюта', max_length=3, unique=True)
    rate = models.DecimalField('Курс к BYN', max_digits=10, decimal_places=4)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Курс валюты'
        verbose_name_plural = 'Курсы валют'
        ordering = ['currency']

    def __str__(self):
        return f'{self.currency}: {self.rate} BYN'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    last_name = models.CharField('Фамилия', max_length=100, blank=True)
    first_name = models.CharField('Имя', max_length=100, blank=True)
    middle_name = models.CharField('Отчество', max_length=100, blank=True)
    company = models.CharField('Компания', max_length=200, blank=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    _skip_user_save = False

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'

    def save(self, *args, **kwargs):
        """Сохраняем профиль и синхронизируем данные с User"""
        if not self._skip_user_save:
            if self.first_name != self.user.first_name or self.last_name != self.user.last_name:
                self.user.first_name = self.first_name
                self.user.last_name = self.last_name
                self.user._skip_profile_save = True
                try:
                    self.user.save()
                finally:
                    self.user._skip_profile_save = False
        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создаем профиль при создании пользователя"""
    if created:
        UserProfile.objects.create(
            user=instance,
            first_name=instance.first_name,
            last_name=instance.last_name,
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    """Обновляем профиль при обновлении пользователя"""
    if hasattr(instance, '_skip_profile_save') and instance._skip_profile_save:
        return

    try:
        profile = instance.profile
        if profile.first_name != instance.first_name or profile.last_name != instance.last_name:
            profile.first_name = instance.first_name
            profile.last_name = instance.last_name
            profile._skip_user_save = True
            try:
                profile.save()
            finally:
                profile._skip_user_save = False
    except UserProfile.DoesNotExist:
        if not created:
            UserProfile.objects.create(
                user=instance,
                first_name=instance.first_name,
                last_name=instance.last_name,
                _skip_user_save=True
            )
