from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from decimal import Decimal
from datetime import datetime, date
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io

from apps.companies.models import Company
from .models import JournalEntry, JournalEntryLine


@login_required
def journal_book_view(request):
    """Vista principal del Libro Diario"""
    # Obtener empresas del usuario
    companies = Company.objects.filter(
        companyuser__user=request.user
    ).distinct()
    
    context = {
        'title': 'Libro Diario',
        'companies': companies,
    }
    return render(request, 'accounting/journal_book.html', context)


@login_required
def journal_book_data(request):
    """API para obtener datos del Libro Diario"""
    try:
        # Obtener parámetros
        company_id = request.GET.get('company_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 50))
        
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
        
        # Generar datos del libro diario
        journal_data = generate_journal_book_data(company, start_date, end_date, page, per_page)
        
        return JsonResponse(journal_data, safe=False)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error al generar el libro diario: {str(e)}'
        }, status=500)


def generate_journal_book_data(company, start_date, end_date, page=1, per_page=50):
    """Genera los datos del Libro Diario"""
    
    # Obtener asientos contables del período
    journal_entries = JournalEntry.objects.filter(
        company=company,
        date__range=[start_date, end_date]
    ).order_by('date', 'number', 'id')
    
    # Paginación
    paginator = Paginator(journal_entries, per_page)
    page_obj = paginator.get_page(page)
    
    # Preparar datos
    entries_data = []
    total_debit = Decimal('0.00')
    total_credit = Decimal('0.00')
    
    for entry in page_obj:
        # Obtener líneas del asiento
        lines = JournalEntryLine.objects.filter(
            journal_entry=entry
        ).select_related('account').order_by('id')
        
        entry_lines = []
        entry_debit = Decimal('0.00')
        entry_credit = Decimal('0.00')
        
        for line in lines:
            line_data = {
                'account_code': line.account.code,
                'account_name': line.account.name,
                'description': line.description or entry.description,
                'debit': float(line.debit) if line.debit else 0,
                'credit': float(line.credit) if line.credit else 0,
                'is_debit': bool(line.debit and line.debit > 0)
            }
            entry_lines.append(line_data)
            
            if line.debit:
                entry_debit += line.debit
            if line.credit:
                entry_credit += line.credit
        
        entry_data = {
            'id': entry.id,
            'date': entry.date.strftime('%Y-%m-%d'),
            'date_formatted': entry.date.strftime('%d/%m/%Y'),
            'number': entry.number,
            'description': entry.description,
            'reference': entry.reference or '',
            'lines': entry_lines,
            'total_debit': float(entry_debit),
            'total_credit': float(entry_credit),
            'is_balanced': entry_debit == entry_credit
        }
        entries_data.append(entry_data)
        
        total_debit += entry_debit
        total_credit += entry_credit
    
    # Estadísticas generales
    all_entries_count = journal_entries.count()
    all_entries_totals = JournalEntryLine.objects.filter(
        journal_entry__company=company,
        journal_entry__date__range=[start_date, end_date]
    ).aggregate(
        total_debit=Sum('debit'),
        total_credit=Sum('credit')
    )
    
    # Manejar casos donde Sum() retorna None
    total_debit = all_entries_totals['total_debit'] or Decimal('0')
    total_credit = all_entries_totals['total_credit'] or Decimal('0')
    
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
        'pagination': {
            'current_page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
            'total_entries': paginator.count,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None
        },
        'entries': entries_data,
        'page_totals': {
            'debit': float(total_debit),
            'credit': float(total_credit)
        },
        'period_totals': {
            'debit': float(total_debit),
            'credit': float(total_credit),
            'entries_count': all_entries_count
        }
    }


@login_required
def export_journal_book_pdf(request):
    """Exporta el Libro Diario a PDF"""
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
        
        # Generar PDF
        buffer = io.BytesIO()
        
        # Obtener todos los datos (sin paginación para PDF)
        all_entries = JournalEntry.objects.filter(
            company=company,
            date__range=[start_date, end_date]
        ).order_by('date', 'number', 'id')
        
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
        
        entry_header_style = ParagraphStyle(
            'EntryHeader',
            parent=styles['Normal'],
            fontSize=10,
            spaceBefore=15,
            spaceAfter=5,
            textColor=colors.HexColor('#333333'),
            fontName='Helvetica-Bold'
        )
        
        # Contenido del documento
        story = []
        
        # Encabezado
        story.append(Paragraph(company.legal_name, title_style))
        story.append(Paragraph(f"RUC: {company.ruc}", subtitle_style))
        story.append(Paragraph("LIBRO DIARIO", title_style))
        story.append(Paragraph(
            f"Del {start_date.strftime('%d/%m/%Y')} al {end_date.strftime('%d/%m/%Y')}",
            subtitle_style
        ))
        story.append(Spacer(1, 20))
        
        # Procesar cada asiento
        total_period_debit = Decimal('0.00')
        total_period_credit = Decimal('0.00')
        
        for entry in all_entries:
            # Encabezado del asiento
            entry_header = f"Asiento No. {entry.number} - Fecha: {entry.date.strftime('%d/%m/%Y')}"
            if entry.reference:
                entry_header += f" - Ref: {entry.reference}"
            
            story.append(Paragraph(entry_header, entry_header_style))
            
            if entry.description:
                story.append(Paragraph(f"Concepto: {entry.description}", styles['Normal']))
                story.append(Spacer(1, 5))
            
            # Obtener líneas del asiento
            lines = JournalEntryLine.objects.filter(
                journal_entry=entry
            ).select_related('account').order_by('id')
            
            # Crear tabla para el asiento
            table_data = []
            table_data.append(['Código', 'Cuenta', 'Concepto', 'Debe', 'Haber'])
            
            entry_debit = Decimal('0.00')
            entry_credit = Decimal('0.00')
            
            for line in lines:
                debit_str = f"${line.debit:,.2f}" if line.debit else "-"
                credit_str = f"${line.credit:,.2f}" if line.credit else "-"
                
                table_data.append([
                    line.account.code,
                    line.account.name,
                    line.description or entry.description or "",
                    debit_str,
                    credit_str
                ])
                
                if line.debit:
                    entry_debit += line.debit
                if line.credit:
                    entry_credit += line.credit
            
            # Fila de totales del asiento
            table_data.append([
                '', '', 'TOTALES:', 
                f"${entry_debit:,.2f}", 
                f"${entry_credit:,.2f}"
            ])
            
            # Crear tabla
            table = Table(table_data, colWidths=[60, 180, 200, 80, 80])
            table.setStyle(TableStyle([
                # Encabezado
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                
                # Datos
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -2), 8),
                ('ALIGN', (0, 1), (0, -2), 'CENTER'),  # Código
                ('ALIGN', (3, 1), (4, -2), 'RIGHT'),   # Montos
                
                # Fila de totales
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 9),
                ('ALIGN', (2, -1), (-1, -1), 'RIGHT'),
                
                # Bordes
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1f4788')),
                
                # Alternar colores de filas
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 15))
            
            total_period_debit += entry_debit
            total_period_credit += entry_credit
        
        # Resumen final
        if all_entries.exists():
            story.append(Spacer(1, 20))
            
            summary_data = [
                ['RESUMEN DEL PERÍODO', '', ''],
                ['Total de Asientos:', str(all_entries.count()), ''],
                ['Total Debe:', f"${total_period_debit:,.2f}", ''],
                ['Total Haber:', f"${total_period_credit:,.2f}", ''],
                ['Diferencia:', f"${abs(total_period_debit - total_period_credit):,.2f}", '']
            ]
            
            summary_table = Table(summary_data, colWidths=[200, 100, 100])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ]))
            
            story.append(summary_table)
        
        # Pie de página con fecha de generación
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
        filename = f"libro_diario_{company.ruc}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return HttpResponse(f'Error al generar PDF: {str(e)}', status=500)