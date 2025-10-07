#!/usr/bin/env python
import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.users.models import User
from apps.companies.models import CompanyUser

# Verificar todos los usuarios
usuarios = User.objects.all()
print("=== USUARIOS EN EL SISTEMA ===")
for user in usuarios:
    print(f"ID: {user.id}, Username: {user.username}, Es staff: {user.is_staff}, Es superuser: {user.is_superuser}")

print("\n=== RELACIONES USUARIO-EMPRESA ===")
relaciones = CompanyUser.objects.all()
for rel in relaciones:
    print(f"{rel.user.username} -> {rel.company.trade_name} ({rel.get_role_display()})")

# Verificar permisos específicos del usuario contador
try:
    contador_user = User.objects.get(username='contador')
    print(f"\n=== PERMISOS USUARIO CONTADOR ===")
    print(f"Es staff: {contador_user.is_staff}")
    print(f"Es superuser: {contador_user.is_superuser}")
    
    # Verificar permisos específicos en CompanyUser
    permisos_grupo = contador_user.user_permissions.all()
    print("Permisos individuales:")
    for permiso in permisos_grupo:
        print(f"  - {permiso}")
    
    # Verificar grupos
    grupos = contador_user.groups.all()
    print("Grupos:")
    for grupo in grupos:
        print(f"  - {grupo.name}")
        
except User.DoesNotExist:
    print("Usuario contador no encontrado")