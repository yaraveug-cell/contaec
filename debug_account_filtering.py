#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO: Sistema de Filtrado de Cuentas
Verifica por qué dejó de funcionar el filtrado del campo cuenta
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import PaymentMethod
from apps.accounting.models import ChartOfAccounts

def main():
    print("🔍 DIAGNÓSTICO: Filtrado de Cuentas")
    print("=" * 60)
    
    # 1. Verificar configuraciones de PaymentMethod
    print("\n1. 📋 CONFIGURACIONES DE MÉTODOS DE PAGO:")
    print("-" * 40)
    
    payment_methods = PaymentMethod.objects.all()
    for pm in payment_methods:
        print(f"   ID: {pm.id}")
        print(f"   Nombre: {pm.name}")
        print(f"   Cuenta Padre: {pm.parent_account}")
        if pm.parent_account:
            print(f"   Código Cuenta Padre: {pm.parent_account.code}")
        print()
    
    # 2. Verificar cuentas disponibles
    print("\n2. 🏦 CUENTAS DISPONIBLES:")
    print("-" * 40)
    
    accounts = ChartOfAccounts.objects.all().order_by('code')
    for account in accounts:
        print(f"   {account.code} - {account.name}")
    
    # 3. Test específico de filtrado para "Transferencia"
    print("\n3. 🔍 TEST DE FILTRADO - TRANSFERENCIA:")
    print("-" * 40)
    
    try:
        transferencia = PaymentMethod.objects.get(name__icontains='transferencia')
        print(f"✅ Método encontrado: {transferencia.name}")
        print(f"   ID: {transferencia.id}")
        print(f"   Cuenta padre: {transferencia.parent_account}")
        
        if transferencia.parent_account:
            parent_code = transferencia.parent_account.code
            print(f"   Código padre: {parent_code}")
            
            # Buscar cuentas hijas
            child_accounts = []
            for account in accounts:
                if account.code.startswith(parent_code + '.') and account.code != parent_code:
                    child_accounts.append(account)
            
            print(f"\n   📋 Cuentas hijas encontradas ({len(child_accounts)}):")
            for child in child_accounts:
                print(f"      {child.code} - {child.name}")
                
        else:
            print("   ❌ No tiene cuenta padre configurada")
            
    except PaymentMethod.DoesNotExist:
        print("❌ Método 'Transferencia' no encontrado")
    
    # 4. Verificar endpoints de la API
    print("\n4. 🌐 VERIFICACIÓN DE ENDPOINTS:")
    print("-" * 40)
    
    from django.test import Client
    from django.contrib.auth import get_user_model
    
    # Crear cliente de test
    client = Client()
    User = get_user_model()
    
    # Verificar si hay usuarios admin
    admin_users = User.objects.filter(is_staff=True)
    if admin_users.exists():
        admin_user = admin_users.first()
        client.force_login(admin_user)
        
        # Test endpoint payment-method-accounts
        response = client.get('/admin/invoicing/invoice/payment-method-accounts/')
        print(f"   payment-method-accounts: {response.status_code}")
        if response.status_code == 200:
            import json
            data = json.loads(response.content)
            print(f"   Configuraciones cargadas: {len(data)}")
            for key, config in data.items():
                print(f"      Método {key}: {config}")
        else:
            print(f"      Error: {response.content}")
            
    else:
        print("   ❌ No hay usuarios admin para probar endpoints")
    
    # 5. Verificar JavaScript en el navegador
    print("\n5. 🔧 VERIFICACIÓN JAVASCRIPT:")
    print("-" * 40)
    print("   Para verificar en el navegador:")
    print("   1. Abre la consola del navegador (F12)")
    print("   2. Ejecuta: window.paymentHandler")
    print("   3. Verifica: window.paymentHandler.paymentMethodAccounts")
    print("   4. Test manual: window.paymentHandler.handlePaymentFormChange('ID_TRANSFERENCIA')")
    
    print("\n✅ Diagnóstico completado")
    print("💡 Si el problema persiste, revisa la consola del navegador")

if __name__ == "__main__":
    main()