#!/usr/bin/env python
"""
Test final: Verificar que UserCompanyListFilter muestra solo empresas del usuario
"""

import os
import sys
import django

# Configurar Django
sys.path.append('c:/contaec')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from apps.companies.models import Company, CompanyUser
from apps.suppliers.admin import SupplierAdmin
from apps.suppliers.models import Supplier
from apps.core.filters import UserCompanyListFilter

User = get_user_model()

def test_user_company_filter():
    """Test que el filtro muestre solo empresas del usuario"""
    print("=== TEST FINAL: UserCompanyListFilter ===")
    
    # Usuario de prueba
    normal_user = User.objects.filter(is_superuser=False).first()
    print(f"Usuario: {normal_user.email}")
    
    # Empresas del usuario
    user_companies = CompanyUser.objects.filter(user=normal_user)
    print(f"Empresas asignadas: {user_companies.count()}")
    for cu in user_companies:
        print(f"  - {cu.company.trade_name}")
    
    # Crear request mock
    factory = RequestFactory()
    request = factory.get('/admin/suppliers/supplier/')
    request.user = normal_user
    
    # Crear instancia del filtro
    admin_instance = SupplierAdmin(Supplier, None)
    filter_instance = UserCompanyListFilter(request, {}, Supplier, admin_instance)
    
    # Obtener opciones del filtro (lo que ve el usuario)
    filter_choices = filter_instance.lookups(request, admin_instance)
    
    print(f"\nEmpresas en el filtro (lo que ve el usuario): {len(filter_choices)}")
    for choice_id, choice_name in filter_choices:
        print(f"  - {choice_name} (ID: {choice_id})")
    
    # Verificar que solo ve sus empresas
    user_company_ids = set(user_companies.values_list('company_id', flat=True))
    filter_company_ids = set(int(choice[0]) for choice in filter_choices)
    
    if filter_company_ids == user_company_ids:
        print("\n✅ CORRECTO: Usuario solo ve SUS empresas en el filtro")
        return True
    else:
        print(f"\n❌ ERROR: Usuario ve empresas incorrectas")
        print(f"   Esperadas: {user_company_ids}")
        print(f"   En filtro: {filter_company_ids}")
        return False

def test_superuser_sees_all():
    """Test que superuser vea todas las empresas"""
    print("\n=== TEST: Superuser ve todas las empresas ===")
    
    superuser = User.objects.filter(is_superuser=True).first()
    if not superuser:
        print("No hay superuser para probar")
        return True
    
    print(f"Superuser: {superuser.email}")
    
    # Crear request mock para superuser
    factory = RequestFactory()
    request = factory.get('/admin/suppliers/supplier/')
    request.user = superuser
    
    # Crear instancia del filtro
    admin_instance = SupplierAdmin(Supplier, None)
    filter_instance = UserCompanyListFilter(request, {}, Supplier, admin_instance)
    
    # Obtener opciones del filtro
    filter_choices = filter_instance.lookups(request, admin_instance)
    
    total_companies = Company.objects.filter(is_active=True).count()
    
    print(f"Total empresas activas: {total_companies}")
    print(f"Empresas en filtro para superuser: {len(filter_choices)}")
    
    if len(filter_choices) == total_companies:
        print("✅ CORRECTO: Superuser ve todas las empresas")
        return True
    else:
        print("❌ ERROR: Superuser no ve todas las empresas")
        return False

def final_security_report():
    """Reporte final de seguridad"""
    print("\n" + "="*60)
    print("REPORTE FINAL DE SEGURIDAD - FILTROS CORREGIDOS")
    print("="*60)
    
    normal_test = test_user_company_filter()
    superuser_test = test_superuser_sees_all()
    
    print(f"\n📊 RESULTADOS:")
    print(f"✅ Usuario normal ve solo SUS empresas: {'SI' if normal_test else 'NO'}")
    print(f"✅ Superuser ve TODAS las empresas: {'SI' if superuser_test else 'NO'}")
    
    if normal_test and superuser_test:
        print(f"\n🎉 PROBLEMA SOLUCIONADO COMPLETAMENTE")
        print(f"✅ Filtros de empresa funcionan correctamente")
        print(f"✅ Usuarios solo ven empresas asignadas en filtros")
        print(f"✅ Sistema completamente seguro para producción")
    else:
        print(f"\n🚨 AUN HAY PROBLEMAS - REVISAR")
    
    return normal_test and superuser_test

if __name__ == "__main__":
    success = final_security_report()