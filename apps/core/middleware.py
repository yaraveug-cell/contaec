"""
Middleware personalizado para manejo de empresas
"""
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser


class CompanyMiddleware(MiddlewareMixin):
    """Middleware para gestionar el contexto de empresa actual"""
    
    def process_request(self, request):
        """Procesa la petición para establecer la empresa actual"""
        if isinstance(request.user, AnonymousUser):
            return None
        
        # Filtrar empresas del usuario para seguridad
        if request.user.is_authenticated and not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            # Obtener empresas asignadas al usuario
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            # Guardar en la sesión para usar en vistas y admin
            request.session['user_companies'] = list(user_companies)
        elif request.user.is_authenticated and request.user.is_superuser:
            # Los superusers pueden ver todas las empresas
            request.session['user_companies'] = 'all'
            
        # Obtener empresa del header o session
        company_id = request.META.get('HTTP_X_COMPANY_ID') or request.session.get('company_id')
        
        if company_id:
            try:
                from apps.companies.models import Company, CompanyUser
                company = Company.objects.get(
                    id=company_id,
                    companyuser__user=request.user,
                    is_active=True
                )
                request.current_company = company
            except (Company.DoesNotExist, ValueError):
                request.current_company = None
        else:
            request.current_company = None
        
        return None
    
    def process_response(self, request, response):
        """Procesa la respuesta"""
        return response