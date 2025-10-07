#!/usr/bin/env python
"""
Script para migrar productos de facturación a inventario antes de eliminar el modelo
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append('.')
django.setup()

from decimal import Decimal
from django.db import transaction
from apps.companies.models import Company


def migrate_products():
    """Migrar productos de facturación a inventario"""
    print("🔄 MIGRANDO PRODUCTOS DE FACTURACIÓN A INVENTARIO")
    
    try:
        from apps.invoicing.models import Product as InvoicingProduct
        from apps.inventory.models import Product as InventoryProduct, Category
        
        invoicing_products = InvoicingProduct.objects.all()
        
        if not invoicing_products.exists():
            print("ℹ️  No hay productos de facturación para migrar")
            return
        
        print(f"📦 Encontrados {invoicing_products.count()} productos de facturación")
        
        migrated_count = 0
        skipped_count = 0
        
        with transaction.atomic():
            for inv_product in invoicing_products:
                company = inv_product.company
                
                # Crear categoría por defecto si no existe
                default_category, created = Category.objects.get_or_create(
                    company=company,
                    name='Productos Migrados',
                    defaults={
                        'description': 'Productos migrados desde facturación'
                    }
                )
                
                if created:
                    print(f"  📁 Creada categoría 'Productos Migrados' para {company.trade_name}")
                
                # Verificar si ya existe en inventario
                existing = InventoryProduct.objects.filter(
                    company=company,
                    code=inv_product.code
                ).first()
                
                if existing:
                    print(f"  ⚠️  Producto {inv_product.code} ya existe en inventario - Omitido")
                    skipped_count += 1
                    continue
                
                # Crear producto en inventario
                new_product = InventoryProduct.objects.create(
                    company=company,
                    category=default_category,
                    code=inv_product.code,
                    name=inv_product.name,
                    description=inv_product.description or '',
                    product_type=inv_product.product_type,
                    unit_of_measure='UND',
                    manages_inventory=inv_product.product_type == 'product',
                    minimum_stock=Decimal('0.00'),
                    maximum_stock=Decimal('0.00'),
                    cost_price=inv_product.cost_price,
                    sale_price=inv_product.sale_price,
                    has_iva=inv_product.has_iva,
                    iva_rate=inv_product.iva_rate,
                    is_active=True
                )
                
                print(f"  ✅ Migrado: {inv_product.code} - {inv_product.name}")
                migrated_count += 1
        
        print(f"📊 Productos migrados: {migrated_count}")
        print(f"📊 Productos omitidos: {skipped_count}")
        print("✅ MIGRACIÓN COMPLETADA")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        raise


if __name__ == '__main__':
    migrate_products()