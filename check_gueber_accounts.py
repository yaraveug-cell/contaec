"""
Script para verificar la empresa GUEBER y sus cuentas
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import ChartOfAccounts
from apps.companies.models import Company

def check_gueber_accounts():
    """Verificar empresa GUEBER y sus cuentas"""
    print("🔍 Verificando empresa GUEBER...")
    
    # Buscar empresa GUEBER
    company = Company.objects.filter(trade_name__icontains='GUEBER').first()
    
    if not company:
        print("❌ No se encontró empresa GUEBER")
        print("📋 Empresas disponibles:")
        for comp in Company.objects.all():
            print(f"   - {comp.trade_name}")
        return False
    
    print(f"✅ Empresa encontrada: {company.trade_name}")
    
    # Verificar cuentas
    accounts = ChartOfAccounts.objects.filter(
        company=company, 
        accepts_movement=True
    ).values_list('code', 'name')[:20]
    
    print(f"\n📋 Cuentas disponibles en {company.trade_name}:")
    for code, name in accounts:
        print(f"   {code} - {name}")
    
    # Buscar cuentas específicas para facturas
    caja_accounts = ChartOfAccounts.objects.filter(
        company=company,
        accepts_movement=True,
        code__icontains='1'
    ).values_list('code', 'name')[:10]
    
    print(f"\n💰 Cuentas de activo (código 1) en {company.trade_name}:")
    for code, name in caja_accounts:
        print(f"   {code} - {name}")
    
    return True

if __name__ == "__main__":
    check_gueber_accounts()