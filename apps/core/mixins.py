"""
Mixins centralizados para evitar duplicación de código
"""

from apps.companies.models import Company, CompanyUser


class CompanyContextMixin:
    """
    Mixin para proporcionar contexto de empresa en vistas CBV
    """
    
    def get_current_company(self):
        """
        Obtiene la empresa actual del usuario
        """
        if self.request.user.is_superuser:
            # Superuser puede ver todo, tomar la primera empresa disponible
            return Company.objects.first()
        
        # Para usuarios normales, obtener sus empresas
        user_companies = CompanyUser.objects.filter(
            user=self.request.user
        ).select_related('company')
        
        if user_companies.exists():
            return user_companies.first().company
            
        return None
    
    def get_user_companies(self):
        """
        Obtiene todas las empresas del usuario
        """
        if self.request.user.is_superuser:
            return Company.objects.all()
        
        return Company.objects.filter(
            companyuser__user=self.request.user
        )


class CompanyFilterMixin:
    """Mixin para filtrar por empresa del usuario - Versión centralizada"""
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        # Filtrar por empresas del usuario
        user_companies = request.session.get('user_companies', [])
        if user_companies and user_companies != 'all':
            if hasattr(self.model, 'company'):
                return qs.filter(company_id__in=user_companies)
            elif hasattr(self.model, 'warehouse') and hasattr(self.model.warehouse.field.related_model, 'company'):
                return qs.filter(warehouse__company_id__in=user_companies)
        return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request and request.user and db_field.name == "company" and not request.user.is_superuser:
            user_companies = request.session.get('user_companies', [])
            if user_companies and user_companies != 'all':
                kwargs["queryset"] = db_field.related_model.objects.filter(id__in=user_companies)
        elif request and request.user and db_field.name == "warehouse" and not request.user.is_superuser:
            user_companies = request.session.get('user_companies', [])
            if user_companies and user_companies != 'all':
                kwargs["queryset"] = db_field.related_model.objects.filter(company_id__in=user_companies)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)