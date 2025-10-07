#!/usr/bin/env python

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from decimal import Decimal
from apps.companies.models import Company, CompanySettings
from apps.inventory.models import Product, Category

def test_product_iva():
    """Probar que los nuevos productos usen el IVA de la empresa"""
    
    print("=== PRUEBA DE IVA EN PRODUCTOS ===")
    
    # Tomar la primera empresa
    company = Company.objects.first()
    if not company:
        print("No hay empresas")
        return
    
    print(f"Empresa: {company.trade_name}")
    
    # Verificar configuracion de IVA
    settings, _ = CompanySettings.objects.get_or_create(company=company)
    print(f"IVA configurado: {settings.default_iva_rate}%")
    
    # Cambiar temporalmente a 18% para la prueba
    original_iva = settings.default_iva_rate
    settings.default_iva_rate = Decimal('18.00')
    settings.save()
    print(f"IVA cambiado temporalmente a: {settings.default_iva_rate}%")
    
    # Obtener o crear categoria
    category = Category.objects.filter(company=company).first()
    if not category:
        category = Category.objects.create(
            company=company,
            name="Test Category",
            description="Categoria de prueba"
        )
    
    # Crear producto nuevo
    test_product = Product.objects.create(
        company=company,
        category=category,
        code="TEST-IVA-001",
        name="Producto Test IVA",
        description="Prueba de IVA dinamico",
        unit_of_measure="UN",
        cost_price=Decimal('10.00'),
        sale_price=Decimal('15.00'),
        has_iva=True
    )
    
    print(f"Producto creado: {test_product.code}")
    print(f"IVA del producto: {test_product.iva_rate}%")
    
    # Verificar resultado
    if test_product.iva_rate == settings.default_iva_rate:
        print("SUCCESS: El producto usa el IVA de la empresa")
    else:
        print(f"ERROR: Esperado {settings.default_iva_rate}%, obtenido {test_product.iva_rate}%")
    
    # Restaurar y limpiar
    settings.default_iva_rate = original_iva
    settings.save()
    test_product.delete()
    
    print(f"IVA restaurado a: {original_iva}%")
    print("Producto de prueba eliminado")
    print("=== PRUEBA COMPLETADA ===")

if __name__ == "__main__":
    test_product_iva()