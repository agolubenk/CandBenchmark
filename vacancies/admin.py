from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Vacancy, GeminiResult, GeminiPrompt, TaskQueue, ExchangeRate, UserProfile
from simple_history.admin import SimpleHistoryAdmin
from django import forms

class UserChangeForm(forms.ModelForm):
    middle_name = forms.CharField(label='Отчество', max_length=100, required=False)
    phone = forms.CharField(label='Телефон', max_length=20, required=False)
    company = forms.CharField(label='Компания', max_length=200, required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email',
                 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',
                 'last_login', 'date_joined', 'middle_name', 'phone', 'company')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            try:
                profile = self.instance.profile
                self.initial['middle_name'] = profile.middle_name
                self.initial['phone'] = profile.phone
                self.initial['company'] = profile.company
            except UserProfile.DoesNotExist:
                pass

    def save(self, commit=True):
        user = super().save(commit=False)
        
        if commit:
            user.save()
            
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                profile = UserProfile(user=user)
            
            profile.middle_name = self.cleaned_data.get('middle_name', '')
            profile.phone = self.cleaned_data.get('phone', '')
            profile.company = self.cleaned_data.get('company', '')
            profile.first_name = user.first_name
            profile.last_name = user.last_name
            profile.save()
        
        return user

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fk_name = 'user'

class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    form = UserChangeForm
    list_display = ('username', 'email', 'get_full_name', 'get_phone', 'get_company', 'is_staff')
    list_select_related = ('profile',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {
            'fields': (
                'last_name', 'first_name', 'middle_name',
                'email', 'phone', 'company'
            ),
            'classes': ('wide',),
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    def get_full_name(self, obj):
        try:
            return f"{obj.profile.last_name} {obj.profile.first_name} {obj.profile.middle_name}".strip()
        except UserProfile.DoesNotExist:
            return ""
    get_full_name.short_description = 'ФИО'

    def get_phone(self, obj):
        try:
            return obj.profile.phone
        except UserProfile.DoesNotExist:
            return ""
    get_phone.short_description = 'Телефон'

    def get_company(self, obj):
        try:
            return obj.profile.company
        except UserProfile.DoesNotExist:
            return ""
    get_company.short_description = 'Компания'

    def save_model(self, request, obj, form, change):
        """Сохраняем пользователя"""
        super().save_model(request, obj, form, change)
        # Синхронизируем данные с профилем
        try:
            profile = obj.profile
            if profile.first_name != obj.first_name or profile.last_name != obj.last_name:
                profile.first_name = obj.first_name
                profile.last_name = obj.last_name
                profile._skip_user_save = True
                profile.save()
        except UserProfile.DoesNotExist:
            pass

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

# Перерегистрируем модель User
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'company', 'phone')
    search_fields = ('user__username', 'first_name', 'last_name', 'company')

    def save_model(self, request, obj, form, change):
        """Сохраняем профиль"""
        if obj.first_name != obj.user.first_name or obj.last_name != obj.user.last_name:
            obj.user.first_name = obj.first_name
            obj.user.last_name = obj.last_name
            obj.user._skip_profile_save = True
            obj.user.save()
        super().save_model(request, obj, form, change)

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('company', 'specialization', 'grade', 'salary_min', 'salary_max', 'currency', 'date_posted')
    list_filter = ('grade', 'currency', 'date_posted')
    search_fields = ('company', 'specialization', 'description')

@admin.register(GeminiResult)
class GeminiResultAdmin(admin.ModelAdmin):
    list_display = ('created_at',)
    readonly_fields = ('created_at',)

@admin.register(GeminiPrompt)
class GeminiPromptAdmin(admin.ModelAdmin):
    list_display = ('prompt_text', 'updated_at')
    readonly_fields = ('updated_at',)

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('currency', 'rate', 'updated_at')
    readonly_fields = ('updated_at',)

admin.site.register(TaskQueue)