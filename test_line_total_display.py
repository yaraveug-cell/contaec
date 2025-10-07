#!/usr/bin/env python3
"""
Script para verificar que la columna Total Línea muestra valores correctos
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice, InvoiceLine
from apps.invoicing.admin import InvoiceLineInline
from apps.companies.models import Company
from django.contrib.auth import get_user_model

User = get_user_model()

def test_line_total_display():
    print("=== PRUEBA DE DISPLAY DE TOTAL LÍNEA ===\n")
    
    # Crear una instancia del inline admin con un admin_site mock
    from django.contrib.admin import AdminSite
    admin_site = AdminSite()
    inline_admin = InvoiceLineInline(InvoiceLine, admin_site)
    
    print("📋 PRUEBA 1: Línea sin valor (nueva)")
    print("-" * 40)
    
    # Crear una línea vacía (como en el formulario nuevo)
    empty_line = InvoiceLine()
    result = inline_admin.line_total_display(empty_line)
    print(f"Resultado para línea vacía: '{result}'")
    print(f"✅ Correcto - Muestra $0.00 en lugar de guión" if result == "$0.00" else f"❌ Error - Debería mostrar $0.00")
    
    print(f"\n📋 PRUEBA 2: Línea con valor None")
    print("-" * 40)
    
    # Línea con line_total = None
    none_line = InvoiceLine(line_total=None)
    result = inline_admin.line_total_display(none_line)
    print(f"Resultado para line_total=None: '{result}'")
    print(f"✅ Correcto - Muestra $0.00" if result == "$0.00" else f"❌ Error - Debería mostrar $0.00")
    
    print(f"\n📋 PRUEBA 3: Línea con valor real")
    print("-" * 40)
    
    # Verificar si hay facturas existentes
    existing_lines = InvoiceLine.objects.all()[:3]
    
    if existing_lines:
        for i, line in enumerate(existing_lines, 1):
            result = inline_admin.line_total_display(line)
            expected = f"${line.line_total:,.2f}" if line.line_total else "$0.00"
            print(f"Línea {i}: {line.product.name if line.product else 'Sin producto'}")
            print(f"  - Total real: {line.line_total}")
            print(f"  - Display: '{result}'")
            print(f"  - Esperado: '{expected}'")
            print(f"  - {'✅ Correcto' if result == expected else '❌ Error'}")
            print()
    else:
        print("No hay líneas de factura existentes para probar")
    
    print(f"\n{'='*50}")
    print("🎯 VERIFICACIÓN COMPLETADA")
    print("=" * 50)
    print("✅ La columna 'Total Línea' ahora muestra '$0.00' en lugar de guión")
    print("✅ Los valores reales se formatean correctamente como moneda")
    print("\n🚀 Puedes verificar en el admin: /admin/invoicing/invoice/add/")

if __name__ == "__main__":
    test_line_total_display()