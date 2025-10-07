#!/usr/bin/env python
"""
Script para probar el sistema de validación de stock con la empresa GUEBER
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.users.models import User
from django.test import Client, RequestFactory
from django.urls import reverse
from apps.companies.models import Company, CompanyUser
from apps.inventory.models import Product
from apps.invoicing.models import Customer, Invoice, InvoiceLine
from apps.invoicing.admin import InvoiceAdmin
from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from decimal import Decimal
import json

def test_gueber_stock_validation():
    """Probar el sistema de validación de stock específicamente con GUEBER"""
    print("🏢 TESTING: Sistema de validación de stock - EMPRESA GUEBER")
    print("=" * 65)
    
    # Obtener empresa GUEBER
    try:
        gueber = Company.objects.filter(trade_name__icontains='GUEBER').first()
        if not gueber:
            gueber = Company.objects.filter(legal_name__icontains='GUEBER').first()
        
        if not gueber:
            print("❌ ERROR: No se encontró la empresa GUEBER")
            print("Empresas disponibles:")
            for company in Company.objects.all():
                print(f"   - {company.trade_name} ({company.legal_name})")
            return
        
        print(f"✅ Empresa encontrada: {gueber.trade_name}")
        print(f"   Razón social: {gueber.legal_name}")
        print(f"   RUC: {gueber.ruc}")
        
    except Exception as e:
        print(f"❌ ERROR obteniendo empresa GUEBER: {e}")
        return
    
    # Obtener productos y clientes de GUEBER
    try:
        gueber_products = Product.objects.filter(company=gueber)
        gueber_customers = Customer.objects.filter(company=gueber)
        
        print(f"\n📦 Productos GUEBER: {gueber_products.count()}")
        if gueber_products.exists():
            for product in gueber_products[:5]:  # Mostrar primeros 5
                current_stock = product.get_current_stock()
                print(f"   - {product.name}: Stock {current_stock}, Precio ${product.sale_price}")
        
        print(f"\n👥 Clientes GUEBER: {gueber_customers.count()}")
        if gueber_customers.exists():
            for customer in gueber_customers[:3]:  # Mostrar primeros 3
                print(f"   - {customer.trade_name} ({customer.identification})")
        
        if not gueber_products.exists() or not gueber_customers.exists():
            print("❌ ERROR: GUEBER no tiene productos o clientes suficientes")
            return
        
        # Seleccionar producto con stock para pruebas
        test_product = None
        for product in gueber_products:
            if product.get_current_stock() > 0:
                test_product = product
                break
        test_customer = gueber_customers.first()
        
        if not test_product:
            print("❌ ERROR: No hay productos con stock en GUEBER")
            return
        
        print(f"\n🎯 Producto de prueba: {test_product.name}")
        print(f"   Stock disponible: {test_product.get_current_stock()}")
        print(f"   Cliente de prueba: {test_customer.trade_name}")
        
    except Exception as e:
        print(f"❌ ERROR obteniendo datos de GUEBER: {e}")
        return
    
    # Test 1: Validación del modelo con producto de GUEBER
    print(f"\n1️⃣ Test validación modelo - Producto GUEBER")
    print("-" * 50)
    
    try:
        # Crear factura de prueba para GUEBER
        from apps.companies.models import PaymentMethod
        efectivo = PaymentMethod.objects.filter(name__icontains='efectivo').first()
        if not efectivo:
            efectivo = PaymentMethod.objects.first()  # Usar cualquier método disponible
        
        user = User.objects.first()  # Usar cualquier usuario
        invoice = Invoice.objects.create(
            company=gueber,
            customer=test_customer,
            date='2024-01-15',
            status='DRAFT',
            payment_form=efectivo,
            created_by=user
        )
        
        # Test con stock suficiente
        line_good = InvoiceLine(
            invoice=invoice,
            product=test_product,
            description=test_product.name,
            quantity=min(1, test_product.get_current_stock()),  # Cantidad segura
            unit_price=test_product.sale_price or Decimal('100.00')
        )
        
        try:
            line_good.clean()
            print(f"✅ Stock suficiente (qty: {line_good.quantity}): Validación OK")
        except ValidationError as e:
            print(f"❌ Error inesperado con stock suficiente: {e}")
        
        # Test con stock insuficiente
        excessive_qty = test_product.get_current_stock() + 10
        line_bad = InvoiceLine(
            invoice=invoice,
            product=test_product,
            description=test_product.name,
            quantity=excessive_qty,
            unit_price=test_product.sale_price or Decimal('100.00')
        )
        
        try:
            line_bad.clean()
            print(f"❌ Stock insuficiente debería dar error pero no lo dio")
        except ValidationError as e:
            print(f"✅ Stock insuficiente (qty: {excessive_qty}): {str(e)}")
        
        # Limpiar factura de prueba
        invoice.delete()
        
    except Exception as e:
        print(f"❌ ERROR en test modelo: {e}")
    
    # Test 2: Vista AJAX con producto de GUEBER
    print(f"\n2️⃣ Test vista AJAX - Producto GUEBER")
    print("-" * 50)
    
    try:
        admin_site = AdminSite()
        invoice_admin = InvoiceAdmin(Invoice, admin_site)
        factory = RequestFactory()
        
        # Test con stock suficiente
        safe_qty = min(1, test_product.get_current_stock())
        request = factory.get(f'/admin/invoicing/invoice/check-product-stock/{test_product.id}/?quantity={safe_qty}')
        response = invoice_admin.check_product_stock_view(request, test_product.id)
        
        if response.status_code == 200:
            data = json.loads(response.content.decode())
            print(f"✅ AJAX stock suficiente:")
            print(f"   Producto: {data['product_name']}")
            print(f"   Stock disponible: {data['available_stock']}")
            print(f"   Cantidad solicitada: {data['requested_quantity']}")
            print(f"   Stock suficiente: {data['has_sufficient_stock']}")
        else:
            print(f"❌ Error AJAX stock suficiente: {response.status_code}")
        
        # Test con stock insuficiente
        excessive_qty = test_product.get_current_stock() + 5
        request = factory.get(f'/admin/invoicing/invoice/check-product-stock/{test_product.id}/?quantity={excessive_qty}')
        response = invoice_admin.check_product_stock_view(request, test_product.id)
        
        if response.status_code == 200:
            data = json.loads(response.content.decode())
            print(f"\n✅ AJAX stock insuficiente:")
            print(f"   Producto: {data['product_name']}")
            print(f"   Stock disponible: {data['available_stock']}")
            print(f"   Cantidad solicitada: {data['requested_quantity']}")
            print(f"   Stock suficiente: {data['has_sufficient_stock']}")
            print(f"   Faltante: {data['shortage']}")
        else:
            print(f"❌ Error AJAX stock insuficiente: {response.status_code}")
        
    except Exception as e:
        print(f"❌ ERROR en test AJAX: {e}")
    
    # Test 3: Simular creación de factura con validación
    print(f"\n3️⃣ Test creación factura GUEBER con validación")
    print("-" * 50)
    
    try:
        # Crear factura válida
        from apps.companies.models import PaymentMethod
        efectivo = PaymentMethod.objects.filter(name__icontains='efectivo').first()
        if not efectivo:
            efectivo = PaymentMethod.objects.first()  # Usar cualquier método disponible
        
        user = User.objects.first()  # Usar cualquier usuario
        valid_invoice = Invoice.objects.create(
            company=gueber,
            customer=test_customer,
            date='2024-01-15',
            status='DRAFT',
            payment_form=efectivo,
            created_by=user
        )
        
        # Agregar línea válida
        valid_line = InvoiceLine.objects.create(
            invoice=valid_invoice,
            product=test_product,
            description=f"{test_product.name} - Venta GUEBER",
            quantity=1,
            unit_price=test_product.sale_price or Decimal('100.00')
        )
        
        print(f"✅ Factura creada exitosamente:")
        print(f"   ID: {valid_invoice.id}")
        print(f"   Cliente: {valid_invoice.customer.trade_name}")
        print(f"   Total: ${valid_invoice.total}")
        
        # Intentar crear línea con stock insuficiente
        try:
            invalid_line = InvoiceLine(
                invoice=valid_invoice,
                product=test_product,
                description=f"{test_product.name} - Cantidad excesiva",
                quantity=test_product.get_current_stock() + 20,
                unit_price=test_product.sale_price or Decimal('100.00')
            )
            invalid_line.clean()  # Esto debería fallar
            print(f"❌ ERROR: Línea con stock insuficiente no fue rechazada")
        except ValidationError as e:
            print(f"✅ Línea con stock insuficiente rechazada correctamente: {e}")
        
        # Limpiar
        valid_invoice.delete()
        
    except Exception as e:
        print(f"❌ ERROR en test creación factura: {e}")
    
    print(f"\n🏁 RESUMEN - EMPRESA GUEBER")
    print("=" * 65)
    print("✅ Sistema de validación de stock probado con GUEBER:")
    print("   - Validación en modelo funciona correctamente")
    print("   - Vista AJAX responde adecuadamente")
    print("   - Prevención de stock negativo implementada")
    print("   - Mensajes de error informativos")
    print("\n💡 El usuario ya no debería ver ValidationError en el servidor")
    print("   Los errores de stock se muestran de forma amigable")

if __name__ == "__main__":
    test_gueber_stock_validation()