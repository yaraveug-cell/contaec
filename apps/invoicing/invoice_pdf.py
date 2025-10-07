"""
Generador de PDF para facturas conforme a regulaciones ecuatorianas (SRI)
Utiliza ReportLab para crear documentos PDF profesionales
Cumple con la Resolución NAC-DGERCGC12-00105 del SRI
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


def generate_invoice_pdf(invoice):
    """
    Genera un PDF completo de la factura
    
    Args:
        invoice: Instancia del modelo Invoice
        
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
        'FacturaTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12,
        alignment=1,  # Centrado
        textColor=colors.black,
        fontName='Helvetica-Bold'
    )
    
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        alignment=1,  # Centrado
        textColor=colors.black,
        fontName='Helvetica'
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=4,
        textColor=colors.black,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=8,
        spaceAfter=3,
        textColor=colors.black,
        fontName='Helvetica'
    )
    
    # Estilo específico para productos con texto largo
    product_style = ParagraphStyle(
        'ProductStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=colors.black,
        fontName='Helvetica',
        wordWrap='CJK'  # Permite wrap de texto
    )
    
    # Estilo para información legal obligatoria
    legal_style = ParagraphStyle(
        'LegalStyle',
        parent=styles['Normal'],
        fontSize=7,
        spaceAfter=2,
        alignment=0,  # Izquierda
        textColor=colors.black,
        fontName='Helvetica'
    )
    
    # Contenido del PDF
    story = []
    
    # === ENCABEZADO CONFORME REGULACIONES ECUATORIANAS ===
    company = invoice.company
    
    # Título principal con numeración SRI
    title_text = f"FACTURA N° {invoice.number}"
    story.append(Paragraph(title_text, title_style))
    
    # Información obligatoria de la empresa (Art. 18 Reglamento de Comprobantes de Venta)
    company_name = Paragraph(f"<b>{company.trade_name}</b>", company_style)
    story.append(company_name)
    
    # RUC obligatorio
    ruc_text = f"RUC: {company.ruc}"
    story.append(Paragraph(ruc_text, company_style))
    
    # Dirección obligatoria usando Paragraph para manejo de texto largo
    address_text = f"Dirección: {company.address}"
    address_para = Paragraph(address_text, company_style)
    story.append(address_para)
    
    # Información de contacto opcional
    if company.phone or company.email:
        contact_parts = []
        if company.phone:
            contact_parts.append(f"Teléfono: {company.phone}")
        if company.email:
            contact_parts.append(f"Email: {company.email}")
        contact_text = " | ".join(contact_parts)
        story.append(Paragraph(contact_text, normal_style))
    
    story.append(Spacer(1, 15))
    
    # Información legal obligatoria
    legal_text = "Obligado a llevar contabilidad: SÍ"
    story.append(Paragraph(legal_text, legal_style))
    story.append(Spacer(1, 10))
    
    # === INFORMACIÓN DE LA FACTURA (REGULACIÓN SRI) ===
    # Información obligatoria según Art. 18 del Reglamento
    invoice_info_data = [
        [Paragraph('<b>FECHA DE EMISIÓN:</b>', header_style), 
         Paragraph(invoice.date.strftime('%d/%m/%Y'), normal_style),
         Paragraph('<b>AMBIENTE:</b>', header_style), 
         Paragraph('PRODUCCIÓN', normal_style)],
        [Paragraph('<b>EMISIÓN:</b>', header_style), 
         Paragraph('NORMAL', normal_style),
         Paragraph('<b>CLAVE DE ACCESO:</b>', header_style), 
         Paragraph('4910202502091234567800110010010000000011234567890', normal_style)],  # Ejemplo
    ]
    
    # Añadir forma de pago y vencimiento si aplica
    payment_form = invoice.payment_form.name if invoice.payment_form else 'EFECTIVO'
    invoice_info_data.append([
        Paragraph('<b>FORMA DE PAGO:</b>', header_style),
        Paragraph(payment_form, normal_style),
        Paragraph('<b>ESTADO:</b>', header_style),
        Paragraph(invoice.get_status_display().upper(), normal_style)
    ])
    
    if invoice.due_date:
        invoice_info_data.append([
            Paragraph('<b>FECHA DE VENCIMIENTO:</b>', header_style),
            Paragraph(invoice.due_date.strftime('%d/%m/%Y'), normal_style),
            Paragraph('', normal_style),
            Paragraph('', normal_style)
        ])
    
    invoice_info_table = Table(invoice_info_data, colWidths=[3.5*cm, 4*cm, 3.5*cm, 4*cm])
    invoice_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3)
    ]))
    
    story.append(invoice_info_table)
    story.append(Spacer(1, 12))
    
    # === INFORMACIÓN DEL ADQUIRIENTE (OBLIGATORIO SRI) ===
    story.append(Paragraph("<b>DATOS DEL ADQUIRIENTE:</b>", header_style))
    
    # Usar Paragraph para manejar nombres largos de clientes
    customer_data = []
    
    # Razón Social/Nombres (obligatorio)
    customer_name_para = Paragraph(f"<b>Razón Social/Nombres:</b> {invoice.customer.trade_name}", normal_style)
    customer_data.append([customer_name_para])
    
    # Identificación (obligatorio con tipo)
    identification_text = f"<b>Identificación:</b> {invoice.customer.identification}"
    # Determinar tipo de identificación según longitud
    if len(invoice.customer.identification) == 13:
        identification_text += " (RUC)"
    elif len(invoice.customer.identification) == 10:
        identification_text += " (CÉDULA)"
    else:
        identification_text += " (PASAPORTE)"
    
    identification_para = Paragraph(identification_text, normal_style)
    customer_data.append([identification_para])
    
    # Dirección usando Paragraph para texto largo
    address_para = Paragraph(f"<b>Dirección:</b> {invoice.customer.address}", normal_style)
    customer_data.append([address_para])
    
    # Información adicional si existe
    if invoice.customer.phone:
        phone_para = Paragraph(f"<b>Teléfono:</b> {invoice.customer.phone}", normal_style)
        customer_data.append([phone_para])
    
    if invoice.customer.email:
        email_para = Paragraph(f"<b>Email:</b> {invoice.customer.email}", normal_style)
        customer_data.append([email_para])
    
    customer_table = Table(customer_data, colWidths=[17*cm])
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4)
    ]))
    
    story.append(customer_table)
    story.append(Spacer(1, 15))
    
    # === DETALLE DE BIENES Y SERVICIOS (OBLIGATORIO SRI) ===
    story.append(Paragraph("<b>DETALLE:</b>", header_style))
    
    # Encabezados según regulación SRI
    header_row = [
        Paragraph('<b>Descripción</b>', header_style),
        Paragraph('<b>Cant.</b>', header_style),
        Paragraph('<b>P. Unitario</b>', header_style),
        Paragraph('<b>Descuento</b>', header_style),
        Paragraph('<b>P. Total</b>', header_style)
    ]
    
    lines_data = [header_row]
    
    # Cálculos según normativa ecuatoriana
    subtotal_0 = Decimal('0.00')   # Base imponible 0%
    subtotal_12 = Decimal('0.00')  # Base imponible 12%
    total_iva = Decimal('0.00')    # IVA total
    total_descuentos = Decimal('0.00')  # Descuentos totales
    
    for line in invoice.lines.all():
        # Cálculos por línea
        subtotal_linea = line.quantity * line.unit_price
        descuento_linea = subtotal_linea * (line.discount / 100)
        base_imponible = subtotal_linea - descuento_linea
        iva_linea = base_imponible * (line.iva_rate / 100)
        total_linea = base_imponible + iva_linea
        
        # Acumular por tarifas de IVA
        if line.iva_rate == 0:
            subtotal_0 += base_imponible
        else:
            subtotal_12 += base_imponible
            total_iva += iva_linea
        
        total_descuentos += descuento_linea
        
        # Usar Paragraph para descripción de producto (maneja texto largo)
        product_description = Paragraph(line.product.name, product_style)
        
        # Construir fila de datos
        row_data = [
            product_description,
            Paragraph(f"{line.quantity:.2f}", normal_style),
            Paragraph(f"${line.unit_price:.2f}", normal_style),
            Paragraph(f"${descuento_linea:.2f}", normal_style),
            Paragraph(f"${total_linea:.2f}", normal_style)
        ]
        
        lines_data.append(row_data)
    
    # Tabla de productos con anchos apropiados para texto largo
    lines_table = Table(lines_data, colWidths=[7*cm, 2*cm, 2.5*cm, 2.5*cm, 3*cm])
    lines_table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # Números a la derecha
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),    # Descripción a la izquierda
        
        # Formato general
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3)
    ]))
    
    story.append(lines_table)
    story.append(Spacer(1, 15))
    
    # === INFORMACIÓN ADICIONAL Y TOTALES (CONFORME SRI) ===
    
    # Calcular totales finales
    subtotal_sin_impuestos = subtotal_0 + subtotal_12
    total_factura = subtotal_sin_impuestos + total_iva
    
    # Tabla de información adicional
    if total_descuentos > 0:
        story.append(Paragraph(f"<b>DESCUENTO TOTAL:</b> ${total_descuentos:.2f}", normal_style))
        story.append(Spacer(1, 5))
    
    # Información de pago usando Paragraph para texto largo
    if hasattr(invoice, 'transfer_detail') and invoice.transfer_detail:
        transfer_info = Paragraph(f"<b>Información de Transferencia:</b> {invoice.transfer_detail}", normal_style)
        story.append(transfer_info)
        story.append(Spacer(1, 8))
    
    # Tabla de totales según regulación SRI
    totals_data = []
    
    # Subtotales por tarifa de IVA
    if subtotal_0 > 0:
        totals_data.append([
            Paragraph('<b>SUBTOTAL (Tarifa 0%):</b>', normal_style), 
            Paragraph(f"${subtotal_0:.2f}", normal_style)
        ])
    
    if subtotal_12 > 0:
        totals_data.append([
            Paragraph('<b>SUBTOTAL (Tarifa 12%):</b>', normal_style), 
            Paragraph(f"${subtotal_12:.2f}", normal_style)
        ])
    
    # Subtotal sin impuestos
    totals_data.append([
        Paragraph('<b>SUBTOTAL SIN IMPUESTOS:</b>', normal_style), 
        Paragraph(f"${subtotal_sin_impuestos:.2f}", normal_style)
    ])
    
    # IVA
    if total_iva > 0:
        totals_data.append([
            Paragraph('<b>IVA 12%:</b>', normal_style), 
            Paragraph(f"${total_iva:.2f}", normal_style)
        ])
    
    # Total final
    totals_data.append([
        Paragraph('<b>VALOR TOTAL:</b>', header_style), 
        Paragraph(f"<b>${total_factura:.2f}</b>", header_style)
    ])
    
    totals_table = Table(totals_data, colWidths=[10*cm, 4*cm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        
        # Resaltar total final
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.black),
    ]))
    
    story.append(totals_table)
    story.append(Spacer(1, 20))
    
    # === INFORMACIÓN ADICIONAL OBLIGATORIA (SRI) ===
    
    # Forma de pago detallada
    forma_pago = invoice.payment_form.name if invoice.payment_form else 'EFECTIVO'
    story.append(Paragraph(f"<b>Forma de Pago:</b> {forma_pago}", legal_style))
    
    # Validez del comprobante
    story.append(Paragraph("<b>ORIGINAL:</b> Cliente / COPIA: Emisor", legal_style))
    
    # Información legal obligatoria
    legal_text = """
    Esta factura es válida únicamente si ha sido autorizada por el SRI.
    La alteración de este documento constituye delito de falsificación.
    """
    story.append(Paragraph(legal_text, legal_style))
    story.append(Spacer(1, 10))
    
    # === PIE DE PÁGINA ===
    # Usar hora local de Ecuador en lugar de UTC
    local_time = timezone.localtime()
    footer_parts = []
    footer_parts.append(f"Documento generado el {local_time.strftime('%d/%m/%Y a las %H:%M')}")
    footer_parts.append(f"Sistema: ContaEC - {company.trade_name}")
    
    footer_text = " | ".join(footer_parts)
    footer_para = Paragraph(f'<para alignment="center"><font size="7">{footer_text}</font></para>', styles['Normal'])
    story.append(footer_para)
    
    # Generar PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer