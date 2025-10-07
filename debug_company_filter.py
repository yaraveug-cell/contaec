#!/usr/bin/env python
"""
Script de debug para verificar el filtrado de empresas específicamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.companies.models import Company, CompanyUser
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from apps.core.middleware import CompanyMiddleware

User = get_user_model()

def test_company_filtering():
    print("=" * 60)
    print("🔍 DEBUG: FILTRADO DE EMPRESAS PARA CONTADOR")
    print("=" * 60)
    
    # Obtener usuarios
    try:
        contador = User.objects.get(email='contador@comecuador.com')
        superuser = User.objects.get(email='admin@contaec.com')
        
        print(f"\n👤 CONTADOR: {contador.email}")
        print(f"   - is_superuser: {contador.is_superuser}")
        print(f"   - is_staff: {contador.is_staff}")
        
        # Verificar empresas asignadas directamente
        contador_companies = CompanyUser.objects.filter(user=contador)
        print(f"\n📊 EMPRESAS ASIGNADAS AL CONTADOR:")
        for cu in contador_companies:
            print(f"   - {cu.company.trade_name} (ID: {cu.company.id}) - Rol: {cu.role}")
        
        # Verificar todas las empresas en el sistema
        all_companies = Company.objects.all()
        print(f"\n🏢 TODAS LAS EMPRESAS EN EL SISTEMA:")
        for company in all_companies:
            print(f"   - {company.trade_name} (ID: {company.id})")
        
        # Simular una request del contador
        factory = RequestFactory()
        request = factory.get('/admin/')
        request.user = contador
        request.session = {}
        
        # Aplicar el middleware
        middleware = CompanyMiddleware()
        middleware.process_request(request)
        
        print(f"\n🔒 EMPRESAS EN SESIÓN DESPUÉS DEL MIDDLEWARE:")
        print(f"   - user_companies en sesión: {request.session.get('user_companies', 'NO DEFINIDO')}")
        
        # Verificar el queryset que ve el contador usando el mixin
        from apps.companies.admin import CompanyFilterMixin
        
        class TestAdmin(CompanyFilterMixin):
            def __init__(self):
                pass
        
        admin_instance = TestAdmin()
        
        # Simular get_queryset
        base_queryset = Company.objects.all()
        print(f"\n📋 QUERYSET BASE: {base_queryset.count()} empresas")
        
        # Aplicar filtro del mixin manualmente
        if hasattr(request, 'user') and request.user.is_authenticated:
            if not request.user.is_superuser:
                user_company_ids = request.session.get('user_companies', [])
                if user_company_ids != 'all':
                    filtered_queryset = base_queryset.filter(id__in=user_company_ids)
                    print(f"🎯 QUERYSET FILTRADO: {filtered_queryset.count()} empresas")
                    for company in filtered_queryset:
                        print(f"   - {company.trade_name} (ID: {company.id})")
        
        print(f"\n" + "=" * 60)
        print("✅ RESULTADO DEL DEBUG COMPLETADO")
        print("=" * 60)
        
    except User.DoesNotExist as e:
        print(f"❌ Error: Usuario no encontrado - {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_company_filtering()