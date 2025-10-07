#!/usr/bin/env python3
"""
Script para diagnosticar la zona horaria del sistema
"""

import os
import django
import sys
from datetime import datetime
import pytz

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.utils import timezone
from django.conf import settings

def diagnose_timezone():
    """Diagnosticar configuración de zona horaria"""
    
    print('🕐 DIAGNÓSTICO DE ZONA HORARIA DEL SISTEMA')
    print('='*50)
    
    # Configuración de Django
    print(f'📋 Configuración Django:')
    print(f'   TIME_ZONE: {settings.TIME_ZONE}')
    print(f'   USE_TZ: {settings.USE_TZ}')
    
    # Hora actual del sistema
    system_now = datetime.now()
    print(f'\n🖥️  Hora del sistema (local): {system_now.strftime("%d/%m/%Y %H:%M:%S")}')
    
    # Hora UTC
    utc_now = datetime.utcnow()
    print(f'🌍 Hora UTC: {utc_now.strftime("%d/%m/%Y %H:%M:%S")}')
    
    # Hora con Django timezone
    django_now = timezone.now()
    print(f'🐍 Django timezone.now(): {django_now.strftime("%d/%m/%Y %H:%M:%S")}')
    
    # Zona horaria de Ecuador
    ecuador_tz = pytz.timezone('America/Guayaquil')
    ecuador_now = datetime.now(ecuador_tz)
    print(f'🇪🇨 Hora Ecuador: {ecuador_now.strftime("%d/%m/%Y %H:%M:%S %Z")}')
    
    # Verificar si Django está usando la zona horaria correcta
    print(f'\n🔍 Verificación:')
    if django_now.tzinfo:
        local_django = django_now.astimezone(ecuador_tz)
        print(f'   Django convertido a Ecuador: {local_django.strftime("%d/%m/%Y %H:%M:%S %Z")}')
        
        # Comparar diferencias
        diff_seconds = abs((local_django.replace(tzinfo=None) - system_now).total_seconds())
        print(f'   Diferencia con sistema: {diff_seconds} segundos')
        
        if diff_seconds < 60:
            print('   ✅ Zona horaria configurada correctamente')
        else:
            print(f'   ⚠️  Diferencia significativa: {diff_seconds/3600:.1f} horas')
    
    # Probar generación de fecha como en el PDF
    print(f'\n📄 Como aparece en PDF:')
    pdf_timestamp = timezone.now().strftime('%d/%m/%Y a las %H:%M')
    print(f'   "{pdf_timestamp}"')
    
    # Sugerir corrección si es necesario
    print(f'\n💡 Recomendaciones:')
    print(f'   • Usar timezone.localtime() para hora local')
    print(f'   • Verificar configuración del servidor')
    print(f'   • Considerar zona horaria del usuario')

if __name__ == '__main__':
    diagnose_timezone()