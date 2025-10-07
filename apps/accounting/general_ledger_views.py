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
def general_ledger_view(request):
    """Vista principal del Libro Mayor"""
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
        'title': 'Libro Mayor',
        'companies': companies,
    }
    return render(request, 'accounting/general_ledger.html', context)


@login_required
def general_ledger_accounts(request):
    """API para obtener cuentas de una empresa"""
    company_id = request.GET.get('company_id')
    
    if not company_id:
        return JsonResponse({'error': 'Debe seleccionar una empresa'}, status=400)
    
    # Verificar permisos
    if not request.user.is_superuser:
        user_companies = request.session.get('user_companies', [])
        if user_companies != 'all' and int(company_id) not in user_companies:
            return JsonResponse({'error': 'No tiene permisos para esta empresa'}, status=403)
    
    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        return JsonResponse({'error': 'Empresa no encontrada'}, status=404)
    
    # Obtener cuentas que aceptan movimiento
    accounts = ChartOfAccounts.objects.filter(
        company=company,
        is_active=True,
        accepts_movement=True
    ).select_related('account_type').order_by('code')
    
    accounts_data = []
    for account in accounts:
        # Contar movimientos
        movements_count = JournalEntryLine.objects.filter(
            account=account,
            journal_entry__company=company,
            journal_entry__state='posted'
        ).count()
        
        accounts_data.append({
            'id': account.id,
            'code': account.code,
            'name': account.name,
            'account_type': account.account_type.name,
            'movements_count': movements_count
        })
    
    return JsonResponse({
        'company': {
            'id': company.id,
            'name': company.trade_name,
            'legal_name': company.legal_name,
        },
        'accounts': accounts_data
    })


@login_required
def general_ledger_data(request):
    """API para obtener datos del Libro Mayor de una cuenta específica"""
    company_id = request.GET.get('company_id')
    account_id = request.GET.get('account_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date', timezone.now().date().isoformat())
    
    if not company_id or not account_id:
        return JsonResponse({'error': 'Debe seleccionar empresa y cuenta'}, status=400)
    
    # Verificar permisos
    if not request.user.is_superuser:
        user_companies = request.session.get('user_companies', [])
        if user_companies != 'all' and int(company_id) not in user_companies:
            return JsonResponse({'error': 'No tiene permisos para esta empresa'}, status=403)
    
    try:
        company = Company.objects.get(id=company_id)
        account = ChartOfAccounts.objects.get(id=account_id, company=company)
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
    except (Company.DoesNotExist, ChartOfAccounts.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Empresa, cuenta o fecha inválida'}, status=400)
    
    # Obtener datos del libro mayor
    ledger_data = calculate_general_ledger(company, account, start_date_obj, end_date_obj)
    
    return JsonResponse({
        'company': {
            'id': company.id,
            'name': company.trade_name,
            'legal_name': company.legal_name,
        },
        'account': {
            'id': account.id,
            'code': account.code,
            'name': account.name,
            'account_type': account.account_type.name,
        },
        'start_date': start_date,
        'end_date': end_date,
        'ledger_data': ledger_data
    })


def calculate_general_ledger(company, account, start_date, end_date):
    """Calcula el Libro Mayor para una cuenta específica en un período"""
    
    # Saldo inicial
    initial_balance = Decimal('0.00')
    if start_date:
        # Obtener movimientos antes de la fecha de inicio
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
        else:
            initial_balance = initial_credit_total - initial_debit_total
    
    # Obtener movimientos del período
    movements_filter = {
        'account': account,
        'journal_entry__company': company,
        'journal_entry__state': 'posted'
    }
    
    if start_date:
        movements_filter['journal_entry__date__gte'] = start_date
    if end_date:
        movements_filter['journal_entry__date__lte'] = end_date
    
    movements = JournalEntryLine.objects.filter(
        **movements_filter
    ).select_related(
        'journal_entry'
    ).order_by(
        'journal_entry__date', 'journal_entry__number', 'id'
    )
    
    # Procesar movimientos
    ledger_entries = []
    running_balance = initial_balance
    
    for movement in movements:
        # Calcular el saldo corriente
        if account.account_type.code in ['ASSET', 'EXPENSE']:
            # Cuentas deudoras: débito suma, crédito resta
            balance_change = movement.debit - movement.credit
        else:
            # Cuentas acreedoras: crédito suma, débito resta
            balance_change = movement.credit - movement.debit
        
        running_balance += balance_change
        
        entry_data = {
            'date': movement.journal_entry.date.isoformat(),
            'journal_number': movement.journal_entry.number,
            'journal_id': movement.journal_entry.id,
            'description': movement.journal_entry.description or movement.description or '',
            'reference': movement.journal_entry.reference or '',
            'debit': float(movement.debit),
            'credit': float(movement.credit),
            'balance': float(running_balance),
            'state': movement.journal_entry.state
        }
        
        ledger_entries.append(entry_data)
    
    # Calcular totales
    total_debit = sum(entry['debit'] for entry in ledger_entries)
    total_credit = sum(entry['credit'] for entry in ledger_entries)
    final_balance = running_balance
    
    return {
        'initial_balance': float(initial_balance),
        'movements': ledger_entries,
        'totals': {
            'debit': total_debit,
            'credit': total_credit,
            'final_balance': float(final_balance),
            'movement_count': len(ledger_entries)
        }
    }


@login_required
def export_general_ledger_pdf(request):
    """Exportar Libro Mayor a PDF"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from io import BytesIO
    
    company_id = request.GET.get('company_id')
    account_id = request.GET.get('account_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date', timezone.now().date().isoformat())
    
    if not company_id or not account_id:
        return JsonResponse({'error': 'Debe seleccionar empresa y cuenta'}, status=400)
    
    company = get_object_or_404(Company, id=company_id)
    account = get_object_or_404(ChartOfAccounts, id=account_id, company=company)
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
    
    # Crear PDF en memoria
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=0.5*inch, rightMargin=0.5*inch)
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
    elements.append(Paragraph("LIBRO MAYOR", title_style))
    elements.append(Paragraph(f"{company.legal_name}", styles['Heading3']))
    
    # Información de la cuenta
    elements.append(Paragraph(f"Cuenta: {account.code} - {account.name}", styles['Heading4']))
    
    # Período
    if start_date_obj:
        period_text = f"Del {start_date_obj.strftime('%d/%m/%Y')} al {end_date_obj.strftime('%d/%m/%Y')}"
    else:
        period_text = f"Al {end_date_obj.strftime('%d/%m/%Y')}"
    elements.append(Paragraph(period_text, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Obtener datos del libro mayor
    ledger_data = calculate_general_ledger(company, account, start_date_obj, end_date_obj)
    
    # Saldo inicial
    if start_date_obj and ledger_data['initial_balance'] != 0:
        initial_text = f"Saldo Inicial: ${ledger_data['initial_balance']:,.2f}"
        elements.append(Paragraph(initial_text, styles['Normal']))
        elements.append(Spacer(1, 10))
    
    # Crear tabla
    data = [
        ['Fecha', 'Asiento', 'Descripción', 'Débito', 'Crédito', 'Saldo']
    ]
    
    # Agregar movimientos
    for movement in ledger_data['movements']:
        row = [
            datetime.strptime(movement['date'], '%Y-%m-%d').strftime('%d/%m/%Y'),
            movement['journal_number'],
            movement['description'][:40] + '...' if len(movement['description']) > 40 else movement['description'],
            f"${movement['debit']:,.2f}" if movement['debit'] > 0 else "",
            f"${movement['credit']:,.2f}" if movement['credit'] > 0 else "",
            f"${movement['balance']:,.2f}",
        ]
        data.append(row)
    
    # Totales
    if ledger_data['movements']:
        totals = ledger_data['totals']
        data.append(['', 'TOTALES', '',
                    f"${totals['debit']:,.2f}",
                    f"${totals['credit']:,.2f}",
                    f"${totals['final_balance']:,.2f}"])
    
    # Crear y estilizar tabla
    if len(data) > 1:  # Solo crear tabla si hay datos
        table = Table(data, colWidths=[1*inch, 1*inch, 2.5*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            # Encabezados
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),  # Montos a la derecha
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Contenido
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            # Totales
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("No hay movimientos en el período seleccionado", styles['Normal']))
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    
    filename = f"libro_mayor_{account.code}_{company.trade_name}_{end_date_obj.strftime('%Y%m%d')}.pdf"
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response