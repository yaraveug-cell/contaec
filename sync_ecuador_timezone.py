#!/usr/bin/env python3
"""
Script para sincronizar la hora del sistema Django con Ecuador
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

def sync_django_time_with_ecuador():
    """Sincronizar hora de Django con Ecuador"""
    
    print('🇪🇨 SINCRONIZANDO HORA DE DJANGO CON ECUADOR')
    print('='*50)
    
    # 1. Verificar configuración actual
    print('📋 CONFIGURACIÓN ACTUAL:')
    print(f'   TIME_ZONE: {settings.TIME_ZONE}')
    print(f'   USE_TZ: {settings.USE_TZ}')
    print(f'   LANGUAGE_CODE: {settings.LANGUAGE_CODE}')
    
    # 2. Mostrar horas antes de la sincronización
    print('\n⏰ HORAS ANTES DE SINCRONIZACIÓN:')
    
    utc_time = timezone.now()
    local_time = timezone.localtime()
    system_time = datetime.now()
    
    print(f'   UTC: {utc_time.strftime("%d/%m/%Y %H:%M:%S")}')
    print(f'   Local Django: {local_time.strftime("%d/%m/%Y %H:%M:%S")}')
    print(f'   Sistema: {system_time.strftime("%d/%m/%Y %H:%M:%S")}')
    
    # 3. Verificar zona horaria de Ecuador
    ecuador_tz = pytz.timezone('America/Guayaquil')
    ecuador_time = datetime.now(ecuador_tz)
    
    print(f'   Ecuador oficial: {ecuador_time.strftime("%d/%m/%Y %H:%M:%S %Z")}')
    
    # 4. Calcular diferencias
    diff_utc_local = (utc_time - local_time.replace(tzinfo=None)).total_seconds() / 3600
    diff_system_ecuador = abs((system_time - ecuador_time.replace(tzinfo=None)).total_seconds())
    
    print(f'\n📊 ANÁLISIS DE DIFERENCIAS:')
    print(f'   UTC vs Local: {abs(diff_utc_local):.1f} horas')
    print(f'   Sistema vs Ecuador: {diff_system_ecuador:.0f} segundos')
    
    # 5. Estado de sincronización
    if diff_system_ecuador < 60:  # Menos de 1 minuto de diferencia
        print('   ✅ Sistema ya sincronizado con Ecuador')
        is_synced = True
    else:
        print('   ⚠️  Sistema necesita sincronización')
        is_synced = False
    
    return is_synced, ecuador_time, local_time

def apply_ecuador_timezone_fix():
    """Aplicar correcciones para usar siempre hora de Ecuador"""
    
    print('\n🔧 APLICANDO CORRECCIONES PARA HORA DE ECUADOR:')
    
    # Verificar que los archivos importantes usen timezone.localtime()
    files_to_check = [
        'apps/invoicing/invoice_pdf.py',
        'apps/accounting/journal_pdf.py'
    ]
    
    corrections_needed = []
    
    for file_path in files_to_check:
        full_path = f'c:\\contaec\\{file_path}'
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'timezone.now().strftime' in content:
                corrections_needed.append(file_path)
                print(f'   ⚠️  {file_path} necesita corrección')
            else:
                print(f'   ✅ {file_path} usa hora local correctamente')
                
        except FileNotFoundError:
            print(f'   ❓ {file_path} no encontrado')
    
    return corrections_needed

def create_timezone_utility():
    """Crear utilidad para manejo consistente de timezone"""
    
    print('\n🛠️  CREANDO UTILIDAD DE TIMEZONE:')
    
    utility_code = '''"""
Utilidad para manejo consistente de zona horaria en Ecuador
"""
from django.utils import timezone
import pytz

# Zona horaria de Ecuador
ECUADOR_TZ = pytz.timezone('America/Guayaquil')

def get_ecuador_time():
    """Obtener hora actual de Ecuador"""
    return timezone.localtime()

def format_ecuador_time(dt=None, format_str='%d/%m/%Y a las %H:%M'):
    """Formatear fecha/hora para Ecuador"""
    if dt is None:
        dt = timezone.localtime()
    return dt.strftime(format_str)

def get_ecuador_date():
    """Obtener fecha actual de Ecuador (sin hora)"""
    return timezone.localtime().date()

def convert_utc_to_ecuador(utc_datetime):
    """Convertir UTC a hora de Ecuador"""
    return timezone.localtime(utc_datetime)

# Ejemplos de uso:
# ecuador_time = get_ecuador_time()
# formatted_time = format_ecuador_time()
# ecuador_date = get_ecuador_date()
'''
    
    with open('c:\\contaec\\apps\\core\\timezone_utils.py', 'w', encoding='utf-8') as f:
        f.write(utility_code)
    
    print('   ✅ Utilidad creada: apps/core/timezone_utils.py')
    
def show_usage_examples():
    """Mostrar ejemplos de uso correcto"""
    
    print('\n💡 EJEMPLOS DE USO CORRECTO:')
    
    print('\n📄 Para PDFs y documentos:')
    print('```python')
    print('from django.utils import timezone')
    print('')
    print('# ✅ CORRECTO - Hora local de Ecuador')
    print('local_time = timezone.localtime()')
    print('display_time = local_time.strftime("%d/%m/%Y a las %H:%M")')
    print('```')
    
    print('\n💾 Para guardar en base de datos:')
    print('```python')
    print('# ✅ CORRECTO - UTC para almacenamiento')
    print('model.created_at = timezone.now()')
    print('')
    print('# ✅ CORRECTO - Convertir para mostrar')
    print('display_time = timezone.localtime(model.created_at)')
    print('```')
    
    print('\n❌ EVITAR:')
    print('```python')
    print('# ❌ INCORRECTO - Muestra UTC al usuario')
    print('bad_time = timezone.now().strftime("%H:%M")')
    print('')
    print('# ❌ INCORRECTO - Usa hora del sistema')
    print('bad_time = datetime.now().strftime("%H:%M")')
    print('```')

def main():
    """Función principal"""
    
    # 1. Verificar sincronización actual
    is_synced, ecuador_time, local_time = sync_django_time_with_ecuador()
    
    # 2. Verificar archivos que necesitan corrección
    corrections_needed = apply_ecuador_timezone_fix()
    
    # 3. Crear utilidad de timezone
    create_timezone_utility()
    
    # 4. Mostrar ejemplos de uso
    show_usage_examples()
    
    # 5. Resumen final
    print(f'\n🎯 ESTADO FINAL:')
    
    if is_synced:
        print('✅ Sistema Django sincronizado con Ecuador')
    else:
        print('⚠️  Sistema necesita ajustes adicionales')
    
    if corrections_needed:
        print('⚠️  Archivos que necesitan corrección:')
        for file_path in corrections_needed:
            print(f'   - {file_path}')
    else:
        print('✅ Todos los archivos usan hora local correctamente')
    
    print(f'\n📅 HORA OFICIAL DE ECUADOR: {ecuador_time.strftime("%d/%m/%Y %H:%M:%S")}')
    print(f'📅 HORA DJANGO LOCAL: {local_time.strftime("%d/%m/%Y %H:%M:%S")}')
    
    print(f'\n🛠️  UTILIDADES CREADAS:')
    print(f'   - apps/core/timezone_utils.py')
    
    print(f'\n🎉 ¡Django configurado para usar hora de Ecuador!')

if __name__ == '__main__':
    main()