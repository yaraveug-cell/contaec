"""
Script para verificar productos disponibles
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.products.models import Product
from apps.companies.models import Company

def check_products():
    """Verificar productos disponibles"""
    
    print("🔍 Verificando productos en el sistema...")
    
    company = Company.objects.filter(legal_name="Yolanda Bermeo").first()
    if not company:
        print("❌ No se encontró la empresa")
        return
        
    products = Product.objects.filter(company=company)
    print(f"📦 Productos encontrados: {products.count()}")
    
    if products.exists():
        print(f"   🏷️ Algunos productos:")
        for product in products[:5]:
            print(f"      ID:{product.id} - {product.name} - ${product.price}")
    else:
        print(f"   ⚠️ No hay productos para esta empresa")

if __name__ == "__main__":
    check_products()