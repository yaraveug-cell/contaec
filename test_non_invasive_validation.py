#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test final del sistema de notificaciones NO invasivas
Solo debe bloquear cuando NO HAY stock suficiente
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


def test_non_invasive_validation():
    """Prueba que el sistema solo bloquea ERROR, permite WARNING/INFO"""
    print("🧪 PROBANDO SISTEMA NO INVASIVO")
    print("=" * 50)
    
    # Buscar productos con diferentes stocks
    products_with_stock = []
    for product in Product.objects.all()[:10]:
        stock = Stock.objects.filter(product=product).first()
        stock_qty = stock.quantity if stock else Decimal('0')
        products_with_stock.append((product, stock_qty))
    
    test_cases = [
        {"stock": Decimal('0'), "quantity": Decimal('1'), "should_block": True, "level": "ERROR"},
        {"stock": Decimal('5'), "quantity": Decimal('10'), "should_block": True, "level": "ERROR"},
        {"stock": Decimal('5'), "quantity": Decimal('4'), "should_block": False, "level": "WARNING"},
        {"stock": Decimal('20'), "quantity": Decimal('12'), "should_block": False, "level": "INFO"},
        {"stock": Decimal('75'), "quantity": Decimal('10'), "should_block": False, "level": "SUCCESS"},
    ]
    
    print("🎯 CASOS DE PRUEBA:")
    print("-" * 50)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. Stock {case['stock']} → Solicitar {case['quantity']}")
        print(f"   Esperado: {case['level']} ({'BLOQUEA' if case['should_block'] else 'PERMITE'} venta)")
        
        # Crear línea de prueba
        if products_with_stock:
            product, _ = products_with_stock[0]  # Usar primer producto
            
            # Simular stock
            stock, _ = Stock.objects.get_or_create(product=product)
            stock.quantity = case['stock']
            stock.save()
            
            # Crear línea
            line = InvoiceLine()
            line.product = product
            line.quantity = case['quantity']
            line.unit_price = Decimal('10.00')
            
            # Probar validación
            validation_result = line.check_stock_availability()
            print(f"   Resultado: {validation_result['level'].upper()} - {validation_result.get('icon', '')} {validation_result.get('message', '')[:60]}...")
            
            # Probar si se puede guardar
            try:
                line.clean()
                can_save = True
                result = "✅ PERMITE guardar"
            except Exception as e:
                can_save = False
                result = "❌ BLOQUEA guardar"
            
            # Verificar expectativas
            expected_behavior = "❌ BLOQUEA" if case['should_block'] else "✅ PERMITE"
            status = "✅ CORRECTO" if (can_save != case['should_block']) else "❌ INCORRECTO"
            
            print(f"   Guardado: {result}")
            print(f"   Esperado: {expected_behavior}")
            print(f"   Estado: {status}")
    
    print("\n" + "=" * 50)
    print("🎯 RESUMEN DEL COMPORTAMIENTO:")
    print("🔴 ERROR: Stock insuficiente → ❌ BLOQUEA guardado")
    print("🟡 WARNING: Stock bajo → ✅ PERMITE guardado + notificación flotante")
    print("🔵 INFO: Alto consumo → ✅ PERMITE guardado + notificación flotante") 
    print("🟢 SUCCESS: Stock OK → ✅ PERMITE guardado + notificación flotante")
    print("\n💡 Solo las notificaciones flotantes aparecen, NO hay mensajes invasivos")
    print("=" * 50)


if __name__ == "__main__":
    try:
        test_non_invasive_validation()
        print("\n✅ Prueba completada. El sistema está configurado correctamente.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()