#!/usr/bin/env python3
"""
Script para obtener información completa del sistema de base de datos
"""

import os
import django
import sys
import sqlite3
from pathlib import Path

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.db import connection
from django.conf import settings
from django.core.management import execute_from_command_line

def get_database_info():
    """Obtener información completa de la base de datos"""
    
    print('💾 INFORMACIÓN DEL SISTEMA DE BASE DE DATOS')
    print('='*50)
    
    # 1. Configuración desde settings
    db_config = settings.DATABASES['default']
    
    print('📋 CONFIGURACIÓN ACTUAL:')
    print(f'   Motor: {db_config["ENGINE"]}')
    print(f'   Archivo: {db_config["NAME"]}')
    
    # 2. Determinar tipo de base de datos
    engine = db_config['ENGINE']
    if 'sqlite3' in engine:
        db_type = 'SQLite'
        db_name = 'SQLite (Archivo local)'
    elif 'postgresql' in engine:
        db_type = 'PostgreSQL'
        db_name = 'PostgreSQL (Servidor)'
    elif 'mysql' in engine:
        db_type = 'MySQL/MariaDB'
        db_name = 'MySQL (Servidor)'
    else:
        db_type = 'Otro'
        db_name = 'Base de datos desconocida'
    
    print(f'\n🎯 TIPO DE BASE DE DATOS:')
    print(f'   Tipo: {db_type}')
    print(f'   Descripción: {db_name}')
    
    return db_type, db_config

def get_sqlite_details():
    """Obtener detalles específicos de SQLite"""
    
    print(f'\n📊 DETALLES DE SQLITE:')
    
    # Verificar si existe el archivo
    db_path = Path('c:/contaec/db.sqlite3')
    
    if db_path.exists():
        # Tamaño del archivo
        size_bytes = db_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        
        print(f'   Archivo: db.sqlite3')
        print(f'   Ruta: {db_path}')
        print(f'   Tamaño: {size_bytes:,} bytes ({size_mb:.2f} MB)')
        print(f'   Existe: ✅ Sí')
        
        # Conectar directamente a SQLite para más info
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Obtener versión de SQLite
            cursor.execute('SELECT sqlite_version()')
            version = cursor.fetchone()[0]
            print(f'   Versión SQLite: {version}')
            
            # Obtener número de tablas
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            print(f'   Número de tablas: {table_count}')
            
            # Obtener algunas tablas principales
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = cursor.fetchall()
            
            print(f'\n📋 ALGUNAS TABLAS PRINCIPALES:')
            for i, (table_name,) in enumerate(tables[:10]):
                if not table_name.startswith('django_') and not table_name.startswith('auth_'):
                    print(f'   • {table_name}')
            
            if len(tables) > 10:
                print(f'   ... y {len(tables) - 10} tablas más')
            
            conn.close()
            
        except Exception as e:
            print(f'   ❌ Error accediendo a SQLite: {e}')
            
    else:
        print(f'   ❌ Archivo db.sqlite3 no encontrado')

def get_django_db_info():
    """Obtener información desde Django"""
    
    print(f'\n🐍 INFORMACIÓN DESDE DJANGO:')
    
    try:
        # Información de conexión
        with connection.cursor() as cursor:
            # Verificar conexión
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f'   Conexión: ✅ Activa')
            
            # Obtener vendor (tipo de DB)
            vendor = connection.vendor
            print(f'   Vendor: {vendor}')
            
    except Exception as e:
        print(f'   ❌ Error de conexión: {e}')

def get_models_info():
    """Obtener información de modelos Django"""
    
    print(f'\n📦 MODELOS DEL SISTEMA CONTABLE:')
    
    try:
        # Importar modelos principales
        from apps.companies.models import Company
        from apps.accounting.models import JournalEntry, ChartOfAccounts
        from apps.invoicing.models import Invoice
        from apps.inventory.models import Product
        
        # Contar registros
        companies = Company.objects.count()
        journals = JournalEntry.objects.count()
        accounts = ChartOfAccounts.objects.count()
        invoices = Invoice.objects.count()
        products = Product.objects.count()
        
        print(f'   Empresas: {companies:,}')
        print(f'   Asientos contables: {journals:,}')
        print(f'   Cuentas contables: {accounts:,}')
        print(f'   Facturas: {invoices:,}')
        print(f'   Productos: {products:,}')
        
    except Exception as e:
        print(f'   ❌ Error obteniendo modelos: {e}')

def show_production_recommendations():
    """Mostrar recomendaciones para producción"""
    
    print(f'\n💡 RECOMENDACIONES:')
    
    print(f'\n✅ ACTUAL (Desarrollo):')
    print(f'   • SQLite es perfecto para desarrollo')
    print(f'   • Fácil backup (un solo archivo)')
    print(f'   • Sin configuración de servidor')
    print(f'   • Ideal para pruebas y demos')
    
    print(f'\n🚀 PARA PRODUCCIÓN (Recomendado):')
    print(f'   • PostgreSQL (mejor rendimiento)')
    print(f'   • Soporte para múltiples usuarios')
    print(f'   • Mejor para datos grandes')
    print(f'   • Funciones avanzadas SQL')
    
    print(f'\n⚙️ CONFIGURACIÓN POSTGRESQL (Ya preparada):')
    print(f'   Descomentar en settings.py:')
    print(f'   ENGINE: django.db.backends.postgresql')
    print(f'   Variables de entorno: DB_NAME, DB_USER, etc.')

def backup_sqlite():
    """Mostrar cómo hacer backup de SQLite"""
    
    print(f'\n💾 BACKUP DE BASE DE DATOS:')
    
    print(f'\n📋 Método simple (SQLite):')
    print(f'   1. Copiar archivo: cp db.sqlite3 backup_$(date +%Y%m%d).sqlite3')
    print(f'   2. O usar Django: python manage.py dumpdata > backup.json')
    
    print(f'\n🔄 Restaurar backup:')
    print(f'   1. Desde archivo: cp backup_20251002.sqlite3 db.sqlite3')
    print(f'   2. Desde JSON: python manage.py loaddata backup.json')

def main():
    """Función principal"""
    
    # 1. Información general
    db_type, db_config = get_database_info()
    
    # 2. Detalles específicos según tipo
    if db_type == 'SQLite':
        get_sqlite_details()
    
    # 3. Información desde Django
    get_django_db_info()
    
    # 4. Información de modelos
    get_models_info()
    
    # 5. Recomendaciones
    show_production_recommendations()
    
    # 6. Información de backup
    backup_sqlite()
    
    # 7. Resumen final
    print(f'\n🎯 RESUMEN:')
    print(f'   Sistema actual: {db_type} ✅')
    print(f'   Estado: Funcional para desarrollo')
    print(f'   Recomendación: Migrar a PostgreSQL para producción')

if __name__ == '__main__':
    main()