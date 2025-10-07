#!/usr/bin/env python
"""
Script de verificación final de filtros de empresa
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.companies.models import Company, CompanyUser
from apps.core.filters import UserCompanyListFilter

User = get_user_model()

def test_custom_filters():
    print("=" * 70)
    print("🔍 VERIFICACIÓN DE FILTROS PERSONALIZADOS")
    print("=" * 70)
    
    try:
        # Obtener usuarios
        contador = User.objects.get(email='contador@comecuador.com')
        superuser = User.objects.get(email='admin@contaec.com')
        
        print(f"\n👤 CONTADOR: {contador.email}")
        print(f"   - is_superuser: {contador.is_superuser}")
        print(f"   - is_staff: {contador.is_staff}")
        
        # Simular request para el contador
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        # Test del filtro personalizado para contador
        request_contador = MockRequest(contador)
        filter_contador = UserCompanyListFilter(
            request=request_contador, 
            params={}, 
            model=None, 
            model_admin=None
        )
        
        lookups_contador = filter_contador.lookups(request_contador, None)
        print(f"\n📊 FILTRO PERSONALIZADO - CONTADOR VE:")
        if lookups_contador:
            for company_id, company_name in lookups_contador:
                print(f"   - {company_name} (ID: {company_id})")
        else:
            print("   - No hay empresas disponibles")
        
        # Test del filtro personalizado para superuser
        request_superuser = MockRequest(superuser)
        filter_superuser = UserCompanyListFilter(
            request=request_superuser, 
            params={}, 
            model=None, 
            model_admin=None
        )
        
        lookups_superuser = filter_superuser.lookups(request_superuser, None)
        print(f"\n👑 FILTRO PERSONALIZADO - SUPERUSER VE:")
        if lookups_superuser:
            for company_id, company_name in lookups_superuser:
                print(f"   - {company_name} (ID: {company_id})")
        else:
            print("   - No hay empresas disponibles")
        
        # Verificar comparación
        print(f"\n🎯 RESULTADO DE LA VERIFICACIÓN:")
        contador_count = len(lookups_contador) if lookups_contador else 0
        superuser_count = len(lookups_superuser) if lookups_superuser else 0
        
        print(f"   - Contador ve {contador_count} empresa(s)")
        print(f"   - Superuser ve {superuser_count} empresa(s)")
        
        if contador_count == 1 and superuser_count >= contador_count:
            print(f"   ✅ FILTRADO CORRECTO: El contador ve solo sus empresas asignadas")
        else:
            print(f"   ❌ PROBLEMA: El filtrado no funciona correctamente")
        
        # Verificar empresas asignadas directamente
        contador_companies = CompanyUser.objects.filter(user=contador).select_related('company')
        print(f"\n📋 VERIFICACIÓN DIRECTA - EMPRESAS ASIGNADAS AL CONTADOR:")
        for cu in contador_companies:
            print(f"   - {cu.company.trade_name} (ID: {cu.company.id}) - Rol: {cu.role}")
        
        all_companies = Company.objects.all()
        print(f"\n🏢 TOTAL DE EMPRESAS EN EL SISTEMA: {all_companies.count()}")
        for company in all_companies:
            print(f"   - {company.trade_name} (ID: {company.id})")
        
        print(f"\n" + "=" * 70)
        print("✅ VERIFICACIÓN DE FILTROS COMPLETADA")
        print("=" * 70)
        
    except User.DoesNotExist as e:
        print(f"❌ Error: Usuario no encontrado - {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_custom_filters()