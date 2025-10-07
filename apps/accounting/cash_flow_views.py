from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Sum, Case, When, DecimalField, Value
from decimal import Decimal
from datetime import datetime, date
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io

from apps.companies.models import Company
from .models import JournalEntry, JournalEntryLine, ChartOfAccounts, AccountType


@login_required
def cash_flow_view(request):
    """Vista principal del Flujo de Caja"""
    # Obtener empresas del usuario
    companies = Company.objects.filter(
        companyuser__user=request.user
    ).distinct()
    
    context = {
        'title': 'Flujo de Caja',
        'companies': companies,
    }
    return render(request, 'accounting/cash_flow.html', context)


@login_required
def cash_flow_data(request):
    """API para obtener datos del Flujo de Caja"""
    try:
        # Obtener parámetros
        company_id = request.GET.get('company_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Validar parámetros requeridos
        if not company_id or not start_date or not end_date:
            return JsonResponse({
                'error': 'Debe proporcionar company_id, start_date y end_date'
            }, status=400)
        
        # Verificar acceso a la empresa
        try:
            company = Company.objects.get(
                id=company_id,
                companyuser__user=request.user
            )
        except Company.DoesNotExist:
            return JsonResponse({
                'error': 'No tiene acceso a esta empresa'
            }, status=403)
        
        # Convertir fechas
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Generar datos del flujo de caja
        cash_flow_data = calculate_cash_flow(company, start_date, end_date)
        
        return JsonResponse(cash_flow_data, safe=False)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error al generar el flujo de caja: {str(e)}'
        }, status=500)


def calculate_cash_flow(company, start_date, end_date):
    """Calcula el flujo de caja del período"""
    
    # Obtener cuentas de efectivo (Caja y Bancos)
    # Buscar cuentas que contengan palabras clave relacionadas con efectivo
    cash_keywords = ['caja', 'banco', 'efectivo', 'cash']
    cash_filter = Q()
    for keyword in cash_keywords:
        cash_filter |= Q(name__icontains=keyword)
    
    cash_accounts = ChartOfAccounts.objects.filter(
        company=company,
        account_type__code='ASSET',  # Solo activos
        is_active=True
    ).filter(cash_filter)
    
    # Saldo inicial de efectivo (antes del período)
    initial_balance = Decimal('0.00')
    for account in cash_accounts:
        # Calcular saldo inicial hasta la fecha de inicio
        account_balance = JournalEntryLine.objects.filter(
            journal_entry__company=company,
            journal_entry__date__lt=start_date,
            account=account
        ).aggregate(
            debit_sum=Sum('debit') or Decimal('0'),
            credit_sum=Sum('credit') or Decimal('0')
        )
        
        # Para cuentas de activo (efectivo), aumentan con débito
        account_initial = (account_balance['debit_sum'] or Decimal('0')) - (account_balance['credit_sum'] or Decimal('0'))
        initial_balance += account_initial
    
    # Obtener movimientos del período
    cash_movements = JournalEntryLine.objects.filter(
        journal_entry__company=company,
        journal_entry__date__range=[start_date, end_date],
        account__in=cash_accounts
    ).select_related('journal_entry', 'account')
    
    # Clasificar movimientos por actividades
    operating_inflows = []
    operating_outflows = []
    investing_inflows = []
    investing_outflows = []
    financing_inflows = []
    financing_outflows = []
    
    # Procesar cada movimiento
    for movement in cash_movements:
        movement_data = {
            'date': movement.journal_entry.date,
            'date_formatted': movement.journal_entry.date.strftime('%d/%m/%Y'),
            'entry_number': movement.journal_entry.number,
            'account_code': movement.account.code,
            'account_name': movement.account.name,
            'description': movement.description or movement.journal_entry.description,
            'debit': float(movement.debit) if movement.debit else 0,
            'credit': float(movement.credit) if movement.credit else 0,
            'amount': float(movement.debit - movement.credit)  # Positivo = entrada, Negativo = salida
        }
        
        # Clasificar por tipo de actividad basándose en la naturaleza del movimiento
        # Esta es una clasificación simplificada que puede ser mejorada
        activity_type = classify_cash_flow_activity(movement)
        
        if movement.debit > movement.credit:  # Entrada de efectivo
            if activity_type == 'operating':
                operating_inflows.append(movement_data)
            elif activity_type == 'investing':
                investing_inflows.append(movement_data)
            elif activity_type == 'financing':
                financing_inflows.append(movement_data)
        else:  # Salida de efectivo
            movement_data['amount'] = abs(movement_data['amount'])
            if activity_type == 'operating':
                operating_outflows.append(movement_data)
            elif activity_type == 'investing':
                investing_outflows.append(movement_data)
            elif activity_type == 'financing':
                financing_outflows.append(movement_data)
    
    # Calcular totales por actividad (convertir a Decimal para consistencia)
    operating_inflow_total = Decimal(str(sum(m['amount'] for m in operating_inflows) or 0))
    operating_outflow_total = Decimal(str(sum(m['amount'] for m in operating_outflows) or 0))
    net_operating = operating_inflow_total - operating_outflow_total
    
    investing_inflow_total = Decimal(str(sum(m['amount'] for m in investing_inflows) or 0))
    investing_outflow_total = Decimal(str(sum(m['amount'] for m in investing_outflows) or 0))
    net_investing = investing_inflow_total - investing_outflow_total
    
    financing_inflow_total = Decimal(str(sum(m['amount'] for m in financing_inflows) or 0))
    financing_outflow_total = Decimal(str(sum(m['amount'] for m in financing_outflows) or 0))
    net_financing = financing_inflow_total - financing_outflow_total
    
    # Flujo neto del período
    net_cash_flow = net_operating + net_investing + net_financing
    
    # Saldo final de efectivo
    final_balance = initial_balance + net_cash_flow
    
    return {
        'company': {
            'id': company.id,
            'legal_name': company.legal_name,
            'trade_name': company.trade_name,
            'ruc': company.ruc
        },
        'period': {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'start_date_formatted': start_date.strftime('%d/%m/%Y'),
            'end_date_formatted': end_date.strftime('%d/%m/%Y')
        },
        'cash_accounts': [
            {
                'code': account.code,
                'name': account.name
            } for account in cash_accounts
        ],
        'cash_flow': {
            'initial_balance': float(initial_balance),
            'operating_activities': {
                'inflows': operating_inflows,
                'outflows': operating_outflows,
                'inflow_total': float(operating_inflow_total),
                'outflow_total': float(operating_outflow_total),
                'net_flow': float(net_operating)
            },
            'investing_activities': {
                'inflows': investing_inflows,
                'outflows': investing_outflows,
                'inflow_total': float(investing_inflow_total),
                'outflow_total': float(investing_outflow_total),
                'net_flow': float(net_investing)
            },
            'financing_activities': {
                'inflows': financing_inflows,
                'outflows': financing_outflows,
                'inflow_total': float(financing_inflow_total),
                'outflow_total': float(financing_outflow_total),
                'net_flow': float(net_financing)
            },
            'net_cash_flow': float(net_cash_flow),
            'final_balance': float(final_balance)
        }
    }


def classify_cash_flow_activity(movement):
    """
    Clasifica un movimiento de efectivo en el tipo de actividad
    Esta es una clasificación simplificada que puede ser mejorada según las necesidades específicas
    """
    entry = movement.journal_entry
    description = (movement.description or entry.description or '').lower()
    
    # Palabras clave para actividades de operación
    operating_keywords = [
        'venta', 'cobro', 'cliente', 'ingreso', 'pago', 'proveedor', 'gasto', 
        'sueldos', 'salario', 'servicio', 'compra', 'inventario', 'iva', 
        'impuesto', 'nomina', 'operacion', 'alquiler', 'arriendo'
    ]
    
    # Palabras clave para actividades de inversión
    investing_keywords = [
        'activo', 'equipo', 'maquinaria', 'propiedad', 'terreno', 'edificio',
        'inversion', 'compra', 'venta', 'inmueble', 'vehiculo', 'tecnologia'
    ]
    
    # Palabras clave para actividades de financiamiento
    financing_keywords = [
        'prestamo', 'credito', 'banco', 'financiamiento', 'capital', 'socio',
        'dividendo', 'interes', 'deuda', 'bonos', 'accion', 'patrimonio'
    ]
    
    # Verificar palabras clave
    for keyword in financing_keywords:
        if keyword in description:
            return 'financing'
    
    for keyword in investing_keywords:
        if keyword in description:
            return 'investing'
    
    for keyword in operating_keywords:
        if keyword in description:
            return 'operating'
    
    # Por defecto, considerar como actividad de operación
    return 'operating'


@login_required
def export_cash_flow_pdf(request):
    """Exporta el Flujo de Caja a PDF"""
    try:
        # Obtener parámetros
        company_id = request.GET.get('company_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if not company_id or not start_date or not end_date:
            return HttpResponse('Parámetros requeridos faltantes', status=400)
        
        # Verificar acceso a la empresa
        try:
            company = Company.objects.get(
                id=company_id,
                companyuser__user=request.user
            )
        except Company.DoesNotExist:
            return HttpResponse('No tiene acceso a esta empresa', status=403)
        
        # Convertir fechas
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Generar datos
        cash_flow_data = calculate_cash_flow(company, start_date, end_date)
        
        # Generar PDF
        buffer = io.BytesIO()
        
        # Crear documento PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20,
            leftMargin=20,
            topMargin=30,
            bottomMargin=30
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            alignment=TA_CENTER,
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#1f4788')
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            alignment=TA_CENTER,
            fontSize=12,
            spaceAfter=10,
            textColor=colors.HexColor('#666666')
        )
        
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=12,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#2c5aa0'),
            fontName='Helvetica-Bold'
        )
        
        # Contenido del documento
        story = []
        
        # Encabezado
        story.append(Paragraph(company.legal_name, title_style))
        story.append(Paragraph(f"RUC: {company.ruc}", subtitle_style))
        story.append(Paragraph("ESTADO DE FLUJO DE EFECTIVO", title_style))
        story.append(Paragraph(
            f"Del {cash_flow_data['period']['start_date_formatted']} al {cash_flow_data['period']['end_date_formatted']}",
            subtitle_style
        ))
        story.append(Spacer(1, 20))
        
        # Saldo inicial
        initial_data = [
            ['EFECTIVO AL INICIO DEL PERÍODO', f"${cash_flow_data['cash_flow']['initial_balance']:,.2f}"]
        ]
        
        initial_table = Table(initial_data, colWidths=[400, 120])
        initial_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f4f8')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#1f4788')),
        ]))
        
        story.append(initial_table)
        story.append(Spacer(1, 15))
        
        # Actividades de Operación
        story.append(Paragraph("FLUJOS DE EFECTIVO POR ACTIVIDADES DE OPERACIÓN", section_style))
        
        operating_data = []
        operating = cash_flow_data['cash_flow']['operating_activities']
        
        # Entradas
        if operating['inflows']:
            operating_data.append(['Entradas de Efectivo:', ''])
            for inflow in operating['inflows']:
                operating_data.append([f"  {inflow['description']}", f"${inflow['amount']:,.2f}"])
            operating_data.append(['Subtotal Entradas:', f"${operating['inflow_total']:,.2f}"])
            operating_data.append(['', ''])
        
        # Salidas
        if operating['outflows']:
            operating_data.append(['Salidas de Efectivo:', ''])
            for outflow in operating['outflows']:
                operating_data.append([f"  {outflow['description']}", f"(${outflow['amount']:,.2f})"])
            operating_data.append(['Subtotal Salidas:', f"(${operating['outflow_total']:,.2f})"])
            operating_data.append(['', ''])
        
        operating_data.append(['Flujo Neto por Actividades de Operación:', f"${operating['net_flow']:,.2f}"])
        
        if operating_data:
            operating_table = Table(operating_data, colWidths=[400, 120])
            operating_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f8ff')),
                ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor('#1f4788')),
            ]))
            story.append(operating_table)
            story.append(Spacer(1, 15))
        
        # Actividades de Inversión
        story.append(Paragraph("FLUJOS DE EFECTIVO POR ACTIVIDADES DE INVERSIÓN", section_style))
        
        investing_data = []
        investing = cash_flow_data['cash_flow']['investing_activities']
        
        if investing['inflows'] or investing['outflows']:
            # Entradas
            if investing['inflows']:
                investing_data.append(['Entradas de Efectivo:', ''])
                for inflow in investing['inflows']:
                    investing_data.append([f"  {inflow['description']}", f"${inflow['amount']:,.2f}"])
                investing_data.append(['Subtotal Entradas:', f"${investing['inflow_total']:,.2f}"])
                investing_data.append(['', ''])
            
            # Salidas
            if investing['outflows']:
                investing_data.append(['Salidas de Efectivo:', ''])
                for outflow in investing['outflows']:
                    investing_data.append([f"  {outflow['description']}", f"(${outflow['amount']:,.2f})"])
                investing_data.append(['Subtotal Salidas:', f"(${investing['outflow_total']:,.2f})"])
                investing_data.append(['', ''])
            
            investing_data.append(['Flujo Neto por Actividades de Inversión:', f"${investing['net_flow']:,.2f}"])
        else:
            investing_data.append(['Sin movimientos de inversión en el período', '$0.00'])
        
        investing_table = Table(investing_data, colWidths=[400, 120])
        investing_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f8ff')),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor('#1f4788')),
        ]))
        story.append(investing_table)
        story.append(Spacer(1, 15))
        
        # Actividades de Financiamiento
        story.append(Paragraph("FLUJOS DE EFECTIVO POR ACTIVIDADES DE FINANCIAMIENTO", section_style))
        
        financing_data = []
        financing = cash_flow_data['cash_flow']['financing_activities']
        
        if financing['inflows'] or financing['outflows']:
            # Entradas
            if financing['inflows']:
                financing_data.append(['Entradas de Efectivo:', ''])
                for inflow in financing['inflows']:
                    financing_data.append([f"  {inflow['description']}", f"${inflow['amount']:,.2f}"])
                financing_data.append(['Subtotal Entradas:', f"${financing['inflow_total']:,.2f}"])
                financing_data.append(['', ''])
            
            # Salidas
            if financing['outflows']:
                financing_data.append(['Salidas de Efectivo:', ''])
                for outflow in financing['outflows']:
                    financing_data.append([f"  {outflow['description']}", f"(${outflow['amount']:,.2f})"])
                financing_data.append(['Subtotal Salidas:', f"(${financing['outflow_total']:,.2f})"])
                financing_data.append(['', ''])
            
            financing_data.append(['Flujo Neto por Actividades de Financiamiento:', f"${financing['net_flow']:,.2f}"])
        else:
            financing_data.append(['Sin movimientos de financiamiento en el período', '$0.00'])
        
        financing_table = Table(financing_data, colWidths=[400, 120])
        financing_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f8ff')),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor('#1f4788')),
        ]))
        story.append(financing_table)
        story.append(Spacer(1, 20))
        
        # Resumen Final
        summary_data = [
            ['RESUMEN DEL FLUJO DE EFECTIVO', ''],
            ['Efectivo al inicio del período', f"${cash_flow_data['cash_flow']['initial_balance']:,.2f}"],
            ['Flujo neto por actividades de operación', f"${operating['net_flow']:,.2f}"],
            ['Flujo neto por actividades de inversión', f"${investing['net_flow']:,.2f}"],
            ['Flujo neto por actividades de financiamiento', f"${financing['net_flow']:,.2f}"],
            ['Flujo neto del período', f"${cash_flow_data['cash_flow']['net_cash_flow']:,.2f}"],
            ['Efectivo al final del período', f"${cash_flow_data['cash_flow']['final_balance']:,.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[400, 120])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f4f8')),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#1f4788')),
            
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        
        story.append(summary_table)
        
        # Pie de página
        story.append(Spacer(1, 30))
        story.append(Paragraph(
            f"Reporte generado el {timezone.localtime(timezone.now()).strftime('%d/%m/%Y a las %H:%M')}",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
        ))
        
        # Generar PDF
        doc.build(story)
        
        # Configurar respuesta
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        filename = f"flujo_caja_{company.ruc}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return HttpResponse(f'Error al generar PDF: {str(e)}', status=500)