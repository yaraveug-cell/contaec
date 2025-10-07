from django.http import JsonResponse
from django.views.generic import View
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from apps.inventory.models import Product
from apps.companies.models import CompanyUser

@method_decorator(staff_member_required, name='dispatch')
class ProductDescriptionAutocompleteView(View):
    """
    Vista AJAX para autocompletado de productos por descripción
    """
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:  # Mínimo 2 caracteres
            return JsonResponse({'results': []})
        
        return self._search_products(query)
    
    def post(self, request):
        """También manejar POST para compatibilidad"""
        query = request.POST.get('query', '').strip()
        
        if len(query) < 2:  # Mínimo 2 caracteres
            return JsonResponse({'results': []})
        
        return self._search_products(query)
    
    def _search_products(self, query):
        """Método común para búsqueda de productos"""
        # Obtener empresas del usuario
        if self.request.user.is_superuser:
            products = Product.objects.all()
        else:
            user_companies = CompanyUser.objects.filter(
                user=self.request.user, 
                is_active=True
            ).values_list('company_id', flat=True)
            products = Product.objects.filter(company_id__in=user_companies)
        
        # Buscar por nombre, descripción o código
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(code__icontains=query)
        ).select_related('company')[:20]  # Limitar a 20 resultados
        
        results = []
        for product in products:
            # Determinar qué mostrar como texto
            display_text = product.description if product.description else product.name
            
            results.append({
                'id': product.id,
                'text': display_text,
                'name': product.name,
                'description': product.description or product.name,
                'code': product.code,
                'sale_price': str(product.sale_price),
                'iva_rate': str(product.iva_rate),
                'unit_of_measure': product.unit_of_measure,
                'company': product.company.trade_name
            })
        
        return JsonResponse({'results': results})


def get_cash_accounts(request):
    """
    Vista AJAX para obtener cuentas de caja filtradas por empresa
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
        
    from apps.accounting.models import ChartOfAccounts
    
    company_id = request.GET.get('company_id')
    
    # Filtrar cuentas de caja
    queryset = ChartOfAccounts.objects.filter(
        accepts_movement=True,
        parent__name__icontains='CAJA'
    )
    
    # Filtrar por empresa según tipo de usuario
    if not request.user.is_superuser:
        # Usuario regular: solo sus empresas
        user_companies = CompanyUser.objects.filter(
            user=request.user, 
            is_active=True
        ).values_list('company', flat=True)
        queryset = queryset.filter(company__in=user_companies)
    elif company_id:
        # Superusuario con empresa específica
        queryset = queryset.filter(company_id=company_id)
    
    # Ordenar por código
    accounts = queryset.select_related('company').order_by('code')[:20]
    
    results = []
    for account in accounts:
        results.append({
            'id': account.id,
            'code': account.code,
            'name': account.name,
            'company': account.company.trade_name
        })
    
    return JsonResponse({'accounts': results})


def get_all_accounts(request):
    """
    Vista AJAX para obtener todas las cuentas que aceptan movimiento
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
        
    from apps.accounting.models import ChartOfAccounts
    
    company_id = request.GET.get('company_id')
    
    # Filtrar cuentas que aceptan movimiento
    queryset = ChartOfAccounts.objects.filter(accepts_movement=True)
    
    # Filtrar por empresa según tipo de usuario
    if not request.user.is_superuser:
        # Usuario regular: solo sus empresas
        user_companies = CompanyUser.objects.filter(
            user=request.user, 
            is_active=True
        ).values_list('company', flat=True)
        queryset = queryset.filter(company__in=user_companies)
    elif company_id:
        # Superusuario con empresa específica
        queryset = queryset.filter(company_id=company_id)
    
    # Ordenar por código
    accounts = queryset.select_related('company').order_by('code')[:50]
    
    results = []
    for account in accounts:
        results.append({
            'id': account.id,
            'code': account.code,
            'name': account.name,
            'company': account.company.trade_name
        })
    
    return JsonResponse({'accounts': results})