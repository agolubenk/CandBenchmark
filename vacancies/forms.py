# vacancies/forms.py

from django import forms
from .models import GeminiPrompt, Vacancy  # <-- Подтягиваем Vacancy
from .utils import unify_currency, unify_grade  # <-- Функции «причесывания», см. Шаг 0

class GeminiInputForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, label="Текст вакансии")

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label="Загрузите Excel-файл")

# Новая форма для изменения промпта Gemini AI
class GeminiPromptForm(forms.ModelForm):
    class Meta:
        model = GeminiPrompt
        fields = ['prompt_text']
        labels = {
            'prompt_text': 'Промпт для Gemini AI',
        }


# Форма для создания/редактирования вакансии
class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = '__all__'
        # Или перечислите, какие поля нужны:
        # fields = [
        #     'company', 'geo', 'specialization', 'grade',
        #     'salary_min', 'salary_max', 'bonus', 'bonus_conditions',
        #     'currency', 'gross_net', 'work_format', 'date_posted',
        #     'source', 'author', 'description'
        # ]

    def clean_currency(self):
        cur = self.cleaned_data.get('currency', '')
        return unify_currency(cur)

    def clean_grade(self):
        gr = self.cleaned_data.get('grade', '')
        return unify_grade(gr)