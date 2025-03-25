from django.db import models


class VacancyHH(models.Model):
    hh_id = models.CharField(max_length=50, unique=True, verbose_name="ID вакансии hh.ru")
    title = models.CharField(max_length=255, verbose_name="Название вакансии")
    employer_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Название компании")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    salary_from = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Зарплата от"
    )
    salary_to = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Зарплата до"
    )
    currency = models.CharField(max_length=10, blank=True, null=True, verbose_name="Валюта")
    area = models.CharField(max_length=255, blank=True, null=True, verbose_name="Город/Регион")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Вакансия hh.ru"
        verbose_name_plural = "Вакансии hh.ru"