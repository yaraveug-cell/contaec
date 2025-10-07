#!/usr/bin/env python
"""
Debug del sistema de inventario en asientos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append('c:\\contaec')
django.setup()

from apps.invoicing.models import Invoice
from apps.companies.models import Company

def debug_latest_invoice():
    """Depurar la última factura creada"""
    try:
        company = Company.objects.get(trade_name="GUEBER")
        
        # Obtener la última factura
        latest_invoice = Invoice.objects.filter(company=company).order_by('-id').first()
        
        if not latest_invoice:
            print("❌ No hay facturas en el sistema")
            return
        
        print(f"🧾 FACTURA: {latest_invoice.number} (ID: {latest_invoice.id})")
        print(f"📅 Fecha: {latest_invoice.date}")
        print(f"👤 Cliente: {latest_invoice.customer}")
        print(f"📊 Estado: {latest_invoice.status}")
        print(f"💰 Total: ${latest_invoice.total}")
        
        print(f"\n📋 LÍNEAS DE FACTURA: {latest_invoice.lines.count()}")
        
        for i, line in enumerate(latest_invoice.lines.all(), 1):
            print(f"\n   Línea {i}:")
            print(f"   📦 Producto: {line.product.code} - {line.product.name}")
            print(f"   🏭 Maneja Inventario: {line.product.manages_inventory}")
            print(f"   💵 Costo: ${line.product.cost_price}")
            print(f"   📈 Precio Venta: ${line.unit_price}")
            print(f"   📊 Cantidad: {line.quantity}")
            print(f"   💯 IVA: {line.iva_rate}%")
        
        # Probar el filtro específico
        inventory_lines = latest_invoice.lines.filter(product__manages_inventory=True)
        print(f"\n🔍 FILTRO DE INVENTARIO:")
        print(f"   Total líneas: {latest_invoice.lines.count()}")
        print(f"   Líneas con inventario: {inventory_lines.count()}")
        
        if inventory_lines.exists():
            print(f"   ✅ Productos con inventario encontrados:")
            for line in inventory_lines:
                print(f"      - {line.product.code}: Maneja={line.product.manages_inventory}")
        else:
            print(f"   ❌ NO se encontraron productos con inventario")
            print(f"   🔧 Verificando cada línea individualmente:")
            for line in latest_invoice.lines.all():
                print(f"      - {line.product.code}: manages_inventory = {line.product.manages_inventory}")
        
        return latest_invoice
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🔍 DEBUG DE INVENTARIO EN ASIENTOS")
    print("=" * 50)
    debug_latest_invoice()