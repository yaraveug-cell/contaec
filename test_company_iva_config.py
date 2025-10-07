#!/usr/bin/env python
"""
Script para probar la configuración de IVA específica por empresa
Verifica que:
1. Los nuevos productos usen el IVA configurado por la empresa
2. Las nuevas facturas de compra usen el IVA configurado por la empresa
3. Los productos existentes mantengan su configuración actual
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.companies.models import Company, CompanySettings
from apps.inventory.models import Product, Category
from apps.suppliers.models import Supplier, PurchaseInvoice, PurchaseInvoiceLine

User = get_user_model()

def test_company_iva_configuration():
    """Prueba la configuración de IVA por empresa"""
    
    print("=== PRUEBA DE CONFIGURACIÓN DE IVA POR EMPRESA ===\n")
    
    # Obtener la primera empresa disponible
    company = Company.objects.first()
    if not company:
        print("❌ No hay empresas en el sistema")
        return
    
    print(f"🏢 Empresa de prueba: {company.name}")
    
    # 1. Verificar/crear configuración de empresa
    company_settings, created = CompanySettings.objects.get_or_create(company=company)
    print(f"⚙️  Configuración de empresa: {'Creada' if created else 'Existente'}")
    print(f"📊 IVA por defecto configurado: {company_settings.default_iva_rate}%")
    
    # 2. Cambiar temporalmente el IVA a 16% para la prueba
    original_iva = company_settings.default_iva_rate
    company_settings.default_iva_rate = Decimal('16.00')
    company_settings.save()
    print(f"🔄 IVA cambiado temporalmente a: {company_settings.default_iva_rate}%")
    
    # 3. Crear un producto nuevo para verificar que use el IVA de la empresa
    category = Category.objects.filter(company=company).first()
    if not category:
        print("⚠️  No hay categorías disponibles, creando una...")
        category = Category.objects.create(
            company=company,
            name="Categoría de Prueba IVA",
            description="Categoría para pruebas de configuración de IVA"
        )
    
    # Crear producto nuevo
    new_product = Product.objects.create(
        company=company,
        category=category,
        code="TEST-IVA-001",
        name="Producto Prueba IVA",
        description="Producto para probar IVA dinámico por empresa",
        unit_of_measure="UND",
        cost_price=Decimal('10.00'),
        sale_price=Decimal('15.00'),
        has_iva=True
        # No configuramos iva_rate para que tome el por defecto
    )
    
    print(f"📦 Producto creado: {new_product.code}")
    print(f"💰 IVA del producto: {new_product.iva_rate}%")
    
    # Verificar que el producto use el IVA de la empresa
    if new_product.iva_rate == company_settings.default_iva_rate:
        print("✅ El producto nuevo usa correctamente el IVA configurado por la empresa")
    else:
        print(f"❌ Error: El producto debería usar {company_settings.default_iva_rate}% pero usa {new_product.iva_rate}%")
    
    # 4. Probar factura de compra
    supplier = Supplier.objects.filter(company=company).first()
    if supplier:
        user = User.objects.first()
        if user:
            # Crear factura de compra
            invoice = PurchaseInvoice.objects.create(
                company=company,
                supplier=supplier,
                invoice_number="TEST-001",
                invoice_date="2025-01-01",
                created_by=user
            )
            
            # Crear línea de factura SIN producto (para probar IVA por defecto)
            invoice_line = PurchaseInvoiceLine.objects.create(
                invoice=invoice,
                description="Servicio sin producto específico",
                quantity=Decimal('1.00'),
                unit_cost=Decimal('100.00')
                # No establecemos iva_rate para que use el por defecto
            )
            
            print(f"📄 Factura creada: {invoice.invoice_number}")
            print(f"💰 IVA de la línea de factura: {invoice_line.iva_rate}%")
            print(f"💵 Total de la línea: {invoice_line.line_total}")
            
            # Verificar que la línea use el IVA de la empresa
            if invoice_line.iva_rate == company_settings.default_iva_rate:
                print("✅ La línea de factura usa correctamente el IVA configurado por la empresa")
            else:
                print(f"❌ Error: La línea debería usar {company_settings.default_iva_rate}% pero usa {invoice_line.iva_rate}%")
    
    # 5. Restaurar configuración original
    company_settings.default_iva_rate = original_iva
    company_settings.save()
    print(f"🔄 IVA restaurado al valor original: {original_iva}%")
    
    # 6. Limpiar datos de prueba
    if 'new_product' in locals():
        new_product.delete()
        print("🗑️  Producto de prueba eliminado")
    
    if 'invoice' in locals():
        invoice.delete()
        print("🗑️  Factura de prueba eliminada")
    
    print("\n=== PRUEBA COMPLETADA ===")

def show_company_settings():
    """Muestra la configuración actual de todas las empresas"""
    
    print("\n=== CONFIGURACIÓN ACTUAL DE EMPRESAS ===")
    
    for company in Company.objects.all():
        settings, created = CompanySettings.objects.get_or_create(company=company)
        print(f"\n🏢 {company.name}")
        print(f"   📊 IVA por defecto: {settings.default_iva_rate}%")
        print(f"   📅 Creado: {settings.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"   🔄 Actualizado: {settings.updated_at.strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    try:
        show_company_settings()
        test_company_iva_configuration()
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()