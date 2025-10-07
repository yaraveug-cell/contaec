from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, date
from decimal import Decimal
import json

from .models import ChartOfAccounts, JournalEntryLine, FiscalYear, JournalEntry
from apps.companies.models import Company, CompanyUser


@login_required
def income_statement_view(request):
    """Vista principal del Estado de Resultados"""
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
        'title': 'Estado de Resultados',
        'companies': companies,
    }
    return render(request, 'accounting/income_statement.html', context)


@login_required
def income_statement_data(request):
    """API para obtener datos del Estado de Resultados"""
    company_id = request.GET.get('company_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not company_id or not start_date or not end_date:
        return JsonResponse({'error': 'Debe proporcionar empresa, fecha inicio y fecha fin'}, status=400)
    
    # Verificar permisos
    if not request.user.is_superuser:
        user_companies = request.session.get('user_companies', [])
        if user_companies != 'all' and int(company_id) not in user_companies:
            return JsonResponse({'error': 'No tiene permisos para esta empresa'}, status=403)
    
    try:
        company = Company.objects.get(id=company_id)
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
    except (Company.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Empresa o fecha inválida'}, status=400)
    
    # Obtener datos del estado de resultados
    income_statement_data = calculate_income_statement(company, start_date_obj, end_date_obj)
    
    return JsonResponse({
        'company': {
            'id': company.id,
            'name': company.trade_name,
            'legal_name': company.legal_name,
        },
        'start_date': start_date,
        'end_date': end_date,
        'income_statement': income_statement_data
    })


def calculate_income_statement(company, start_date, end_date):
    """Calcula el Estado de Resultados para una empresa en un período"""
    
    # Obtener movimientos del período
    movements = JournalEntryLine.objects.filter(
        journal_entry__company=company,
        journal_entry__date__gte=start_date,
        journal_entry__date__lte=end_date,
        journal_entry__state='posted'
    ).select_related('account', 'account__account_type')
    
    # Agrupar por cuenta
    account_balances = {}
    
    for movement in movements:
        account = movement.account
        account_id = account.id
        
        if account_id not in account_balances:
            account_balances[account_id] = {
                'account': account,
                'debit_total': Decimal('0.00'),
                'credit_total': Decimal('0.00'),
                'balance': Decimal('0.00')
            }
        
        account_balances[account_id]['debit_total'] += movement.debit
        account_balances[account_id]['credit_total'] += movement.credit
    
    # Clasificar cuentas y calcular balances
    income_accounts = []
    expense_accounts = []
    total_income = Decimal('0.00')
    total_expenses = Decimal('0.00')
    
    for account_data in account_balances.values():
        account = account_data['account']
        account_type = account.account_type.code
        
        # Calcular balance según naturaleza de la cuenta
        if account_type == 'INCOME':
            # Cuentas de ingreso: naturaleza acreedora
            balance = account_data['credit_total'] - account_data['debit_total']
            if balance != 0:
                income_accounts.append({
                    'code': account.code,
                    'name': account.name,
                    'account_type': account.account_type.name,
                    'debit': float(account_data['debit_total']),
                    'credit': float(account_data['credit_total']),
                    'balance': float(balance)
                })
                total_income += balance
                
        elif account_type == 'EXPENSE':
            # Cuentas de gasto: naturaleza deudora
            balance = account_data['debit_total'] - account_data['credit_total']
            if balance != 0:
                expense_accounts.append({
                    'code': account.code,
                    'name': account.name,
                    'account_type': account.account_type.name,
                    'debit': float(account_data['debit_total']),
                    'credit': float(account_data['credit_total']),
                    'balance': float(balance)
                })
                total_expenses += balance
    
    # Ordenar cuentas por código
    income_accounts.sort(key=lambda x: x['code'])
    expense_accounts.sort(key=lambda x: x['code'])
    
    # Calcular utilidad/pérdida neta
    net_income = total_income - total_expenses
    
    return {
        'income': {
            'accounts': income_accounts,
            'total': float(total_income)
        },
        'expenses': {
            'accounts': expense_accounts,
            'total': float(total_expenses)
        },
        'net_income': float(net_income),
        'is_profit': net_income >= 0
    }


@login_required
def export_income_statement_pdf(request):
    """Exportar Estado de Resultados a PDF"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from io import BytesIO
    
    company_id = request.GET.get('company_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not company_id or not start_date or not end_date:
        return JsonResponse({'error': 'Debe proporcionar todos los parámetros'}, status=400)
    
    company = get_object_or_404(Company, id=company_id)
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    # Crear PDF en memoria
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=0.5*inch, rightMargin=0.5*inch)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=1  # Centrado
    )
    
    # Título
    elements.append(Paragraph("ESTADO DE RESULTADOS", title_style))
    elements.append(Paragraph(f"{company.legal_name}", styles['Heading2']))
    
    # Período
    period_text = f"Del {start_date_obj.strftime('%d/%m/%Y')} al {end_date_obj.strftime('%d/%m/%Y')}"
    elements.append(Paragraph(period_text, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Obtener datos del estado de resultados
    income_data = calculate_income_statement(company, start_date_obj, end_date_obj)
    
    # Crear tabla
    data = [['Código', 'Cuenta', 'Valor']]
    
    # Ingresos
    data.append(['', 'INGRESOS', ''])
    if income_data['income']['accounts']:
        for account in income_data['income']['accounts']:
            data.append([
                account['code'],
                account['name'],
                f"${account['balance']:,.2f}"
            ])
    else:
        data.append(['', 'Sin movimientos de ingresos', '$0.00'])
    
    data.append(['', 'Total Ingresos', f"${income_data['income']['total']:,.2f}"])
    
    # Espaciador
    data.append(['', '', ''])
    
    # Gastos
    data.append(['', 'GASTOS', ''])
    if income_data['expenses']['accounts']:
        for account in income_data['expenses']['accounts']:
            data.append([
                account['code'],
                account['name'],
                f"${account['balance']:,.2f}"
            ])
    else:
        data.append(['', 'Sin movimientos de gastos', '$0.00'])
    
    data.append(['', 'Total Gastos', f"${income_data['expenses']['total']:,.2f}"])
    
    # Resultado
    data.append(['', '', ''])
    result_text = "UTILIDAD NETA" if income_data['is_profit'] else "PÉRDIDA NETA"
    data.append(['', result_text, f"${income_data['net_income']:,.2f}"])
    
    # Crear y estilizar tabla
    table = Table(data, colWidths=[1*inch, 3.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        # Encabezados
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),  # Montos a la derecha
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Contenido
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        
        # Secciones principales
        ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),  # INGRESOS
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        
        # Totales
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue if income_data['is_profit'] else colors.lightcoral),
    ]))
    
    elements.append(table)
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    
    filename = f"estado_resultados_{company.trade_name}_{start_date_obj.strftime('%Y%m%d')}_{end_date_obj.strftime('%Y%m%d')}.pdf"
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response