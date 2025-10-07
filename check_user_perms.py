#!/usr/bin/env python
import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.users.models import User
from django.contrib.auth.models import Permission

# Obtener el usuario contador
contador = User.objects.get(email='contador@comecuador.com')

# Verificar permisos para el modelo User
user_perms = Permission.objects.filter(content_type__app_label='users', content_type__model='user')

print('=== PERMISOS MODELO USER ===')
for p in user_perms:
    tiene_permiso = contador.has_perm(f'users.{p.codename}')
    print(f'{p.codename}: {"✓" if tiene_permiso else "✗"}')

print(f'\n=== ID USUARIO CONTADOR ===')
print(f'ID: {contador.id}')
print(f'Email: {contador.email}')
print(f'Es staff: {contador.is_staff}')

# Verificar si puede cambiar su propio usuario específicamente
can_change_self = contador.has_perm('users.change_user')
print(f'\nPuede cambiar usuario: {"✓" if can_change_self else "✗"}')