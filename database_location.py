#!/usr/bin/env python3
"""
Script para mostrar la ubicación completa de archivos de base de datos
"""

import os
import django
import sys
from pathlib import Path

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.conf import settings
from django.db import connection

def show_database_location():
    """Mostrar ubicación completa de archivos de base de datos"""
    
    print('📂 UBICACIÓN DE ARCHIVOS DE BASE DE DATOS')
    print('='*50)
    
    # 1. Configuración desde Django
    db_config = settings.DATABASES['default']
    engine = db_config['ENGINE']
    
    print(f'🎯 CONFIGURACIÓN ACTUAL:')
    print(f'   Motor: {engine}')
    
    if 'sqlite3' in engine:
        # Para SQLite
        db_path = Path(db_config['NAME'])
        
        print(f'\n💾 ARCHIVO SQLITE:')
        print(f'   Nombre: {db_path.name}')
        print(f'   Ruta completa: {db_path.absolute()}')
        print(f'   Directorio: {db_path.parent.absolute()}')
        
        # Verificar existencia
        if db_path.exists():
            stat = db_path.stat()
            size_mb = stat.st_size / (1024 * 1024)
            
            print(f'   Estado: ✅ Existe')
            print(f'   Tamaño: {stat.st_size:,} bytes ({size_mb:.2f} MB)')
            print(f'   Última modificación: {stat.st_mtime}')
        else:
            print(f'   Estado: ❌ No existe')
    
    elif 'postgresql' in engine:
        # Para PostgreSQL (si fuera el caso)
        print(f'\n🐘 POSTGRESQL:')
        print(f'   Host: {db_config.get("HOST", "localhost")}')
        print(f'   Puerto: {db_config.get("PORT", "5432")}')
        print(f'   Base de datos: {db_config.get("NAME", "N/A")}')
        print(f'   Usuario: {db_config.get("USER", "N/A")}')
    
    # 2. Directorio del proyecto
    base_dir = settings.BASE_DIR
    print(f'\n📁 DIRECTORIOS DEL PROYECTO:')
    print(f'   BASE_DIR: {base_dir}')
    print(f'   Proyecto: {base_dir.name}')
    print(f'   Ruta completa: {base_dir.absolute()}')

def show_related_files():
    """Mostrar archivos relacionados con la base de datos"""
    
    print(f'\n📋 ARCHIVOS RELACIONADOS:')
    
    # Buscar archivos de migración
    migrations_dirs = []
    apps_dir = Path('apps')
    
    if apps_dir.exists():
        for app_dir in apps_dir.iterdir():
            if app_dir.is_dir():
                migrations_dir = app_dir / 'migrations'
                if migrations_dir.exists():
                    migration_files = list(migrations_dir.glob('*.py'))
                    if migration_files:
                        migrations_dirs.append((app_dir.name, len(migration_files)))
    
    print(f'\n🔄 MIGRACIONES POR APP:')
    for app_name, count in migrations_dirs:
        print(f'   {app_name}: {count} archivos de migración')
    
    # Archivos de configuración
    config_files = [
        'manage.py',
        'requirements.txt',
        'contaec/settings.py',
        '.env.example'
    ]
    
    print(f'\n⚙️ ARCHIVOS DE CONFIGURACIÓN:')
    for config_file in config_files:
        if Path(config_file).exists():
            print(f'   ✅ {config_file}')
        else:
            print(f'   ❌ {config_file}')

def show_backup_recommendations():
    """Mostrar recomendaciones de backup"""
    
    print(f'\n💾 RECOMENDACIONES DE BACKUP:')
    
    print(f'\n📋 Backup completo del sistema:')
    print(f'   1. Archivo de base de datos:')
    print(f'      C:\\contaec\\db.sqlite3')
    
    print(f'\n   2. Archivos de media (si existen):')
    print(f'      C:\\contaec\\media\\**')
    
    print(f'\n   3. Archivos estáticos:')
    print(f'      C:\\contaec\\static\\**')
    
    print(f'\n   4. Configuración:')
    print(f'      C:\\contaec\\contaec\\settings.py')
    print(f'      C:\\contaec\\.env (si existe)')
    
    print(f'\n🔄 Comandos de backup:')
    print(f'   # Backup completo del directorio')
    print(f'   xcopy C:\\contaec C:\\backup\\contaec_$(Get-Date -Format "yyyyMMdd") /E /I')
    print(f'   ')
    print(f'   # Solo base de datos')
    print(f'   copy C:\\contaec\\db.sqlite3 C:\\backup\\db_$(Get-Date -Format "yyyyMMdd").sqlite3')

def show_directory_structure():
    """Mostrar estructura del directorio"""
    
    print(f'\n🗂️ ESTRUCTURA DEL DIRECTORIO:')
    
    current_dir = Path('.')
    
    # Mostrar estructura básica
    important_paths = [
        'db.sqlite3',
        'manage.py', 
        'apps/',
        'contaec/',
        'static/',
        'media/',
        'templates/',
        '.venv/',
        'requirements.txt'
    ]
    
    for path_name in important_paths:
        path = current_dir / path_name
        if path.exists():
            if path.is_file():
                size = path.stat().st_size
                print(f'   📄 {path_name} ({size:,} bytes)')
            else:
                # Contar contenido del directorio
                try:
                    content_count = len(list(path.iterdir()))
                    print(f'   📁 {path_name}/ ({content_count} elementos)')
                except:
                    print(f'   📁 {path_name}/')
        else:
            print(f'   ❌ {path_name} (no existe)')

def main():
    """Función principal"""
    
    show_database_location()
    show_related_files()
    show_directory_structure()
    show_backup_recommendations()
    
    print(f'\n🎯 RESUMEN DE UBICACIONES:')
    print(f'   Base de datos: C:\\contaec\\db.sqlite3')
    print(f'   Proyecto: C:\\contaec\\')
    print(f'   Configuración: C:\\contaec\\contaec\\settings.py')
    print(f'   Apps: C:\\contaec\\apps\\')

if __name__ == '__main__':
    main()