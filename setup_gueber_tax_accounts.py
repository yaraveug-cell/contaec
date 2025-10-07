#!/usr/bin/env python
"""
Script para configurar cuentas IVA iniciales para GUEBER
Siguiendo el mapeo hardcodeado actual
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import Company, CompanyTaxAccountMapping
from apps.accounting.models import ChartOfAccounts
from decimal import Decimal

def setup_gueber_tax_accounts():
    """Configurar cuentas IVA para GUEBER siguiendo el mapeo actual"""
    
    print("🏢 CONFIGURACIÓN INICIAL: CUENTAS IVA PARA GUEBER")
    print("=" * 60)
    
    # 1. Obtener empresa GUEBER
    try:
        gueber = Company.objects.get(trade_name__icontains='gueber')
        print(f"✅ Empresa encontrada: {gueber.trade_name}")
    except Company.DoesNotExist:
        print("❌ Empresa GUEBER no encontrada")
        return False
    
    # 2. Configuraciones IVA a crear
    tax_configurations = [
        {
            'tax_rate': Decimal('15.00'),
            'account_code': '2.1.01.01.03.01',
            'description': 'IVA Ventas 15%'
        },
        {
            'tax_rate': Decimal('5.00'),
            'account_code': '2.1.01.01.03.02',
            'description': 'IVA Ventas 5%'
        },
        # IVA 0% no necesita cuenta según mapeo actual
    ]
    
    print(f"\n📋 Configuraciones a crear:")
    created_count = 0
    updated_count = 0
    
    for config in tax_configurations:
        # Buscar la cuenta contable
        try:
            account = ChartOfAccounts.objects.get(
                company=gueber,
                code=config['account_code']
            )
            print(f"   ✅ Cuenta encontrada: {account.code} - {account.name}")
        except ChartOfAccounts.DoesNotExist:
            print(f"   ❌ Cuenta no encontrada: {config['account_code']}")
            continue
        
        # Crear o actualizar configuración
        mapping, created = CompanyTaxAccountMapping.objects.get_or_create(
            company=gueber,
            tax_rate=config['tax_rate'],
            defaults={'account': account}
        )
        
        if created:
            created_count += 1
            status = "✅ CREADO"
        else:
            # Actualizar cuenta si ya existe
            mapping.account = account
            mapping.save()
            updated_count += 1
            status = "🔄 ACTUALIZADO"
        
        print(f"   {status}: IVA {mapping.tax_rate}% → {mapping.account.code}")
    
    # 3. Mostrar configuración final
    print(f"\n🎯 RESULTADO:")
    print(f"   ✅ Creadas: {created_count}")
    print(f"   🔄 Actualizadas: {updated_count}")
    
    print(f"\n📊 CONFIGURACIÓN FINAL PARA {gueber.trade_name}:")
    print("-" * 50)
    
    mappings = CompanyTaxAccountMapping.objects.filter(company=gueber).order_by('tax_rate')
    
    if mappings.exists():
        for mapping in mappings:
            print(f"   • IVA {mapping.tax_rate}% → {mapping.account.code} - {mapping.account.name}")
    else:
        print("   (Sin configuraciones)")
    
    print(f"\n🔄 COMPATIBILIDAD:")
    print(f"   • Mapeo hardcodeado sigue funcionando como fallback")
    print(f"   • AutomaticJournalEntryService usa configuración dinámica primero")
    print(f"   • Facturas existentes no se ven afectadas")
    
    print(f"\n🚀 LISTO PARA USAR:")
    print(f"   📝 Admin → Empresas → {gueber.trade_name} → Configuración Contable")
    print(f"   ➕ Agregar/editar configuraciones IVA en la sección inferior")
    
    return True

if __name__ == "__main__":
    success = setup_gueber_tax_accounts()
    sys.exit(0 if success else 1)