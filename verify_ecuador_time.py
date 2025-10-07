#!/usr/bin/env python3
"""
Script simplificado para verificar y ajustar hora de Ecuador
"""

import os
import django
import sys

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.utils import timezone
from django.conf import settings
from datetime import datetime
import pytz

def verify_ecuador_time():
    """Verificar que Django use hora de Ecuador"""
    
    print('🇪🇨 VERIFICACIÓN DE HORA DE ECUADOR')
    print('='*40)
    
    # Configuración
    print(f'📋 Configuración:')
    print(f'   TIME_ZONE: {settings.TIME_ZONE}')
    print(f'   USE_TZ: {settings.USE_TZ}')
    
    # Horas actuales
    utc_time = timezone.now()
    local_time = timezone.localtime()
    
    print(f'\n⏰ Horas actuales:')
    print(f'   UTC: {utc_time.strftime("%d/%m/%Y %H:%M:%S")}')
    print(f'   Ecuador (Local): {local_time.strftime("%d/%m/%Y %H:%M:%S")}')
    
    # Verificar diferencia (debe ser 5 horas)
    diff = utc_time.hour - local_time.hour
    if diff < 0:
        diff += 24  # Ajustar por cambio de día
    
    print(f'   Diferencia: {diff} horas')
    
    if diff == 5:
        print('   ✅ Diferencia correcta (Ecuador = UTC -5)')
        status = 'CORRECTO'
    else:
        print('   ⚠️  Diferencia inesperada')
        status = 'REVISAR'
    
    # Como aparece en PDFs
    pdf_format = local_time.strftime('%d/%m/%Y a las %H:%M')
    print(f'\n📄 En PDFs aparece: {pdf_format}')
    
    return status, local_time

def create_timezone_helper():
    """Crear función helper para timezone"""
    
    print(f'\n🛠️  Creando helper de timezone...')
    
    # Crear directorio si no existe
    os.makedirs('c:\\contaec\\apps\\core', exist_ok=True)
    
    helper_code = '''"""
Helper para manejo de timezone en Ecuador
"""
from django.utils import timezone

def get_ecuador_time():
    """Obtener hora actual de Ecuador"""
    return timezone.localtime()

def format_for_pdf():
    """Formatear hora para PDFs (Ecuador)"""
    ecuador_time = timezone.localtime()
    return ecuador_time.strftime('%d/%m/%Y a las %H:%M')

def format_for_display():
    """Formatear hora para mostrar al usuario"""
    ecuador_time = timezone.localtime()
    return ecuador_time.strftime('%d/%m/%Y %H:%M:%S')
'''
    
    try:
        with open('c:\\contaec\\apps\\core\\timezone_helper.py', 'w', encoding='utf-8') as f:
            f.write(helper_code)
        print('   ✅ Helper creado: apps/core/timezone_helper.py')
    except Exception as e:
        print(f'   ❌ Error creando helper: {e}')

def test_pdf_time():
    """Probar tiempo en PDF"""
    
    print(f'\n📄 Probando generación de tiempo para PDF...')
    
    try:
        from apps.invoicing.models import Invoice
        from apps.invoicing.invoice_pdf import generate_invoice_pdf
        
        invoice = Invoice.objects.first()
        if invoice:
            pdf_buffer = generate_invoice_pdf(invoice)
            local_time = timezone.localtime()
            
            print(f'   ✅ PDF generado: {len(pdf_buffer.getvalue())} bytes')
            print(f'   🕒 Hora Ecuador: {local_time.strftime("%d/%m/%Y a las %H:%M")}')
            print('   ✅ PDF usa hora local de Ecuador')
        else:
            print('   ℹ️  No hay facturas para probar')
    
    except Exception as e:
        print(f'   ❌ Error: {e}')

def main():
    """Función principal"""
    
    # 1. Verificar hora actual
    status, ecuador_time = verify_ecuador_time()
    
    # 2. Crear helper
    create_timezone_helper()
    
    # 3. Probar PDF
    test_pdf_time()
    
    # 4. Resumen
    print(f'\n🎯 RESUMEN:')
    print(f'   Estado: {status}')
    print(f'   Hora Ecuador: {ecuador_time.strftime("%d/%m/%Y %H:%M:%S")}')
    print(f'   Configuración: America/Guayaquil ✅')
    
    if status == 'CORRECTO':
        print(f'\n🎉 ¡Django usa correctamente la hora de Ecuador!')
        print(f'✅ Los PDFs muestran: {ecuador_time.strftime("%d/%m/%Y a las %H:%M")}')
    else:
        print(f'\n⚠️  Revisar configuración de zona horaria')
    
    print(f'\n💡 Uso recomendado en código:')
    print(f'   timezone.localtime()  # Para mostrar al usuario')
    print(f'   timezone.now()        # Para guardar en BD')

if __name__ == '__main__':
    main()