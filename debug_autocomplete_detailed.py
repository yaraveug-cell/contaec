#!/usr/bin/env python3
"""
Script para verificar debugging del autocompletado de productos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.inventory.models import Product

def debug_autocomplete_functionality():
    print("=== DEBUG AUTOCOMPLETADO DE PRODUCTOS ===\n")
    
    products = Product.objects.all()[:5]
    
    print(f"📦 PRODUCTOS DISPONIBLES ({len(products)}):")
    for product in products:
        print(f"  ID {product.id}: {product.name}")
        print(f"    Descripción: '{product.description}'")
        print(f"    Precio: ${product.sale_price}")
        print()
    
    print("🔧 CAMBIOS APLICADOS AL JAVASCRIPT:")
    print("✅ Event delegation en lugar de listeners individuales")
    print("✅ Selectores más específicos para campos (-description, -unit_price)")
    print("✅ Console.log para debugging en navegador")
    print("✅ MutationObserver mejorado para nuevas filas")
    print("✅ Manejo robusto de elementos DOM")
    print()
    
    print("🧪 INSTRUCCIONES DE PRUEBA DETALLADA:")
    print("1. Abrir: http://127.0.0.1:8000/admin/invoicing/invoice/add/")
    print("2. Abrir Developer Tools (F12)")
    print("3. Ir a la pestaña Console")
    print("4. En la primera línea de factura:")
    print("   a. Seleccionar un producto")
    print("   b. Verificar mensajes en consola")
    print("   c. Cambiar a otro producto")
    print("   d. Verificar que campos se actualizan")
    print("5. Hacer clic en 'Add another Invoice line'")
    print("6. En la nueva línea:")
    print("   a. Seleccionar un producto")
    print("   b. Verificar que funciona igual")
    print()
    
    print("📋 MENSAJES ESPERADOS EN CONSOLA:")
    print("- 'Iniciando autocompletado de productos...'")
    print("- 'Productos cargados: X'")
    print("- 'Event delegation configurado para selects de producto'")
    print("- 'Producto seleccionado: X'")
    print("- 'Datos del producto: {...}'")
    print("- 'Campo descripción encontrado: true'")
    print("- 'Campo precio encontrado: true'")
    print("- 'Descripción actualizada: ...'")
    print("- 'Precio actualizado: ...'")
    print()
    
    print("❌ SI NO FUNCIONA, VERIFICAR:")
    print("- ¿Los mensajes aparecen en consola?")
    print("- ¿Se muestran errores JavaScript?")
    print("- ¿Los nombres de campos coinciden con los esperados?")
    print("- ¿window.productsData contiene los datos?")
    print()
    
    print("🔍 PARA DEBUG MANUAL EN CONSOLA DEL NAVEGADOR:")
    print("console.log(window.productsData); // Ver datos de productos")
    print("document.querySelectorAll('select[name*=\"product\"]'); // Ver selects")
    print("document.querySelectorAll('input[name$=\"-description\"]'); // Ver campos descripción")

if __name__ == "__main__":
    debug_autocomplete_functionality()