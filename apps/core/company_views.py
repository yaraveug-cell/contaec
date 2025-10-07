from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count
from apps.companies.models import CompanyUser


def user_has_accounting_access(user):
    """Verificar si el usuario tiene acceso a contabilidad"""
    if user.is_superuser:
        return True
    
    # Verificar roles en empresas
    company_users = CompanyUser.objects.filter(user=user)
    allowed_roles = ['owner', 'admin', 'accountant']
    
    return any(cu.role in allowed_roles for cu in company_users)


def get_user_companies(request):
    """Obtener empresas del usuario actual"""
    if request.user.is_superuser:
        from apps.companies.models import Company
        return Company.objects.all()
    
    user_companies = request.session.get('user_companies', [])
    if user_companies and user_companies != 'all':
        from apps.companies.models import Company
        return Company.objects.filter(id__in=user_companies)
    return Company.objects.none()


@login_required
@user_passes_test(user_has_accounting_access)
def accounting_module(request):
    """Módulo de contabilidad filtrado por empresa"""
    from apps.accounting.models import ChartOfAccounts, JournalEntry
    
    user_companies = get_user_companies(request)
    
    # Estadísticas filtradas por empresa
    if user_companies.exists():
        total_accounts = ChartOfAccounts.objects.filter(
            company__in=user_companies, 
            is_active=True
        ).count()
        
        total_entries = JournalEntry.objects.filter(
            company__in=user_companies
        ).count()
        
        posted_entries = JournalEntry.objects.filter(
            company__in=user_companies,
            is_posted=True
        ).count()
    else:
        total_accounts = 0
        total_entries = 0
        posted_entries = 0
    
    context = {
        'title': 'Módulo de Contabilidad',
        'user_companies': user_companies,
        'total_accounts': total_accounts,
        'total_entries': total_entries,
        'posted_entries': posted_entries,
        'pending_entries': total_entries - posted_entries,
    }
    return render(request, 'modules/accounting.html', context)


@login_required
@user_passes_test(user_has_accounting_access)
def reports_module(request):
    """Módulo de reportes filtrado por empresa"""
    from apps.accounting.models import ChartOfAccounts
    
    user_companies = get_user_companies(request)
    
    context = {
        'title': 'Módulo de Reportes',
        'user_companies': user_companies,
        'has_data': user_companies.exists() and ChartOfAccounts.objects.filter(
            company__in=user_companies
        ).exists()
    }
    return render(request, 'modules/reports.html', context)


@login_required
def companies_module(request):
    """Módulo de empresas - solo las asignadas al usuario"""
    user_companies = get_user_companies(request)
    
    context = {
        'title': 'Módulo de Empresas',
        'user_companies': user_companies,
    }
    return render(request, 'modules/companies.html', context)