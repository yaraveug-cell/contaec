from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, date
from decimal import Decimal
import json

from .models import ChartOfAccounts, JournalEntryLine, FiscalYear
from apps.companies.models import Company, CompanyUser


@login_required
def balance_sheet_view(request):
    """Vista principal del Balance General"""
    # Obtener empresas del usuario
    if request.user.is_superuser:
        companies = Company.objects.filter(is_active=True)
    else:
        user_companies = request.session.get('user_companies', [])
        if user_companies and user_companies != 'all':
            companies = Company.objects.filter(id__in=user_companies, is_active=True)
        else:
            companies = Company.objects.none()
    
    context = {
        'title': 'Balance General',
        'companies': companies,
    }
    return render(request, 'accounting/balance_sheet.html', context)


@login_required
def balance_sheet_data(request):
    """API para obtener datos del Balance General"""
    company_id = request.GET.get('company_id')
    date_str = request.GET.get('date', timezone.now().date().isoformat())
    
    if not company_id:
        return JsonResponse({'error': 'Debe seleccionar una empresa'}, status=400)
    
    # Verificar permisos
    if not request.user.is_superuser:
        user_companies = request.session.get('user_companies', [])
        if user_companies != 'all' and int(company_id) not in user_companies:
            return JsonResponse({'error': 'No tiene permisos para esta empresa'}, status=403)
    
    try:
        company = Company.objects.get(id=company_id)
        report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (Company.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Empresa o fecha inválida'}, status=400)
    
    # Obtener cuentas y calcular saldos
    balance_data = calculate_balance_sheet(company, report_date)
    
    return JsonResponse({
        'company': {
            'id': company.id,
            'name': company.trade_name,
            'legal_name': company.legal_name,
        },
        'date': date_str,
        'balance_sheet': balance_data
    })


def calculate_balance_sheet(company, report_date):
    """Calcula el Balance General para una empresa en una fecha específica"""
    
    # Obtener todas las cuentas de la empresa
    accounts = ChartOfAccounts.objects.filter(
        company=company,
        is_active=True,
        accepts_movement=True
    ).select_related('account_type')
    
    # Calcular saldos para cada cuenta
    account_balances = {}
    
    for account in accounts:
        # Sumar movimientos hasta la fecha del reporte
        movements = JournalEntryLine.objects.filter(
            account=account,
            journal_entry__company=company,
            journal_entry__date__lte=report_date,
            journal_entry__state='posted'
        ).aggregate(
            total_debit=Sum('debit') or Decimal('0.00'),
            total_credit=Sum('credit') or Decimal('0.00')
        )
        
        debit_total = movements['total_debit'] or Decimal('0.00')
        credit_total = movements['total_credit'] or Decimal('0.00')
        
        # Calcular saldo según tipo de cuenta
        if account.account_type.code in ['ASSET', 'EXPENSE']:
            # Activos y Gastos: Débito aumenta, Crédito disminuye
            balance = debit_total - credit_total
        else:
            # Pasivos, Patrimonio, Ingresos: Crédito aumenta, Débito disminuye
            balance = credit_total - debit_total
        
        if balance != 0:  # Solo incluir cuentas con saldo
            account_balances[account.id] = {
                'code': account.code,
                'name': account.name,
                'account_type': account.account_type.code,
                'balance': float(balance),
                'debit_total': float(debit_total),
                'credit_total': float(credit_total),
                'parent_id': account.parent.id if account.parent else None
            }
    
    # Organizar por categorías del Balance General
    balance_sheet = {
        'assets': {
            'current_assets': [],
            'non_current_assets': [],
            'total': Decimal('0.00')
        },
        'liabilities': {
            'current_liabilities': [],
            'non_current_liabilities': [],
            'total': Decimal('0.00')
        },
        'equity': {
            'items': [],
            'total': Decimal('0.00')
        },
        'totals': {
            'total_assets': Decimal('0.00'),
            'total_liabilities_equity': Decimal('0.00'),
            'difference': Decimal('0.00')
        }
    }
    
    # Clasificar cuentas por tipo
    for account_id, data in account_balances.items():
        balance = Decimal(str(data['balance']))
        
        if data['account_type'] == 'ASSET':
            # Clasificar activos (simplificado - se puede mejorar con subcategorías)
            if data['code'].startswith('11') or data['code'].startswith('12'):
                balance_sheet['assets']['current_assets'].append(data)
            else:
                balance_sheet['assets']['non_current_assets'].append(data)
            balance_sheet['assets']['total'] += balance
            
        elif data['account_type'] == 'LIABILITY':
            # Clasificar pasivos
            if data['code'].startswith('21'):
                balance_sheet['liabilities']['current_liabilities'].append(data)
            else:
                balance_sheet['liabilities']['non_current_liabilities'].append(data)
            balance_sheet['liabilities']['total'] += balance
            
        elif data['account_type'] == 'EQUITY':
            balance_sheet['equity']['items'].append(data)
            balance_sheet['equity']['total'] += balance
    
    # Calcular totales
    balance_sheet['totals']['total_assets'] = balance_sheet['assets']['total']
    balance_sheet['totals']['total_liabilities_equity'] = (
        balance_sheet['liabilities']['total'] + balance_sheet['equity']['total']
    )
    balance_sheet['totals']['difference'] = (
        balance_sheet['totals']['total_assets'] - 
        balance_sheet['totals']['total_liabilities_equity']
    )
    
    # Convertir Decimals a float para JSON
    def decimal_to_float(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [decimal_to_float(item) for item in obj]
        return obj
    
    return decimal_to_float(balance_sheet)


@login_required
def export_balance_sheet_pdf(request):
    """Exportar Balance General a PDF"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from io import BytesIO
    
    company_id = request.GET.get('company_id')
    date_str = request.GET.get('date', timezone.now().date().isoformat())
    
    if not company_id:
        return JsonResponse({'error': 'Debe seleccionar una empresa'}, status=400)
    
    company = get_object_or_404(Company, id=company_id)
    report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    # Crear PDF en memoria
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Centrado
    )
    
    # Título
    elements.append(Paragraph(f"BALANCE GENERAL", title_style))
    elements.append(Paragraph(f"{company.legal_name}", styles['Heading2']))
    elements.append(Paragraph(f"Al {report_date.strftime('%d de %B de %Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Obtener datos del balance
    balance_data = calculate_balance_sheet(company, report_date)
    
    # Crear tabla del balance
    data = [
        ['ACTIVOS', '', 'PASIVOS Y PATRIMONIO', ''],
        ['', '', '', ''],
    ]
    
    # Activos Corrientes
    if balance_data['assets']['current_assets']:
        data.append(['ACTIVOS CORRIENTES', '', 'PASIVOS CORRIENTES', ''])
        max_rows = max(
            len(balance_data['assets']['current_assets']),
            len(balance_data['liabilities']['current_liabilities'])
        )
        
        for i in range(max_rows):
            left_account = balance_data['assets']['current_assets'][i] if i < len(balance_data['assets']['current_assets']) else None
            right_account = balance_data['liabilities']['current_liabilities'][i] if i < len(balance_data['liabilities']['current_liabilities']) else None
            
            left_name = f"{left_account['code']} {left_account['name']}" if left_account else ""
            left_amount = f"${left_account['balance']:,.2f}" if left_account else ""
            right_name = f"{right_account['code']} {right_account['name']}" if right_account else ""
            right_amount = f"${right_account['balance']:,.2f}" if right_account else ""
            
            data.append([left_name, left_amount, right_name, right_amount])
    
    # Totales
    data.append(['', '', '', ''])
    data.append(['TOTAL ACTIVOS', f"${balance_data['totals']['total_assets']:,.2f}", 
                'TOTAL PASIVOS Y PATRIMONIO', f"${balance_data['totals']['total_liabilities_equity']:,.2f}"])
    
    # Crear y estilizar tabla
    table = Table(data, colWidths=[3*inch, 1*inch, 3*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="balance_general_{company.trade_name}_{report_date}.pdf"'
    
    return response