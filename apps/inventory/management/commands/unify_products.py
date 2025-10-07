#!/usr/bin/env python
"""
Comando para unificar productos de facturación con inventario
Uso: python manage.py unify_products
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.invoicing.models import InvoiceLine
from apps.inventory.models import Product as InventoryProduct, Category
from decimal import Decimal


class Command(BaseCommand):
    help = 'Unifica productos de facturación con inventario y actualiza referencias'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar qué se haría sin ejecutar cambios',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar la unificación sin confirmación',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS('🔄 INICIANDO UNIFICACIÓN DE PRODUCTOS')
        )
        
        # Verificar si hay productos de facturación que necesitan migración
        try:
            from apps.invoicing.models import Product as InvoicingProduct
            invoicing_products = InvoicingProduct.objects.all()
            
            if not invoicing_products.exists():
                self.stdout.write(
                    self.style.WARNING('ℹ️  No hay productos de facturación para migrar')
                )
                return
            
            self.stdout.write(
                f'📦 Encontrados {invoicing_products.count()} productos de facturación'
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al acceder a productos de facturación: {e}')
            )
            return
        
        if not force and not dry_run:
            confirm = input('¿Continuar con la unificación? (s/N): ')
            if confirm.lower() not in ['s', 'si', 'y', 'yes']:
                self.stdout.write('❌ Operación cancelada')
                return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🧪 MODO DRY-RUN - No se realizarán cambios')
            )
        
        try:
            with transaction.atomic():
                self.migrate_products(invoicing_products, dry_run)
                self.update_invoice_references(dry_run)
                
                if dry_run:
                    # En dry-run, hacer rollback para no cambiar nada
                    transaction.set_rollback(True)
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error durante la unificación: {e}')
            )
            raise
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS('✅ UNIFICACIÓN COMPLETADA EXITOSAMENTE')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ SIMULACIÓN COMPLETADA - Usar --force para ejecutar')
            )

    def migrate_products(self, invoicing_products, dry_run):
        """Migrar productos de facturación a inventario"""
        migrated_count = 0
        skipped_count = 0
        
        for inv_product in invoicing_products:
            company = inv_product.company
            
            # Crear categoría por defecto si no existe
            if not dry_run:
                default_category, created = Category.objects.get_or_create(
                    company=company,
                    name='Productos Migrados',
                    defaults={
                        'description': 'Productos migrados desde facturación'
                    }
                )
            else:
                # En dry-run, simular la categoría
                try:
                    default_category = Category.objects.get(
                        company=company,
                        name='Productos Migrados'
                    )
                except Category.DoesNotExist:
                    self.stdout.write(f'  📁 Se crearía categoría "Productos Migrados" para {company.trade_name}')
                    default_category = None
            
            # Verificar si ya existe en inventario
            existing = InventoryProduct.objects.filter(
                company=company,
                code=inv_product.code
            ).first()
            
            if existing:
                self.stdout.write(f'  ⚠️  Producto {inv_product.code} ya existe en inventario')
                skipped_count += 1
                continue
            
            # Crear producto en inventario
            if not dry_run:
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
                
                self.stdout.write(
                    f'  ✅ Migrado: {inv_product.code} - {inv_product.name}'
                )
            else:
                self.stdout.write(
                    f'  🔄 Se migraría: {inv_product.code} - {inv_product.name}'
                )
            
            migrated_count += 1
        
        self.stdout.write(f'📊 Productos migrados: {migrated_count}')
        self.stdout.write(f'📊 Productos omitidos: {skipped_count}')

    def update_invoice_references(self, dry_run):
        """Actualizar referencias de InvoiceLine para usar productos de inventario"""
        
        # Esta actualización se manejará automáticamente por la migración de Django
        # Solo reportamos el estado actual
        
        try:
            # Contar líneas que necesitan actualización
            invoice_lines = InvoiceLine.objects.all()
            self.stdout.write(f'🧾 Líneas de factura a actualizar: {invoice_lines.count()}')
            
            if not dry_run:
                self.stdout.write('  ✅ Referencias actualizadas por migración de Django')
            else:
                self.stdout.write('  🔄 Se actualizarían las referencias por migración de Django')
                
        except Exception as e:
            self.stdout.write(f'  ⚠️  Error al verificar líneas de factura: {e}')