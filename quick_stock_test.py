#!/usr/bin/env python3

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import InvoiceLine
from apps.inventory.models import Product, Stock, Warehouse
from decimal import Decimal

def quick_test():
    product = Product.objects.first()
    if not product:
        print("No hay productos")
        return
    
    print(f"Producto: {product.name}")
    
    # Obtener o crear bodega
    warehouse = Warehouse.objects.first()
    if not warehouse:
        print("No hay bodegas disponibles")
        return
    
    # Eliminar stock existente y crear uno nuevo conocido
    Stock.objects.filter(product=product).delete()
    
    stock_obj = Stock.objects.create(
        product=product,
        warehouse=warehouse,
        quantity=Decimal('3')  # Solo 3 unidades
    )
    
    current_stock = product.get_current_stock()
    print(f"Stock establecido: {current_stock}")
    
    # Caso 1: Stock suficiente (2 de 5)
    line = InvoiceLine()
    line.product = product
    line.quantity = Decimal('2')
    
    stock_info = line.check_stock_availability()
    print(f"\nCaso 1 - Cantidad: 2, Stock: {current_stock}")
    if stock_info:
        print(f"Has sufficient: {stock_info.get('has_sufficient_stock')}")
        print(f"Level: {stock_info.get('level')}")
    
    # Caso 2: Stock crítico (4 de 5, queda 1)
    line.quantity = Decimal('4')
    
    stock_info = line.check_stock_availability()
    print(f"\nCaso 2 - Cantidad: 4, Stock: {current_stock} (queda 1)")
    if stock_info:
        print(f"Has sufficient: {stock_info.get('has_sufficient_stock')}")
        print(f"Level: {stock_info.get('level')}")
    
    # Caso 3: Stock insuficiente (10 de 5)
    line.quantity = Decimal('10')
    
    stock_info = line.check_stock_availability()
    print(f"\nCaso 3 - Cantidad: 10, Stock: {current_stock} (insuficiente)")
    if stock_info:
        print(f"Has sufficient: {stock_info.get('has_sufficient_stock')}")
        print(f"Level: {stock_info.get('level')}")
        print(f"Shortage: {stock_info.get('shortage')}")
        
    # Caso 4: Probar validación clean() con stock insuficiente
    print(f"\nCaso 4 - Probando validación clean() con stock insuficiente")
    try:
        line.clean()
        print("✅ Clean() pasó - ERROR no debería pasar")
    except Exception as e:
        print(f"❌ Clean() falló correctamente: {str(e)[:100]}")
    
    # Verificar lógica
    available = Decimal('5')
    requested = Decimal('8')
    print(f"Lógica manual: {available} >= {requested} = {available >= requested}")

if __name__ == "__main__":
    quick_test()