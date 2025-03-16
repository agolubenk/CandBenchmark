from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Vacancyhh

# Create your views here.

class HHVacancyListView(ListView):
    model = Vacancyhh
    template_name = 'hhru/vacancy_list.html'
    context_object_name = 'vacancies'
    paginate_by = 50
    ordering = ['-id']  # или другое поле для сортировки

class HHVacancyDetailView(DetailView):
    model = Vacancyhh
    template_name = 'hhru/vacancy_detail.html'
    context_object_name = 'vacancy'
