from django.contrib import admin
from .models import Vacancyhh

@admin.register(Vacancyhh)
class VacancyhhAdmin(admin.ModelAdmin):
    list_display = ('hh_id', 'title', 'description', 'salary_from', 'salary_to', 'currency', 'area', 'created_at')

    search_fields = ('hh_id', 'title', 'description', 'salary_from', 'salary_to', 'currency', 'area', 'created_at')
    list_filter = ('title', 'salary_from', 'salary_to', 'currency', 'area', 'created_at')