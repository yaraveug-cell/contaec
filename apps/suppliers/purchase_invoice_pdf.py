"""
Generador de PDF para facturas de compra conforme a regulaciones ecuatorianas (SRI)
Utiliza ReportLab para crear documentos PDF profesionales
Adaptado del sistema de facturas de venta - No afecta sistemas existentes
"""

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfgen import canvas
from django.utils import timezone
from decimal import Decimal
import os
from django.conf import settings


def generate_purchase_invoice_pdf(purchase_invoice):
    """
    Genera un PDF completo de la factura de compra
    
    Args:
        purchase_invoice: Instancia del modelo PurchaseInvoice
        
    Returns:
        BytesIO: Buffer con el contenido del PDF
    """
    buffer = BytesIO()
    
    # Configurar documento PDF
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=60,
        bottomMargin=60
    )
    
    # Obtener estilos
    styles = getSampleStyleSheet()
    
    # Estilos personalizados conforme regulaciones ecuatorianas
    title_style = ParagraphStyle(
        'PurchaseInvoiceTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12,
        alignment=1,  # Centrado
        textColor=colors.darkblue
    )
    
    company_style = ParagraphStyle(
        'CompanyInfo',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=0,  # Izquierda
    )
    
    supplier_style = ParagraphStyle(
        'SupplierInfo',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=4,
        alignment=0,
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=3,
    )
    
    # Lista de elementos del documento
    story = []
    
    # --- ENCABEZADO ---
    story.append(Paragraph("FACTURA DE COMPRA", title_style))
    story.append(Spacer(1, 20))
    
    # --- INFORMACIÓN DE LA EMPRESA ---
    company_info = []
    company_info.append([
        Paragraph("<b>EMPRESA COMPRADORA:</b>", company_style),
        Paragraph(f"<b>Nº INTERNO:</b> {purchase_invoice.internal_number}", company_style)
    ])
    company_info.append([
        Paragraph(f"<b>{purchase_invoice.company.trade_name}</b>", company_style),
        Paragraph(f"<b>Nº PROVEEDOR:</b> {purchase_invoice.supplier_invoice_number}", company_style)
    ])
    company_info.append([
        Paragraph(f"RUC: {purchase_invoice.company.ruc}", company_style),
        Paragraph(f"<b>FECHA:</b> {purchase_invoice.date.strftime('%d/%m/%Y')}", company_style)
    ])
    
    if hasattr(purchase_invoice.company, 'legal_name'):
        company_info.append([
            Paragraph(f"Razón Social: {purchase_invoice.company.legal_name}", company_style),
            ""
        ])
    
    company_table = Table(company_info, colWidths=[8*cm, 6*cm])
    company_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    story.append(company_table)
    story.append(Spacer(1, 20))
    
    # --- INFORMACIÓN DEL PROVEEDOR ---
    story.append(Paragraph("<b>PROVEEDOR:</b>", supplier_style))
    
    supplier_info = []
    supplier_info.append([
        Paragraph(f"<b>{purchase_invoice.supplier.trade_name}</b>", supplier_style),
    ])
    supplier_info.append([
        Paragraph(f"RUC/Cédula: {purchase_invoice.supplier.identification}", supplier_style),
    ])
    
    if hasattr(purchase_invoice.supplier, 'address') and purchase_invoice.supplier.address:
        supplier_info.append([
            Paragraph(f"Dirección: {purchase_invoice.supplier.address}", supplier_style),
        ])
    
    if hasattr(purchase_invoice.supplier, 'phone') and purchase_invoice.supplier.phone:
        supplier_info.append([
            Paragraph(f"Teléfono: {purchase_invoice.supplier.phone}", supplier_style),
        ])
    
    supplier_table = Table(supplier_info, colWidths=[14*cm])
    supplier_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
    ]))
    
    story.append(supplier_table)
    story.append(Spacer(1, 20))
    
    # --- DETALLE DE LÍNEAS DE FACTURA ---
    story.append(Paragraph("<b>DETALLE:</b>", normal_style))
    
    # Encabezados de la tabla de líneas
    line_headers = [
        'Descripción',
        'Cant.',
        'P. Unit.',
        'Desc.%',
        'IVA%',
        'Total'
    ]
    
    line_data = [line_headers]
    
    # Agregar líneas de la factura
    for line in purchase_invoice.lines.all():
        line_data.append([
            Paragraph(str(line.description), normal_style),
            str(line.quantity),
            f"${line.unit_cost:,.2f}",
            f"{line.discount}%",
            f"{line.iva_rate}%",
            f"${line.line_total:,.2f}"
        ])
    
    # Crear tabla de líneas
    lines_table = Table(line_data, colWidths=[6*cm, 1.5*cm, 2*cm, 1.5*cm, 1.5*cm, 2.5*cm])
    lines_table.setStyle(TableStyle([
        # Encabezados
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Datos
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # Números alineados a la derecha
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),    # Descripción a la izquierda
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white]),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(lines_table)
    story.append(Spacer(1, 20))
    
    # --- TOTALES ---
    totals_data = []
    
    # Subtotal
    totals_data.append(['', '', 'SUBTOTAL:', f'${purchase_invoice.subtotal:,.2f}'])
    
    # IVA
    totals_data.append(['', '', 'IVA:', f'${purchase_invoice.tax_amount:,.2f}'])
    
    # Total Bruto
    totals_data.append(['', '', 'TOTAL BRUTO:', f'${purchase_invoice.total:,.2f}'])
    
    # Línea separadora
    totals_data.append(['', '', '─' * 20, '─' * 15])
    
    # Retenciones (si aplica)
    if purchase_invoice.iva_retention_amount > 0:
        totals_data.append([
            '', '', 
            f'RET. IVA ({purchase_invoice.iva_retention_percentage}%):', 
            f'-${purchase_invoice.iva_retention_amount:,.2f}'
        ])
    
    if purchase_invoice.ir_retention_amount > 0:
        totals_data.append([
            '', '', 
            f'RET. IR ({purchase_invoice.ir_retention_percentage}%):', 
            f'-${purchase_invoice.ir_retention_amount:,.2f}'
        ])
    
    # Total retenciones
    if purchase_invoice.total_retentions > 0:
        totals_data.append(['', '', 'TOTAL RETENCIONES:', f'-${purchase_invoice.total_retentions:,.2f}'])
    
    # Neto a pagar
    totals_data.append(['', '', '', ''])  # Línea en blanco
    totals_data.append(['', '', 'NETO A PAGAR:', f'${purchase_invoice.net_payable:,.2f}'])
    
    totals_table = Table(totals_data, colWidths=[4*cm, 4*cm, 3*cm, 3*cm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (2, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (2, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        
        # Destacar neto a pagar
        ('BACKGROUND', (2, -1), (-1, -1), colors.lightblue),
        ('BOX', (2, -1), (-1, -1), 2, colors.darkblue),
        ('FONTSIZE', (2, -1), (-1, -1), 12),
    ]))
    
    story.append(totals_table)
    story.append(Spacer(1, 30))
    
    # --- PIE DE PÁGINA ---
    footer_info = [
        f"Documento generado el: {timezone.now().strftime('%d/%m/%Y %H:%M')}",
        f"Sistema ContaEC - Contabilidad Ecuatoriana",
        "Este documento es una representación interna de la factura de compra registrada en el sistema."
    ]
    
    for info in footer_info:
        story.append(Paragraph(info, ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1,  # Centrado
            spaceAfter=3
        )))
    
    # Construir PDF
    doc.build(story)
    
    # Retornar buffer
    buffer.seek(0)
    return buffer


def generate_multiple_purchase_invoices_pdf(invoices):
    """
    Genera un PDF con múltiples facturas de compra
    
    Args:
        invoices: QuerySet de PurchaseInvoice
        
    Returns:
        BytesIO: Buffer con el contenido del PDF
    """
    buffer = BytesIO()
    
    # Configurar documento PDF
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=60,
        bottomMargin=60
    )
    
    story = []
    
    # Título del documento
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'MultipleInvoicesTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        alignment=1,
        textColor=colors.darkblue
    )
    
    story.append(Paragraph(f"FACTURAS DE COMPRA - LOTE DE {len(invoices)} DOCUMENTOS", title_style))
    story.append(Paragraph(f"Generado el: {timezone.now().strftime('%d/%m/%Y %H:%M')}", ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        spaceAfter=30
    )))
    
    # Generar cada factura
    for i, invoice in enumerate(invoices):
        if i > 0:
            story.append(PageBreak())  # Nueva página para cada factura
        
        # Generar contenido de la factura individual
        individual_buffer = generate_purchase_invoice_pdf(invoice)
        
        # Re-crear el story para esta factura específica
        # (esto es una simplificación, en un caso real se extraería el contenido)
        story.append(Paragraph(f"FACTURA DE COMPRA #{invoice.internal_number}", ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            textColor=colors.darkblue
        )))
        
        story.append(Paragraph(f"Proveedor: {invoice.supplier.trade_name}", styles['Normal']))
        story.append(Paragraph(f"Fecha: {invoice.date.strftime('%d/%m/%Y')}", styles['Normal']))
        story.append(Paragraph(f"Total: ${invoice.total:,.2f}", styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Construir PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer