#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import ChartOfAccounts
from apps.companies.models import Company

print("🔍 ANÁLISIS DETALLADO: aux_type en ChartOfAccounts")
print("=" * 52)

# Obtener empresa GUEBER
gueber = Company.objects.get(trade_name='GUEBER')
print(f"🏢 Empresa: {gueber.trade_name} (ID: {gueber.id})")

# Verificar estructura de aux_type
print(f"\n1. 📊 ESTRUCTURA DE aux_type:")
print("-" * 30)

# Obtener todos los valores únicos de aux_type
aux_types = ChartOfAccounts.objects.values_list('aux_type', flat=True).distinct()
aux_types = [t for t in aux_types if t is not None]
print(f"   📋 Valores de aux_type existentes: {aux_types}")

# Contar por aux_type
for aux_type in aux_types:
    count = ChartOfAccounts.objects.filter(aux_type=aux_type).count()
    print(f"   📝 {aux_type}: {count} cuentas")

# Contar cuentas sin aux_type
null_count = ChartOfAccounts.objects.filter(aux_type__isnull=True).count()
print(f"   📝 Sin aux_type (NULL): {null_count} cuentas")

# 2. Cuentas que podrían ser bancarias por código
print(f"\n2. 🏦 CUENTAS POTENCIALMENTE BANCARIAS DE GUEBER:")
print("-" * 49)

# Buscar cuentas que empiecen con códigos típicos de bancos
bank_patterns = ['1.1.01', '1.1.02', '1.1.03']  # Típicos códigos de bancos en Ecuador

for pattern in bank_patterns:
    accounts = ChartOfAccounts.objects.filter(
        company=gueber,
        code__startswith=pattern,
        is_active=True
    )
    
    if accounts.exists():
        print(f"   💰 Código {pattern}.*: {accounts.count()} cuentas")
        for acc in accounts:
            aux_display = acc.aux_type or 'SIN_DEFINIR'
            print(f"      📝 {acc.code} - {acc.name}")
            print(f"         aux_type: {aux_display}")

# 3. Buscar por nombre que contenga palabras bancarias
print(f"\n3. 🔍 BÚSQUEDA POR NOMBRE (palabras bancarias):")
print("-" * 47)

bank_keywords = ['banco', 'cuenta', 'corriente', 'ahorro', 'deposito']
for keyword in bank_keywords:
    accounts = ChartOfAccounts.objects.filter(
        company=gueber,
        name__icontains=keyword,
        is_active=True
    )
    
    if accounts.exists():
        print(f"   🔍 Keyword '{keyword}': {accounts.count()} cuentas")
        for acc in accounts[:3]:  # Primeras 3
            aux_display = acc.aux_type or 'SIN_DEFINIR'
            print(f"      📝 {acc.code} - {acc.name}")
            print(f"         aux_type: {aux_display}")

# 4. Verificar el modelo ChartOfAccounts
print(f"\n4. 📋 VERIFICAR MODELO ChartOfAccounts:")
print("-" * 39)

# Obtener las opciones de aux_type del modelo
from apps.accounting.models import ChartOfAccounts
field = ChartOfAccounts._meta.get_field('aux_type')
if hasattr(field, 'choices') and field.choices:
    print(f"   ⚙️ aux_type.choices definidas:")
    for choice_value, choice_label in field.choices:
        print(f"      📝 '{choice_value}': {choice_label}")
        
        # Contar cuántas cuentas usan cada choice
        count = ChartOfAccounts.objects.filter(aux_type=choice_value).count()
        print(f"         (Usada en {count} cuentas)")
else:
    print(f"   ⚠️ aux_type no tiene choices definidas")
    print(f"   📋 Campo type: {type(field)}")

# 5. Verificar ChartOfAccountsAdmin
print(f"\n5. 🔍 VERIFICAR ChartOfAccountsAdmin:")
print("-" * 36)

try:
    from apps.accounting.admin import ChartOfAccountsAdmin
    from django.contrib import admin
    
    # Verificar si ChartOfAccounts está registrado
    if ChartOfAccounts in admin.site._registry:
        chart_admin = admin.site._registry[ChartOfAccounts]
        
        # Verificar search_fields
        search_fields = getattr(chart_admin, 'search_fields', [])
        print(f"   🔍 search_fields: {search_fields}")
        
        if search_fields:
            print(f"   ✅ ChartOfAccountsAdmin tiene search_fields para autocomplete")
        else:
            print(f"   ❌ ChartOfAccountsAdmin SIN search_fields")
            print(f"   🔧 NECESITA: search_fields = ['code', 'name']")
            
        # Verificar list_filter
        list_filter = getattr(chart_admin, 'list_filter', [])
        print(f"   📋 list_filter: {list_filter}")
        
    else:
        print(f"   ❌ ChartOfAccounts NO registrado en admin")
        
except ImportError as e:
    print(f"   ❌ Error importando ChartOfAccountsAdmin: {e}")

print(f"\n📊 RESUMEN DEL PROBLEMA:")
print("-" * 25)
print(f"   ❌ PROBLEMA PRINCIPAL: No hay cuentas con aux_type='bank'")
print(f"   📝 CAUSA: Las cuentas bancarias no tienen aux_type configurado")
print(f"   🔧 SOLUCIÓN: Actualizar aux_type para cuentas bancarias existentes")

print(f"\n💡 OPCIONES DE SOLUCIÓN:")
print("-" * 25)
print(f"   1. 🔧 Actualizar aux_type manualmente en admin")
print(f"   2. 🔧 Crear script para actualizar aux_type automáticamente")  
print(f"   3. 🔧 Modificar filtro en BankAccountAdmin (menos restrictivo)")
print(f"   4. 🔧 Crear cuentas bancarias nuevas con aux_type='bank'")

print(f"\n🎯 RECOMENDACIÓN INMEDIATA:")
print("-" * 27)
print(f"   📝 Identificar cuentas bancarias por código (1.1.01.xx)")
print(f"   ⚙️ Actualizar aux_type='bank' para estas cuentas")
print(f"   ✅ Verificar que aparezcan en el autocomplete de BankAccount")