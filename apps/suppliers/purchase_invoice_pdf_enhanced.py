"""
Generador de PDFs para facturas de compra - VERSIÓN MEJORADA
Sistema ContaEC - Ecuador
"""

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.units import mm, cm
from django.http import HttpResponse
from datetime import datetime
from decimal import Decimal


def generate_purchase_invoice_pdf_enhanced(invoice):
    """
    Generar PDF COMPLETO de factura de compra con todos los detalles.
    Versión mejorada con formato profesional y completo.
    
    Args:
        invoice: Instancia de PurchaseInvoice
        
    Returns:
        BytesIO: Buffer con el PDF generado
    """
    
    buffer = BytesIO()
    
    # Configurar documento con orientación A4 y márgenes apropiados
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=20*mm,
        bottomMargin=20*mm,
        leftMargin=20*mm,
        rightMargin=20*mm
    )
    
    # Inicializar historia para elementos del documento
    story = []
    
    # ==================
    # ESTILOS DEL DOCUMENTO
    # ==================
    styles = getSampleStyleSheet()
    
    # Estilo título principal
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=15,
        alignment=TA_CENTER,
        textColor=colors.darkblue,
        fontName='Helvetica-Bold'
    )
    
    # Estilo encabezado
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=8,
        alignment=TA_LEFT,
        textColor=colors.darkblue,
        fontName='Helvetica-Bold'
    )
    
    # Estilo normal con espaciado
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=4,
        alignment=TA_LEFT,
        fontName='Helvetica'
    )
    
    # Estilo para información importante
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=4,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        textColor=colors.darkgreen
    )
    
    # ==================
    # ENCABEZADO DEL DOCUMENTO
    # ==================
    
    # Título del documento
    story.append(Paragraph("FACTURA DE COMPRA", title_style))
    story.append(Spacer(1, 8*mm))
    
    # Información de la empresa (datos del sistema)
    if invoice.company:
        story.append(Paragraph(f"<b>EMPRESA:</b> {invoice.company.trade_name}", info_style))
        story.append(Paragraph(f"<b>RUC:</b> {invoice.company.ruc}", normal_style))
        story.append(Spacer(1, 6*mm))
    
    # ==================
    # INFORMACIÓN DE LA FACTURA
    # ==================
    
    story.append(Paragraph("DATOS DE LA FACTURA", header_style))
    
    # Crear tabla con información básica
    invoice_data = [
        ['Número Interno:', invoice.internal_number],
        ['Número del Proveedor:', getattr(invoice, 'supplier_invoice_number', 'N/A')],
        ['Fecha:', invoice.date.strftime('%d/%m/%Y')],
        ['Estado:', invoice.get_status_display()],
        ['Forma de Pago:', invoice.payment_form.name if invoice.payment_form else 'N/A']
    ]
    
    invoice_table = Table(invoice_data, colWidths=[4*cm, 6*cm])
    invoice_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(invoice_table)
    story.append(Spacer(1, 8*mm))
    
    # ==================
    # INFORMACIÓN DEL PROVEEDOR
    # ==================
    
    story.append(Paragraph("DATOS DEL PROVEEDOR", header_style))
    
    supplier_data = [
        ['Nombre Comercial:', invoice.supplier.trade_name],
        ['Razón Social:', invoice.supplier.legal_name or 'N/A'],
        ['RUC/Cédula:', invoice.supplier.identification],
        ['Tipo:', invoice.supplier.get_supplier_type_display()]
    ]
    
    supplier_table = Table(supplier_data, colWidths=[4*cm, 8*cm])
    supplier_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(supplier_table)
    story.append(Spacer(1, 8*mm))
    
    # ==================
    # DETALLE DE PRODUCTOS/SERVICIOS
    # ==================
    
    story.append(Paragraph("DETALLE DE PRODUCTOS/SERVICIOS", header_style))
    
    # Obtener líneas de la factura
    from apps.suppliers.models import PurchaseInvoiceLine
    lines = PurchaseInvoiceLine.objects.filter(purchase_invoice=invoice).order_by('id')
    
    if lines.exists():
        # Crear tabla de productos
        products_data = [
            ['#', 'Producto/Servicio', 'Cant.', 'Precio Unit.', 'Subtotal', 'IVA %', 'IVA', 'Total']
        ]
        
        for i, line in enumerate(lines, 1):
            subtotal = line.quantity * line.unit_cost
            iva_amount = subtotal * (line.iva_rate / 100)
            line_total = subtotal + iva_amount
            
            product_name = line.product.name if line.product else line.description
            
            products_data.append([
                str(i),
                product_name[:25] + ('...' if len(product_name) > 25 else ''),
                f"{line.quantity:.0f}",
                f"${line.unit_cost:.2f}",
                f"${subtotal:.2f}",
                f"{line.iva_rate:.0f}%",
                f"${iva_amount:.2f}",
                f"${line_total:.2f}"
            ])
        
        products_table = Table(products_data, colWidths=[0.8*cm, 4.5*cm, 1.2*cm, 2*cm, 2*cm, 1.2*cm, 1.8*cm, 2*cm])
        products_table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            
            # Contenido
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Producto/Servicio alineado a la izquierda
            
            # Bordes
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Colores alternos en las filas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(products_table)
    else:
        story.append(Paragraph("No hay líneas de productos registradas.", normal_style))
    
    story.append(Spacer(1, 8*mm))
    
    # ==================
    # TOTALES
    # ==================
    
    story.append(Paragraph("RESUMEN DE TOTALES", header_style))
    
    totals_data = [
        ['Subtotal (Sin IVA):', f"${invoice.subtotal:.2f}"],
        ['IVA Total:', f"${invoice.tax_amount:.2f}"],
        ['TOTAL A PAGAR:', f"${invoice.total:.2f}"]
    ]
    
    totals_table = Table(totals_data, colWidths=[5*cm, 3*cm])
    totals_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -2), colors.lightgrey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.darkgreen),  # Última fila (total) en verde
        ('TEXTCOLOR', (0, 0), (-1, -2), colors.black),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),  # Total en blanco
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),  # Montos alineados a la derecha
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),  # Total en bold
        ('FONTSIZE', (0, 0), (-1, -2), 10),
        ('FONTSIZE', (0, -1), (-1, -1), 12),  # Total más grande
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(totals_table)
    
    # ==================
    # INFORMACIÓN ADICIONAL
    # ==================
    
    if invoice.notes:
        story.append(Spacer(1, 8*mm))
        story.append(Paragraph("OBSERVACIONES", header_style))
        story.append(Paragraph(invoice.notes, normal_style))
    
    # ==================
    # PIE DE PÁGINA
    # ==================
    
    story.append(Spacer(1, 10*mm))
    
    footer_text = f"""
    <i>Documento generado por ContaEC - Sistema de Contabilidad Ecuatoriano<br/>
    Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
    Este documento es una representación impresa de la factura de compra registrada en el sistema.</i>
    """
    
    story.append(Paragraph(footer_text, ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.grey,
        fontName='Helvetica-Oblique',
        spaceAfter=0
    )))
    
    # Construir el PDF
    doc.build(story)
    
    # Retornar buffer posicionado al inicio
    buffer.seek(0)
    return buffer


def generate_multiple_purchase_invoices_pdf_enhanced(invoices):
    """
    Genera un PDF con múltiples facturas de compra COMPLETAS - VERSIÓN MEJORADA
    
    Args:
        invoices: QuerySet de PurchaseInvoice
        
    Returns:
        BytesIO: Buffer con el PDF generado
    """
    
    buffer = BytesIO()
    
    # Configurar documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=20*mm,
        bottomMargin=20*mm,
        leftMargin=20*mm,
        rightMargin=20*mm
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Estilo título principal para portada
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        fontSize=16,
        spaceAfter=15,
        alignment=TA_CENTER,
        textColor=colors.darkblue,
        fontName='Helvetica-Bold'
    )
    
    # ==================
    # PÁGINA DE PORTADA
    # ==================
    
    # Título del lote
    story.append(Paragraph(f"FACTURAS DE COMPRA", title_style))
    story.append(Paragraph(f"LOTE DE {len(invoices)} DOCUMENTOS", title_style))
    story.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                          ParagraphStyle('SubTitle', parent=styles['Normal'], 
                                       fontSize=12, alignment=TA_CENTER, textColor=colors.grey)))
    story.append(Spacer(1, 15*mm))
    
    # Resumen de facturas en la portada
    summary_data = [['#', 'Número', 'Proveedor', 'Fecha', 'Total']]
    
    for i, invoice in enumerate(invoices, 1):
        summary_data.append([
            str(i),
            invoice.internal_number,
            invoice.supplier.trade_name[:30] + ('...' if len(invoice.supplier.trade_name) > 30 else ''),
            invoice.date.strftime('%d/%m/%Y'),
            f"${invoice.total:.2f}"
        ])
    
    summary_table = Table(summary_data, colWidths=[1*cm, 3*cm, 6*cm, 2.5*cm, 2.5*cm])
    summary_table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        
        # Contenido
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),  # Proveedor alineado a la izquierda
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'),  # Total alineado a la derecha
        
        # Bordes
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Colores alternos en las filas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    story.append(summary_table)
    story.append(PageBreak())
    
    # ==================
    # FACTURAS COMPLETAS
    # ==================
    
    # Generar cada factura COMPLETA usando la función individual mejorada
    for i, invoice in enumerate(invoices):
        if i > 0:
            story.append(PageBreak())
        
        # Agregar título de factura individual
        invoice_title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading1'],
            fontSize=14,
            spaceAfter=10,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        story.append(Paragraph(f"DOCUMENTO {i+1} DE {len(invoices)}", invoice_title_style))
        story.append(Spacer(1, 5*mm))
        
        # ==================
        # CONTENIDO COMPLETO DE LA FACTURA
        # ==================
        
        # Recrear todo el contenido de la factura individual aquí
        # (copiando la lógica de generate_purchase_invoice_pdf_enhanced)
        
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=8,
            alignment=TA_LEFT,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            alignment=TA_LEFT,
            fontName='Helvetica'
        )
        
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            textColor=colors.darkgreen
        )
        
        # Título del documento
        story.append(Paragraph("FACTURA DE COMPRA", ParagraphStyle(
            'TitleStyleInvoice',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=10,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )))
        
        # Información de la empresa
        if invoice.company:
            story.append(Paragraph(f"<b>EMPRESA:</b> {invoice.company.trade_name}", info_style))
            story.append(Paragraph(f"<b>RUC:</b> {invoice.company.ruc}", normal_style))
            story.append(Spacer(1, 6*mm))
        
        # INFORMACIÓN DE LA FACTURA
        story.append(Paragraph("DATOS DE LA FACTURA", header_style))
        
        invoice_data = [
            ['Número Interno:', invoice.internal_number],
            ['Número del Proveedor:', getattr(invoice, 'supplier_invoice_number', 'N/A')],
            ['Fecha:', invoice.date.strftime('%d/%m/%Y')],
            ['Estado:', invoice.get_status_display()],
            ['Forma de Pago:', invoice.payment_form.name if invoice.payment_form else 'N/A']
        ]
        
        invoice_table = Table(invoice_data, colWidths=[4*cm, 6*cm])
        invoice_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(invoice_table)
        story.append(Spacer(1, 6*mm))
        
        # INFORMACIÓN DEL PROVEEDOR
        story.append(Paragraph("DATOS DEL PROVEEDOR", header_style))
        
        supplier_data = [
            ['Nombre Comercial:', invoice.supplier.trade_name],
            ['Razón Social:', invoice.supplier.legal_name or 'N/A'],
            ['RUC/Cédula:', invoice.supplier.identification],
            ['Tipo:', invoice.supplier.get_supplier_type_display()]
        ]
        
        supplier_table = Table(supplier_data, colWidths=[4*cm, 8*cm])
        supplier_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(supplier_table)
        story.append(Spacer(1, 6*mm))
        
        # DETALLE DE PRODUCTOS/SERVICIOS
        story.append(Paragraph("DETALLE DE PRODUCTOS/SERVICIOS", header_style))
        
        from apps.suppliers.models import PurchaseInvoiceLine
        lines = PurchaseInvoiceLine.objects.filter(purchase_invoice=invoice).order_by('id')
        
        if lines.exists():
            products_data = [
                ['#', 'Producto/Servicio', 'Cant.', 'Precio Unit.', 'Subtotal', 'IVA %', 'IVA', 'Total']
            ]
            
            for j, line in enumerate(lines, 1):
                subtotal = line.quantity * line.unit_cost
                iva_amount = subtotal * (line.iva_rate / 100)
                line_total = subtotal + iva_amount
                
                product_name = line.product.name if line.product else line.description
                
                products_data.append([
                    str(j),
                    product_name[:25] + ('...' if len(product_name) > 25 else ''),
                    f"{line.quantity:.0f}",
                    f"${line.unit_cost:.2f}",
                    f"${subtotal:.2f}",
                    f"{line.iva_rate:.0f}%",
                    f"${iva_amount:.2f}",
                    f"${line_total:.2f}"
                ])
            
            products_table = Table(products_data, colWidths=[0.8*cm, 4.5*cm, 1.2*cm, 2*cm, 2*cm, 1.2*cm, 1.8*cm, 2*cm])
            products_table.setStyle(TableStyle([
                # Encabezado
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                
                # Contenido
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                
                # Bordes
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Colores alternos en las filas
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(products_table)
        else:
            story.append(Paragraph("No hay líneas de productos registradas.", normal_style))
        
        story.append(Spacer(1, 6*mm))
        
        # TOTALES
        story.append(Paragraph("RESUMEN DE TOTALES", header_style))
        
        totals_data = [
            ['Subtotal (Sin IVA):', f"${invoice.subtotal:.2f}"],
            ['IVA Total:', f"${invoice.tax_amount:.2f}"],
            ['TOTAL A PAGAR:', f"${invoice.total:.2f}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[5*cm, 3*cm])
        totals_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -2), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, -2), colors.black),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -2), 10),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(totals_table)
        
        # OBSERVACIONES si existen
        if invoice.notes:
            story.append(Spacer(1, 6*mm))
            story.append(Paragraph("OBSERVACIONES", header_style))
            story.append(Paragraph(invoice.notes, normal_style))
    
    # PIE DE PÁGINA FINAL
    story.append(Spacer(1, 10*mm))
    
    footer_text = f"""
    <i>Documento generado por ContaEC - Sistema de Contabilidad Ecuatoriano<br/>
    Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
    Lote de {len(invoices)} facturas de compra completas.</i>
    """
    
    story.append(Paragraph(footer_text, ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.grey,
        fontName='Helvetica-Oblique',
        spaceAfter=0
    )))
    
    # Construir PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer