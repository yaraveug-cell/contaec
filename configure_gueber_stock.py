#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para agregar stock a los productos de la empresa GUEBER
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.inventory.models import Product, Stock
from apps.companies.models import Company


def add_stock_to_gueber_products():
    """Agrega stock variado a productos de GUEBER para pruebas"""
    print("🏢 Buscando empresa GUEBER...")
    
    # Buscar empresa GUEBER
    gueber = Company.objects.filter(trade_name__icontains='GUEBER').first()
    if not gueber:
        print("❌ No se encontró la empresa GUEBER")
        # Mostrar empresas disponibles
        companies = Company.objects.all()
        print("🏢 Empresas disponibles:")
        for company in companies:
            print(f"   - {company.trade_name} (RUC: {company.ruc})")
        return
    
    print(f"✅ Empresa encontrada: {gueber.trade_name} (RUC: {gueber.ruc})")
    
    # Buscar productos de GUEBER
    products = Product.objects.filter(company=gueber)
    if not products:
        print("❌ No hay productos en la empresa GUEBER")
        return
    
    print(f"📦 Encontrados {products.count()} productos de GUEBER")
    
    # Definir diferentes niveles de stock para probar todas las validaciones
    stock_levels = [
        {"min": 0, "max": 2, "description": "Sin stock / Stock crítico"},
        {"min": 3, "max": 9, "description": "Stock bajo (advertencia)"},
        {"min": 15, "max": 25, "description": "Stock medio (info alto consumo)"},
        {"min": 50, "max": 100, "description": "Stock alto (éxito)"},
    ]
    
    updated_count = 0
    
    for i, product in enumerate(products):
        # Rotar entre diferentes niveles de stock
        level = stock_levels[i % len(stock_levels)]
        
        # Calcular stock específico basado en el índice
        if i % 4 == 0:  # Sin stock
            new_quantity = Decimal('0')
        elif i % 4 == 1:  # Stock bajo
            new_quantity = Decimal('5')
        elif i % 4 == 2:  # Stock medio
            new_quantity = Decimal('20')
        else:  # Stock alto
            new_quantity = Decimal('75')
        
        # Crear o actualizar stock
        stock, created = Stock.objects.get_or_create(
            product=product,
            defaults={'quantity': new_quantity}
        )
        
        if not created:
            stock.quantity = new_quantity
            stock.save()
        
        print(f"   📊 {product.name[:40]:40} → Stock: {new_quantity:6}")
        updated_count += 1
    
    print(f"\n✅ Stock actualizado para {updated_count} productos de GUEBER")
    
    # Mostrar resumen por niveles
    print("\n📈 RESUMEN DE STOCK CONFIGURADO:")
    print("   🔴 Stock 0:     Para probar ERROR (sin stock)")
    print("   🟡 Stock 5:     Para probar WARNING (stock bajo)")
    print("   🔵 Stock 20:    Para probar INFO (alto consumo)")
    print("   🟢 Stock 75:    Para probar SUCCESS (stock suficiente)")
    
    return updated_count


def show_test_instructions():
    """Muestra instrucciones para probar el sistema"""
    print("\n" + "🧪 INSTRUCCIONES PARA PROBAR NOTIFICACIONES")
    print("=" * 50)
    print("1. Ve al admin: http://127.0.0.1:8000/admin/")
    print("2. Selecciona empresa GUEBER en el filtro")
    print("3. Crea nueva factura: Invoicing → Invoices → Add")
    print("4. En líneas de factura, prueba diferentes cantidades:")
    print("   • Productos con stock 0  → Cantidad 1   = 🔴 ERROR")
    print("   • Productos con stock 5  → Cantidad 6   = 🔴 ERROR")
    print("   • Productos con stock 5  → Cantidad 4   = 🟡 WARNING")
    print("   • Productos con stock 20 → Cantidad 12  = 🔵 INFO")
    print("   • Productos con stock 75 → Cantidad 10  = 🟢 SUCCESS")
    print("\n5. Observa notificaciones flotantes en esquina superior derecha")
    print("6. Las notificaciones duran 6 segundos y desaparecen")
    print("7. Demo completo: F12 → Console → stockValidator.demo()")
    print("=" * 50)


if __name__ == "__main__":
    print("🚀 CONFIGURANDO STOCK PARA PRUEBAS DE NOTIFICACIONES")
    print("=" * 55)
    
    try:
        updated_count = add_stock_to_gueber_products()
        
        if updated_count > 0:
            show_test_instructions()
            print(f"\n🎯 ¡Listo! {updated_count} productos configurados para pruebas")
        else:
            print("\n❌ No se pudo configurar el stock")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()