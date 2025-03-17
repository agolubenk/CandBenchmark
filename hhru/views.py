from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Vacancyhh
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

# Create your views here.

class HHVacancyListView(LoginRequiredMixin, ListView):
    model = Vacancyhh
    template_name = 'hhru/vacancy_list.html'
    context_object_name = 'vacancies'
    paginate_by = 50
    ordering = ['-id']  # или другое поле для сортировки
    login_url = '/login/'  # URL для перенаправления неавторизованных пользователей

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(area__icontains=search_query) |
                Q(hh_id__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset

class HHVacancyDetailView(LoginRequiredMixin, DetailView):
    model = Vacancyhh
    template_name = 'hhru/vacancy_detail.html'
    context_object_name = 'vacancy'
    login_url = '/login/'  # URL для перенаправления неавторизованных пользователей
