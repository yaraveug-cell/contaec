#!/usr/bin/env python
"""
Script para actualizar los niveles automáticamente en el plan de cuentas existente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import ChartOfAccounts


def update_account_levels():
    """Actualiza los niveles de todas las cuentas existentes"""
    print("🔄 Iniciando actualización de niveles del plan de cuentas...")
    
    # Obtener todas las cuentas ordenadas por código
    accounts = ChartOfAccounts.objects.all().order_by('company', 'code')
    
    updated_count = 0
    
    for account in accounts:
        old_level = account.level
        
        # Calcular el nuevo nivel
        if account.parent:
            new_level = account.parent.level + 1
        else:
            new_level = 1
        
        # Solo actualizar si cambió
        if old_level != new_level:
            account.level = new_level
            account.save(update_fields=['level'])
            print(f"📊 {account.company.trade_name} - {account.code}: Nivel {old_level} → {new_level}")
            updated_count += 1
    
    print(f"\n✅ Proceso completado. {updated_count} cuentas actualizadas.")
    
    # Mostrar resumen por empresa y nivel
    print("\n📋 Resumen por empresa:")
    from django.db.models import Count
    
    summary = ChartOfAccounts.objects.values(
        'company__trade_name', 'level'
    ).annotate(
        count=Count('id')
    ).order_by('company__trade_name', 'level')
    
    current_company = None
    for item in summary:
        if item['company__trade_name'] != current_company:
            current_company = item['company__trade_name']
            print(f"\n🏢 {current_company}:")
        
        print(f"   Nivel {item['level']}: {item['count']} cuentas")


def validate_hierarchy():
    """Valida que la jerarquía sea consistente"""
    print("\n🔍 Validando jerarquía del plan de cuentas...")
    
    errors = []
    
    # Verificar que las cuentas padre tengan nivel menor que las hijas
    for account in ChartOfAccounts.objects.filter(parent__isnull=False):
        if account.level <= account.parent.level:
            errors.append(f"❌ {account.code}: Nivel incorrecto ({account.level} <= {account.parent.level})")
    
    # Verificar que las cuentas raíz tengan nivel 1
    root_accounts = ChartOfAccounts.objects.filter(parent__isnull=True)
    for account in root_accounts:
        if account.level != 1:
            errors.append(f"❌ {account.code}: Cuenta raíz debe tener nivel 1 (actual: {account.level})")
    
    if errors:
        print(f"⚠️  Se encontraron {len(errors)} errores:")
        for error in errors:
            print(f"   {error}")
    else:
        print("✅ La jerarquía es consistente.")


def show_hierarchy_sample():
    """Muestra una muestra de la jerarquía por empresa"""
    print("\n🌳 Muestra de jerarquía por empresa:")
    
    for company in ChartOfAccounts.objects.values_list('company__trade_name', flat=True).distinct():
        print(f"\n🏢 {company}")
        
        accounts = ChartOfAccounts.objects.filter(
            company__trade_name=company
        ).order_by('code')[:10]  # Primeras 10 cuentas
        
        for account in accounts:
            print(f"   {account.hierarchy_display}")
        
        total = ChartOfAccounts.objects.filter(company__trade_name=company).count()
        if total > 10:
            print(f"   ... y {total - 10} cuentas más")


if __name__ == '__main__':
    try:
        update_account_levels()
        validate_hierarchy()
        show_hierarchy_sample()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)