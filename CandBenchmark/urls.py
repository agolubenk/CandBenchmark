from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('admin/', admin.site.urls),
    path('', include('vacancies.urls')),
    path('hh/', include('hhru.urls')),
]