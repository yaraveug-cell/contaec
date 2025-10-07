#!/usr/bin/env python
"""
Verificar stock de productos GUEBER
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append('c:\\contaec')
django.setup()

from apps.companies.models import Company
from apps.inventory.models import Product

def check_gueber_stock():
    """Verificar stock disponible de productos GUEBER"""
    try:
        company = Company.objects.get(trade_name="GUEBER")
        print(f"🏢 Empresa: {company.trade_name}")
        
        products = Product.objects.filter(
            company=company,
            manages_inventory=True
        )
        
        print(f"\n📦 PRODUCTOS CON INVENTARIO: {products.count()}")
        
        available_products = []
        
        for product in products:
            current_stock = product.get_current_stock()
            print(f"\n   Código: {product.code}")
            print(f"   Nombre: {product.name}")
            print(f"   Precio Costo: ${product.cost_price}")
            print(f"   Precio Venta: ${product.sale_price}")
            print(f"   Stock Actual: {current_stock}")
            print(f"   Stock Mínimo: {product.minimum_stock}")
            print(f"   Maneja Inventario: {product.manages_inventory}")
            
            if current_stock > 0:
                available_products.append(product)
        
        # Convertir a QuerySet simulado para mantener compatibilidad
        
        print(f"\n✅ PRODUCTOS CON STOCK DISPONIBLE: {len(available_products)}")
        for product in available_products:
            print(f"   {product.code}: Stock = {product.get_current_stock()}")
        
        if not available_products:
            print(f"\n⚠️ NINGÚN PRODUCTO TIENE STOCK DISPONIBLE")
            print(f"Recomendación: Agregar stock a los productos o deshabilitar validación")
        
        return available_products
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    check_gueber_stock()