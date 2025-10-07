"""
Script para verificar las cuentas contables existentes
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import ChartOfAccounts
from apps.companies.models import Company

def check_accounts():
    """Verificar las cuentas contables disponibles"""
    
    print("🔍 Verificando cuentas contables en el sistema...")
    
    companies = Company.objects.all()
    print(f"📊 Empresas encontradas: {companies.count()}")
    
    for company in companies[:3]:  # Solo las primeras 3
        print(f"\n🏢 Empresa: {company.legal_name}")
        
        accounts = ChartOfAccounts.objects.filter(company=company)
        print(f"   📋 Total de cuentas: {accounts.count()}")
        
        movement_accounts = accounts.filter(accepts_movement=True)
        print(f"   ✅ Cuentas que aceptan movimientos: {movement_accounts.count()}")
        
        if movement_accounts.exists():
            print(f"   🏦 Algunas cuentas disponibles:")
            for account in movement_accounts[:10]:  # Primeras 10
                print(f"      {account.code} - {account.name}")
        else:
            print(f"   ⚠️ No hay cuentas que acepten movimientos")
            
            # Mostrar todas las cuentas para diagnóstico
            print(f"   📋 Todas las cuentas (primeras 10):")
            for account in accounts[:10]:
                print(f"      {account.code} - {account.name} (acepta_mov: {account.accepts_movement})")

if __name__ == "__main__":
    check_accounts()