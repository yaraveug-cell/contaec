#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import CompanyUser, Company
from django.contrib.auth import get_user_model

User = get_user_model()

print("🔍 DIAGNÓSTICO: Campo Select de Empresa en Cuentas Bancarias")
print("=" * 60)

# Verificar usuarios existentes
users = User.objects.all()
print(f"\n1. 👥 USUARIOS EN EL SISTEMA:")
print("-" * 30)
for user in users:
    print(f"   ID: {user.id} - Username: {user.username} - Superuser: {user.is_superuser}")

# Verificar empresas existentes  
companies = Company.objects.all()
print(f"\n2. 🏢 EMPRESAS EN EL SISTEMA:")
print("-" * 30)
for company in companies:
    print(f"   ID: {company.id} - Nombre: {company.trade_name}")

# Verificar relaciones CompanyUser
company_users = CompanyUser.objects.all()
print(f"\n3. 🔗 RELACIONES USUARIO-EMPRESA (CompanyUser):")
print("-" * 45)
if company_users.exists():
    for cu in company_users:
        is_active_info = getattr(cu, 'is_active', 'FIELD NOT EXISTS')
        print(f"   Usuario: {cu.user.username} → Empresa: {cu.company.trade_name}")
        print(f"   Rol: {cu.get_role_display()}")
        print(f"   is_active: {is_active_info}")
        print()
else:
    print("   ❌ NO HAY RELACIONES CompanyUser CREADAS")
    print("   ⚠️  ESTE ES EL PROBLEMA: El usuario no está vinculado a ninguna empresa")

# Verificar si existe el campo is_active
print(f"\n4. 🔧 VERIFICACIÓN CAMPO is_active:")
print("-" * 35)

try:
    # Verificar si CompanyUser tiene campo is_active
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info(companies_companyuser)")
    columns = cursor.fetchall()
    
    has_is_active = any('is_active' in col for col in columns)
    print(f"   Campo 'is_active' existe: {has_is_active}")
    
    if has_is_active:
        print("   ✅ El campo exists - problema puede ser filtro")
    else:
        print("   ❌ El campo NO existe - código asume que existe")
        
    print(f"\n   📋 Columnas en CompanyUser:")
    for col in columns:
        print(f"      {col}")
        
except Exception as e:
    print(f"   ❌ Error verificando estructura: {e}")

# Comparar con implementación que funciona (invoicing)
print(f"\n5. 📊 COMPARACIÓN CON ADMIN QUE FUNCIONA:")
print("-" * 45)
print("   Banking usa:")
print("   CompanyUser.objects.filter(user=request.user).values_list('company_id', flat=True)")
print()
print("   Invoicing usa:")  
print("   CompanyUser.objects.filter(user=request.user, is_active=True).values_list('company', flat=True)")
print()
print("   🔍 DIFERENCIAS DETECTADAS:")
print("   1. Banking NO usa filtro is_active=True")
print("   2. Banking usa 'company_id' vs Invoicing usa 'company'")
print("   3. Invoicing verifica que el campo existe primero")

# Diagnóstico final
print(f"\n6. 🎯 DIAGNÓSTICO FINAL:")
print("-" * 25)

if not company_users.exists():
    print("   ❌ PROBLEMA PRINCIPAL: No hay relaciones CompanyUser")
    print("   💡 SOLUCIÓN: Crear relación usuario-empresa")
else:
    print("   ✅ Relaciones CompanyUser existen")
    
    # Verificar el filtro específico que usa banking
    try:
        test_user = users.first() if users.exists() else None
        if test_user:
            banking_query = CompanyUser.objects.filter(
                user=test_user
            ).values_list('company_id', flat=True)
            
            print(f"   🔍 Query Banking para usuario {test_user.username}:")
            print(f"      Empresas encontradas: {list(banking_query)}")
            
            # Probar query de invoicing
            invoicing_query = CompanyUser.objects.filter(
                user=test_user
            ).values_list('company', flat=True)
            
            print(f"   🔍 Query Invoicing para usuario {test_user.username}:")
            print(f"      Empresas encontradas: {list(invoicing_query)}")
            
    except Exception as e:
        print(f"   ❌ Error en consulta de prueba: {e}")

print(f"\n7. 📋 RECOMENDACIONES:")
print("-" * 25)
if not company_users.exists():
    print("   1. Crear relación CompanyUser para el usuario activo")
    print("   2. Verificar que el usuario tenga empresas asignadas")
else:
    print("   1. Verificar implementación del filtro is_active")
    print("   2. Comparar con implementación de invoicing que funciona")
    print("   3. Considerar usar 'company' en lugar de 'company_id'")