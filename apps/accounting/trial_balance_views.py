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
def trial_balance_view(request):
    """Vista principal del Balance de Comprobación"""
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
        'title': 'Balance de Comprobación',
        'companies': companies,
    }
    return render(request, 'accounting/trial_balance.html', context)


@login_required
def trial_balance_data(request):
    """API para obtener datos del Balance de Comprobación"""
    company_id = request.GET.get('company_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date', timezone.now().date().isoformat())
    
    if not company_id:
        return JsonResponse({'error': 'Debe seleccionar una empresa'}, status=400)
    
    # Verificar permisos
    if not request.user.is_superuser:
        user_companies = request.session.get('user_companies', [])
        if user_companies != 'all' and int(company_id) not in user_companies:
            return JsonResponse({'error': 'No tiene permisos para esta empresa'}, status=403)
    
    try:
        company = Company.objects.get(id=company_id)
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
    except (Company.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Empresa o fecha inválida'}, status=400)
    
    # Obtener datos del balance de comprobación
    trial_balance_data = calculate_trial_balance(company, start_date_obj, end_date_obj)
    
    return JsonResponse({
        'company': {
            'id': company.id,
            'name': company.trade_name,
            'legal_name': company.legal_name,
        },
        'start_date': start_date,
        'end_date': end_date,
        'trial_balance': trial_balance_data
    })


def calculate_trial_balance(company, start_date, end_date):
    """Calcula el Balance de Comprobación para una empresa en un período"""
    
    # Obtener todas las cuentas que tienen movimientos registrados
    # Primero obtener IDs de cuentas que tienen líneas de asientos
    account_ids_with_movements = JournalEntryLine.objects.filter(
        journal_entry__company=company,
        journal_entry__state='posted'
    ).values_list('account_id', flat=True).distinct()
    
    # Obtener las cuentas correspondientes
    accounts = ChartOfAccounts.objects.filter(
        id__in=account_ids_with_movements,
        company=company,
        is_active=True
    ).select_related('account_type').order_by('code')
    
    trial_balance = []
    total_initial_debit = Decimal('0.00')
    total_initial_credit = Decimal('0.00')
    total_period_debit = Decimal('0.00')
    total_period_credit = Decimal('0.00')
    total_final_debit = Decimal('0.00')
    total_final_credit = Decimal('0.00')
    
    for account in accounts:
        # Saldo inicial (hasta la fecha de inicio - 1 día)
        initial_debit = Decimal('0.00')
        initial_credit = Decimal('0.00')
        
        if start_date:
            initial_movements = JournalEntryLine.objects.filter(
                account=account,
                journal_entry__company=company,
                journal_entry__date__lt=start_date,
                journal_entry__state='posted'
            ).aggregate(
                debit_sum=Sum('debit') or Decimal('0.00'),
                credit_sum=Sum('credit') or Decimal('0.00')
            )
            
            initial_debit_total = initial_movements['debit_sum'] or Decimal('0.00')
            initial_credit_total = initial_movements['credit_sum'] or Decimal('0.00')
            
            # Calcular saldo inicial según tipo de cuenta
            if account.account_type.code in ['ASSET', 'EXPENSE']:
                initial_balance = initial_debit_total - initial_credit_total
                if initial_balance >= 0:
                    initial_debit = initial_balance
                else:
                    initial_credit = abs(initial_balance)
            else:
                initial_balance = initial_credit_total - initial_debit_total
                if initial_balance >= 0:
                    initial_credit = initial_balance
                else:
                    initial_debit = abs(initial_balance)
        
        # Movimientos del período
        period_filter = {
            'account': account,
            'journal_entry__company': company,
            'journal_entry__state': 'posted'
        }
        
        if start_date:
            period_filter['journal_entry__date__gte'] = start_date
        if end_date:
            period_filter['journal_entry__date__lte'] = end_date
            
        period_movements = JournalEntryLine.objects.filter(
            **period_filter
        ).aggregate(
            debit_sum=Sum('debit') or Decimal('0.00'),
            credit_sum=Sum('credit') or Decimal('0.00')
        )
        
        period_debit = period_movements['debit_sum'] or Decimal('0.00')
        period_credit = period_movements['credit_sum'] or Decimal('0.00')
        
        # Saldo final
        final_debit_total = initial_debit + period_debit
        final_credit_total = initial_credit + period_credit
        
        # Calcular saldo final neto
        if account.account_type.code in ['ASSET', 'EXPENSE']:
            final_balance = final_debit_total - final_credit_total
            if final_balance >= 0:
                final_debit = final_balance
                final_credit = Decimal('0.00')
            else:
                final_debit = Decimal('0.00')
                final_credit = abs(final_balance)
        else:
            final_balance = final_credit_total - final_debit_total
            if final_balance >= 0:
                final_credit = final_balance
                final_debit = Decimal('0.00')
            else:
                final_credit = Decimal('0.00')
                final_debit = abs(final_balance)
        
        # Solo incluir cuentas con movimiento
        if (initial_debit + initial_credit + period_debit + period_credit + 
            final_debit + final_credit) > 0:
            
            account_data = {
                'code': account.code,
                'name': account.name,
                'account_type': account.account_type.name,
                'account_type_code': account.account_type.code,
                'initial_debit': float(initial_debit),
                'initial_credit': float(initial_credit),
                'period_debit': float(period_debit),
                'period_credit': float(period_credit),
                'final_debit': float(final_debit),
                'final_credit': float(final_credit),
            }
            
            trial_balance.append(account_data)
            
            # Sumar a totales
            total_initial_debit += initial_debit
            total_initial_credit += initial_credit
            total_period_debit += period_debit
            total_period_credit += period_credit
            total_final_debit += final_debit
            total_final_credit += final_credit
    
    # Totales del balance
    totals = {
        'initial_debit': float(total_initial_debit),
        'initial_credit': float(total_initial_credit),
        'period_debit': float(total_period_debit),
        'period_credit': float(total_period_credit),
        'final_debit': float(total_final_debit),
        'final_credit': float(total_final_credit),
        'initial_balanced': abs(total_initial_debit - total_initial_credit) < 0.01,
        'period_balanced': abs(total_period_debit - total_period_credit) < 0.01,
        'final_balanced': abs(total_final_debit - total_final_credit) < 0.01,
    }
    
    return {
        'accounts': trial_balance,
        'totals': totals
    }


@login_required
def export_trial_balance_pdf(request):
    """Exportar Balance de Comprobación a PDF"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from io import BytesIO
    
    company_id = request.GET.get('company_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date', timezone.now().date().isoformat())
    
    if not company_id:
        return JsonResponse({'error': 'Debe seleccionar una empresa'}, status=400)
    
    company = get_object_or_404(Company, id=company_id)
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
    
    # Crear PDF en memoria
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=0.5*inch, rightMargin=0.5*inch)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=20,
        alignment=1  # Centrado
    )
    
    # Título
    elements.append(Paragraph("BALANCE DE COMPROBACIÓN", title_style))
    elements.append(Paragraph(f"{company.legal_name}", styles['Heading3']))
    
    # Período
    if start_date_obj:
        period_text = f"Del {start_date_obj.strftime('%d/%m/%Y')} al {end_date_obj.strftime('%d/%m/%Y')}"
    else:
        period_text = f"Al {end_date_obj.strftime('%d/%m/%Y')}"
    elements.append(Paragraph(period_text, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Obtener datos del balance
    trial_data = calculate_trial_balance(company, start_date_obj, end_date_obj)
    
    # Crear tabla
    data = [
        ['Código', 'Cuenta', 'Saldo Inicial', '', 'Movimientos del Período', '', 'Saldo Final', ''],
        ['', '', 'Débito', 'Crédito', 'Débito', 'Crédito', 'Débito', 'Crédito']
    ]
    
    # Agregar cuentas
    for account in trial_data['accounts']:
        row = [
            account['code'],
            account['name'],
            f"${account['initial_debit']:,.2f}" if account['initial_debit'] > 0 else "",
            f"${account['initial_credit']:,.2f}" if account['initial_credit'] > 0 else "",
            f"${account['period_debit']:,.2f}" if account['period_debit'] > 0 else "",
            f"${account['period_credit']:,.2f}" if account['period_credit'] > 0 else "",
            f"${account['final_debit']:,.2f}" if account['final_debit'] > 0 else "",
            f"${account['final_credit']:,.2f}" if account['final_credit'] > 0 else "",
        ]
        data.append(row)
    
    # Totales
    totals = trial_data['totals']
    data.append(['', 'TOTALES', 
                f"${totals['initial_debit']:,.2f}",
                f"${totals['initial_credit']:,.2f}",
                f"${totals['period_debit']:,.2f}",
                f"${totals['period_credit']:,.2f}",
                f"${totals['final_debit']:,.2f}",
                f"${totals['final_credit']:,.2f}"])
    
    # Crear y estilizar tabla
    table = Table(data, colWidths=[1*inch, 3*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        # Encabezados
        ('BACKGROUND', (0, 0), (-1, 1), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),  # Montos a la derecha
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 1), 12),
        
        # Contenido
        ('BACKGROUND', (0, 2), (-1, -2), colors.beige),
        ('FONTSIZE', (0, 2), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        
        # Totales
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(table)
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    
    filename = f"balance_comprobacion_{company.trade_name}_{end_date_obj.strftime('%Y%m%d')}.pdf"
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response