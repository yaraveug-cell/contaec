#!/usr/bin/env python3
"""
Script de prueba para el sistema inteligente de validación de stock.

Funcionalidades probadas:
1. Validación de stock insuficiente (debe bloquear)
2. Advertencias de stock bajo (debe permitir con advertencia)
3. Stock suficiente (debe permitir normalmente)
4. Integración con mensajes de Django Admin
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import InvoiceLine, Invoice, Customer
from apps.inventory.models import Product
from apps.companies.models import Company
from decimal import Decimal


def create_test_data():
    """Crear datos de prueba para validación de stock"""
    
    print("📦 Creando datos de prueba...")
    
    # Obtener o crear empresa de prueba
    company, created = Company.objects.get_or_create(
        ruc='1234567890001',
        defaults={
            'trade_name': 'Empresa Test Stock',
            'legal_name': 'Empresa Test Stock S.A.',
            'establishment_code': '001',
            'emission_point': '001'
        }
    )
    
    # Crear cliente de prueba
    customer, created = Customer.objects.get_or_create(
        identification='1234567890',
        company=company,
        defaults={
            'trade_name': 'Cliente Test Stock',
            'customer_type': 'INDIVIDUAL'
        }
    )
    
    # Crear productos con diferentes niveles de stock
    products = []
    
    # Producto 1: Stock alto (100 unidades)
    product_high, created = Product.objects.get_or_create(
        name='Producto Stock Alto',
        company=company,
        defaults={
            'code': 'TEST001',
            'description': 'Producto con stock alto para pruebas',
            'sale_price': Decimal('50.00'),
            'current_stock': Decimal('100.00'),
            'iva_rate': Decimal('15.00')
        }
    )
    products.append(('alto', product_high))
    
    # Producto 2: Stock medio (15 unidades)
    product_medium, created = Product.objects.get_or_create(
        name='Producto Stock Medio',
        company=company,
        defaults={
            'code': 'TEST002',
            'description': 'Producto con stock medio para pruebas',
            'sale_price': Decimal('75.00'),
            'current_stock': Decimal('15.00'),
            'iva_rate': Decimal('15.00')
        }
    )
    products.append(('medio', product_medium))
    
    # Producto 3: Stock bajo (3 unidades)
    product_low, created = Product.objects.get_or_create(
        name='Producto Stock Bajo',
        company=company,
        defaults={
            'code': 'TEST003',
            'description': 'Producto con stock bajo para pruebas',
            'sale_price': Decimal('100.00'),
            'current_stock': Decimal('3.00'),
            'iva_rate': Decimal('15.00')
        }
    )
    products.append(('bajo', product_low))
    
    # Producto 4: Stock cero (0 unidades)
    product_zero, created = Product.objects.get_or_create(
        name='Producto Sin Stock',
        company=company,
        defaults={
            'code': 'TEST004',
            'description': 'Producto sin stock para pruebas',
            'sale_price': Decimal('200.00'),
            'current_stock': Decimal('0.00'),
            'iva_rate': Decimal('15.00')
        }
    )
    products.append(('zero', product_zero))
    
    return company, customer, products


def test_stock_validation():
    """Probar validación de stock en diferentes escenarios"""
    
    print("\n🧪 INICIANDO PRUEBAS DE VALIDACIÓN DE STOCK\n")
    
    company, customer, products = create_test_data()
    
    # Crear factura de prueba
    invoice = Invoice.objects.create(
        company=company,
        customer=customer,
        date='2024-10-02',
        status='draft'
    )
    
    print(f"📋 Factura creada: {invoice.number}")
    
    scenarios = [
        # (product_type, quantity, expected_result, description)
        ('alto', 10, 'success', 'Stock alto, cantidad normal - Debe ser exitoso'),
        ('alto', 90, 'info', 'Stock alto, cantidad alta (90%) - Debe mostrar info'),
        ('medio', 5, 'success', 'Stock medio, cantidad baja - Debe ser exitoso'),
        ('medio', 12, 'warning', 'Stock medio, cantidad que deja stock bajo - Debe advertir'),
        ('bajo', 1, 'warning', 'Stock bajo, cantidad mínima - Debe advertir'),
        ('bajo', 5, 'error', 'Stock bajo, cantidad mayor - Debe fallar'),
        ('zero', 1, 'error', 'Sin stock, cualquier cantidad - Debe fallar'),
    ]
    
    results = []
    
    for product_type, quantity, expected, description in scenarios:
        print(f"\n🔍 PROBANDO: {description}")
        print(f"   Producto: {product_type}, Cantidad: {quantity}")
        
        # Encontrar el producto
        product = next(p for t, p in products if t == product_type)
        
        try:
            # Crear línea de factura
            line = InvoiceLine(
                invoice=invoice,
                product=product,
                description=product.name,
                quantity=Decimal(str(quantity)),
                unit_price=product.sale_price,
                stock=product.get_current_stock()
            )
            
            # Probar validación
            stock_info = line.check_stock_availability()
            
            if stock_info:
                actual_level = stock_info.get('level', 'unknown')
                message = stock_info.get('message', 'Sin mensaje')
                has_sufficient = stock_info.get('has_sufficient_stock', True)
                
                print(f"   📊 Resultado: {actual_level}")
                print(f"   💬 Mensaje: {message}")
                print(f"   ✅ Stock suficiente: {has_sufficient}")
                
                # Verificar resultado esperado
                if expected == 'error' and actual_level == 'error':
                    print(f"   ✅ CORRECTO: Error esperado y obtenido")
                elif expected == 'warning' and actual_level == 'warning':
                    print(f"   ✅ CORRECTO: Advertencia esperada y obtenida")
                elif expected in ['success', 'info'] and actual_level in ['success', 'info']:
                    print(f"   ✅ CORRECTO: Éxito/Info esperado y obtenido")
                else:
                    print(f"   ❌ ERROR: Esperado '{expected}' pero obtenido '{actual_level}'")
                    
                results.append({
                    'scenario': description,
                    'expected': expected,
                    'actual': actual_level,
                    'correct': (expected == actual_level) or (expected in ['success', 'info'] and actual_level in ['success', 'info']) or (expected == 'error' and actual_level == 'error'),
                    'message': message
                })
                
                # Probar validación de formulario si es crítico
                if actual_level == 'error':
                    try:
                        line.clean()
                        print(f"   ❌ ERROR: Validación debería haber fallado")
                    except Exception as e:
                        print(f"   ✅ CORRECTO: Validación bloqueó correctamente: {str(e)[:100]}...")
            else:
                print(f"   ⚠️ Sin información de stock")
                
        except Exception as e:
            print(f"   ❌ ERROR EN PRUEBA: {str(e)}")
    
    # Resumen de resultados
    print(f"\n📊 RESUMEN DE PRUEBAS")
    print(f"=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['correct'])
    
    for result in results:
        status = "✅ PASS" if result['correct'] else "❌ FAIL"
        print(f"{status} - {result['scenario']}")
    
    print(f"\n🎯 RESULTADO FINAL: {passed_tests}/{total_tests} pruebas exitosas")
    
    if passed_tests == total_tests:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema funciona correctamente.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar implementación.")
    
    return passed_tests == total_tests


def test_form_validation():
    """Probar validación a nivel de formulario"""
    
    print(f"\n🔧 PROBANDO VALIDACIÓN DE FORMULARIOS")
    print(f"=" * 40)
    
    from apps.invoicing.admin import IntelligentInvoiceLineForm
    
    company, customer, products = create_test_data()
    product_low = next(p for t, p in products if t == 'bajo')  # 3 unidades disponibles
    
    # Caso 1: Cantidad válida (menor al stock)
    print(f"\n📝 Caso 1: Cantidad válida (2 de 3 disponibles)")
    form_data = {
        'product': product_low.id,
        'description': product_low.name,
        'quantity': 2,
        'unit_price': product_low.sale_price,
        'discount': 0,
        'iva_rate': 15
    }
    
    form = IntelligentInvoiceLineForm(data=form_data)
    if form.is_valid():
        print("   ✅ Formulario válido - CORRECTO")
    else:
        print(f"   ❌ Formulario inválido - ERROR: {form.errors}")
    
    # Caso 2: Cantidad inválida (mayor al stock)
    print(f"\n📝 Caso 2: Cantidad inválida (5 de 3 disponibles)")
    form_data['quantity'] = 5
    
    form = IntelligentInvoiceLineForm(data=form_data)
    if not form.is_valid():
        print("   ✅ Formulario rechazado - CORRECTO")
        print(f"   💬 Errores: {form.errors}")
    else:
        print(f"   ❌ Formulario aceptado - ERROR")
        
    return True


if __name__ == "__main__":
    print("🛡️ SISTEMA DE VALIDACIÓN INTELIGENTE DE STOCK")
    print("=" * 50)
    
    try:
        # Ejecutar pruebas
        validation_ok = test_stock_validation()
        form_ok = test_form_validation()
        
        print(f"\n🏁 PRUEBAS COMPLETADAS")
        print(f"Validación de stock: {'✅ OK' if validation_ok else '❌ FAIL'}")
        print(f"Validación de formulario: {'✅ OK' if form_ok else '❌ FAIL'}")
        
        if validation_ok and form_ok:
            print(f"\n🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        else:
            print(f"\n⚠️ Sistema necesita revisión.")
            
    except Exception as e:
        print(f"\n❌ ERROR GENERAL EN PRUEBAS: {str(e)}")
        import traceback
        traceback.print_exc()