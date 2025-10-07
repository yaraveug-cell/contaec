#!/usr/bin/env python
"""
Verificar diferencias de timezone en el sistema
"""

import os
import sys
import django
from datetime import datetime
import pytz

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.utils import timezone
from django.conf import settings

def verificar_timezone():
    print("🕐 VERIFICACIÓN DE ZONA HORARIA")
    print("="*50)
    
    # 1. Configuración de Django
    print(f"📍 CONFIGURACIÓN DE DJANGO:")
    print(f"   TIME_ZONE: {settings.TIME_ZONE}")
    print(f"   USE_TZ: {settings.USE_TZ}")
    
    # 2. Tiempo actual del sistema
    now_system = datetime.now()
    print(f"\n⏰ HORA DEL SISTEMA:")
    print(f"   Hora local: {now_system.strftime('%d/%m/%Y %H:%M:%S')}")
    
    # 3. Tiempo de Django (con timezone)
    now_django = timezone.now()
    print(f"\n🐍 HORA DE DJANGO:")
    print(f"   UTC: {now_django.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"   Con timezone: {now_django.strftime('%d/%m/%Y %H:%M:%S')}")
    
    # 4. Convertir a zona horaria local configurada
    local_tz = pytz.timezone(settings.TIME_ZONE)
    now_local = now_django.astimezone(local_tz)
    print(f"   Local ({settings.TIME_ZONE}): {now_local.strftime('%d/%m/%Y %H:%M:%S')}")
    
    # 5. Simular lo que hace el PDF
    pdf_timestamp = timezone.now().strftime('%d/%m/%Y a las %H:%M')
    print(f"\n📄 HORA EN PDF ACTUAL:")
    print(f"   Formato PDF: {pdf_timestamp}")
    
    # 6. Corrección sugerida
    corrected_timestamp = timezone.localtime(timezone.now()).strftime('%d/%m/%Y a las %H:%M')
    print(f"\n✅ HORA CORREGIDA PARA PDF:")
    print(f"   Formato corregido: {corrected_timestamp}")
    
    # 7. Diferencia
    utc_offset = now_local.utcoffset()
    print(f"\n📊 INFORMACIÓN ADICIONAL:")
    print(f"   Offset UTC: {utc_offset}")
    print(f"   Diferencia horaria: UTC{utc_offset}")
    
    # 8. Verificar si hay diferencia significativa
    system_hour = now_system.hour
    django_hour = now_django.hour
    local_hour = now_local.hour
    
    print(f"\n🔍 COMPARACIÓN DE HORAS:")
    print(f"   Sistema: {system_hour}:XX")
    print(f"   Django (UTC): {django_hour}:XX")
    print(f"   Django (Local): {local_hour}:XX")
    
    if system_hour != local_hour:
        diff = abs(system_hour - local_hour)
        print(f"\n⚠️  DISCREPANCIA DETECTADA:")
        print(f"   Diferencia: {diff} horas")
        print(f"   Causa probable: timezone.now() usa UTC, no hora local")
    else:
        print(f"\n✅ Las horas coinciden correctamente")

def mostrar_solucion():
    print(f"\n🔧 SOLUCIÓN RECOMENDADA:")
    print(f"   Cambiar en journal_pdf.py:")
    print(f"   ANTES: timezone.now().strftime()")
    print(f"   DESPUÉS: timezone.localtime(timezone.now()).strftime()")
    print(f"")
    print(f"   Esto convertirá UTC a hora local de Ecuador")

if __name__ == "__main__":
    verificar_timezone()
    mostrar_solucion()