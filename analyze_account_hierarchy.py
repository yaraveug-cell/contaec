#!/usr/bin/env python3
"""
Análisis detallado de la jerarquía de cuentas contables para filtro en cascada
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import PaymentMethod
from apps.accounting.models import ChartOfAccounts

def main():
    print("🌳 ANÁLISIS JERÁRQUICO DETALLADO - FILTRO EN CASCADA")
    print("=" * 70)
    
    # Obtener GUEBER (empresa principal de ejemplo)
    from apps.companies.models import Company
    gueber = Company.objects.get(trade_name="GUEBER")
    
    print(f"🏢 Empresa: {gueber.trade_name}")
    print(f"📋 Forma de pago configurada: {gueber.payment_method}")
    print()
    
    # Análisis por cada forma de pago
    payment_methods = PaymentMethod.objects.filter(parent_account__isnull=False)
    
    for method in payment_methods:
        print(f"💳 FORMA DE PAGO: {method.name}")
        print(f"   └─ Cuenta Padre: {method.parent_account.code} - {method.parent_account.name}")
        
        # Buscar cuentas hijas de la cuenta padre
        parent_code = method.parent_account.code
        child_accounts = ChartOfAccounts.objects.filter(
            company=gueber,
            code__startswith=parent_code,
            accepts_movement=True
        ).exclude(
            code=parent_code  # Excluir la cuenta padre
        ).order_by('code')
        
        print(f"   📁 Cuentas hijas disponibles ({child_accounts.count()}):")
        for account in child_accounts:
            indent = "      " + "  " * (account.code.count('.') - method.parent_account.code.count('.'))
            print(f"{indent}├─ {account.code} - {account.name}")
            
        print()
    
    print("🎯 CONFIGURACIÓN PROPUESTA PARA FILTRO EN CASCADA:")
    print("-" * 70)
    print("""
    COMPORTAMIENTO ESPERADO:
    
    1. Al seleccionar "Efectivo":
       → Mostrar cuentas que empiecen con "1.1.01."
       → Ejemplo: "1.1.01.01 - CAJA GENERAL"
    
    2. Al seleccionar "Transferencia":
       → Mostrar cuentas que empiecen con "1.1.02."
       → Ejemplo: "1.1.02.01 - BANCO INTERNACIONAL", "1.1.02.02 - BANCO PICHINCHA"
    
    3. Al seleccionar "Crédito":
       → Mostrar cuentas que empiecen con "1.1.03.01.01."
       → Ejemplo: "1.1.03.01.01.01 - CLIENTE CREDITO AUTORIZADO 1"
    
    IMPLEMENTACIÓN JAVASCRIPT:
    - Evento onChange en select payment_form
    - AJAX al endpoint: /admin/invoicing/invoice/filter-accounts-by-payment/
    - Parámetros: payment_method_id, company_id
    - Response: JSON con cuentas filtradas
    - Actualizar dinámicamente el select de account
    """)
    
    print("\n🔧 ENDPOINT AJAX NECESARIO:")
    print("-" * 30)
    print("""
    URL: /admin/invoicing/invoice/filter-accounts-by-payment/
    Método: GET
    Parámetros:
    - payment_method_id: ID de la forma de pago seleccionada
    - company_id: ID de la empresa actual
    
    Respuesta JSON:
    {
        "accounts": [
            {
                "id": 39,
                "code": "1.1.02.02",
                "name": "BANCO PICHINCHA",
                "display": "1.1.02.02 - BANCO PICHINCHA"
            },
            ...
        ]
    }
    """)

if __name__ == '__main__':
    main()