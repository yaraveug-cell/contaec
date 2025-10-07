#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounting.models import ChartOfAccounts
from apps.companies.models import Company

User = get_user_model()

print("🔍 ANÁLISIS: Campo 'chart_account' en BankAccount")
print("=" * 50)

# Obtener usuario Yolanda y empresa GUEBER
yolanda = User.objects.get(username='Yolanda')
gueber = Company.objects.get(trade_name='GUEBER')

print(f"👤 Usuario: {yolanda.username} (ID: {yolanda.id})")
print(f"🏢 Empresa: {gueber.trade_name} (ID: {gueber.id})")

# 1. Verificar cuentas contables disponibles
print(f"\n1. 📊 CUENTAS CONTABLES DISPONIBLES:")
print("-" * 39)

# Verificar todas las cuentas
all_accounts = ChartOfAccounts.objects.all()
print(f"   📋 Total cuentas contables: {all_accounts.count()}")

# Verificar cuentas con aux_type='bank'
bank_accounts = ChartOfAccounts.objects.filter(aux_type='bank')
print(f"   🏦 Cuentas con aux_type='bank': {bank_accounts.count()}")

if bank_accounts.exists():
    print(f"   📝 Cuentas bancarias encontradas:")
    for acc in bank_accounts[:10]:  # Primeras 10
        print(f"      ✅ {acc.code} - {acc.name} (Empresa: {acc.company})")
else:
    print(f"   ❌ NO hay cuentas con aux_type='bank'")

# 2. Verificar filtro por empresa del usuario
print(f"\n2. 🔍 FILTRADO POR EMPRESA USUARIO:")
print("-" * 35)

# Simular el filtro que hace BankAccountAdmin.formfield_for_foreignkey
filtered_accounts = ChartOfAccounts.objects.filter(
    aux_type='bank',
    is_active=True
)
print(f"   📊 Cuentas aux_type='bank' + is_active=True: {filtered_accounts.count()}")

if filtered_accounts.exists():
    print(f"   📝 Cuentas filtradas:")
    for acc in filtered_accounts:
        print(f"      ✅ {acc.code} - {acc.name} (Empresa: {acc.company})")
        print(f"         - is_active: {acc.is_active}")
        print(f"         - aux_type: {acc.aux_type}")
else:
    print(f"   ❌ NO hay cuentas que cumplan los criterios")

# 3. Verificar si hay cuentas de la empresa GUEBER
print(f"\n3. 🏢 CUENTAS DE LA EMPRESA GUEBER:")
print("-" * 34)

gueber_accounts = ChartOfAccounts.objects.filter(company=gueber)
print(f"   📊 Total cuentas de GUEBER: {gueber_accounts.count()}")

gueber_bank_accounts = ChartOfAccounts.objects.filter(
    company=gueber,
    aux_type='bank',
    is_active=True
)
print(f"   🏦 Cuentas bancarias de GUEBER: {gueber_bank_accounts.count()}")

if gueber_bank_accounts.exists():
    print(f"   📝 Cuentas bancarias GUEBER:")
    for acc in gueber_bank_accounts:
        print(f"      ✅ {acc.code} - {acc.name}")
else:
    print(f"   ❌ GUEBER no tiene cuentas con aux_type='bank'")

# 4. Buscar cuentas que podrían ser bancarias
print(f"\n4. 🔍 BUSCAR CUENTAS POTENCIALMENTE BANCARIAS:")
print("-" * 47)

# Buscar por código (típicamente 1.1.01.xx para bancos)
potential_bank_accounts = ChartOfAccounts.objects.filter(
    company=gueber,
    code__startswith='1.1.01',  # Activo corriente - Bancos
    is_active=True
)
print(f"   💰 Cuentas que inician con '1.1.01': {potential_bank_accounts.count()}")

if potential_bank_accounts.exists():
    print(f"   📝 Posibles cuentas bancarias:")
    for acc in potential_bank_accounts:
        print(f"      🏦 {acc.code} - {acc.name}")
        print(f"         - aux_type: {acc.aux_type or 'NO_DEFINIDO'}")
else:
    print(f"   ❌ No hay cuentas con código 1.1.01.xx")

# 5. Verificar permisos para ChartOfAccounts
print(f"\n5. 🔐 VERIFICAR PERMISOS ChartOfAccounts:")
print("-" * 39)

chart_view_perm = yolanda.has_perm('accounting.view_chartofaccounts')
chart_change_perm = yolanda.has_perm('accounting.change_chartofaccounts')

view_status = "✅" if chart_view_perm else "❌"
change_status = "✅" if chart_change_perm else "❌"

print(f"   {view_status} accounting.view_chartofaccounts")
print(f"   {change_status} accounting.change_chartofaccounts")

if not chart_view_perm:
    print(f"   ⚠️ SIN PERMISO DE VISTA - Puede afectar autocomplete")

# 6. Analizar el problema
print(f"\n6. 🎯 ANÁLISIS DEL PROBLEMA:")
print("-" * 30)

print(f"   📊 Configuración actual en BankAccountAdmin:")
print(f"   kwargs['queryset'] = ChartOfAccounts.objects.filter(")
print(f"       aux_type='bank',")
print(f"       is_active=True")
print(f"   )")

# Verificar si el problema es:
issues = []

if not chart_view_perm:
    issues.append("❌ Sin permisos para ver ChartOfAccounts")

if not gueber_bank_accounts.exists():
    issues.append("❌ No hay cuentas con aux_type='bank' en GUEBER")

if not filtered_accounts.exists():
    issues.append("❌ No hay cuentas que cumplan el filtro global")

if issues:
    print(f"\n   🚨 PROBLEMAS IDENTIFICADOS:")
    for issue in issues:
        print(f"      {issue}")
else:
    print(f"   ✅ No se detectaron problemas obvios")

# 7. Posibles soluciones
print(f"\n7. 💡 POSIBLES SOLUCIONES:")
print("-" * 28)

if not gueber_bank_accounts.exists() and potential_bank_accounts.exists():
    print(f"   🔧 SOLUCIÓN 1: Actualizar aux_type de cuentas bancarias")
    print(f"      UPDATE chart_of_accounts SET aux_type='bank'")
    print(f"      WHERE company_id={gueber.id} AND code LIKE '1.1.01%'")

if not chart_view_perm:
    print(f"   🔧 SOLUCIÓN 2: Asignar permisos ChartOfAccounts a Yolanda")
    print(f"      view_chartofaccounts, change_chartofaccounts")

print(f"   🔧 SOLUCIÓN 3: Modificar filtro en BankAccountAdmin")
print(f"      Usar filtro más amplio o por empresa del usuario")

print(f"   🔧 SOLUCIÓN 4: Verificar configuración autocomplete")
print(f"      Asegurar que ChartOfAccountsAdmin tiene search_fields")

print(f"\n📋 RECOMENDACIÓN:")
print("-" * 17)
if not gueber_bank_accounts.exists() and potential_bank_accounts.exists():
    print(f"   🎯 PRIMERA PRIORIDAD: Configurar aux_type='bank'")
    print(f"   📝 Las cuentas existen pero no tienen aux_type correcto")
elif not chart_view_perm:
    print(f"   🎯 PRIMERA PRIORIDAD: Asignar permisos ChartOfAccounts")
    print(f"   🔐 Sin permisos no puede ver las opciones de autocomplete")
else:
    print(f"   🎯 Revisar configuración de autocomplete en ChartOfAccountsAdmin")