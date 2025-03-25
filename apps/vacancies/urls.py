from django.urls import path
from apps.vacancies import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_vacancy, name='add_vacancy'),
    path('export/', views.export_vacancies, name='export_vacancies'),
    path('gemini/', views.gemini, name='gemini'),
    path('gemini/results/', views.gemini_result, name='gemini_result'),
    path('change_prompt/', views.change_prompt, name='change_prompt'),
    path('vacancy/<int:vacancy_id>/', views.vacancy_detail, name='vacancy_detail'),
    path('vacancy/<int:vacancy_id>/edit/', views.edit_vacancy, name='edit_vacancy'),
    # Новый маршрут для сводной статистики
    path('pivot/', views.pivot_summary, name='pivot_summary'),
    path('upload-excel/', views.upload_excel, name='upload_excel'),
    path('preview-excel/', views.preview_excel, name='preview_excel'),
    path('process-excel/', views.process_excel, name='process_excel'),
]