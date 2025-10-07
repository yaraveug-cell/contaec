from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from .models import ChartOfAccounts

@staff_member_required
@require_http_methods(["GET"])
def get_company_accounts(request):
    """Vista AJAX para obtener cuentas de una empresa específica"""
    company_id = request.GET.get('company_id')
    
    if not company_id:
        return JsonResponse({'accounts': []})
    
    # Filtrar por empresa y por permisos del usuario
    if request.user.is_superuser:
        accounts = ChartOfAccounts.objects.filter(
            company_id=company_id, 
            is_active=True
        )
    else:
        user_companies = request.session.get('user_companies', [])
        if user_companies and user_companies != 'all':
            if int(company_id) not in user_companies:
                return JsonResponse({'accounts': []})
        
        accounts = ChartOfAccounts.objects.filter(
            company_id=company_id, 
            is_active=True
        )
    
    accounts_data = [
        {
            'id': account.id,
            'code': account.code,
            'name': account.name
        }
        for account in accounts.order_by('code')
    ]
    
    return JsonResponse({'accounts': accounts_data})