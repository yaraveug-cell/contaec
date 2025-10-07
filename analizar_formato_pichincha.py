"""
Analizar formato completo PICHINCHA para encontrar datos reales
"""
import os
import django
import sys
import csv

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.banking.models import BankAccount, ExtractoBancario

def analizar_formato_completo():
    """Analizar formato completo del archivo PICHINCHA"""
    
    print("🔍 ANÁLISIS FORMATO COMPLETO PICHINCHA")
    print("="*60)
    
    try:
        cuenta_pichincha = BankAccount.objects.get(account_number='2201109377')
        extracto = ExtractoBancario.objects.filter(bank_account=cuenta_pichincha).first()
        
        if extracto and extracto.file:
            print(f"📄 Analizando: {extracto.file.path}")
            
            # Leer archivo completo
            with open(extracto.file.path, 'r', encoding='latin-1') as f:
                reader = csv.reader(f, delimiter=';')
                rows = list(reader)
            
            print(f"📊 Total filas: {len(rows)}")
            print(f"\n📋 TODAS LAS FILAS:")
            
            for i, row in enumerate(rows):
                # Limpiar row para mostrar
                row_clean = [cell.strip() for cell in row if cell.strip()]
                
                print(f"{i:2d}: {row_clean}")
                
                # Buscar patrones de datos bancarios
                if row_clean:
                    first_cell = row_clean[0]
                    
                    # ¿Parece una fecha?
                    if any(char in first_cell for char in ['/', '-']):
                        if len(first_cell) >= 8:  # Mínimo para fecha
                            print(f"     🎯 POSIBLE FECHA: '{first_cell}'")
                    
                    # ¿Menciona movimientos?
                    if any(word in first_cell.lower() for word in ['movimiento', 'transaccion', 'fecha', 'detalle']):
                        print(f"     🎯 POSIBLE HEADER: '{first_cell}'")
                    
                    # ¿Tiene montos? (números con punto/coma)
                    for cell in row_clean:
                        if cell.replace(',', '').replace('.', '').replace('-', '').replace('$', '').strip().isdigit():
                            if len(cell) > 1:  # No solo un dígito
                                print(f"     💰 POSIBLE MONTO: '{cell}'")
            
            # Buscar sección de movimientos
            print(f"\n🔍 BUSCANDO SECCIÓN DE MOVIMIENTOS:")
            movimientos_start = None
            
            for i, row in enumerate(rows):
                row_text = ' '.join(row).lower()
                
                if any(word in row_text for word in ['movimientos', 'transacciones', 'detalle de cuenta', 'historial']):
                    print(f"   📍 Fila {i}: Posible inicio de movimientos")
                    movimientos_start = i
                    
                # Buscar headers típicos
                if any(word in row_text for word in ['fecha', 'descripcion', 'referencia', 'debito', 'credito', 'saldo']):
                    print(f"   📋 Fila {i}: Posible header de datos - '{row_text.strip()}'")
            
            if movimientos_start:
                print(f"\n📊 ANÁLISIS DESDE FILA {movimientos_start}:")
                for i in range(movimientos_start, min(movimientos_start + 10, len(rows))):
                    row_clean = [cell.strip() for cell in rows[i] if cell.strip()]
                    print(f"   {i}: {row_clean}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    analizar_formato_completo()