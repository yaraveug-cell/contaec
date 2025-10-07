#!/usr/bin/env python
"""
Script de prueba para verificar el sistema de permisos del dashboard
Ejecutar con: python test_permissions.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append('.')
django.setup()

from django.contrib.auth import get_user_model
from apps.companies.models import Company, CompanyUser
from apps.core.permissions import get_available_modules

User = get_user_model()

def test_permissions():
    """Prueba el sistema de permisos para diferentes roles"""
    
    print("🔍 TESTING DASHBOARD PERMISSIONS SYSTEM")
    print("=" * 50)
    
    # Crear usuarios de prueba si no existen
    users = {}
    
    # Superuser
    superuser, created = User.objects.get_or_create(
        email='admin@contaec.com',
        defaults={
            'username': 'admin',
            'first_name': 'Admin',
            'last_name': 'Sistema',
            'is_superuser': True,
            'is_staff': True,
            'is_active': True
        }
    )
    if created:
        superuser.set_password('admin123')
        superuser.save()
    users['superuser'] = superuser
    
    # Usuario normal
    normal_user, created = User.objects.get_or_create(
        email='contador@empresa.com',
        defaults={
            'username': 'contador',
            'first_name': 'Contador',
            'last_name': 'Empresa',
            'is_active': True
        }
    )
    if created:
        normal_user.set_password('contador123')
        normal_user.save()
    users['normal_user'] = normal_user
    
    # Crear empresa de prueba
    company, created = Company.objects.get_or_create(
        ruc='1234567890001',
        defaults={
            'name': 'Empresa de Prueba S.A.',
            'address': 'Av. Principal 123',
            'phone': '0999999999',
            'email': 'info@empresa.com'
        }
    )
    
    # Asignar usuario a empresa con rol de contador
    company_user, created = CompanyUser.objects.get_or_create(
        user=normal_user,
        company=company,
        defaults={'role': 'accountant'}
    )
    
    # Test para cada usuario
    for user_type, user in users.items():
        print(f"\n👤 USER: {user.full_name} ({user_type})")
        print(f"📧 Email: {user.email}")
        print(f"🏢 Is Superuser: {user.is_superuser}")
        print(f"📋 Is Staff: {user.is_staff}")
        
        # Obtener empresas del usuario
        if user.is_superuser:
            user_companies = CompanyUser.objects.all()
        else:
            user_companies = CompanyUser.objects.filter(user=user)
        
        print(f"🏭 Empresas asignadas: {user_companies.count()}")
        for cu in user_companies:
            print(f"   - {cu.company.name} (Rol: {cu.role})")
        
        # Obtener módulos disponibles
        modules = get_available_modules(user)
        print(f"\n📋 Módulos disponibles: {len(modules)}")
        
        for module in modules:
            print(f"   ✅ {module['name']}")
            print(f"      📝 {module['description']}")
            print(f"      🔗 {module['url']}")
            print(f"      🎨 {module['color']}")
            print()
        
        print("-" * 50)

if __name__ == '__main__':
    test_permissions()