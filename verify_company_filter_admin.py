#!/usr/bin/env python
"""
Verificar filtros de empresa en el admin de Django
Especificamente en el menu de proveedores
"""

import os
import sys
import django

# Configurar Django
sys.path.append('c:/contaec')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.contrib import admin
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from apps.companies.models import Company, CompanyUser
from apps.suppliers.models import Supplier
from apps.suppliers.admin import SupplierAdmin

User = get_user_model()

def test_company_filter_in_admin():
    """Probar el filtro de empresas en el admin"""
    print("=== VERIFICANDO FILTRO DE EMPRESAS EN ADMIN ===")
    
    # Obtener usuario normal (no superuser)
    normal_user = User.objects.filter(is_superuser=False).first()
    if not normal_user:
        print("ERROR: No hay usuarios normales para probar")
        return
    
    print(f"Usuario de prueba: {normal_user.email}")
    
    # Verificar empresas asignadas
    user_companies = CompanyUser.objects.filter(user=normal_user)
    print(f"Empresas asignadas al usuario: {user_companies.count()}")
    for cu in user_companies:
        print(f"  - {cu.company.trade_name} (ID: {cu.company.id})")
    
    # Crear request mock
    factory = RequestFactory()
    request = factory.get('/admin/suppliers/supplier/')
    request.user = normal_user
    
    # Simular sesión con empresas del usuario
    user_company_ids = list(user_companies.values_list('company_id', flat=True))
    request.session = {'user_companies': user_company_ids}
    
    print(f"Session user_companies: {user_company_ids}")
    
    # Obtener instancia del admin
    admin_instance = SupplierAdmin(Supplier, admin.site)
    
    print("\n=== PROBANDO list_filter ===")
    if hasattr(admin_instance, 'list_filter'):
        print(f"list_filter configurado: {admin_instance.list_filter}")
        
        # Verificar si 'company' está en list_filter
        if 'company' in admin_instance.list_filter:
            print("PROBLEMA ENCONTRADO: 'company' está en list_filter")
            print("Esto muestra TODAS las empresas en el filtro lateral")
        else:
            print("OK: 'company' no está en list_filter básico")
    
    print("\n=== PROBANDO get_list_filter ===")
    if hasattr(admin_instance, 'get_list_filter'):
        list_filter = admin_instance.get_list_filter(request)
        print(f"list_filter dinámico: {list_filter}")
    else:
        print("No tiene get_list_filter personalizado")
    
    print("\n=== VERIFICANDO FILTROS PERSONALIZADOS ===")
    # Verificar si usa filtros personalizados de UserCompanyListFilter
    from apps.core.filters import UserCompanyListFilter
    
    for filter_item in admin_instance.list_filter:
        if hasattr(filter_item, '__name__'):
            print(f"Filtro: {filter_item.__name__}")
        else:
            print(f"Filtro: {filter_item}")
    
    print("\n=== PROBANDO QUERYSET DE EMPRESAS EN FILTRO ===")
    # Simular lo que vería el usuario en el filtro
    all_companies = Company.objects.all()
    print(f"Total empresas en BD: {all_companies.count()}")
    
    for company in all_companies:
        print(f"  - {company.trade_name} (ID: {company.id})")
    
    # Si usa filtro estándar 'company', mostraría todas estas
    # Si usa UserCompanyListFilter, debería mostrar solo las del usuario

def check_filter_implementation():
    """Verificar como está implementado el filtro"""
    print("\n" + "="*60)
    print("VERIFICANDO IMPLEMENTACION DEL FILTRO")
    print("="*60)
    
    # Leer el admin actual
    admin_instance = SupplierAdmin(Supplier, admin.site)
    
    print("list_filter actual:")
    for i, filter_item in enumerate(admin_instance.list_filter):
        print(f"  {i+1}. {filter_item}")
    
    # Verificar si hay UserCompanyListFilter
    from apps.core.filters import UserCompanyListFilter
    
    uses_custom_filter = False
    for filter_item in admin_instance.list_filter:
        if filter_item == UserCompanyListFilter or (
            hasattr(filter_item, '__name__') and 
            'UserCompany' in filter_item.__name__
        ):
            uses_custom_filter = True
            break
        if filter_item == 'company':
            print("PROBLEMA: Usa filtro 'company' estándar")
            print("SOLUCION: Cambiar por UserCompanyListFilter")
    
    if uses_custom_filter:
        print("OK: Usa filtro personalizado")
    else:
        print("PROBLEMA: No usa filtro personalizado UserCompanyListFilter")

def propose_fix():
    """Proponer la corrección"""
    print("\n" + "="*60)
    print("SOLUCION PROPUESTA")
    print("="*60)
    
    print("PROBLEMA IDENTIFICADO:")
    print("- El list_filter usa 'company' en lugar de UserCompanyListFilter")
    print("- Esto muestra TODAS las empresas en el filtro lateral")
    print("- Usuario puede VER (aunque no acceder a) empresas de otros")
    
    print("\nSOLUCION:")
    print("Cambiar en apps/suppliers/admin.py:")
    print("  DE:   list_filter = (..., 'company', ...)")
    print("  A:    list_filter = (..., UserCompanyListFilter, ...)")
    
    print("\nIMPACTO:")
    print("✅ Usuario solo verá SU empresa en el filtro")
    print("✅ Mejor experiencia de usuario")
    print("✅ Mayor seguridad visual")

if __name__ == "__main__":
    test_company_filter_in_admin()
    check_filter_implementation()
    propose_fix()