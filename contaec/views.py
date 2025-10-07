from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from rest_framework.response import Response


def home_view(request):
    """Vista principal del sistema"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    context = {
        'title': 'ContaEC - Sistema de Contabilidad para Empresas Ecuatorianas',
        'description': 'Sistema integral de contabilidad diseñado específicamente para pequeñas y medianas empresas en Ecuador.',
        'version': '1.0.0',
        'features': [
            'Contabilidad General',
            'Facturación Electrónica SRI',
            'Inventarios',
            'Reportes Financieros',
            'Gestión Multiempresa',
            'API REST Completa'
        ]
    }
    return render(request, 'home.html', context)


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido {user.full_name}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Credenciales inválidas. Verifica tu email y contraseña.')
        else:
            messages.error(request, 'Por favor ingresa email y contraseña.')
    
    context = {
        'title': 'Iniciar Sesión - ContaEC'
    }
    return render(request, 'registration/login.html', context)


@login_required
def profile_view(request):
    """Vista del perfil personal del usuario"""
    from django.shortcuts import redirect
    
    # Redirigir al admin del usuario con los permisos correctos
    return redirect(f'/admin/users/user/{request.user.id}/change/')


@login_required
def dashboard_view(request):
    """Dashboard principal después del login"""
    from apps.companies.models import Company, CompanyUser
    from apps.core.permissions import get_available_modules
    from apps.accounting.models import JournalEntry, JournalEntryLine, ChartOfAccounts
    from apps.invoicing.models import Invoice
    from apps.suppliers.models import Supplier, PurchaseInvoice
    from django.db.models import Sum, Count, Q
    from django.utils import timezone
    from datetime import datetime, timedelta
    from decimal import Decimal
    
    # Obtener SOLO las empresas asignadas al usuario
    if request.user.is_superuser:
        # Superuser ve todas las empresas
        user_companies = CompanyUser.objects.all().select_related('company')
        all_companies = Company.objects.all()
    else:
        # Usuario normal solo ve sus empresas asignadas
        user_companies = CompanyUser.objects.filter(user=request.user).select_related('company')
        all_companies = Company.objects.filter(
            id__in=user_companies.values_list('company_id', flat=True)
        )
    
    # Obtener módulos disponibles usando la función centralizada de permisos
    modules = get_available_modules(request.user)
    
    # Obtener roles del usuario en las empresas
    user_roles = set()
    has_companies = user_companies.exists()
    
    for company_user in user_companies:
        user_roles.add(company_user.role)
    
    # Determinar el rol principal del usuario (el más alto)
    role_hierarchy = ['owner', 'admin', 'accountant', 'employee', 'viewer']
    primary_role = 'USER'
    for role in role_hierarchy:
        if role in user_roles:
            primary_role = role.upper()
            break
    
    # === CÁLCULO DE MÉTRICAS FINANCIERAS ===
    
    # Filtrar por empresas del usuario
    company_ids = all_companies.values_list('id', flat=True)
    
    # Métricas de Asientos Contables
    total_entries = JournalEntry.objects.filter(company__in=company_ids).count()
    draft_entries = JournalEntry.objects.filter(company__in=company_ids, state='draft').count()
    posted_entries = JournalEntry.objects.filter(company__in=company_ids, state='posted').count()
    
    # Métricas de Facturas de Venta
    total_invoices = Invoice.objects.filter(company__in=company_ids).count()
    draft_invoices = Invoice.objects.filter(company__in=company_ids, status='draft').count()
    sent_invoices = Invoice.objects.filter(company__in=company_ids, status='sent').count()
    paid_invoices = Invoice.objects.filter(company__in=company_ids, status='paid').count()
    
    # Métricas de Proveedores y Compras
    total_suppliers = Supplier.objects.filter(company__in=company_ids).count()
    active_suppliers = Supplier.objects.filter(company__in=company_ids, is_active=True).count()
    
    total_purchase_invoices = PurchaseInvoice.objects.filter(company__in=company_ids).count()
    draft_purchases = PurchaseInvoice.objects.filter(company__in=company_ids, status='draft').count()
    received_purchases = PurchaseInvoice.objects.filter(company__in=company_ids, status='received').count()
    validated_purchases = PurchaseInvoice.objects.filter(company__in=company_ids, status='validated').count()
    paid_purchases = PurchaseInvoice.objects.filter(company__in=company_ids, status='paid').count()
    
    # Fecha del mes actual
    today = timezone.now().date()
    first_day_month = today.replace(day=1)
    
    # Ingresos del mes (facturas pagadas)
    monthly_income = Invoice.objects.filter(
        company__in=company_ids,
        status='paid',
        created_at__date__gte=first_day_month
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    # Total Compras del Mes (facturas de compra validadas/pagadas)
    monthly_expenses = PurchaseInvoice.objects.filter(
        company__in=company_ids,
        status__in=['validated', 'paid'],
        created_at__date__gte=first_day_month
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    # Cuentas por pagar pendientes
    pending_payables = PurchaseInvoice.objects.filter(
        company__in=company_ids,
        status__in=['received', 'validated']
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    # Cálculo de Balance Completo (incluye cuentas de resultados)
    balance_data = {}
    try:
        # Obtener saldos por tipo de cuenta
        activos_query = JournalEntryLine.objects.filter(
            journal_entry__company__in=company_ids,
            journal_entry__state='posted',
            account__code__startswith='1'
        ).aggregate(
            debit_total=Sum('debit'),
            credit_total=Sum('credit')
        )
        
        pasivos_query = JournalEntryLine.objects.filter(
            journal_entry__company__in=company_ids,
            journal_entry__state='posted',
            account__code__startswith='2'
        ).aggregate(
            debit_total=Sum('debit'),
            credit_total=Sum('credit')
        )
        
        patrimonio_query = JournalEntryLine.objects.filter(
            journal_entry__company__in=company_ids,
            journal_entry__state='posted',
            account__code__startswith='3'
        ).aggregate(
            debit_total=Sum('debit'),
            credit_total=Sum('credit')
        )
        
        # INCLUIR CUENTAS DE RESULTADOS
        ingresos_query = JournalEntryLine.objects.filter(
            journal_entry__company__in=company_ids,
            journal_entry__state='posted',
            account__code__startswith='4'
        ).aggregate(
            debit_total=Sum('debit'),
            credit_total=Sum('credit')
        )
        
        gastos_query = JournalEntryLine.objects.filter(
            journal_entry__company__in=company_ids,
            journal_entry__state='posted',
            account__code__startswith='5'
        ).aggregate(
            debit_total=Sum('debit'),
            credit_total=Sum('credit')
        )
        
        # Calcular saldos netos
        activos_debit = activos_query['debit_total'] or Decimal('0.00')
        activos_credit = activos_query['credit_total'] or Decimal('0.00')
        activos_saldo = activos_debit - activos_credit
        
        pasivos_debit = pasivos_query['debit_total'] or Decimal('0.00')
        pasivos_credit = pasivos_query['credit_total'] or Decimal('0.00')
        pasivos_saldo = pasivos_credit - pasivos_debit
        
        patrimonio_debit = patrimonio_query['debit_total'] or Decimal('0.00')
        patrimonio_credit = patrimonio_query['credit_total'] or Decimal('0.00')
        patrimonio_saldo = patrimonio_credit - patrimonio_debit
        
        # Calcular resultado del ejercicio (ingresos - gastos)
        ingresos_debit = ingresos_query['debit_total'] or Decimal('0.00')
        ingresos_credit = ingresos_query['credit_total'] or Decimal('0.00')
        ingresos_neto = ingresos_credit - ingresos_debit  # Los ingresos son crédito
        
        gastos_debit = gastos_query['debit_total'] or Decimal('0.00')
        gastos_credit = gastos_query['credit_total'] or Decimal('0.00')
        gastos_neto = gastos_debit - gastos_credit  # Los gastos son débito
        
        resultado_ejercicio = ingresos_neto - gastos_neto
        
        # Patrimonio total incluye resultado del ejercicio
        patrimonio_total = patrimonio_saldo + resultado_ejercicio
        
        # Verificar ecuación contable: Activos = Pasivos + Patrimonio Total
        diferencia_balance = activos_saldo - (pasivos_saldo + patrimonio_total)
        
        balance_data = {
            'activos': activos_saldo,
            'pasivos': pasivos_saldo,
            'patrimonio': patrimonio_saldo,
            'patrimonio_total': patrimonio_total,
            'ingresos': ingresos_neto,
            'gastos': gastos_neto,
            'resultado_ejercicio': resultado_ejercicio,
            'diferencia': diferencia_balance,
            'is_balanced': abs(diferencia_balance) < Decimal('0.01')
        }
        
    except Exception as e:
        balance_data = {
            'activos': Decimal('0.00'),
            'pasivos': Decimal('0.00'),
            'patrimonio': Decimal('0.00'),
            'is_balanced': True,
            'error': str(e)
        }
    
    # Datos para gráficos
    chart_data = {
        'invoices_by_state': {
            'draft': draft_invoices,
            'sent': sent_invoices,
            'paid': paid_invoices,
            'cancelled': total_invoices - (draft_invoices + sent_invoices + paid_invoices)
        },
        'purchases_by_state': {
            'draft': draft_purchases,
            'received': received_purchases,
            'validated': validated_purchases,
            'paid': paid_purchases,
            'cancelled': total_purchase_invoices - (draft_purchases + received_purchases + validated_purchases + paid_purchases)
        },
        'entries_by_state': {
            'draft': draft_entries,
            'posted': posted_entries,
            'cancelled': total_entries - (draft_entries + posted_entries)
        },
        'financial_flow': {
            'income': float(monthly_income),
            'expenses': float(monthly_expenses),
            'net': float(monthly_income - monthly_expenses)
        }
    }
    
    # KPIs calculados
    kpis = {
        'total_invoices': total_invoices,
        'total_suppliers': total_suppliers,
        'total_purchases': total_purchase_invoices,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'monthly_profit': monthly_income - monthly_expenses,
        'pending_payables': pending_payables,
        'pending_entries': draft_entries,
        'balance_health': balance_data['is_balanced'],
        'collection_rate': round((paid_invoices / total_invoices * 100) if total_invoices > 0 else 0, 1),
        'payment_rate': round((paid_purchases / total_purchase_invoices * 100) if total_purchase_invoices > 0 else 0, 1),
        'posted_rate': round((posted_entries / total_entries * 100) if total_entries > 0 else 0, 1),
        'profit_margin': round(((monthly_income - monthly_expenses) / monthly_income * 100) if monthly_income > 0 else 0, 1)
    }
    
    context = {
        'title': 'Dashboard - ContaEC',
        'user_companies': user_companies,
        'available_companies': all_companies,
        'all_companies': all_companies,
        'total_companies': user_companies.count(),
        'modules': modules,
        'user_role': primary_role,
        'all_roles': list(user_roles),
        'has_companies': has_companies,
        'show_access_message': not has_companies and not request.user.is_superuser and not request.user.is_staff,
        
        # === MÉTRICAS FINANCIERAS ===
        'financial_metrics': {
            'journal_entries': {
                'total': total_entries,
                'draft': draft_entries,
                'posted': posted_entries
            },
            'invoices': {
                'total': total_invoices,
                'draft': draft_invoices,
                'sent': sent_invoices,
                'paid': paid_invoices
            },
            'suppliers': {
                'total': total_suppliers,
                'active': active_suppliers
            },
            'purchases': {
                'total': total_purchase_invoices,
                'draft': draft_purchases,
                'received': received_purchases,
                'validated': validated_purchases,
                'paid': paid_purchases
            },
            'balance': balance_data,
            'monthly_income': monthly_income,
            'monthly_expenses': monthly_expenses,
            'pending_payables': pending_payables
        },
        'kpis': kpis,
        'chart_data': chart_data,
        'current_month': today.strftime('%B %Y')
    }
    return render(request, 'dashboard.html', context)


def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('home')


def api_docs_view(request):
    """Vista de documentación de API"""
    return render(request, 'api_docs.html')


@api_view(['GET'])
def api_info(request):
    """Información de la API"""
    return Response({
        'message': 'Bienvenido a ContaEC API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/v1/auth/',
            'companies': '/api/v1/companies/',
            'accounting': '/api/v1/accounting/',
            'invoicing': '/api/v1/invoicing/',
            'inventory': '/api/v1/inventory/',
            'reports': '/api/v1/reports/',
            'sri': '/api/v1/sri/',
            'documentation': '/api/docs/',
            'schema': '/api/schema/'
        },
        'support': {
            'email': 'soporte@contaec.com',
            'docs': 'https://docs.contaec.com'
        }
    })