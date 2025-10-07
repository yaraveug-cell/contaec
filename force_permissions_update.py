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

print("🔄 FORZAR ACTUALIZACIÓN DE PERMISOS")
print("=" * 36)

# Obtener usuario Yolanda
yolanda = User.objects.get(username='Yolanda')
print(f"👤 Usuario: {yolanda.username} (ID: {yolanda.id})")

# Limpiar caché de permisos del usuario
if hasattr(yolanda, '_perm_cache'):
    del yolanda._perm_cache
    print(f"🗑️ Caché de permisos limpiado")

if hasattr(yolanda, '_group_perm_cache'):
    del yolanda._group_perm_cache
    print(f"🗑️ Caché de permisos de grupo limpiado")

# Refrescar el usuario desde la base de datos
yolanda.refresh_from_db()
print(f"🔄 Usuario refrescado desde DB")

# Verificar permisos directamente en la base de datos
content_type = ContentType.objects.get_for_model(Company)

print(f"\n📊 VERIFICACIÓN DIRECTA EN BASE DE DATOS:")
print("-" * 41)

# Permisos directos del usuario
user_perms = yolanda.user_permissions.filter(content_type=content_type)
print(f"   👤 Permisos directos del usuario:")
for perm in user_perms:
    print(f"      ✅ {perm.codename}")

# Permisos a través de grupos
print(f"   👥 Permisos a través de grupos:")
group_perms = Permission.objects.filter(
    group__user=yolanda,
    content_type=content_type
)
for perm in group_perms:
    print(f"      ✅ {perm.codename} (grupo: {perm.group_set.filter(user=yolanda).first()})")

# Verificar con has_perm() después de limpiar caché
print(f"\n🔍 VERIFICACIÓN CON has_perm() (sin caché):")
print("-" * 42)

view_perm = yolanda.has_perm('companies.view_company')
change_perm = yolanda.has_perm('companies.change_company')

view_status = "✅" if view_perm else "❌"
change_status = "✅" if change_perm else "❌"

print(f"   {view_status} companies.view_company")
print(f"   {change_status} companies.change_company")

# Si aún no funciona, crear un grupo y asignar permisos
if not view_perm or not change_perm:
    print(f"\n🔧 CREANDO GRUPO 'Company Users':")
    print("-" * 33)
    
    group, created = Group.objects.get_or_create(name='Company Users')
    if created:
        print(f"   ✅ Grupo creado: {group.name}")
    else:
        print(f"   ℹ️ Grupo ya existe: {group.name}")
    
    # Asignar permisos al grupo
    required_perms = ['view_company', 'change_company']
    for perm_code in required_perms:
        permission = Permission.objects.get(
            codename=perm_code,
            content_type=content_type
        )
        group.permissions.add(permission)
        print(f"   ✅ Permiso agregado al grupo: {perm_code}")
    
    # Agregar usuario al grupo
    yolanda.groups.add(group)
    print(f"   ✅ Usuario agregado al grupo")
    
    # Limpiar caché otra vez
    if hasattr(yolanda, '_perm_cache'):
        del yolanda._perm_cache
    if hasattr(yolanda, '_group_perm_cache'):
        del yolanda._group_perm_cache
    
    # Verificar de nuevo
    print(f"\n🔍 VERIFICACIÓN FINAL:")
    print("-" * 20)
    
    view_perm_final = yolanda.has_perm('companies.view_company')
    change_perm_final = yolanda.has_perm('companies.change_company')
    
    view_status = "✅" if view_perm_final else "❌"
    change_status = "✅" if change_perm_final else "❌"
    
    print(f"   {view_status} companies.view_company")
    print(f"   {change_status} companies.change_company")
    
    if view_perm_final and change_perm_final:
        print(f"\n✅ ¡PERMISOS CORREGIDOS!")
        print(f"🔄 REINICIA EL SERVIDOR DJANGO")
        print(f"🌐 Prueba el autocomplete en el navegador")
    else:
        print(f"\n❌ Permisos aún no funcionan")
        print(f"🔧 Podrían necesitar más configuración")

else:
    print(f"\n✅ ¡PERMISOS YA FUNCIONAN!")
    print(f"🔄 El problema podría estar en otro lugar")

# Verificar si el servidor necesita reinicio
print(f"\n⚠️ IMPORTANTE:")
print("-" * 12)
print(f"   🔄 Los cambios de permisos requieren reiniciar el servidor Django")
print(f"   🛑 Detén el servidor (Ctrl+C)")
print(f"   ▶️ Ejecuta: python manage.py runserver")
print(f"   🌐 Luego prueba el autocomplete de nuevo")