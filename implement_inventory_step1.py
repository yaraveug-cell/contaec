"""
Script para implementar de forma segura el sistema de inventario en asientos contables
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import Company
from apps.accounting.models import ChartOfAccounts
from apps.inventory.models import Category
from django.db import transaction

def implement_inventory_accounting_safe():
    """Implementar sistema de inventario de forma segura"""
    print("🚀 IMPLEMENTACIÓN SEGURA: Sistema de Inventario en Asientos Contables")
    print("=" * 80)
    
    # Obtener empresa GUEBER
    gueber = Company.objects.filter(trade_name__icontains='GUEBER').first()
    if not gueber:
        print("❌ Empresa GUEBER no encontrada")
        return False
    
    print(f"🏢 Empresa: {gueber.trade_name}")
    
    # ==========================================
    # PASO 1: VERIFICAR CUENTAS REQUERIDAS
    # ==========================================
    print(f"\\n1️⃣ VERIFICACIÓN DE CUENTAS REQUERIDAS")
    print("-" * 60)
    
    # Verificar cuenta de costo
    cost_account = ChartOfAccounts.objects.filter(
        company=gueber,
        code='4.2.01'
    ).first()
    
    if not cost_account or not cost_account.is_active or not cost_account.accepts_movement:
        print(f"❌ Cuenta 4.2.01 no está disponible")
        return False
    
    print(f"✅ Cuenta costo: {cost_account.code} - {cost_account.name}")
    
    # Verificar cuenta de inventario
    inventory_account = ChartOfAccounts.objects.filter(
        company=gueber,
        code='1.1.06.01.01'
    ).first()
    
    if not inventory_account or not inventory_account.is_active or not inventory_account.accepts_movement:
        print(f"❌ Cuenta 1.1.06.01.01 no está disponible")
        return False
    
    print(f"✅ Cuenta inventario: {inventory_account.code} - {inventory_account.name}")
    
    # ==========================================
    # PASO 2: BACKUP DE CONFIGURACIÓN ACTUAL
    # ==========================================
    print(f"\\n2️⃣ BACKUP DE CONFIGURACIÓN ACTUAL")
    print("-" * 60)
    
    categories = Category.objects.filter(company=gueber)
    backup_config = {}
    
    for category in categories:
        backup_config[category.id] = {
            'name': category.name,
            'current_cost_account_id': category.default_cost_account_id if category.default_cost_account else None,
            'current_cost_account_code': category.default_cost_account.code if category.default_cost_account else None
        }
        print(f"📋 {category.name}: actual={backup_config[category.id]['current_cost_account_code']}")
    
    print(f"✅ Backup de {len(backup_config)} categorías completado")
    
    # ==========================================
    # PASO 3: ACTUALIZAR CONFIGURACIÓN DE CATEGORÍAS
    # ==========================================
    print(f"\\n3️⃣ ACTUALIZAR CONFIGURACIÓN DE CATEGORÍAS")
    print("-" * 60)
    
    try:
        with transaction.atomic():
            updated_count = 0
            
            for category in categories:
                # Solo actualizar si la cuenta actual es diferente
                if (not category.default_cost_account or 
                    category.default_cost_account.code != '4.2.01'):
                    
                    old_account = category.default_cost_account.code if category.default_cost_account else 'Sin cuenta'
                    category.default_cost_account = cost_account
                    category.save()
                    
                    print(f"✅ {category.name}: {old_account} → 4.2.01")
                    updated_count += 1
                else:
                    print(f"ℹ️ {category.name}: Ya usa 4.2.01 (sin cambios)")
            
            print(f"\\n✅ Configuración actualizada: {updated_count} categorías modificadas")
            
    except Exception as e:
        print(f"❌ Error actualizando configuración: {e}")
        return False
    
    return True

def rollback_configuration(backup_config):
    """Función de rollback en caso de problemas"""
    print(f"\\n🔄 EJECUTANDO ROLLBACK...")
    
    try:
        with transaction.atomic():
            for category_id, config in backup_config.items():
                category = Category.objects.get(id=category_id)
                
                if config['current_cost_account_id']:
                    old_account = ChartOfAccounts.objects.get(id=config['current_cost_account_id'])
                    category.default_cost_account = old_account
                    category.save()
                    print(f"↩️ {category.name}: Restaurado a {config['current_cost_account_code']}")
                else:
                    category.default_cost_account = None
                    category.save()
                    print(f"↩️ {category.name}: Restaurado a sin cuenta")
            
            print(f"✅ Rollback completado exitosamente")
            return True
            
    except Exception as e:
        print(f"❌ Error en rollback: {e}")
        return False

if __name__ == "__main__":
    success = implement_inventory_accounting_safe()
    
    if success:
        print(f"\\n🎉 PASO 1 COMPLETADO EXITOSAMENTE")
        print(f"✅ Configuración de categorías actualizada")
        print(f"📋 Siguiente paso: Modificar AutomaticJournalEntryService")
    else:
        print(f"\\n❌ PASO 1 FALLÓ - Configuración no modificada")
    
    sys.exit(0 if success else 1)