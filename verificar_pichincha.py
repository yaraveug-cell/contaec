"""
Verificar archivo de extracto PICHINCHA y procesar si es necesario
"""
import os
import django
import sys
from decimal import Decimal
import csv
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.banking.models import BankAccount, ExtractoBancario, ExtractoBancarioDetalle

def verificar_archivo_pichincha():
    """Verificar y procesar archivo PICHINCHA"""
    
    print("🔍 VERIFICACIÓN ARCHIVO PICHINCHA")
    print("="*50)
    
    # Buscar extracto PICHINCHA
    try:
        cuenta_pichincha = BankAccount.objects.get(account_number='2201109377')
        extracto = ExtractoBancario.objects.filter(bank_account=cuenta_pichincha).first()
        
        if extracto:
            print(f"📄 Extracto encontrado: {extracto}")
            print(f"   📂 Archivo: {extracto.file}")
            print(f"   📊 Status: {extracto.status}")
            print(f"   📋 Detalles: {ExtractoBancarioDetalle.objects.filter(extracto=extracto).count()}")
            
            # Verificar si existe el archivo
            if extracto.file and os.path.exists(extracto.file.path):
                print(f"   ✅ Archivo existe: {extracto.file.path}")
                
                # Leer archivo
                print(f"\n📖 CONTENIDO DEL ARCHIVO:")
                try:
                    with open(extracto.file.path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(f"   📊 Tamaño: {len(content)} caracteres")
                        print(f"   📄 Primeras 300 chars:")
                        print(f"   {repr(content[:300])}")
                        
                except UnicodeDecodeError:
                    try:
                        with open(extracto.file.path, 'r', encoding='latin1') as f:
                            content = f.read()
                            print(f"   📊 Tamaño (latin1): {len(content)} caracteres")
                            print(f"   📄 Primeras 300 chars:")
                            print(f"   {repr(content[:300])}")
                    except Exception as e:
                        print(f"   ❌ Error leyendo archivo: {e}")
                
                # Intentar procesar como CSV
                print(f"\n🔧 INTENTO DE PROCESAMIENTO CSV:")
                try:
                    # Intentar primero UTF-8, luego Latin-1
                    encoding = 'utf-8'
                    try:
                        with open(extracto.file.path, 'r', encoding='utf-8') as f:
                            f.read(100)  # Test read
                    except UnicodeDecodeError:
                        encoding = 'latin-1'
                        print(f"   📊 Usando encoding: {encoding}")
                    
                    with open(extracto.file.path, 'r', encoding=encoding) as f:
                        # Detectar si es CSV
                        first_line = f.readline().strip()
                        print(f"   📄 Primera línea: {repr(first_line)}")
                        
                        # ¿Tiene comas? ¿Punto y coma?
                        if ',' in first_line:
                            delimiter = ','
                            print(f"   📊 Detectado delimitador: coma")
                        elif ';' in first_line:
                            delimiter = ';'
                            print(f"   📊 Detectado delimitador: punto y coma")
                        elif '\t' in first_line:
                            delimiter = '\t'
                            print(f"   📊 Detectado delimitador: tab")
                        else:
                            print(f"   ❌ No se detectó delimitador CSV")
                            return
                        
                        # Leer CSV
                        f.seek(0)  # Volver al inicio
                        reader = csv.reader(f, delimiter=delimiter)
                        rows = list(reader)
                        
                        print(f"   📊 Filas CSV: {len(rows)}")
                        if rows:
                            print(f"   📄 Headers: {rows[0]}")
                            if len(rows) > 1:
                                print(f"   📄 Ejemplo fila 1: {rows[1]}")
                            if len(rows) > 2:
                                print(f"   📄 Ejemplo fila 2: {rows[2]}")
                        
                        # Si hay datos, procesar
                        if len(rows) > 1:  # Más de solo headers
                            print(f"\n🚀 PROCESANDO DETALLES:")
                            procesar_detalles_pichincha(extracto, rows)
                        
                except Exception as e:
                    print(f"   ❌ Error procesando CSV: {e}")
            
            else:
                print(f"   ❌ Archivo no existe: {extracto.file}")
        
        else:
            print(f"❌ No se encontró extracto para PICHINCHA")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def procesar_detalles_pichincha(extracto, rows):
    """Procesar detalles del extracto PICHINCHA"""
    
    print(f"   🔧 Procesando {len(rows)-1} filas de datos...")
    
    headers = rows[0] if rows else []
    print(f"   📋 Headers disponibles: {headers}")
    
    # Mapeo típico de campos PICHINCHA
    campo_fecha = None
    campo_descripcion = None  
    campo_referencia = None
    campo_debito = None
    campo_credito = None
    campo_saldo = None
    
    # Detectar campos automáticamente
    for i, header in enumerate(headers):
        header_lower = header.lower()
        if 'fecha' in header_lower:
            campo_fecha = i
        elif 'descripcion' in header_lower or 'detalle' in header_lower:
            campo_descripcion = i
        elif 'referencia' in header_lower or 'ref' in header_lower:
            campo_referencia = i
        elif 'debito' in header_lower or 'debe' in header_lower:
            campo_debito = i
        elif 'credito' in header_lower or 'haber' in header_lower:
            campo_credito = i
        elif 'saldo' in header_lower:
            campo_saldo = i
    
    print(f"   🎯 Campo fecha: {campo_fecha} ({headers[campo_fecha] if campo_fecha is not None else 'N/A'})")
    print(f"   🎯 Campo descripción: {campo_descripcion} ({headers[campo_descripcion] if campo_descripcion is not None else 'N/A'})")
    print(f"   🎯 Campo débito: {campo_debito} ({headers[campo_debito] if campo_debito is not None else 'N/A'})")
    print(f"   🎯 Campo crédito: {campo_credito} ({headers[campo_credito] if campo_credito is not None else 'N/A'})")
    
    if campo_fecha is None:
        print(f"   ❌ No se pudo detectar campo fecha")
        return
    
    # Procesar filas de datos
    detalles_creados = 0
    errores = 0
    
    for i, row in enumerate(rows[1:], 1):  # Saltar headers
        try:
            if len(row) <= max(campo_fecha or 0, campo_descripcion or 0, campo_debito or 0, campo_credito or 0):
                print(f"   ⚠️  Fila {i}: Insuficientes columnas ({len(row)})")
                continue
            
            # Extraer fecha
            fecha_str = row[campo_fecha] if campo_fecha is not None else ''
            if not fecha_str.strip():
                continue
            
            # Parsear fecha (varios formatos posibles)
            fecha = None
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y']:
                try:
                    fecha = datetime.strptime(fecha_str.strip(), fmt).date()
                    break
                except:
                    continue
            
            if not fecha:
                print(f"   ⚠️  Fila {i}: Fecha inválida '{fecha_str}'")
                continue
            
            # Extraer descripción
            descripcion = row[campo_descripcion].strip() if campo_descripcion is not None else f'Movimiento {i}'
            
            # Extraer montos
            debito = None
            credito = None
            
            if campo_debito is not None and row[campo_debito].strip():
                try:
                    debito = Decimal(row[campo_debito].replace(',', '').replace('$', '').strip())
                except:
                    pass
            
            if campo_credito is not None and row[campo_credito].strip():
                try:
                    credito = Decimal(row[campo_credito].replace(',', '').replace('$', '').strip())
                except:
                    pass
            
            # Extraer saldo
            saldo = None
            if campo_saldo is not None and row[campo_saldo].strip():
                try:
                    saldo = Decimal(row[campo_saldo].replace(',', '').replace('$', '').strip())
                except:
                    pass
            
            # Crear detalle
            detalle = ExtractoBancarioDetalle.objects.create(
                extracto=extracto,
                fecha=fecha,
                descripcion=descripcion,
                referencia=row[campo_referencia].strip() if campo_referencia is not None else '',
                debito=debito,
                credito=credito,
                saldo=saldo,
                is_reconciled=False
            )
            
            detalles_creados += 1
            if i <= 3:  # Mostrar primeros 3
                print(f"   ✅ Creado {i}: {fecha} - {descripcion} - D:{debito} C:{credito}")
        
        except Exception as e:
            errores += 1
            print(f"   ❌ Error fila {i}: {e}")
    
    # Actualizar status del extracto
    if detalles_creados > 0:
        extracto.status = 'processed'
        extracto.save()
        
        print(f"\n🎉 RESULTADO:")
        print(f"   ✅ Detalles creados: {detalles_creados}")
        print(f"   ❌ Errores: {errores}")
        print(f"   📊 Status actualizado: processed")
    else:
        print(f"\n❌ No se crearon detalles")

if __name__ == "__main__":
    verificar_archivo_pichincha()