# vacancies/forms.py

from django import forms
from .models import GeminiPrompt, Vacancy, UserProfile
from .utils import unify_currency, unify_grade  # <-- Функции «причесывания», см. Шаг 0

class GeminiInputForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, label="")

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label="",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

# Новая форма для изменения промпта Gemini AI
class GeminiPromptForm(forms.ModelForm):
    class Meta:
        model = GeminiPrompt
        fields = ['prompt_text']
        labels = {
            'prompt_text': '',
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

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['last_name', 'first_name', 'middle_name', 'company', 'phone']
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }