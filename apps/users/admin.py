from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'document_number', 'is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'document_type']
    search_fields = ['email', 'username', 'first_name', 'last_name', 'document_number']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Personal Adicional', {
            'fields': ('document_type', 'document_number', 'phone', 'address', 'is_verified')
        }),
        ('Fechas Importantes', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def has_change_permission(self, request, obj=None):
        """Permitir que los usuarios editen su propio perfil"""
        if obj and obj.id == request.user.id:
            return True
        return super().has_change_permission(request, obj)
    
    def has_view_permission(self, request, obj=None):
        """Permitir que los usuarios vean su propio perfil"""
        if obj and obj.id == request.user.id:
            return True
        return super().has_view_permission(request, obj)
    
    def get_queryset(self, request):
        """Los usuarios no-superuser solo pueden ver usuarios de sus empresas"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        # Los staff pueden ver usuarios de sus empresas
        if request.user.is_staff:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(user=request.user).values_list('company_id', flat=True)
            company_users = CompanyUser.objects.filter(company_id__in=user_companies).values_list('user_id', flat=True)
            return qs.filter(id__in=company_users)
        
        # Usuarios normales solo pueden ver su propio perfil
        return qs.filter(id=request.user.id)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'birth_date', 'timezone', 'language']
    list_filter = ['timezone', 'language']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']