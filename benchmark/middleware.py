from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверяем, не является ли путь исключением
        if any(request.path.startswith(url) for url in settings.LOGIN_EXEMPT_URLS):
            return self.get_response(request)

        # Проверяем, авторизован ли пользователь
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        return self.get_response(request)

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not request.user.groups.filter(name='Administrators').exists() and not request.user.is_superuser:
                messages.error(request, 'У вас нет прав доступа к админ-панели')
                return redirect('profile')

        response = self.get_response(request)
        return response 