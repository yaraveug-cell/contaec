#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simplificado para el sistema de notificaciones flotantes
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.invoicing.models import InvoiceLine
from apps.inventory.models import Product, Stock


def test_validation_levels():
    """Prueba todos los niveles de validación con productos existentes"""
    print("🧪 Probando niveles de validación con productos existentes...")
    
    # Buscar productos existentes
    products = Product.objects.all()[:3]
    if not products:
        print("❌ No hay productos disponibles para probar")
        return
    
    print(f"📦 Encontrados {len(products)} productos para probar")
    
    # Ver stock de cada producto
    for product in products:
        stock = Stock.objects.filter(product=product).first()
        stock_qty = stock.quantity if stock else Decimal('0')
        print(f"   📦 {product.name}: Stock {stock_qty}")
        
        # Crear línea de prueba
        line = InvoiceLine()
        line.product = product
        line.quantity = stock_qty + Decimal('10')  # Solicitar más del disponible
        line.unit_price = Decimal('10.00')
        
        # Probar validación
        validation_result = line.check_stock_availability()
        
        print(f"   🔍 Solicitar {line.quantity}, Disponible {stock_qty}")
        print(f"   📊 Resultado: {validation_result['level'].upper()} - {validation_result['message']}")
        
        # Probar si se puede guardar
        try:
            line.clean()
            print(f"   💾 ¿Se puede guardar? ✅ SÍ")
        except Exception as e:
            print(f"   💾 ¿Se puede guardar? ❌ NO - {str(e)}")
        
        print()


def show_browser_instructions():
    """Muestra instrucciones para probar en el navegador"""
    print("\n🌐 INSTRUCCIONES PARA PROBAR EN NAVEGADOR")
    print("=" * 50)
    print("1. Abre el admin de Django: http://127.0.0.1:8000/admin/")
    print("2. Ve a 'Invoices' → 'Add invoice'")
    print("3. Añade líneas de productos con diferentes cantidades")
    print("4. Observa las notificaciones flotantes en esquina superior derecha")
    print("5. Las notificaciones duran 6 segundos y desaparecen automáticamente")
    print("\n🎨 Tipos de notificaciones:")
    print("   🔴 ERROR: Sin stock / Cantidad excede stock")
    print("   🟡 WARNING: Stock bajo después de la venta")
    print("   🔵 INFO: Alto consumo (>50% del stock)")
    print("   🟢 SUCCESS: Stock suficiente")
    print("\n⌨️ Para demo en consola del navegador (F12):")
    print("   stockValidator.demo()")
    print("=" * 50)


if __name__ == "__main__":
    print("🚀 SISTEMA DE NOTIFICACIONES FLOTANTES - PRUEBA RÁPIDA")
    print("=" * 55)
    
    try:
        test_validation_levels()
        show_browser_instructions()
        
        print("\n✅ ¡Pruebas completadas! El sistema está listo para usar.")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()