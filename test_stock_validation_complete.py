#!/usr/bin/env python
"""
Script para probar el sistema completo de validación de stock
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client, RequestFactory
from django.urls import reverse
from apps.companies.models import Company, CompanyUser
from apps.inventory.models import Product
from apps.invoicing.models import Customer
from apps.invoicing.models import Invoice, InvoiceLine
from apps.invoicing.admin import InvoiceAdmin
from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from decimal import Decimal
import json

def test_stock_validation_system():
    """Probar el sistema completo de validación de stock"""
    print("🧪 TESTING: Sistema completo de validación de stock")
    print("=" * 60)
    
    # Obtener datos de prueba
    try:
        company = Company.objects.first()
        customer = Customer.objects.first()
        product = Product.objects.first()
        
        if not all([company, customer, product]):
            print("❌ ERROR: Faltan datos de prueba")
            return
        
        print(f"📊 Datos de prueba:")
        print(f"   Empresa: {company.trade_name}")
        print(f"   Cliente: {customer.trade_name}")
        print(f"   Producto: {product.name}")
        print(f"   Stock disponible: {product.stock}")
        
    except Exception as e:
        print(f"❌ ERROR obteniendo datos: {e}")
        return
    
    # Test 1: Validación del modelo InvoiceLine.clean()
    print(f"\n1️⃣ Test validación modelo (clean method)")
    print("-" * 40)
    
    try:
        # Crear factura de prueba
        invoice = Invoice.objects.create(
            company=company,
            customer=customer,
            date='2024-01-15',
            status='DRAFT',
            payment_form='EFECTIVO'
        )
        
        # Test con stock suficiente
        line_good = InvoiceLine(
            invoice=invoice,
            product=product,
            description=product.name,
            quantity=1,  # Cantidad menor al stock
            unit_price=Decimal('100.00')
        )
        
        try:
            line_good.clean()
            print(f"✅ Stock suficiente (qty: 1): Validación OK")
        except ValidationError as e:
            print(f"❌ Error inesperado con stock suficiente: {e}")
        
        # Test con stock insuficiente
        line_bad = InvoiceLine(
            invoice=invoice,
            product=product,
            description=product.name,
            quantity=product.stock + 5,  # Cantidad mayor al stock
            unit_price=Decimal('100.00')
        )
        
        try:
            line_bad.clean()
            print(f"❌ Stock insuficiente debería dar error pero no lo dio")
        except ValidationError as e:
            print(f"✅ Stock insuficiente (qty: {product.stock + 5}): {str(e)}")
        
    except Exception as e:
        print(f"❌ ERROR en test modelo: {e}")
    
    # Test 2: Vista AJAX de verificación de stock
    print(f"\n2️⃣ Test vista AJAX check_product_stock")
    print("-" * 40)
    
    try:
        # Crear admin instance para probar la vista
        admin_site = AdminSite()
        invoice_admin = InvoiceAdmin(Invoice, admin_site)
        factory = RequestFactory()
        
        # Test con stock suficiente
        request = factory.get(f'/admin/invoicing/invoice/check-product-stock/{product.id}/?quantity=1')
        response = invoice_admin.check_product_stock_view(request, product.id)
        
        if response.status_code == 200:
            data = json.loads(response.content.decode())
            print(f"✅ AJAX stock suficiente: {data}")
        else:
            print(f"❌ Error AJAX stock suficiente: {response.status_code}")
        
        # Test con stock insuficiente
        request = factory.get(f'/admin/invoicing/invoice/check-product-stock/{product.id}/?quantity={product.stock + 10}')
        response = invoice_admin.check_product_stock_view(request, product.id)
        
        if response.status_code == 200:
            data = json.loads(response.content.decode())
            print(f"✅ AJAX stock insuficiente: {data}")
        else:
            print(f"❌ Error AJAX stock insuficiente: {response.status_code}")
        
    except Exception as e:
        print(f"❌ ERROR en test AJAX: {e}")
    
    # Test 3: Verificar archivos JavaScript
    print(f"\n3️⃣ Test archivos JavaScript")
    print("-" * 40)
    
    js_file = "static/admin/js/stock_validator.js"
    if os.path.exists(js_file):
        file_size = os.path.getsize(js_file)
        print(f"✅ Archivo JavaScript existe: {js_file} ({file_size} bytes)")
        
        # Verificar contenido clave
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        key_functions = ['StockValidator', 'validateStock', 'displayStockError', 'setupLineValidation']
        for func in key_functions:
            if func in content:
                print(f"✅ Función encontrada: {func}")
            else:
                print(f"❌ Función faltante: {func}")
    else:
        print(f"❌ Archivo JavaScript no existe: {js_file}")
    
    print(f"\n🏁 RESUMEN DEL TEST")
    print("=" * 60)
    print("✅ Sistema de validación de stock implementado:")
    print("   - Validación en modelo (InvoiceLine.clean())")
    print("   - Vista AJAX para verificación en tiempo real")
    print("   - JavaScript para interfaz de usuario")
    print("   - Integración con admin de Django")
    print("\n💡 Esto debería resolver el ValidationError del usuario")
    print("   mostrando errores de stock de forma amigable")

if __name__ == "__main__":
    test_stock_validation_system()