#!/usr/bin/env python3
"""
Guía completa para manejar la hora del sistema Django
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

def show_django_time_options():
    """Mostrar todas las opciones para obtener hora en Django"""
    
    print('🕐 GUÍA COMPLETA DE HORA EN DJANGO')
    print('='*50)
    
    # 1. Configuración actual
    print('\n📋 CONFIGURACIÓN ACTUAL:')
    print(f'   TIME_ZONE: {settings.TIME_ZONE}')
    print(f'   USE_TZ: {settings.USE_TZ}')
    
    # 2. Diferentes formas de obtener hora
    print('\n⏰ DIFERENTES FORMAS DE OBTENER HORA:')
    
    # Django timezone.now() - UTC
    utc_time = timezone.now()
    print(f'1. timezone.now() - UTC:')
    print(f'   {utc_time.strftime("%d/%m/%Y %H:%M:%S")}')
    print(f'   Uso: Almacenar en base de datos')
    
    # Django timezone.localtime() - Hora local
    local_time = timezone.localtime()
    print(f'\n2. timezone.localtime() - Hora Local:')
    print(f'   {local_time.strftime("%d/%m/%Y %H:%M:%S")}')
    print(f'   Uso: Mostrar al usuario (PDFs, interfaces)')
    
    # Python datetime.now() - Sistema
    system_time = datetime.now()
    print(f'\n3. datetime.now() - Sistema:')
    print(f'   {system_time.strftime("%d/%m/%Y %H:%M:%S")}')
    print(f'   Uso: Hora del servidor (no recomendado)')
    
    # Zona específica
    ecuador_tz = pytz.timezone('America/Guayaquil')
    ecuador_time = datetime.now(ecuador_tz)
    print(f'\n4. Zona específica - Ecuador:')
    print(f'   {ecuador_time.strftime("%d/%m/%Y %H:%M:%S %Z")}')
    print(f'   Uso: Forzar zona horaria específica')
    
    print('\n' + '='*50)
    
def show_timezone_configuration():
    """Mostrar cómo configurar zona horaria"""
    
    print('\n🛠️  CONFIGURACIÓN DE ZONA HORARIA:')
    print('\n1. En settings.py:')
    print('   TIME_ZONE = "America/Guayaquil"  # Ecuador')
    print('   USE_TZ = True  # Usar timezone-aware datetimes')
    
    print('\n2. Zonas horarias disponibles para Ecuador:')
    print('   - America/Guayaquil (Ecuador Continental)')
    print('   - Pacific/Galapagos (Islas Galápagos)')
    
    print('\n3. Otras zonas comunes en Latinoamérica:')
    print('   - America/Bogota (Colombia)')
    print('   - America/Lima (Perú)')
    print('   - America/Santiago (Chile)')
    print('   - America/Argentina/Buenos_Aires (Argentina)')

def show_practical_examples():
    """Mostrar ejemplos prácticos de uso"""
    
    print('\n💡 EJEMPLOS PRÁCTICOS:')
    
    print('\n📄 Para PDFs y documentos:')
    print('```python')
    print('from django.utils import timezone')
    print('')
    print('# Hora local para mostrar al usuario')
    print('local_time = timezone.localtime()')
    print('display_time = local_time.strftime("%d/%m/%Y a las %H:%M")')
    print('```')
    
    print('\n💾 Para guardar en base de datos:')
    print('```python')
    print('# Hora UTC para almacenamiento')
    print('invoice.created_at = timezone.now()  # Se guarda en UTC')
    print('```')
    
    print('\n🔄 Para convertir entre zonas:')
    print('```python')
    print('# Convertir UTC a local')
    print('utc_time = timezone.now()')
    print('local_time = timezone.localtime(utc_time)')
    print('')
    print('# Convertir a zona específica')
    print('import pytz')
    print('ecuador_tz = pytz.timezone("America/Guayaquil")')
    print('ecuador_time = utc_time.astimezone(ecuador_tz)')
    print('```')

def show_current_times():
    """Mostrar todas las horas actuales"""
    
    print('\n🕒 HORAS ACTUALES DEL SISTEMA:')
    
    # UTC
    utc_now = timezone.now()
    print(f'UTC: {utc_now.strftime("%d/%m/%Y %H:%M:%S")}')
    
    # Local (Ecuador)
    local_now = timezone.localtime()
    print(f'Ecuador: {local_now.strftime("%d/%m/%Y %H:%M:%S")}')
    
    # Sistema
    system_now = datetime.now()
    print(f'Sistema: {system_now.strftime("%d/%m/%Y %H:%M:%S")}')
    
    # Diferencia
    diff = (utc_now - local_now.replace(tzinfo=None)).total_seconds() / 3600
    print(f'Diferencia UTC vs Local: {abs(diff):.0f} horas')

def change_timezone_example():
    """Ejemplo de cómo cambiar zona horaria"""
    
    print('\n⚙️  CÓMO CAMBIAR ZONA HORARIA:')
    
    print('\n1. Modificar settings.py:')
    print('   # Para Ecuador Continental')
    print('   TIME_ZONE = "America/Guayaquil"')
    print('')
    print('   # Para Galápagos (1 hora menos)')
    print('   TIME_ZONE = "Pacific/Galapagos"')
    
    print('\n2. Reiniciar el servidor Django')
    print('   python manage.py runserver')
    
    print('\n3. Verificar cambios:')
    print('   - Los nuevos registros usarán la nueva zona')
    print('   - Los registros existentes se convertirán automáticamente')
    print('   - Las fechas mostradas cambiarán inmediatamente')

def main():
    """Función principal"""
    show_django_time_options()
    show_timezone_configuration()
    show_practical_examples()
    show_current_times()
    change_timezone_example()
    
    print('\n🎯 RECOMENDACIONES:')
    print('✅ Usar timezone.localtime() para mostrar al usuario')
    print('✅ Usar timezone.now() para guardar en base de datos')
    print('✅ Mantener USE_TZ = True siempre')
    print('✅ Configurar TIME_ZONE según ubicación del negocio')
    
    print('\n📚 DOCUMENTACIÓN:')
    print('https://docs.djangoproject.com/en/4.2/topics/i18n/timezones/')

if __name__ == '__main__':
    main()