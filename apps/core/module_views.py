from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from apps.companies.models import CompanyUser


def user_has_accounting_access(user):
    """Verifica si el usuario tiene acceso a contabilidad"""
    if user.is_superuser or user.is_staff:
        return True
    
    # Verificar roles en empresas
    company_users = CompanyUser.objects.filter(user=user)
    allowed_roles = ['owner', 'admin', 'accountant']
    
    return any(cu.role in allowed_roles for cu in company_users)


def user_has_invoicing_access(user):
    """Verifica si el usuario tiene acceso a facturación"""
    if user.is_superuser or user.is_staff:
        return True
    
    company_users = CompanyUser.objects.filter(user=user)
    allowed_roles = ['owner', 'admin']
    
    return any(cu.role in allowed_roles for cu in company_users)


def user_has_full_admin_access(user):
    """Verifica si el usuario tiene acceso completo de administración"""
    return user.is_superuser


@login_required
@user_passes_test(user_has_accounting_access)
def accounting_module(request):
    """Vista del módulo de contabilidad"""
    from apps.companies.models import Company
    from apps.accounting.models import ChartOfAccounts, JournalEntry
    
    # Obtener empresas del usuario
    user_companies = CompanyUser.objects.filter(user=request.user).select_related('company')
    
    # Estadísticas básicas
    total_accounts = ChartOfAccounts.objects.filter(
        company__in=[cu.company for cu in user_companies]
    ).count()
    
    total_entries = JournalEntry.objects.filter(
        company__in=[cu.company for cu in user_companies]
    ).count()
    
    context = {
        'title': 'Módulo de Contabilidad - ContaEC',
        'user_companies': user_companies,
        'total_accounts': total_accounts,
        'total_entries': total_entries,
        'module': 'accounting'
    }
    return render(request, 'modules/accounting.html', context)


@login_required
@user_passes_test(user_has_invoicing_access)
def invoicing_module(request):
    """Vista del módulo de facturación"""
    try:
        from apps.invoicing.models import Invoice, Customer
        
        user_companies = CompanyUser.objects.filter(user=request.user).select_related('company')
        
        total_invoices = Invoice.objects.filter(
            company__in=[cu.company for cu in user_companies]
        ).count()
        
        total_customers = Customer.objects.filter(
            company__in=[cu.company for cu in user_companies]
        ).count()
    except ImportError:
        # Si no hay modelos, mostrar valores por defecto
        user_companies = CompanyUser.objects.filter(user=request.user).select_related('company')
        total_invoices = 0
        total_customers = 0
    
    context = {
        'title': 'Módulo de Facturación - ContaEC',
        'user_companies': user_companies,
        'total_invoices': total_invoices,
        'total_customers': total_customers,
        'module': 'invoicing'
    }
    return render(request, 'modules/invoicing.html', context)


@login_required
@user_passes_test(user_has_invoicing_access)
def inventory_module(request):
    """Vista del módulo de inventarios"""
    try:
        from apps.inventory.models import Product, StockMovement
        
        user_companies = CompanyUser.objects.filter(user=request.user).select_related('company')
        
        total_products = Product.objects.filter(
            company__in=[cu.company for cu in user_companies]
        ).count()
        
        total_movements = StockMovement.objects.filter(
            product__company__in=[cu.company for cu in user_companies]
        ).count()
    except ImportError:
        # Si no hay modelos, mostrar valores por defecto
        user_companies = CompanyUser.objects.filter(user=request.user).select_related('company')
        total_products = 0
        total_movements = 0
    
    context = {
        'title': 'Módulo de Inventarios - ContaEC',
        'user_companies': user_companies,
        'total_products': total_products,
        'total_movements': total_movements,
        'module': 'inventory'
    }
    return render(request, 'modules/inventory.html', context)


@login_required
@user_passes_test(user_has_accounting_access)
@login_required
@user_passes_test(user_has_accounting_access)
def reports_module(request):
    """Vista del módulo de reportes"""
    user_companies = CompanyUser.objects.filter(user=request.user).select_related('company')
    
    context = {
        'title': 'Módulo de Reportes - ContaEC',
        'user_companies': user_companies,
        'module': 'reports'
    }
    return render(request, 'modules/reports.html', context)


@login_required
@user_passes_test(user_has_full_admin_access)
def admin_module(request):
    """Redirige al panel de administración completo"""
    return redirect('/admin/')


@login_required
def companies_module(request):
    """Vista del módulo de empresas"""
    user_companies = CompanyUser.objects.filter(user=request.user).select_related('company')
    
    context = {
        'title': 'Mis Empresas - ContaEC',
        'user_companies': user_companies,
        'module': 'companies'
    }
    return render(request, 'modules/companies.html', context)