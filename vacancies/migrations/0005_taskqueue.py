# Generated by Django 4.2.20 on 2025-03-14 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0004_vacancy_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskQueue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
