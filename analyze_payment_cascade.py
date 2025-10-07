#!/usr/bin/env python3
"""
Análisis de la relación entre Forma de Pago y Cuenta Contable
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import Company, PaymentMethod
from apps.accounting.models import ChartOfAccounts

def main():
    print("🔍 ANÁLISIS DE FILTRO EN CASCADA: FORMA DE PAGO → CUENTA CONTABLE")
    print("=" * 80)
    
    # 1. Análisis de PaymentMethod
    print("\n📋 1. FORMAS DE PAGO DISPONIBLES:")
    print("-" * 50)
    payment_methods = PaymentMethod.objects.all()
    for pm in payment_methods:
        print(f"   📝 {pm.name}")
        if pm.parent_account:
            print(f"      └─ Cuenta Padre: {pm.parent_account.code} - {pm.parent_account.name}")
        else:
            print(f"      └─ Sin cuenta padre configurada")
    
    # 2. Análisis de Companies y su payment_method
    print(f"\n🏢 2. EMPRESAS Y SUS FORMAS DE PAGO CONFIGURADAS:")
    print("-" * 50)
    companies = Company.objects.select_related('payment_method').all()
    
    for company in companies:
        print(f"   🏢 {company.trade_name}")
        if company.payment_method:
            print(f"      └─ Forma de Pago: {company.payment_method.name}")
            if company.payment_method.parent_account:
                print(f"      └─ Cuenta Asociada: {company.payment_method.parent_account.code} - {company.payment_method.parent_account.name}")
            else:
                print(f"      └─ Sin cuenta asociada")
        else:
            print(f"      └─ Sin forma de pago configurada")
    
    # 3. Análisis de posible filtro en cascada
    print(f"\n⚙️ 3. ANÁLISIS PARA FILTRO EN CASCADA:")
    print("-" * 50)
    
    # Verificar si las formas de pago tienen parent_account configurado
    methods_with_accounts = PaymentMethod.objects.filter(parent_account__isnull=False)
    methods_without_accounts = PaymentMethod.objects.filter(parent_account__isnull=True)
    
    print(f"   ✅ Formas de pago con cuenta padre: {methods_with_accounts.count()}")
    for method in methods_with_accounts:
        print(f"      - {method.name} → {method.parent_account.code}")
    
    print(f"   ❌ Formas de pago sin cuenta padre: {methods_without_accounts.count()}")
    for method in methods_without_accounts:
        print(f"      - {method.name}")
    
    # 4. Propuesta de implementación
    print(f"\n🎯 4. PROPUESTA DE IMPLEMENTACIÓN:")
    print("-" * 50)
    print("""
    ESCENARIO ACTUAL:
    - PaymentMethod.parent_account apunta a ChartOfAccounts
    - Company.payment_method apunta a PaymentMethod
    - Invoice.payment_form apunta a PaymentMethod
    - Invoice.account apunta a ChartOfAccounts
    
    FILTRO EN CASCADA PROPUESTO:
    1. Al seleccionar una Forma de Pago en Invoice
    2. Filtrar las Cuentas Contables que sean hijas de parent_account
    3. Mostrar solo cuentas que accepts_movement=True
    4. De la empresa actual del usuario
    
    EJEMPLO:
    - Forma de Pago: "Transferencia" → parent_account: "1.1.02 BANCOS"
    - Mostrar cuentas: "1.1.02.01 Banco Pichincha", "1.1.02.02 Banco Guayaquil"
    
    JAVASCRIPT NECESARIO:
    - Event listener en payment_form field
    - AJAX call para obtener cuentas filtradas
    - Actualización dinámica del campo account
    """)
    
    # 5. Verificar cuentas disponibles por empresa
    print(f"\n📊 5. CUENTAS CONTABLES DISPONIBLES POR EMPRESA:")
    print("-" * 50)
    
    for company in companies[:2]:  # Solo mostrar primeras 2 empresas para brevedad
        print(f"\n   🏢 {company.trade_name}:")
        accounts = ChartOfAccounts.objects.filter(
            company=company,
            accepts_movement=True
        ).order_by('code')[:10]  # Primeras 10 cuentas
        
        for account in accounts:
            print(f"      - {account.code} - {account.name}")
        
        if accounts.count() > 10:
            print(f"      ... y {accounts.count() - 10} cuentas más")

if __name__ == '__main__':
    main()