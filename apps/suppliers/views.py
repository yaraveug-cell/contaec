from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from .models import PurchaseInvoice
from apps.companies.models import CompanyUser
from io import BytesIO
from datetime import datetime


def generate_sri_compliant_voucher(invoice, elements, styles):
    """
    Genera un comprobante de retención individual con formato SRI-compliant
    Esta función se usa tanto para comprobantes individuales como múltiples
    """
    # Estilos personalizados
    title_style = ParagraphStyle(
        'SRITitle',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.darkblue,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'SRIHeading',
        parent=styles['Heading2'],
        fontSize=11,
        spaceAfter=8,
        textColor=colors.darkblue,
        fontName='Helvetica-Bold',
        spaceBefore=8
    )
    
    normal_style = styles['Normal']
    
    # Título del comprobante
    elements.append(Paragraph("COMPROBANTE DE RETENCIÓN EN LA FUENTE", title_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Número y fecha del comprobante (SRI requirement)
    voucher_info_data = [
        ['No. Comprobante:', f"RET-{invoice.internal_number}", 'Fecha:', datetime.now().strftime('%d/%m/%Y')],
    ]
    voucher_info_table = Table(voucher_info_data, colWidths=[1.2*inch, 2*inch, 1*inch, 1.5*inch])
    voucher_info_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(voucher_info_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # DATOS DEL AGENTE DE RETENCIÓN (Empresa)
    elements.append(Paragraph("DATOS DEL AGENTE DE RETENCIÓN", heading_style))
    company_data = [
        ['Razón Social:', invoice.company.trade_name],
        ['RUC:', invoice.company.ruc],
        ['Dirección:', getattr(invoice.company, 'address', 'No especificada')],
        ['Teléfono:', getattr(invoice.company, 'phone', 'No especificado')],
    ]
    company_table = Table(company_data, colWidths=[1.5*inch, 4.5*inch])
    company_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(company_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # DATOS DEL SUJETO RETENIDO (Proveedor)
    elements.append(Paragraph("DATOS DEL SUJETO RETENIDO", heading_style))
    supplier_data = [
        ['Razón Social:', invoice.supplier.trade_name],
        ['RUC/Cédula:', invoice.supplier.identification],
        ['Tipo Contribuyente:', invoice.supplier.get_supplier_type_display()],
        ['Dirección:', getattr(invoice.supplier, 'address', 'No especificada')],
    ]
    supplier_table = Table(supplier_data, colWidths=[1.5*inch, 4.5*inch])
    supplier_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(supplier_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # INFORMACIÓN DE LA FACTURA
    elements.append(Paragraph("INFORMACIÓN DEL COMPROBANTE DE VENTA", heading_style))
    invoice_data = [
        ['Tipo Comprobante:', 'Factura'],
        ['Serie-Número:', invoice.supplier_invoice_number],
        ['Fecha Emisión:', invoice.date.strftime('%d/%m/%Y')],
        ['Base Imponible 0%:', f"$ 0.00"],
        ['Base Imponible 12%:', f"$ {invoice.subtotal:,.2f}"],
        ['Valor IVA:', f"$ {invoice.tax_amount:,.2f}"],
        ['TOTAL FACTURA:', f"$ {invoice.total:,.2f}"],
    ]
    invoice_table = Table(invoice_data, colWidths=[2*inch, 4*inch])
    invoice_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),  # Total en negrita
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),  # Resaltar total
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(invoice_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # DETALLE DE RETENCIONES (Formato SRI)
    elements.append(Paragraph("DETALLE DE RETENCIONES", heading_style))
    
    retention_data = [
        ['IMPUESTO', 'CÓDIGO', 'BASE IMPONIBLE', '% RETENCIÓN', 'VALOR RETENIDO']
    ]
    
    # Retención de IVA
    if invoice.iva_retention_amount > 0:
        retention_data.append([
            'IVA',
            '2',  # Código SRI para IVA
            f"$ {invoice.tax_amount:,.2f}",
            f"{invoice.iva_retention_percentage:.2f}%",
            f"$ {invoice.iva_retention_amount:,.2f}"
        ])
    
    # Retención de Impuesto a la Renta
    if invoice.ir_retention_amount > 0:
        retention_data.append([
            'RENTA',
            '1',  # Código SRI para Renta
            f"$ {invoice.subtotal:,.2f}",
            f"{invoice.ir_retention_percentage:.2f}%",
            f"$ {invoice.ir_retention_amount:,.2f}"
        ])
    
    # Total de retenciones
    retention_data.append([
        'TOTAL RETENIDO',
        '',
        '',
        '',
        f"$ {invoice.total_retentions:,.2f}"
    ])
    
    retention_table = Table(retention_data, colWidths=[1.2*inch, 0.8*inch, 1.4*inch, 1*inch, 1.4*inch])
    retention_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -2), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, -1), (-1, -1), colors.yellow),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    elements.append(retention_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # VALOR A PAGAR (Destacado según SRI)
    elements.append(Paragraph("LIQUIDACIÓN", heading_style))
    payment_data = [
        ['Total Factura:', f"$ {invoice.total:,.2f}"],
        ['(-) Total Retenciones:', f"$ {invoice.total_retentions:,.2f}"],
        ['VALOR NETO A PAGAR:', f"$ {invoice.net_payable:,.2f}"],
    ]
    payment_table = Table(payment_data, colWidths=[3*inch, 2*inch])
    payment_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -2), 10),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(payment_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # PIE DE PÁGINA CON INFORMACIÓN LEGAL
    footer_text = f"""
    <b>OBSERVACIONES:</b><br/>
    • Comprobante de Retención generado según Art. 50 del Reglamento de Comprobantes de Venta, Retención y Documentos Complementarios.<br/>
    • Este documento constituye crédito tributario para el sujeto retenido.<br/>
    • Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')} por el sistema ContaEC.
    """
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=normal_style,
        fontSize=8,
        textColor=colors.gray,
        spaceAfter=10,
        leftIndent=0,
        rightIndent=0
    )
    
    elements.append(Paragraph(footer_text, footer_style))
    
    return elements


@login_required
def print_retention_voucher(request, invoice_id):
    """
    Vista para generar e imprimir comprobante de retención individual en PDF SRI-compliant
    """
    # Validar seguridad: usuario solo puede imprimir facturas de sus empresas
    if not request.user.is_superuser:
        user_companies = CompanyUser.objects.filter(
            user=request.user
        ).values_list('company_id', flat=True)
        
        if not user_companies:
            messages.error(request, "No tiene empresas asignadas.")
            return HttpResponse("Acceso denegado", status=403)
    else:
        user_companies = None
    
    try:
        # Obtener la factura con validación de empresa
        if user_companies is not None:
            invoice = get_object_or_404(
                PurchaseInvoice.objects.select_related('company', 'supplier'),
                pk=invoice_id,
                company_id__in=user_companies
            )
        else:
            invoice = get_object_or_404(
                PurchaseInvoice.objects.select_related('company', 'supplier'),
                pk=invoice_id
            )
        
        # Verificar que la factura tiene retenciones
        if invoice.total_retentions <= 0:
            messages.error(request, f"La factura {invoice.internal_number} no tiene retenciones aplicadas.")
            return HttpResponse("Sin retenciones", status=400)
        
        # Generar PDF usando ReportLab con formato SRI
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=0.5*inch, rightMargin=0.5*inch, 
                               topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        
        # Obtener estilos
        styles = getSampleStyleSheet()
        
        # Generar comprobante SRI-compliant
        elements = generate_sri_compliant_voucher(invoice, elements, styles)
        
        # Generar PDF
        doc.build(elements)
        
        # Crear respuesta HTTP con PDF para descarga
        buffer.seek(0)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="comprobante_retencion_{invoice.internal_number}.pdf"'
        response.write(buffer.getvalue())
        buffer.close()
        
        return response
        
    except Exception as e:
        messages.error(request, f"Error al generar el comprobante: {str(e)}")
        return HttpResponse(f"Error interno: {str(e)}", status=500)


@login_required
def print_multiple_retention_vouchers(request):
    """
    Vista para generar múltiples comprobantes de retención SRI-compliant en un solo PDF
    """
    # Obtener IDs de facturas desde parámetros GET
    invoice_ids_param = request.GET.get('invoice_ids', '')
    if not invoice_ids_param:
        messages.error(request, "No se especificaron facturas para imprimir.")
        return HttpResponse("Parámetros faltantes", status=400)
    
    try:
        invoice_ids = [int(id.strip()) for id in invoice_ids_param.split(',') if id.strip()]
    except ValueError:
        messages.error(request, "IDs de factura inválidos.")
        return HttpResponse("Parámetros inválidos", status=400)
    
    # Validar seguridad: usuario solo puede imprimir facturas de sus empresas
    if not request.user.is_superuser:
        user_companies = CompanyUser.objects.filter(
            user=request.user
        ).values_list('company_id', flat=True)
        
        if not user_companies:
            messages.error(request, "No tiene empresas asignadas.")
            return HttpResponse("Acceso denegado", status=403)
            
        # Filtrar facturas por empresas del usuario
        invoices = PurchaseInvoice.objects.filter(
            pk__in=invoice_ids,
            company_id__in=user_companies,
            total_retentions__gt=0
        ).select_related('company', 'supplier').order_by('internal_number')
    else:
        invoices = PurchaseInvoice.objects.filter(
            pk__in=invoice_ids,
            total_retentions__gt=0
        ).select_related('company', 'supplier').order_by('internal_number')
    
    if not invoices:
        messages.error(request, "No se encontraron facturas válidas con retenciones.")
        return HttpResponse("Sin facturas válidas", status=404)
    
    try:
        # Generar PDF con múltiples comprobantes SRI-compliant
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=0.5*inch, rightMargin=0.5*inch,
                               topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        
        # Obtener estilos
        styles = getSampleStyleSheet()
        
        # Generar cada comprobante individual con formato SRI
        for i, invoice in enumerate(invoices):
            if i > 0:
                elements.append(PageBreak())  # Nueva página para cada comprobante
            
            # Generar comprobante SRI-compliant individual
            elements = generate_sri_compliant_voucher(invoice, elements, styles)
        
        # Generar PDF
        doc.build(elements)
        
        # Crear respuesta HTTP con PDF para descarga
        buffer.seek(0)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="comprobantes_retencion_lote_{len(invoices)}_facturas.pdf"'
        response.write(buffer.getvalue())
        buffer.close()
        
        return response
        
    except Exception as e:
        messages.error(request, f"Error al generar los comprobantes: {str(e)}")
        return HttpResponse(f"Error interno: {str(e)}", status=500)


# =====================================
# VISTAS PARA PDF DE FACTURAS DE COMPRA
# =====================================

@login_required
def print_purchase_invoice_pdf(request, invoice_id):
    """
    Vista para generar e imprimir factura de compra individual en PDF
    No afecta sistemas de facturación ni asientos contables existentes
    """
    try:
        # Obtener factura con validación de empresa
        invoice = get_object_or_404(PurchaseInvoice, pk=invoice_id)
        
        # Validación de seguridad por empresa
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            if invoice.company_id not in user_companies:
                messages.error(request, "No tiene permisos para acceder a esta factura.")
                return HttpResponse("Acceso denegado", status=403)
        
        # Generar PDF usando el generador mejorado
        from .purchase_invoice_pdf_enhanced import generate_purchase_invoice_pdf_enhanced
        
        pdf_buffer = generate_purchase_invoice_pdf_enhanced(invoice)
        
        # Crear respuesta HTTP con PDF para descarga
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="factura_compra_{invoice.internal_number}.pdf"'
        response.write(pdf_buffer.read())
        
        return response
        
    except PurchaseInvoice.DoesNotExist:
        messages.error(request, "Factura no encontrada.")
        return HttpResponse("Factura no encontrada", status=404)
    except Exception as e:
        messages.error(request, f"Error al generar PDF de factura: {str(e)}")
        return HttpResponse(f"Error interno: {str(e)}", status=500)


@login_required
def print_multiple_purchase_invoices_pdf(request):
    """
    Vista para generar múltiples facturas de compra en un solo PDF
    No afecta sistemas de facturación ni asientos contables existentes
    """
    try:
        # Obtener IDs de facturas desde parámetros GET
        invoice_ids = request.GET.get('invoice_ids', '')
        if not invoice_ids:
            messages.error(request, "No se especificaron facturas para imprimir.")
            return HttpResponse("No se especificaron facturas", status=400)
        
        # Convertir a lista de enteros
        try:
            invoice_ids = [int(id.strip()) for id in invoice_ids.split(',') if id.strip()]
        except ValueError:
            messages.error(request, "IDs de facturas inválidos.")
            return HttpResponse("IDs inválidos", status=400)
        
        # Obtener facturas con validación de empresa
        invoices = PurchaseInvoice.objects.filter(id__in=invoice_ids)
        
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            invoices = invoices.filter(company_id__in=user_companies)
        
        if not invoices.exists():
            messages.error(request, "No se encontraron facturas válidas para imprimir.")
            return HttpResponse("No se encontraron facturas", status=404)
        
        # Generar PDF con múltiples facturas
        from .purchase_invoice_pdf_enhanced import generate_multiple_purchase_invoices_pdf_enhanced
        
        pdf_buffer = generate_multiple_purchase_invoices_pdf_enhanced(invoices)
        
        # Crear respuesta HTTP con PDF para descarga
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="facturas_compra_lote_{len(invoices)}_documentos.pdf"'
        response.write(pdf_buffer.read())
        
        return response
        
    except Exception as e:
        messages.error(request, f"Error al generar PDFs de facturas: {str(e)}")
        return HttpResponse(f"Error interno: {str(e)}", status=500)