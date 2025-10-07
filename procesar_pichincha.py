"""
Procesador específico para extractos PICHINCHA
"""
import os
import django
import sys
import csv
from datetime import datetime
from decimal import Decimal

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.banking.models import BankAccount, ExtractoBancario, ExtractoBancarioDetalle

def procesar_extracto_pichincha():
    """Procesar extracto PICHINCHA con formato específico"""
    
    print("🚀 PROCESADOR EXTRACTO PICHINCHA")
    print("="*50)
    
    try:
        cuenta_pichincha = BankAccount.objects.get(account_number='2201109377')
        extracto = ExtractoBancario.objects.filter(bank_account=cuenta_pichincha).first()
        
        if not extracto:
            print("❌ No se encontró extracto PICHINCHA")
            return
        
        print(f"📄 Procesando: {extracto}")
        
        # Limpiar detalles existentes (si los hay)
        detalles_existentes = ExtractoBancarioDetalle.objects.filter(extracto=extracto).count()
        if detalles_existentes > 0:
            print(f"🧹 Limpiando {detalles_existentes} detalles existentes")
            ExtractoBancarioDetalle.objects.filter(extracto=extracto).delete()
        
        # Leer archivo
        with open(extracto.file.path, 'r', encoding='latin-1') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
        
        # Buscar inicio de datos (fila que contiene "Movimientos")
        datos_inicio = None
        headers_fila = None
        
        for i, row in enumerate(rows):
            if any('Movimientos' in str(cell) for cell in row):
                datos_inicio = i + 1  # La siguiente fila debería ser headers
                break
        
        if datos_inicio and datos_inicio < len(rows):
            # Verificar headers
            headers_row = rows[datos_inicio]
            headers_clean = [cell.strip() for cell in headers_row if cell.strip()]
            
            print(f"📋 Headers encontrados en fila {datos_inicio}: {headers_clean}")
            
            # Mapear campos PICHINCHA
            # Headers esperados: ['Fecha', 'Tipo', 'Monto', 'Detalle', 'Fecha contable', 'Categoría']
            campo_fecha = 0        # Fecha
            campo_tipo = 1         # Tipo (Ingreso/Egreso)
            campo_monto = 2        # Monto
            campo_detalle = 3      # Detalle/Descripción
            campo_fecha_contable = 4  # Fecha contable
            
            print(f"🎯 Campos mapeados:")
            print(f"   - Fecha: columna {campo_fecha}")
            print(f"   - Tipo: columna {campo_tipo}")  
            print(f"   - Monto: columna {campo_monto}")
            print(f"   - Detalle: columna {campo_detalle}")
            
            # Procesar filas de datos
            datos_filas = rows[datos_inicio + 1:]  # Saltar headers
            detalles_creados = 0
            errores = 0
            
            print(f"\n🔧 Procesando {len(datos_filas)} filas de datos...")
            
            for i, row in enumerate(datos_filas):
                try:
                    # Limpiar row
                    row_clean = [cell.strip() for cell in row]
                    
                    if len(row_clean) < 4:  # Mínimo fecha, tipo, monto, detalle
                        continue
                    
                    # Extraer fecha
                    fecha_str = row_clean[campo_fecha]
                    if not fecha_str:
                        continue
                    
                    fecha = datetime.strptime(fecha_str, '%d/%m/%Y').date()
                    
                    # Extraer tipo y monto
                    tipo = row_clean[campo_tipo]
                    monto_str = row_clean[campo_monto].replace('$', '').replace(',', '')
                    monto = Decimal(monto_str)
                    
                    # Extraer descripción
                    descripcion = row_clean[campo_detalle] if len(row_clean) > campo_detalle else ''
                    
                    # Determinar débito/crédito según tipo
                    if tipo == 'Egreso':
                        debito = abs(monto)  # Siempre positivo para débito
                        credito = None
                    else:  # Ingreso
                        debito = None
                        credito = abs(monto)  # Siempre positivo para crédito
                    
                    # Crear detalle (saldo temporal, se puede calcular después)
                    detalle = ExtractoBancarioDetalle.objects.create(
                        extracto=extracto,
                        fecha=fecha,
                        descripcion=descripcion,
                        referencia='',  # PICHINCHA no tiene referencia separada
                        debito=debito,
                        credito=credito,
                        saldo=Decimal('0.00'),  # Saldo temporal (requerido por modelo)
                        is_reconciled=False
                    )
                    
                    detalles_creados += 1
                    
                    if i < 5:  # Mostrar primeros 5
                        print(f"   ✅ {i+1}: {fecha} - {tipo} - {descripcion} - D:{debito} C:{credito}")
                
                except Exception as e:
                    errores += 1
                    if errores <= 3:  # Mostrar primeros errores
                        print(f"   ❌ Error fila {i+1}: {e}")
            
            # Actualizar status del extracto
            if detalles_creados > 0:
                extracto.status = 'processed'
                extracto.save()
                
                print(f"\n🎉 RESULTADO:")
                print(f"   ✅ Detalles creados: {detalles_creados}")
                print(f"   ❌ Errores: {errores}")
                print(f"   📊 Status actualizado: processed")
                
                # Verificar resultado
                print(f"\n🔍 VERIFICACIÓN:")
                detalles_final = ExtractoBancarioDetalle.objects.filter(extracto=extracto)
                print(f"   📊 Detalles en BD: {detalles_final.count()}")
                print(f"   💰 Total débitos: {sum(d.debito or Decimal('0') for d in detalles_final)}")
                print(f"   💰 Total créditos: {sum(d.credito or Decimal('0') for d in detalles_final)}")
            else:
                print(f"\n❌ No se crearon detalles")
        
        else:
            print(f"❌ No se encontró sección de movimientos")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    procesar_extracto_pichincha()