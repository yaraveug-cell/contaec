#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para verificar que NO aparecen mensajes invasivos de stock
Solo deben aparecer notificaciones flotantes JavaScript
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.invoicing.admin import IntelligentInvoiceLineForm
from apps.inventory.models import Product, Stock
from apps.companies.models import Company


def test_no_invasive_messages():
    """Probar que no hay mensajes invasivos en los formularios"""
    print("🧪 PROBANDO QUE NO HAY MENSAJES INVASIVOS")
    print("=" * 50)
    
    # Buscar productos GUEBER
    gueber = Company.objects.filter(trade_name__icontains='GUEBER').first()
    if not gueber:
        print("❌ No se encontró empresa GUEBER")
        return
    
    products = Product.objects.filter(company=gueber)[:5]
    if not products:
        print("❌ No hay productos en GUEBER")
        return
    
    print(f"🏢 Empresa: {gueber.trade_name}")
    print(f"📦 Productos a probar: {products.count()}")
    
    test_cases = [
        {"stock": 0, "quantity": 1, "should_have_error": True, "desc": "Sin stock"},
        {"stock": 3, "quantity": 2, "should_have_error": False, "desc": "Stock crítico pero suficiente"},
        {"stock": 5, "quantity": 4, "should_have_error": False, "desc": "Stock bajo pero suficiente"},
        {"stock": 20, "quantity": 15, "should_have_error": False, "desc": "Alto consumo pero suficiente"},
    ]
    
    for i, case in enumerate(test_cases):
        print(f"\n--- Caso {i+1}: {case['desc']} ---")
        
        product = products[i % len(products)]
        
        # Configurar stock
        stock_obj, _ = Stock.objects.get_or_create(product=product)
        stock_obj.quantity = Decimal(str(case['stock']))
        stock_obj.save()
        
        # Crear formulario
        form_data = {
            'product': product.id,
            'quantity': case['quantity'],
            'unit_price': '10.00'
        }
        
        form = IntelligentInvoiceLineForm(data=form_data)
        is_valid = form.is_valid()
        
        print(f"   📊 Stock: {case['stock']}, Cantidad: {case['quantity']}")
        print(f"   🔍 Formulario válido: {is_valid}")
        
        if form.errors:
            print(f"   🚨 Errores encontrados:")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"      {field}: {error}")
                    # Verificar si es mensaje invasivo
                    if any(word in str(error).lower() for word in ['advertencia', 'crítico', 'considere', 'reabastecer']):
                        print(f"      ❌ MENSAJE INVASIVO DETECTADO: {error}")
                    else:
                        print(f"      ✅ Error apropiado (no invasivo)")
        else:
            print(f"   ✅ Sin errores de formulario")
        
        # Verificar expectativas
        if case['should_have_error'] and not is_valid:
            print(f"   ✅ CORRECTO: Error esperado para {case['desc']}")
        elif not case['should_have_error'] and is_valid:
            print(f"   ✅ CORRECTO: Sin error para {case['desc']}")
        elif case['should_have_error'] and is_valid:
            print(f"   ❌ INCORRECTO: Debería tener error para {case['desc']}")
        else:
            print(f"   ❌ INCORRECTO: No debería tener error para {case['desc']}")
    
    print("\n" + "=" * 50)
    print("🎯 VERIFICACIÓN COMPLETADA")
    print("💡 Solo errores críticos (sin stock) deben bloquear")
    print("💡 Stock bajo/crítico NO debe mostrar mensajes invasivos")
    print("💡 Las notificaciones flotantes JavaScript manejan el UX")
    print("=" * 50)


if __name__ == "__main__":
    try:
        test_no_invasive_messages()
        print("\n✅ Test completado - Verificar que no hay mensajes invasivos")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()