#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from apps.companies.models import Company

User = get_user_model()

print("🔐 DIAGNÓSTICO Y CORRECCIÓN DE PERMISOS")
print("=" * 42)

# Obtener usuario Yolanda
yolanda = User.objects.get(username='Yolanda')
print(f"👤 Usuario: {yolanda.username} (ID: {yolanda.id})")

# Verificar permisos actuales para Company
content_type = ContentType.objects.get_for_model(Company)
company_permissions = Permission.objects.filter(content_type=content_type)

print(f"\n📋 PERMISOS DISPONIBLES PARA COMPANY:")
print("-" * 37)
for perm in company_permissions:
    has_perm = yolanda.has_perm(f'companies.{perm.codename}')
    status = "✅" if has_perm else "❌"
    print(f"   {status} {perm.codename}: {perm.name}")

# Verificar grupos del usuario
print(f"\n👥 GRUPOS DEL USUARIO:")
print("-" * 22)
user_groups = yolanda.groups.all()
if user_groups:
    for group in user_groups:
        print(f"   📂 {group.name}")
        group_perms = group.permissions.filter(content_type=content_type)
        for perm in group_perms:
            print(f"      ✅ {perm.codename}")
else:
    print(f"   ❌ Sin grupos asignados")

# Verificar si necesita permisos específicos
required_perms = ['view_company', 'change_company']
print(f"\n🎯 PERMISOS REQUERIDOS PARA AUTOCOMPLETE:")
print("-" * 42)

missing_perms = []
for perm_code in required_perms:
    has_perm = yolanda.has_perm(f'companies.{perm_code}')
    status = "✅" if has_perm else "❌"
    print(f"   {status} companies.{perm_code}")
    if not has_perm:
        missing_perms.append(perm_code)

if missing_perms:
    print(f"\n🔧 ASIGNAR PERMISOS FALTANTES:")
    print("-" * 31)
    
    for perm_code in missing_perms:
        try:
            permission = Permission.objects.get(
                codename=perm_code,
                content_type=content_type
            )
            yolanda.user_permissions.add(permission)
            print(f"   ✅ Asignado: {perm_code}")
        except Permission.DoesNotExist:
            print(f"   ❌ No existe: {perm_code}")
    
    # Verificar después de asignar
    print(f"\n🔍 VERIFICACIÓN DESPUÉS DE ASIGNAR:")
    print("-" * 35)
    for perm_code in required_perms:
        has_perm = yolanda.has_perm(f'companies.{perm_code}')
        status = "✅" if has_perm else "❌"
        print(f"   {status} companies.{perm_code}")
        
else:
    print(f"\n✅ TODOS LOS PERMISOS YA ESTÁN ASIGNADOS")

# Verificar otros módulos para comparar
print(f"\n🔄 COMPARAR CON OTROS MÓDULOS:")
print("-" * 32)

modules_to_check = [
    ('banking', 'BankAccount'),
    ('invoicing', 'SalesInvoice'),
    ('accounting', 'JournalEntry'),
]

for app_name, model_name in modules_to_check:
    try:
        # Obtener el modelo dinámicamente
        from django.apps import apps
        model = apps.get_model(app_name, model_name)
        ct = ContentType.objects.get_for_model(model)
        
        view_perm = f'{app_name}.view_{model_name.lower()}'
        change_perm = f'{app_name}.change_{model_name.lower()}'
        
        has_view = yolanda.has_perm(view_perm)
        has_change = yolanda.has_perm(change_perm)
        
        view_status = "✅" if has_view else "❌"
        change_status = "✅" if has_change else "❌"
        
        print(f"   📦 {app_name}.{model_name}:")
        print(f"      {view_status} view   {change_status} change")
        
    except Exception as e:
        print(f"   📦 {app_name}.{model_name}: Error - {e}")

print(f"\n🎯 RESULTADO:")
print("-" * 11)
# Verificar una vez más después de los cambios
final_view = yolanda.has_perm('companies.view_company')
final_change = yolanda.has_perm('companies.change_company')

if final_view and final_change:
    print(f"   ✅ PERMISOS CORREGIDOS")
    print(f"   ✅ Autocomplete debería funcionar ahora")
    print(f"   🔄 Reinicia el servidor Django y prueba de nuevo")
elif final_view:
    print(f"   ⚠️ Solo permiso de vista - podría no ser suficiente")
    print(f"   🔧 Considera asignar también change_company")
else:
    print(f"   ❌ Permisos aún faltantes")
    print(f"   🔧 Revisa la configuración de grupos o permisos manuales")