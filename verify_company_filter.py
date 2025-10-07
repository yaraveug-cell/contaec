#!/usr/bin/env python
import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.users.models import User
from apps.companies.models import Company, CompanyUser

print("=== VERIFICACIÓN DE EMPRESAS POR USUARIO ===")

# Verificar cada usuario
usuarios = User.objects.all()

for user in usuarios:
    print(f"\n👤 Usuario: {user.email}")
    print(f"   Es superuser: {user.is_superuser}")
    
    if user.is_superuser:
        print("   🔓 SUPERUSER - Ve todas las empresas:")
        all_companies = Company.objects.all()
        for company in all_companies:
            print(f"      - {company.trade_name} ({company.ruc})")
    else:
        print("   🔒 USUARIO NORMAL - Solo ve empresas asignadas:")
        user_companies = CompanyUser.objects.filter(user=user).select_related('company')
        
        if user_companies.exists():
            for cu in user_companies:
                print(f"      - {cu.company.trade_name} ({cu.company.ruc}) - Rol: {cu.get_role_display()}")
        else:
            print("      ❌ No tiene empresas asignadas")

print(f"\n=== RESUMEN DE SEGURIDAD ===")
contador_user = User.objects.filter(email='contador@comecuador.com').first()
if contador_user:
    empresas_contador = CompanyUser.objects.filter(user=contador_user)
    print(f"✅ Contador solo ve {empresas_contador.count()} empresa(s):")
    for cu in empresas_contador:
        print(f"   - {cu.company.trade_name}")
else:
    print("❌ Usuario contador no encontrado")

admin_user = User.objects.filter(is_superuser=True).first()
if admin_user:
    total_empresas = Company.objects.count()
    print(f"✅ Superuser ve todas las {total_empresas} empresas del sistema")
else:
    print("❌ Superuser no encontrado")