#!/usr/bin/env python
import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.users.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

print("=== VERIFICACIÓN DE MODELOS REGISTRADOS ===")

# Ver todos los modelos disponibles
content_types = ContentType.objects.all().order_by('app_label', 'model')

for ct in content_types:
    print(f"{ct.app_label}.{ct.model}")

print("\n=== VERIFICAR ACCESO CONTADOR A COMPANYUSER ===")

try:
    contador_user = User.objects.get(username='contador')
    
    # Verificar permisos específicos para CompanyUser
    companyuser_ct = ContentType.objects.get(app_label='companies', model='companyuser')
    permisos_companyuser = Permission.objects.filter(content_type=companyuser_ct)
    
    print("Permisos para CompanyUser:")
    for permiso in permisos_companyuser:
        tiene_permiso = contador_user.has_perm(permiso.content_type.app_label + '.' + permiso.codename)
        print(f"  {permiso} -> {'✓' if tiene_permiso else '✗'}")
        
    # Verificar si puede acceder al admin de CompanyUser específicamente
    can_view = contador_user.has_perm('companies.view_companyuser')
    can_change = contador_user.has_perm('companies.change_companyuser')
    
    print(f"\nPuede ver CompanyUser: {'✓' if can_view else '✗'}")
    print(f"Puede editar CompanyUser: {'✓' if can_change else '✗'}")
    print(f"Es staff: {'✓' if contador_user.is_staff else '✗'}")

except Exception as e:
    print(f"Error: {e}")