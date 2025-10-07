#!/usr/bin/env python
import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.users.models import User
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# Obtener el usuario contador
contador = User.objects.get(email='contador@comecuador.com')

# Obtener el content type para el modelo User
user_content_type = ContentType.objects.get(app_label='users', model='user')

# Otorgar permisos para el modelo User
permisos_user = Permission.objects.filter(content_type=user_content_type)

print('=== OTORGANDO PERMISOS USER ===')
for permiso in permisos_user:
    if not contador.user_permissions.filter(id=permiso.id).exists():
        contador.user_permissions.add(permiso)
        print(f'Agregado: {permiso}')
    else:
        print(f'Ya tiene: {permiso}')

print('\n=== VERIFICACIÓN FINAL ===')
for p in permisos_user:
    tiene_permiso = contador.has_perm(f'users.{p.codename}')
    print(f'{p.codename}: {"✓" if tiene_permiso else "✗"}')

print('\nPermisos de usuario actualizados correctamente.')