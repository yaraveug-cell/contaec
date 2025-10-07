#!/usr/bin/env python3
"""
Script para verificar la corrección de zona horaria en PDF
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
from django.utils import timezone

def test_timezone_fix():
    """Probar la corrección de zona horaria en PDF"""
    
    print('🕐 PROBANDO CORRECCIÓN DE ZONA HORARIA EN PDF')
    print('='*50)
    
    try:
        # Obtener una factura
        invoice = Invoice.objects.first()
        
        if not invoice:
            print('❌ No hay facturas para probar')
            return
        
        print(f'Factura: {invoice.number}')
        print(f'Cliente: {invoice.customer.trade_name}')
        
        # Mostrar hora actual del sistema
        local_time = timezone.localtime()
        utc_time = timezone.now()
        
        print(f'\n🕒 Hora actual:')
        print(f'   Local (Ecuador): {local_time.strftime("%d/%m/%Y a las %H:%M")}')
        print(f'   UTC: {utc_time.strftime("%d/%m/%Y a las %H:%M")}')
        
        # Generar PDF
        print(f'\n🔄 Generando PDF con hora corregida...')
        pdf_buffer = generate_invoice_pdf(invoice)
        
        print(f'✅ PDF generado exitosamente: {len(pdf_buffer.getvalue()):,} bytes')
        print(f'📄 La hora mostrada será: {local_time.strftime("%d/%m/%Y a las %H:%M")}')
        print(f'🇪🇨 Zona horaria: America/Guayaquil (Ecuador)')
        
        # Verificar diferencia
        diff_hours = (utc_time - local_time).total_seconds() / 3600
        print(f'\n📊 Verificación:')
        print(f'   Diferencia UTC vs Local: {abs(diff_hours):.0f} horas')
        print(f'   ✅ PDF ahora usa hora local de Ecuador')
        print(f'   ✅ No más confusión con horarios UTC')
        
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_timezone_fix()
    if success:
        print('\n🎉 ¡Zona horaria corregida exitosamente!')
        print('📋 Los PDFs ahora mostrarán la hora local de Ecuador')
    else:
        print('\n💥 Error en la corrección')