# Generated by Django 5.1.7 on 2025-03-22 17:44

import django.core.validators
import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(max_length=3, unique=True, verbose_name='Валюта')),
                ('rate', models.DecimalField(decimal_places=4, max_digits=10, verbose_name='Курс к BYN')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
            ],
            options={
                'verbose_name': 'Курс валюты',
                'verbose_name_plural': 'Курсы валют',
                'ordering': ['currency'],
            },
        ),
        migrations.CreateModel(
            name='GeminiPrompt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prompt_text', models.TextField(verbose_name='Промпт для Gemini AI')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Промпт для AI',
                'verbose_name_plural': 'Промпт для AI',
            },
        ),
        migrations.CreateModel(
            name='GeminiResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input_text', models.TextField()),
                ('processed_text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Результат обработки AI с сайта',
                'verbose_name_plural': 'Результаты обработки AI с сайта',
            },
        ),
        migrations.CreateModel(
            name='TaskQueue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('priority', models.IntegerField(blank=True, choices=[(50, 'Low'), (25, 'Medium'), (5, 'High'), (0, 'Critical')], default=50)),
            ],
        ),
        migrations.CreateModel(
            name='Vacancy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=255, verbose_name='Компания')),
                ('geo', models.CharField(db_index=True, max_length=255, verbose_name='Локация')),
                ('specialization', models.CharField(db_index=True, max_length=255, verbose_name='Специализация')),
                ('grade', models.CharField(db_index=True, max_length=255, verbose_name='Грейд')),
                ('salary_min', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Min')),
                ('salary_max', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Max')),
                ('bonus', models.CharField(blank=True, max_length=255, verbose_name='Бонус')),
                ('bonus_conditions', models.CharField(blank=True, max_length=255, verbose_name='Описание бонуса')),
                ('currency', models.CharField(max_length=50, verbose_name='Валюта')),
                ('gross_net', models.CharField(max_length=50, verbose_name='Gross/Net')),
                ('work_format', models.CharField(max_length=255, verbose_name='Формат работы')),
                ('date_posted', models.DateField(db_index=True, verbose_name='Дата')),
                ('source', models.CharField(blank=True, max_length=255, verbose_name='Источник')),
                ('author', models.CharField(blank=True, max_length=255, verbose_name='Автор')),
                ('description', models.TextField(blank=True, verbose_name='Описание вакансии')),
            ],
            options={
                'verbose_name': 'Сохраненная вакансия',
                'verbose_name_plural': 'Сохраненные вакансии',
            },
        ),
        migrations.CreateModel(
            name='HistoricalGeminiPrompt',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('prompt_text', models.TextField(verbose_name='Промпт для Gemini AI')),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Промпт для AI',
                'verbose_name_plural': 'historical Промпт для AI',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(blank=True, max_length=100, verbose_name='Фамилия')),
                ('first_name', models.CharField(blank=True, max_length=100, verbose_name='Имя')),
                ('middle_name', models.CharField(blank=True, max_length=100, verbose_name='Отчество')),
                ('company', models.CharField(blank=True, max_length=200, verbose_name='Компания')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Телефон')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Профиль пользователя',
                'verbose_name_plural': 'Профили пользователей',
            },
        ),
    ]
