"""
Script para configurar las cuentas contables por defecto para GUEBER
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import Company, CompanyAccountDefaults, CompanyTaxAccountMapping
from apps.accounting.models import ChartOfAccounts
from decimal import Decimal

def configure_gueber_accounts():
    """Configurar cuentas por defecto para GUEBER"""
    print("🔧 Configurando cuentas contables por defecto para GUEBER...")
    
    # Obtener empresa GUEBER
    company = Company.objects.filter(trade_name__icontains='GUEBER').first()
    if not company:
        print("❌ No se encontró empresa GUEBER")
        return False
    
    print(f"✅ Empresa: {company.trade_name}")
    
    # Obtener cuentas necesarias
    accounts = {
        'sales': ChartOfAccounts.objects.filter(company=company, code='4.1.01').first(),
        'iva_retention': ChartOfAccounts.objects.filter(company=company, code='1.1.05.05').first(),
        'ir_retention': ChartOfAccounts.objects.filter(company=company, code='1.1.05.06').first(),
        'iva_15': ChartOfAccounts.objects.filter(company=company, code='2.1.01.01.03.01').first(),
        'iva_5': ChartOfAccounts.objects.filter(company=company, code='2.1.01.01.03.02').first(),
    }
    
    print("📋 Cuentas encontradas:")
    for key, account in accounts.items():
        if account:
            print(f"   ✅ {key}: {account.code} - {account.name}")
        else:
            print(f"   ❌ {key}: No encontrada")
    
    # 1. Configurar cuentas por defecto
    defaults, created = CompanyAccountDefaults.objects.get_or_create(
        company=company,
        defaults={
            'default_sales_account': accounts['sales'],
            'iva_retention_receivable_account': accounts['iva_retention'],
            'ir_retention_receivable_account': accounts['ir_retention'],
        }
    )
    
    if created:
        print("✅ Configuración por defecto creada")
    else:
        # Actualizar si ya existe
        defaults.default_sales_account = accounts['sales']
        defaults.iva_retention_receivable_account = accounts['iva_retention']
        defaults.ir_retention_receivable_account = accounts['ir_retention']
        defaults.save()
        print("✅ Configuración por defecto actualizada")
    
    # 2. Configurar mapeos de IVA
    iva_mappings = [
        {'rate': Decimal('15.00'), 'account': accounts['iva_15'], 'retention': accounts['iva_retention']},
        {'rate': Decimal('5.00'), 'account': accounts['iva_5'], 'retention': accounts['iva_retention']},
    ]
    
    for mapping_data in iva_mappings:
        if mapping_data['account']:
            mapping, created = CompanyTaxAccountMapping.objects.get_or_create(
                company=company,
                tax_rate=mapping_data['rate'],
                defaults={
                    'account': mapping_data['account'],
                    'retention_account': mapping_data['retention'],
                }
            )
            
            if created:
                print(f"✅ Mapeo IVA {mapping_data['rate']}% creado")
            else:
                # Actualizar retención si ya existe
                mapping.retention_account = mapping_data['retention']
                mapping.save()
                print(f"✅ Mapeo IVA {mapping_data['rate']}% actualizado")
        else:
            print(f"⚠️ No se pudo configurar mapeo IVA {mapping_data['rate']}% - cuenta no encontrada")
    
    print("\\n📊 Configuración completada:")
    print(f"   🏢 Empresa: {company.trade_name}")
    print(f"   📋 Cuenta ventas por defecto: {defaults.default_sales_account.code if defaults.default_sales_account else 'No configurada'}")
    print(f"   📋 Retención IVA por cobrar: {defaults.iva_retention_receivable_account.code if defaults.iva_retention_receivable_account else 'No configurada'}")
    print(f"   📋 Retención IR por cobrar: {defaults.ir_retention_receivable_account.code if defaults.ir_retention_receivable_account else 'No configurada'}")
    
    # Mostrar mapeos IVA configurados
    mappings = CompanyTaxAccountMapping.objects.filter(company=company).select_related('account', 'retention_account')
    print(f"   📊 Mapeos IVA configurados: {mappings.count()}")
    for mapping in mappings:
        ret_info = f" | Retención: {mapping.retention_account.code}" if mapping.retention_account else ""
        print(f"      IVA {mapping.tax_rate}%: {mapping.account.code}{ret_info}")
    
    return True

if __name__ == "__main__":
    success = configure_gueber_accounts()
    
    if success:
        print(f"\\n🎉 ¡Configuración completada exitosamente!")
        print(f"📋 GUEBER ahora tiene configuración contable flexible para retenciones")
        print(f"🚀 El sistema usará estas configuraciones en lugar de valores hardcodeados")
    else:
        print(f"\\n❌ Error en la configuración")
        
    sys.exit(0 if success else 1)