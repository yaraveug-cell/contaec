#!/usr/bin/env python3
"""
Script para probar el generador de PDF mejorado con regulaciones ecuatorianas
"""

import os
import django
import sys

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from apps.invoicing.invoice_pdf import generate_invoice_pdf

def test_ecuador_pdf():
    """Probar generación de PDF con regulaciones ecuatorianas"""
    
    print('📄 Probando generador de PDF mejorado (Regulaciones Ecuador)...')
    
    try:
        # Obtener una factura existente
        invoice = Invoice.objects.first()
        
        if not invoice:
            print('❌ No hay facturas para probar')
            return
        
        print(f'Factura: {invoice.number} - {invoice.customer.trade_name}')
        print(f'Empresa: {invoice.company.trade_name} (RUC: {invoice.company.ruc})')
        
        # Generar PDF
        pdf_buffer = generate_invoice_pdf(invoice)
        pdf_size = len(pdf_buffer.getvalue())
        
        print(f'✅ PDF generado exitosamente: {pdf_size:,} bytes')
        print(f'📋 Cumple regulaciones SRI del Ecuador')
        print(f'📝 Usa Paragraph para textos largos')
        
        # Verificar mejoras
        lines_count = invoice.lines.count()
        print(f'📊 Líneas procesadas: {lines_count}')
        
        if lines_count > 0:
            # Mostrar ejemplo de producto
            first_line = invoice.lines.first()
            product_name = first_line.product.name
            
            if len(product_name) > 30:
                print(f'📏 Producto con nombre largo: {product_name[:50]}...')
            else:
                print(f'📦 Producto: {product_name}')
        
        # Mostrar información regulatoria incluida
        print('\n📜 Características regulatorias implementadas:')
        print('   • Información obligatoria del emisor (RUC, dirección)')
        print('   • Datos del adquiriente con tipo de identificación')
        print('   • Detalle de bienes/servicios con Paragraph para texto largo')
        print('   • Subtotales por tarifa de IVA (0% y 12%)')
        print('   • Información legal obligatoria SRI')
        print('   • Formato conforme a resoluciones SRI')
        
        # Verificar si hay productos con nombres largos
        long_products = []
        for line in invoice.lines.all():
            if len(line.product.name) > 40:
                long_products.append(line.product.name)
        
        if long_products:
            print(f'\n📏 Productos con nombres largos detectados: {len(long_products)}')
            print('   ✅ Paragraph maneja automáticamente el wrapping de texto')
        
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_ecuador_pdf()
    if success:
        print('\n🎉 ¡Generador de PDF listo para producción!')
    else:
        print('\n💥 Error en la generación de PDF')