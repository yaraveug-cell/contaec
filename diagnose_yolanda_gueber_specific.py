#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import CompanyUser, Company
from django.contrib.auth import get_user_model

User = get_user_model()

print("🔍 DIAGNÓSTICO ESPECÍFICO: Usuario Yolanda - Empresa GUEBER")
print("=" * 65)

# Obtener usuario Yolanda específicamente
try:
    yolanda = User.objects.get(username='Yolanda')
    print(f"\n1. 👤 USUARIO ACTIVO - YOLANDA:")
    print("-" * 35)
    print(f"   ID: {yolanda.id}")
    print(f"   Username: {yolanda.username}")
    print(f"   Is Superuser: {yolanda.is_superuser}")
    print(f"   Is Active: {yolanda.is_active}")
    
except User.DoesNotExist:
    print("❌ ERROR: Usuario 'Yolanda' no encontrado")
    exit()

# Obtener empresa GUEBER
try:
    gueber = Company.objects.get(trade_name='GUEBER')
    print(f"\n2. 🏢 EMPRESA - GUEBER:")
    print("-" * 25)
    print(f"   ID: {gueber.id}")
    print(f"   Trade Name: {gueber.trade_name}")
    print(f"   Legal Name: {gueber.legal_name}")
    print(f"   Is Active: {gueber.is_active}")
    
except Company.DoesNotExist:
    print("❌ ERROR: Empresa 'GUEBER' no encontrada")
    exit()

# Verificar relación específica Yolanda-GUEBER
print(f"\n3. 🔗 RELACIÓN YOLANDA ↔ GUEBER:")
print("-" * 35)

try:
    yolanda_company_relation = CompanyUser.objects.get(
        user=yolanda, 
        company=gueber
    )
    print(f"   ✅ RELACIÓN EXISTE:")
    print(f"   Usuario: {yolanda_company_relation.user.username}")
    print(f"   Empresa: {yolanda_company_relation.company.trade_name}")
    print(f"   Rol: {yolanda_company_relation.get_role_display()}")
    print(f"   Is Active: {yolanda_company_relation.is_active}")
    print(f"   Created: {yolanda_company_relation.created_at}")
    
except CompanyUser.DoesNotExist:
    print("   ❌ NO EXISTE relación directa Yolanda-GUEBER")
    
    # Buscar todas las relaciones de Yolanda
    yolanda_relations = CompanyUser.objects.filter(user=yolanda)
    if yolanda_relations.exists():
        print(f"   📋 Relaciones de Yolanda encontradas:")
        for rel in yolanda_relations:
            print(f"      → {rel.company.trade_name} ({rel.get_role_display()}) - Active: {rel.is_active}")
    else:
        print(f"   ❌ Yolanda NO tiene relaciones con ninguna empresa")

# SIMULACIÓN EXACTA DEL CÓDIGO DE BANKING ADMIN
print(f"\n4. 🧪 SIMULACIÓN CÓDIGO BANKING ADMIN:")
print("-" * 40)

print(f"   🔍 Simulando: if not request.user.is_superuser:")
print(f"   Usuario Yolanda es superuser: {yolanda.is_superuser}")

if not yolanda.is_superuser:
    print(f"\n   ✅ Entrando en lógica de usuario no-superuser")
    
    # Código ACTUAL de Banking (problemático)
    print(f"\n   📋 CÓDIGO ACTUAL DE BANKING:")
    user_companies_current = CompanyUser.objects.filter(
        user=yolanda
    ).values_list('company_id', flat=True)
    
    print(f"   Query: CompanyUser.objects.filter(user=yolanda).values_list('company_id', flat=True)")
    print(f"   Resultado: {list(user_companies_current)}")
    
    # Código CORRECTO de Invoicing (que funciona)
    print(f"\n   📋 CÓDIGO CORRECTO DE INVOICING:")
    user_companies_correct = CompanyUser.objects.filter(
        user=yolanda,
        is_active=True
    ).values_list('company', flat=True)
    
    print(f"   Query: CompanyUser.objects.filter(user=yolanda, is_active=True).values_list('company', flat=True)")
    print(f"   Resultado: {list(user_companies_correct)}")
    
    # Verificar qué pasaría en formfield_for_foreignkey
    print(f"\n   🎯 SIMULACIÓN formfield_for_foreignkey:")
    
    if user_companies_current:
        print(f"   ✅ Banking encontraría empresas: {list(user_companies_current)}")
        
        # Simular el queryset que se generaría
        from apps.companies.models import Company
        company_queryset = Company.objects.filter(id__in=user_companies_current)
        print(f"   📊 Empresas en queryset: {[c.trade_name for c in company_queryset]}")
        
    else:
        print(f"   ❌ Banking NO encontraría empresas")
        
    if user_companies_correct:
        print(f"   ✅ Invoicing encontraría empresas: {list(user_companies_correct)}")
        
        # Simular el queryset correcto
        company_queryset_correct = Company.objects.filter(id__in=user_companies_correct)
        print(f"   📊 Empresas en queryset correcto: {[c.trade_name for c in company_queryset_correct]}")
        
    else:
        print(f"   ❌ Invoicing NO encontraría empresas")

else:
    print(f"   ⚠️ Yolanda ES superuser - se saltaría el filtro")

# Verificar estado de sesión y permisos
print(f"\n5. 🛡️ VERIFICACIÓN DE PERMISOS Y SESIÓN:")
print("-" * 40)

# Verificar si Yolanda tiene permisos para banking
from django.contrib.auth.models import Permission
banking_perms = Permission.objects.filter(content_type__app_label='banking')

print(f"   📋 Permisos de Banking disponibles:")
for perm in banking_perms:
    has_perm = yolanda.has_perm(f'banking.{perm.codename}')
    print(f"      banking.{perm.codename}: {'✅' if has_perm else '❌'}")

# DIAGNÓSTICO FINAL ESPECÍFICO
print(f"\n6. 🎯 DIAGNÓSTICO FINAL PARA YOLANDA:")
print("-" * 40)

if not yolanda.is_superuser:
    current_query_result = list(CompanyUser.objects.filter(
        user=yolanda
    ).values_list('company_id', flat=True))
    
    correct_query_result = list(CompanyUser.objects.filter(
        user=yolanda,
        is_active=True
    ).values_list('company', flat=True))
    
    print(f"   👤 Usuario: Yolanda (ID: {yolanda.id})")
    print(f"   🏢 Empresa esperada: GUEBER (ID: {gueber.id})")
    print(f"   📊 Query actual devuelve: {current_query_result}")
    print(f"   📊 Query correcto devuelve: {correct_query_result}")
    
    if current_query_result and gueber.id in current_query_result:
        print(f"\n   ✅ El código actual DEBERÍA funcionar")
        print(f"   🤔 Si no aparece GUEBER en el select, el problema puede ser:")
        print(f"      1. Cache del navegador")
        print(f"      2. Sesión no actualizada")  
        print(f"      3. Problema en el widget autocomplete")
        print(f"      4. JavaScript interferencia")
    elif not current_query_result:
        print(f"\n   ❌ El código actual NO funciona - query vacía")
        print(f"   💡 CAUSA: El filtro sin is_active=True no encuentra relaciones")
    else:
        print(f"\n   ❌ El código actual encuentra empresas pero NO GUEBER")
        print(f"   💡 CAUSA: Problema en la lógica de filtrado")
        
    if correct_query_result and gueber.id in correct_query_result:
        print(f"\n   ✅ El código correcto SÍ funcionaría")
        print(f"   🔧 SOLUCIÓN: Aplicar los cambios identificados")
    else:
        print(f"\n   ❌ Ni siquiera el código correcto funcionaría")
        print(f"   🚨 PROBLEMA MÁS PROFUNDO: Revisar datos o lógica de negocio")

else:
    print(f"   ⚠️ Yolanda es superuser - debería ver todas las empresas")
    all_companies = Company.objects.all()
    print(f"   📊 Total empresas que debería ver: {[c.trade_name for c in all_companies]}")

print(f"\n7. 💡 RECOMENDACIONES ESPECÍFICAS:")
print("-" * 35)

if not yolanda.is_superuser:
    if list(CompanyUser.objects.filter(user=yolanda).values_list('company_id', flat=True)):
        print("   1. ✅ Los datos están correctos")
        print("   2. 🔧 Aplicar correcciones de filtrado identificadas")
        print("   3. 🔄 Limpiar cache del navegador")
        print("   4. 🔍 Verificar sesión actualizada")
    else:
        print("   1. ❌ Crear/verificar relación CompanyUser para Yolanda")
        print("   2. 🔄 Verificar que is_active=True en la relación")
else:
    print("   1. ⚠️ Yolanda como superuser debería ver todas las empresas")
    print("   2. 🔍 El problema podría ser de interfaz, no de datos")