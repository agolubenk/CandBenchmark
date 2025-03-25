from django.urls import path
from django.contrib.auth import views as auth_views
from apps.hhru import views

urlpatterns = [
    path('', views.HHVacancyListView.as_view(), name='hhru_vacancy_list'),
    path('vacancy/<int:pk>/', views.HHVacancyDetailView.as_view(), name='hhru_vacancy_detail'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
] 