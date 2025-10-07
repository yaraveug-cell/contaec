"""
Generador de PDF para asientos contables
Utiliza ReportLab para crear documentos PDF profesionales
"""

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from django.utils import timezone
from decimal import Decimal


def generate_journal_entry_pdf(journal_entry):
    """
    Genera un PDF completo del asiento contable
    
    Args:
        journal_entry: Instancia del modelo JournalEntry
        
    Returns:
        BytesIO: Buffer con el contenido del PDF
    """
    buffer = BytesIO()
    
    # Configurar documento PDF con márgenes optimizados
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=50,  # Márgenes más pequeños para más espacio
        leftMargin=50,
        topMargin=60,
        bottomMargin=60
    )
    
    # Obtener estilos
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=1,  # Centrado
        textColor=colors.HexColor('#2c3e50')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=10,
        textColor=colors.HexColor('#34495e')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Estilos adicionales para tablas
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        wordWrap='LTR',
        splitLongWords=True
    )
    
    # Construir contenido del PDF
    story = []
    
    # 1. ENCABEZADO PRINCIPAL
    company_name = journal_entry.company.trade_name
    # Truncar nombre de empresa si es muy largo
    if len(company_name) > 50:
        company_name = company_name[:47] + "..."
    title = f"ASIENTO CONTABLE - {company_name}"
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 12))
    
    # 2. INFORMACIÓN BÁSICA DEL ASIENTO
    info_data = [
        ['Número de Asiento:', str(journal_entry.number)],
        ['Fecha:', journal_entry.date.strftime('%d/%m/%Y')],
        ['Estado:', journal_entry.get_state_display()],
    ]
    
    # Manejar referencia larga
    reference = journal_entry.reference or 'Sin referencia'
    if len(reference) > 60:
        reference_paragraph = Paragraph(reference, cell_style)
        info_data.append(['Referencia:', reference_paragraph])
    else:
        info_data.append(['Referencia:', reference])
    
    # Manejar descripción larga
    if journal_entry.description:
        if len(journal_entry.description) > 60:
            description_paragraph = Paragraph(journal_entry.description, cell_style)
            info_data.append(['Descripción:', description_paragraph])
        else:
            info_data.append(['Descripción:', journal_entry.description])
    
    # Información de usuario
    created_by_name = journal_entry.created_by.get_full_name() or journal_entry.created_by.username
    info_data.extend([
        ['Creado por:', created_by_name],
        ['Fecha de creación:', timezone.localtime(journal_entry.created_at).strftime('%d/%m/%Y %H:%M')],
    ])
    
    if journal_entry.posted_by:
        posted_by_name = journal_entry.posted_by.get_full_name() or journal_entry.posted_by.username
        info_data.extend([
            ['Contabilizado por:', posted_by_name],
            ['Fecha contabilización:', timezone.localtime(journal_entry.posted_at).strftime('%d/%m/%Y %H:%M') if journal_entry.posted_at else 'N/A'],
        ])
    
    # Tabla de información básica con anchos optimizados
    info_table = Table(info_data, colWidths=[2.2*inch, 4.5*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # 3. LÍNEAS DEL ASIENTO
    story.append(Paragraph("DETALLE DE LÍNEAS CONTABLES", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Encabezados de la tabla de líneas
    lines_data = [
        ['Cuenta', 'Descripción', 'Débito', 'Crédito']
    ]
    
    # Obtener todas las líneas del asiento
    journal_lines = journal_entry.lines.all().order_by('id')
    
    total_debit = Decimal('0.00')
    total_credit = Decimal('0.00')
    
    for line in journal_lines:
        # Usar Paragraphs para mejor manejo de texto largo
        account_code = line.account.code
        account_name = line.account.name
        account_info = f"{account_code}<br/>{account_name}"
        
        # Crear párrafos para las celdas que pueden tener texto largo
        account_paragraph = Paragraph(account_info, cell_style)
        
        description = line.description or ''
        description_paragraph = Paragraph(description, cell_style)
        
        debit_amount = f"${line.debit:,.2f}" if line.debit > 0 else ''
        credit_amount = f"${line.credit:,.2f}" if line.credit > 0 else ''
        
        lines_data.append([
            account_paragraph,
            description_paragraph,
            debit_amount,
            credit_amount
        ])
        
        total_debit += line.debit
        total_credit += line.credit
    
    # Agregar fila de totales
    lines_data.append([
        'TOTALES:',
        '',
        f"${total_debit:,.2f}",
        f"${total_credit:,.2f}"
    ])
    
    # Crear tabla de líneas con anchos optimizados
    # Total disponible: aproximadamente 7 pulgadas en A4
    lines_table = Table(lines_data, colWidths=[2.8*inch, 2.5*inch, 1*inch, 1*inch])
    lines_table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        
        # Contenido
        ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
        ('ALIGN', (0, 1), (1, -2), 'LEFT'),  # Cuenta y descripción alineadas a la izquierda
        ('ALIGN', (2, 1), (-1, -2), 'RIGHT'),  # Montos alineados a la derecha
        ('FONTNAME', (2, 1), (-1, -2), 'Helvetica'),  # Solo aplicar fuente a celdas numéricas
        ('FONTSIZE', (2, 1), (-1, -2), 10),  # Solo aplicar tamaño a celdas numéricas
        ('VALIGN', (0, 1), (-1, -2), 'TOP'),  # Alinear contenido al tope para mejor visualización
        
        # Fila de totales
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
        ('ALIGN', (0, -1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 10),
        
        # Bordes y alternancia de colores
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f9f9f9')]),
    ]))
    
    story.append(lines_table)
    story.append(Spacer(1, 20))
    
    # 4. VALIDACIÓN DE BALANCE
    story.append(Paragraph("VALIDACIÓN DE BALANCE", subtitle_style))
    
    is_balanced = total_debit == total_credit
    balance_status = "✓ ASIENTO BALANCEADO" if is_balanced else "✗ ASIENTO DESBALANCEADO"
    balance_color = colors.green if is_balanced else colors.red
    
    balance_style = ParagraphStyle(
        'BalanceStatus',
        parent=normal_style,
        fontSize=12,
        textColor=balance_color,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph(balance_status, balance_style))
    
    if not is_balanced:
        difference = abs(total_debit - total_credit)
        diff_text = f"Diferencia: ${difference:,.2f}"
        story.append(Paragraph(diff_text, normal_style))
    
    story.append(Spacer(1, 20))
    
    # 5. PIE DE PÁGINA
    footer_style = ParagraphStyle(
        'Footer',
        parent=normal_style,
        fontSize=8,
        textColor=colors.grey,
        alignment=1  # Centrado
    )
    
    footer_text = f"Documento generado el {timezone.localtime(timezone.now()).strftime('%d/%m/%Y a las %H:%M')} - Sistema Contable CONTAEC"
    story.append(Paragraph(footer_text, footer_style))
    
    # Generar el PDF
    doc.build(story)
    
    # Mover el puntero del buffer al inicio
    buffer.seek(0)
    
    return buffer


class NumberedCanvas(canvas.Canvas):
    """Canvas personalizado para agregar numeración de páginas"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
    
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
    
    def save(self):
        """Agregar numeración a todas las páginas"""
        num_pages = len(self._saved_page_states)
        for (page_num, page_state) in enumerate(self._saved_page_states):
            self.__dict__.update(page_state)
            self.draw_page_number(page_num + 1, num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
    
    def draw_page_number(self, page_num, total_pages):
        """Dibujar número de página en el pie"""
        self.setFont("Helvetica", 9)
        self.drawRightString(
            letter[0] - 72, 
            36, 
            f"Página {page_num} de {total_pages}"
        )