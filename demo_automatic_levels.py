#!/usr/bin/env python
"""
Script de prueba para demostrar el cálculo automático de niveles en el plan de cuentas
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import ChartOfAccounts, AccountType
from apps.companies.models import Company


def demo_automatic_levels():
    """Demonstración del cálculo automático de niveles"""
    print("🎯 DEMO: Cálculo Automático de Niveles en Plan de Cuentas")
    print("=" * 60)
    
    # Obtener la primera empresa disponible
    try:
        company = Company.objects.first()
        if not company:
            print("❌ No hay empresas disponibles.")
            return
        
        print(f"🏢 Empresa: {company.trade_name}")
        print()
        
        # Obtener tipo de cuenta ACTIVO
        asset_type = AccountType.objects.get(code='ASSET')
        
        # Crear cuenta padre (Nivel 1 - automático)
        print("📝 Creando cuenta ACTIVOS CIRCULANTES...")
        parent_account = ChartOfAccounts.objects.create(
            company=company,
            code='11',
            name='ACTIVOS CIRCULANTES',
            account_type=asset_type,
            parent=None  # Sin padre = Nivel 1
        )
        print(f"   ✅ Creada: {parent_account.code} - Nivel: {parent_account.level} (automático)")
        
        # Crear cuenta hija (Nivel 2 - automático)
        print("\n📝 Creando cuenta EFECTIVO Y EQUIVALENTES...")
        child_account = ChartOfAccounts.objects.create(
            company=company,
            code='1101',
            name='EFECTIVO Y EQUIVALENTES',
            account_type=asset_type,
            parent=parent_account  # Con padre = Nivel padre + 1
        )
        print(f"   ✅ Creada: {child_account.code} - Nivel: {child_account.level} (automático)")
        
        # Crear cuenta nieta (Nivel 3 - automático) 
        print("\n📝 Creando cuenta CAJA GENERAL...")
        grandchild_account = ChartOfAccounts.objects.create(
            company=company,
            code='110101',
            name='CAJA GENERAL',
            account_type=asset_type,
            parent=child_account  # Con padre nivel 2 = Nivel 3
        )
        print(f"   ✅ Creada: {grandchild_account.code} - Nivel: {grandchild_account.level} (automático)")
        
        # Crear otra cuenta nieta (Nivel 3 - automático)
        print("\n📝 Creando cuenta BANCOS...")
        bank_account = ChartOfAccounts.objects.create(
            company=company,
            code='110102',
            name='BANCOS',
            account_type=asset_type,
            parent=child_account  # Con padre nivel 2 = Nivel 3
        )
        print(f"   ✅ Creada: {bank_account.code} - Nivel: {bank_account.level} (automático)")
        
        # Mostrar jerarquía completa
        print("\n🌳 JERARQUÍA RESULTANTE:")
        print("-" * 40)
        
        accounts = [parent_account, child_account, grandchild_account, bank_account]
        for account in accounts:
            print(f"   {account.hierarchy_display}")
        
        # Mostrar propiedades automáticas
        print("\n📊 PROPIEDADES AUTOMÁTICAS:")
        print("-" * 40)
        
        for account in accounts:
            print(f"📋 {account.code} - {account.name}")
            print(f"    Nivel: {account.level}")
            print(f"    Es cuenta de detalle: {account.is_detail}")
            print(f"    Acepta movimiento: {account.accepts_movement}")
            print(f"    Subcuentas: {account.children_count}")
            print(f"    Código completo: {account.full_code}")
            print()
        
        # Demostrar actualización automática del padre
        print("🔄 DEMOSTRACIÓN: Actualización automática del estado padre")
        print("-" * 50)
        
        print(f"📝 Estado actual de '{parent_account.name}':")
        print(f"    Es cuenta de detalle: {parent_account.is_detail}")
        print(f"    Acepta movimiento: {parent_account.accepts_movement}")
        
        # Recargar para ver cambios
        parent_account.refresh_from_db()
        parent_account._update_detail_status()
        
        print(f"📝 Estado después de tener subcuentas:")
        print(f"    Es cuenta de detalle: {parent_account.is_detail}")
        print(f"    Acepta movimiento: {parent_account.accepts_movement}")
        
        print("\n✅ Demo completada exitosamente!")
        print("\n💡 BENEFICIOS DEL SISTEMA AUTOMÁTICO:")
        print("   • No necesitas calcular niveles manualmente")
        print("   • La jerarquía se mantiene consistente automáticamente")
        print("   • Las cuentas padre se configuran automáticamente")
        print("   • Previene errores de configuración manual")
        
        # Limpiar cuentas de prueba
        print("\n🧹 Limpiando cuentas de prueba...")
        accounts_to_delete = ChartOfAccounts.objects.filter(
            company=company,
            code__in=['11', '1101', '110101', '110102']
        )
        count = accounts_to_delete.count()
        accounts_to_delete.delete()
        print(f"   ✅ {count} cuentas de prueba eliminadas")
        
    except Exception as e:
        print(f"❌ Error en la demostración: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    demo_automatic_levels()