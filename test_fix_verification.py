#!/usr/bin/env python
"""
TEST FINAL: Verificación del fix aplicado al filtrado de cuentas
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import PaymentMethod
from apps.accounting.models import ChartOfAccounts

print("🔧 TEST FINAL: Fix del filtrado de cuentas v5.1")
print("=" * 60)

# Test de la función corregida
def simulate_isChildAccount(account_text, parent_account_obj):
    """Simulación de la función JavaScript isChildAccount CORREGIDA"""
    import re
    
    # Extraer código de cuenta del texto
    code_match = re.match(r'^(\d+(?:\.\d+)*)', account_text)
    if not code_match:
        return False
    
    account_code = code_match.group(1)
    
    # 🔧 FIX: Manejar correctamente el objeto parent_account
    if isinstance(parent_account_obj, dict):
        parent_code = parent_account_obj.get('code', '')
    else:
        parent_code = str(parent_account_obj)
    
    # Normalizar código padre
    if parent_code.endswith('.'):
        parent_code = parent_code[:-1]
    
    # Verificar jerarquía
    is_child = account_code.startswith(parent_code + '.') and account_code != parent_code
    
    print(f"   Test: {account_code} vs {parent_code} → {is_child}")
    return is_child

print("1. 🏦 Test con datos reales de Transferencia:")
print("-" * 40)

try:
    transferencia = PaymentMethod.objects.get(name="Transferencia")
    parent_account = {
        'code': transferencia.parent_account.code,
        'name': transferencia.parent_account.name
    }
    
    print(f"✅ Transferencia configurada con cuenta padre:")
    print(f"   {parent_account['code']} - {parent_account['name']}")
    
    # Cuentas de prueba que deberían filtrarse
    test_accounts = [
        "1.1.02.01 - BANCO INTERNACIONAL",
        "1.1.02.02 - BANCO PICHINCHA", 
        "1.1.02. - BANCOS",  # Esta NO debe aparecer (es la padre)
        "1.1.03.01 - OTRA CUENTA"  # Esta NO debe aparecer
    ]
    
    print(f"\n2. 🧪 Test de filtrado:")
    print("-" * 30)
    
    filtered_accounts = []
    for account_text in test_accounts:
        is_child = simulate_isChildAccount(account_text, parent_account)
        status = "✅ INCLUIR" if is_child else "❌ EXCLUIR"
        print(f"   {account_text} → {status}")
        if is_child:
            filtered_accounts.append(account_text)
    
    print(f"\n3. 📊 Resultado esperado:")
    print("-" * 30)
    print(f"   Cuentas que deberían aparecer: {len(filtered_accounts)}")
    for account in filtered_accounts:
        print(f"      ✅ {account}")
    
    if len(filtered_accounts) == 2:
        print(f"\n🎉 ¡CORRECTO! El fix debería mostrar exactamente 2 cuentas hijas")
    else:
        print(f"\n⚠️ Resultado inesperado: {len(filtered_accounts)} cuentas")
        
except PaymentMethod.DoesNotExist:
    print("❌ Transferencia no encontrada")

print(f"\n4. ✅ INSTRUCCIONES PARA VERIFICAR:")
print("-" * 40)
print("   1. Recarga la página de factura en el navegador")
print("   2. Selecciona la empresa GUEBER")
print("   3. Selecciona forma de pago: Transferencia")
print("   4. Verifica que aparezcan solo:")
print("      ✅ BANCO INTERNACIONAL")
print("      ✅ BANCO PICHINCHA")
print("\n💡 Si no funciona, abre la consola del navegador (F12)")
print("   y verifica los mensajes de debug que empiecen con 🔍")

print(f"\n🏁 Test completado - Fix v5.1 aplicado")