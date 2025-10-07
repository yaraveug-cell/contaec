"""
Verificar contenido del nuevo archivo PICHINCHA
"""
import os
import django
import sys
import csv

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.banking.models import ExtractoBancario

def verificar_nuevo_archivo():
    """Verificar el nuevo archivo de PICHINCHA"""
    
    print("🔍 VERIFICACIÓN NUEVO ARCHIVO PICHINCHA")
    print("="*50)
    
    extracto = ExtractoBancario.objects.filter(
        bank_account__account_number='2201109377'
    ).first()
    
    if extracto:
        print(f"📄 Archivo: {extracto.file}")
        print(f"📂 Path: {extracto.file.path}")
        
        # Verificar si existe
        if os.path.exists(extracto.file.path):
            print(f"✅ Archivo existe")
            
            # Leer contenido
            try:
                with open(extracto.file.path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"📊 Tamaño UTF-8: {len(content)} caracteres")
                    print(f"📄 Primeras 500 chars:")
                    print(repr(content[:500]))
            except UnicodeDecodeError:
                try:
                    with open(extracto.file.path, 'r', encoding='latin-1') as f:
                        content = f.read()
                        print(f"📊 Tamaño Latin-1: {len(content)} caracteres")
                        print(f"📄 Primeras 500 chars:")
                        print(repr(content[:500]))
                except Exception as e:
                    print(f"❌ Error leyendo: {e}")
            
            # Analizar como CSV
            try:
                encoding = 'utf-8'
                try:
                    with open(extracto.file.path, 'r', encoding='utf-8') as f:
                        f.read(100)
                except UnicodeDecodeError:
                    encoding = 'latin-1'
                
                print(f"\n📊 ANÁLISIS CSV (encoding: {encoding}):")
                with open(extracto.file.path, 'r', encoding=encoding) as f:
                    # Detectar delimitador
                    first_line = f.readline().strip()
                    print(f"Primera línea: {repr(first_line)}")
                    
                    delimiter = ';' if ';' in first_line else (',' if ',' in first_line else '\t')
                    print(f"Delimitador detectado: '{delimiter}'")
                    
                    # Leer como CSV
                    f.seek(0)
                    reader = csv.reader(f, delimiter=delimiter)
                    rows = list(reader)
                    
                    print(f"Total filas: {len(rows)}")
                    
                    print(f"\nPrimeras 10 filas:")
                    for i, row in enumerate(rows[:10]):
                        row_clean = [cell.strip() for cell in row if cell.strip()]
                        print(f"  {i}: {row_clean}")
                        
                        # Buscar palabras clave
                        row_text = ' '.join(row).lower()
                        if any(word in row_text for word in ['movimiento', 'fecha', 'detalle']):
                            print(f"     🎯 Posible header/sección")
                
            except Exception as e:
                print(f"❌ Error CSV: {e}")
        else:
            print(f"❌ Archivo no existe: {extracto.file.path}")
    else:
        print(f"❌ No se encontró extracto")

if __name__ == "__main__":
    verificar_nuevo_archivo()