"""
Verificar problema de decimales en extracto PICHINCHA
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.banking.models import ExtractoBancario, ExtractoBancarioDetalle

def verificar_decimales_pichincha():
    """Verificar problema de decimales"""
    
    print("🔍 VERIFICACIÓN PROBLEMA DECIMALES PICHINCHA")
    print("="*60)
    
    # Buscar extracto PICHINCHA procesado
    extracto = ExtractoBancario.objects.filter(
        bank_account__account_number='2201109377',
        status='processed'
    ).first()
    
    if not extracto:
        print("❌ No se encontró extracto PICHINCHA procesado")
        return
    
    print(f"📄 Extracto: {extracto}")
    print(f"📊 Detalles: {extracto.detalles.count()}")
    
    # Verificar algunos detalles
    print(f"\n📋 PRIMEROS 10 DETALLES CON MONTOS:")
    detalles = extracto.detalles.all()[:10]
    
    for i, detalle in enumerate(detalles, 1):
        debito = detalle.debito or 0
        credito = detalle.credito or 0
        saldo = detalle.saldo or 0
        
        print(f"  {i:2d}. {detalle.fecha} - {detalle.descripcion[:40]}")
        print(f"      💰 Débito: ${debito:,.2f}")
        print(f"      💰 Crédito: ${credito:,.2f}")
        print(f"      💰 Saldo: ${saldo:,.2f}")
        print()
    
    # Verificar archivo original para comparar
    print(f"📄 VERIFICACIÓN ARCHIVO ORIGINAL:")
    try:
        with open(extracto.file.path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Buscar primeras líneas con datos
        print(f"   Buscando líneas con montos en el archivo...")
        
        count = 0
        for i, line in enumerate(lines):
            if '$' in line and count < 5:
                print(f"   Línea {i}: {line.strip()}")
                count += 1
    
    except Exception as e:
        print(f"   ❌ Error leyendo archivo: {e}")

if __name__ == "__main__":
    verificar_decimales_pichincha()