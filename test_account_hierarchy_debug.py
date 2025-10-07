#!/usr/bin/env python
"""
DEBUG: Test específico del filtrado de jerarquía de cuentas
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import PaymentMethod
from apps.accounting.models import ChartOfAccounts

print("🔍 DEBUG: Análisis específico de jerarquía de cuentas")
print("=" * 60)

# 1. Obtener configuración de Transferencia
try:
    transferencia = PaymentMethod.objects.get(name="Transferencia")
    print(f"✅ Método Transferencia encontrado: ID {transferencia.id}")
    print(f"   Cuenta padre: {transferencia.parent_account}")
    print(f"   Código: {transferencia.parent_account.code}")
    
    parent_code = transferencia.parent_account.code
    if parent_code.endswith('.'):
        normalized_parent = parent_code[:-1]  # Remover punto final
    else:
        normalized_parent = parent_code
        
    print(f"   Código normalizado: '{normalized_parent}'")
    
except PaymentMethod.DoesNotExist:
    print("❌ Método Transferencia no encontrado")
    exit()

print("\n2. 🏦 TODAS LAS CUENTAS DISPONIBLES:")
print("-" * 40)
all_accounts = ChartOfAccounts.objects.all().order_by('code')
for account in all_accounts:
    print(f"   {account.code} - {account.name}")

print(f"\n3. 🔍 BUSCANDO CUENTAS HIJAS DE '{parent_code}':")
print("-" * 40)

# Buscar cuentas que empiecen con el código padre + punto
child_accounts = []

for account in all_accounts:
    account_code = account.code
    
    # Lógica JavaScript traducida a Python
    if account_code.startswith(normalized_parent + '.') and account_code != normalized_parent:
        child_accounts.append(account)
        print(f"   ✅ HIJA: {account_code} - {account.name}")
    else:
        # Debug detallado
        if account_code.startswith(normalized_parent):
            print(f"   📋 PREFIJO: {account_code} - {account.name}")
            if account_code == normalized_parent:
                print(f"       ⚪ Es la cuenta padre misma")
            elif not account_code.startswith(normalized_parent + '.'):
                print(f"       ❌ No tiene punto después del prefijo")
        elif "1.1.02" in account_code:
            print(f"   🔍 RELACIONADA: {account_code} - {account.name}")

print(f"\n4. 📊 RESUMEN:")
print(f"   Cuenta padre: {parent_code}")
print(f"   Código normalizado: {normalized_parent}")
print(f"   Cuentas hijas encontradas: {len(child_accounts)}")

if child_accounts:
    print("\n   ✅ Cuentas que deberían aparecer:")
    for account in child_accounts:
        print(f"      {account.code} - {account.name}")
else:
    print("\n   ❌ No se encontraron cuentas hijas")
    
    # Buscar cuentas que contengan 1.1.02 para diagnóstico
    related = ChartOfAccounts.objects.filter(code__contains='1.1.02').order_by('code')
    print(f"\n   🔍 Cuentas relacionadas con 1.1.02 ({len(related)}):")
    for account in related:
        print(f"      {account.code} - {account.name}")

print("\n5. 🧪 TEST LÓGICA JAVASCRIPT:")
print("-" * 40)
print("   Simulando lógica JavaScript isChildAccount():")

# Simular las cuentas que vimos en el diagnóstico
test_accounts = [
    "1.1.02.01 - BANCO INTERNACIONAL",
    "1.1.02.02 - BANCO PICHINCHA"
]

for account_text in test_accounts:
    # JavaScript: const codeMatch = accountText.match(/^(\d+(?:\.\d+)*)/);
    import re
    code_match = re.match(r'^(\d+(?:\.\d+)*)', account_text)
    if code_match:
        account_code = code_match.group(1)
        
        # JavaScript: accountCode.startsWith(parentCode + '.') && accountCode !== parentCode
        is_child = account_code.startswith(normalized_parent + '.') and account_code != normalized_parent
        
        print(f"   Cuenta: {account_text}")
        print(f"   Código extraído: '{account_code}'")
        print(f"   Prefijo esperado: '{normalized_parent + '.'}'")
        print(f"   ¿Empieza con prefijo?: {account_code.startswith(normalized_parent + '.')}")
        print(f"   ¿Es diferente del padre?: {account_code != normalized_parent}")
        print(f"   ✅ ¿Es hija?: {is_child}")
        print()

print("🏁 Análisis completado")