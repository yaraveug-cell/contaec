"""
Script para crear las cuentas contables necesarias para retenciones por cobrar
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import ChartOfAccounts, AccountType
from apps.companies.models import Company
from decimal import Decimal

def create_retention_accounts():
    """Crear cuentas de retención por cobrar para GUEBER"""
    print("🔧 Creando cuentas de retención por cobrar...")
    
    # Obtener empresa GUEBER
    company = Company.objects.filter(trade_name__icontains='GUEBER').first()
    if not company:
        print("❌ No se encontró empresa GUEBER")
        return False
    
    print(f"✅ Empresa: {company.trade_name}")
    
    # Obtener tipo de cuenta activo
    asset_type = AccountType.objects.filter(name__icontains='activo').first()
    if not asset_type:
        asset_type = AccountType.objects.first()  # Usar el primer tipo disponible
        
    print(f"📋 Tipo de cuenta: {asset_type.name}")
    
    # Cuentas a crear
    accounts_to_create = [
        {
            'code': '1.1.05.05',
            'name': 'RETENCION IVA POR COBRAR',
            'account_type': asset_type,
            'accepts_movement': True,
        },
        {
            'code': '1.1.05.06',
            'name': 'RETENCION IR POR COBRAR', 
            'account_type': asset_type,
            'accepts_movement': True,
        }
    ]
    
    created_count = 0
    
    for account_data in accounts_to_create:
        # Verificar si ya existe
        existing = ChartOfAccounts.objects.filter(
            company=company,
            code=account_data['code']
        ).first()
        
        if existing:
            print(f"⚠️ Cuenta {account_data['code']} ya existe: {existing.name}")
            continue
        
        # Crear nueva cuenta
        account = ChartOfAccounts.objects.create(
            company=company,
            code=account_data['code'],
            name=account_data['name'],
            account_type=account_data['account_type'],
            accepts_movement=account_data['accepts_movement'],
            is_detail=True,  # Cuenta de detalle para movimientos
            level=4  # Nivel apropiado para subcuentas
        )
        
        print(f"✅ Cuenta creada: {account.code} - {account.name}")
        created_count += 1
    
    print(f"\\n📊 Resumen: {created_count} cuentas creadas")
    return True

if __name__ == "__main__":
    success = create_retention_accounts()
    
    if success:
        print(f"\\n🎉 ¡Cuentas de retención creadas exitosamente!")
        print(f"📋 Ahora GUEBER puede manejar retenciones de clientes agentes de retención")
    else:
        print(f"\\n❌ Error creando cuentas")
        
    sys.exit(0 if success else 1)