#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script para el sistema de notificaciones flotantes inteligentes
Ejecutar desde Django shell para probar todos los niveles de validación
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.invoicing.models import Invoice, InvoiceLine, Customer
from apps.inventory.models import Product, Stock
from apps.companies.models import Company
from apps.users.models import User


def setup_test_data():
    """Configura datos de prueba para las notificaciones"""
    print("🔧 Configurando datos de prueba...")
    
    # Obtener o crear empresa
    company = Company.objects.first()
    if not company:
        company = Company.objects.create(
            name="Test Company",
            ruc="1234567890001",
            email="test@test.com"
        )
    
    # Obtener o crear usuario
    user = User.objects.first()
    if not user:
        user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
    
    # Obtener o crear cliente
    customer = Customer.objects.first()
    if not customer:
        customer = Customer.objects.create(
            name="Cliente Test",
            identification="0123456789"
        )
    
    # Crear productos con diferentes niveles de stock
    productos = [
        {"name": "Producto SIN STOCK", "price": "10.00", "stock": "0.00"},
        {"name": "Producto STOCK BAJO", "price": "15.00", "stock": "5.00"},
        {"name": "Producto STOCK MEDIO", "price": "20.00", "stock": "25.00"},
        {"name": "Producto STOCK ALTO", "price": "25.00", "stock": "100.00"},
    ]
    
    created_products = []
    for prod_data in productos:
        # Crear o actualizar producto
        product, created = Product.objects.get_or_create(
            name=prod_data["name"],
            defaults={
                "price": Decimal(prod_data["price"]),
                "company": company
            }
        )
        if not created:
            product.price = Decimal(prod_data["price"])
            product.save()
        
        # Crear o actualizar stock
        stock, stock_created = Stock.objects.get_or_create(
            product=product,
            defaults={"quantity": Decimal(prod_data["stock"])}
        )
        if not stock_created:
            stock.quantity = Decimal(prod_data["stock"])
            stock.save()
        
        created_products.append(product)
    
    print(f"✅ Configuración completa:")
    for product in created_products:
        stock = Stock.objects.filter(product=product).first()
        stock_qty = stock.quantity if stock else Decimal('0')
        print(f"   📦 {product.name}: Stock {stock_qty}")
    
    return company, user, customer, created_products


def test_validation_levels():
    """Prueba todos los niveles de validación"""
    print("\n🧪 Probando niveles de validación...")
    
    company, user, customer, products = setup_test_data()
    
    # Crear factura
    invoice = Invoice.objects.create(
        customer=customer,
        company=company,
        created_by=user
    )
    
    print(f"\n📄 Factura #{invoice.invoice_number} creada")
    
    # Probar cada nivel de validación
    test_cases = [
        {"product": products[0], "quantity": "1.00", "expected": "ERROR - Sin stock"},
        {"product": products[1], "quantity": "6.00", "expected": "ERROR - Supera stock"},
        {"product": products[1], "quantity": "4.00", "expected": "WARNING - Stock bajo"},
        {"product": products[2], "quantity": "15.00", "expected": "INFO - Alto consumo"},
        {"product": products[3], "quantity": "10.00", "expected": "SUCCESS - Stock suficiente"},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['expected']} ---")
        
        # Crear línea de factura
        line = InvoiceLine(
            invoice=invoice,
            product=test_case['product'],
            quantity=Decimal(test_case['quantity']),
            unit_price=test_case['product'].price
        )
        
        # Obtener stock disponible
        stock = Stock.objects.filter(product=test_case['product']).first()
        available_stock = stock.quantity if stock else Decimal('0')
        
        # Probar validación
        validation_result = line.check_stock_availability()
        
        print(f"   📦 Producto: {test_case['product'].name}")
        print(f"   📊 Stock disponible: {available_stock}")
        print(f"   🛒 Cantidad solicitada: {test_case['quantity']}")
        print(f"   🔍 Resultado: {validation_result['level'].upper()} - {validation_result['message']}")
        
        # Probar si se puede guardar
        try:
            line.clean()
            can_save = True
            print(f"   💾 ¿Se puede guardar? ✅ SÍ")
        except Exception as e:
            can_save = False
            print(f"   💾 ¿Se puede guardar? ❌ NO - {str(e)}")
    
    print("\n" + "="*60)
    print("🎯 RESUMEN DE PRUEBAS COMPLETADO")
    print("="*60)
    
    return invoice


def show_browser_demo_instructions():
    """Muestra instrucciones para probar en el navegador"""
    print("\n" + "🌐 INSTRUCCIONES PARA PROBAR EN NAVEGADOR")
    print("="*50)
    print("1. Abre el admin de Django en tu navegador")
    print("2. Ve a 'Invoices' y crea una nueva factura")
    print("3. Añade líneas con diferentes productos")
    print("4. Observa las notificaciones flotantes en la esquina superior derecha")
    print("5. Para demo completo, abre consola del navegador (F12) y ejecuta:")
    print("   stockValidator.demo()")
    print("\n🎨 Las notificaciones aparecerán con:")
    print("   🔴 ERROR: Fondo rojo - Bloquea guardado")
    print("   🟡 WARNING: Fondo amarillo - Permite guardar con advertencia")
    print("   🔵 INFO: Fondo azul - Información sobre alto consumo")
    print("   🟢 SUCCESS: Fondo verde - Todo correcto")
    print("\n⏰ Todas las notificaciones desaparecen automáticamente en 6 segundos")
    print("="*50)


if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE NOTIFICACIONES FLOTANTES")
    print("="*60)
    
    try:
        # Ejecutar pruebas
        invoice = test_validation_levels()
        
        # Mostrar instrucciones para navegador
        show_browser_demo_instructions()
        
        print(f"\n✅ ¡Todas las pruebas completadas exitosamente!")
        print(f"📄 Factura de prueba creada: #{invoice.invoice_number}")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()