#!/usr/bin/env python
import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.contrib.admin.sites import site
from apps.companies.models import Company

print("=== VERIFICACIÓN ADMIN DJANGO ===")

# Ver todos los modelos registrados en admin
registered_models = site._registry
print("Modelos registrados en admin:")

for model, admin_class in registered_models.items():
    if 'company' in model.__name__.lower() or 'empresa' in model.__name__.lower():
        print(f"📋 {model.__name__}: {admin_class.__class__.__name__}")
        
        # Verificar si tiene filtrado por empresa
        if hasattr(admin_class, 'get_queryset'):
            print(f"   ✅ Tiene método get_queryset personalizado")
        else:
            print(f"   ❌ NO tiene filtrado por empresa")
            
        # Verificar filtros laterales
        if hasattr(admin_class, 'list_filter'):
            print(f"   🔍 Filtros laterales: {admin_class.list_filter}")
        
        if hasattr(admin_class, 'get_queryset'):
            print(f"   🏢 Filtrado por empresa aplicado")

print(f"\n=== VERIFICACIÓN ESPECÍFICA MODELO COMPANY ===")

from apps.companies.admin import CompanyAdmin
if hasattr(CompanyAdmin, 'get_queryset'):
    print("✅ CompanyAdmin tiene filtrado personalizado")
else:
    print("❌ CompanyAdmin NO tiene filtrado - PROBLEMA IDENTIFICADO")

print(f"\n=== RECOMENDACIÓN ===")
print("Si el problema es en Django Admin, el usuario ve todas las empresas")
print("en la interface admin porque CompanyAdmin no está usando CompanyFilterMixin")
print("\nSolución: Aplicar CompanyFilterMixin a CompanyAdmin también")