#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import CompanyUser, Company
from apps.companies.admin import CompanyAdmin
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.contrib.admin.sites import AdminSite

User = get_user_model()

print("🧪 TEST: CompanyAdmin Autocomplete DESPUÉS de la corrección")
print("=" * 60)

# Configurar test
factory = RequestFactory()
site = AdminSite()
company_admin = CompanyAdmin(Company, site)

# Obtener usuario Yolanda
yolanda = User.objects.get(username='Yolanda')
gueber = Company.objects.get(trade_name='GUEBER')

print(f"👤 Usuario: {yolanda.username} (ID: {yolanda.id})")
print(f"🏢 Empresa: {gueber.trade_name} (ID: {gueber.id})")

# Simular request de autocomplete
request = factory.get('/admin/companies/company/autocomplete/')
request.user = yolanda

print(f"\n🔍 SIMULACIÓN get_queryset() CORREGIDO:")
print("-" * 42)

# Llamar al método corregido
queryset = company_admin.get_queryset(request)

print(f"   ✅ Método: CompanyAdmin.get_queryset()")
print(f"   📊 Queryset: {queryset}")
print(f"   📋 Empresas: {[c.trade_name for c in queryset]}")
print(f"   🔢 Cantidad: {queryset.count()}")

# Verificar si GUEBER está en el queryset
if gueber in queryset:
    print(f"   ✅ GUEBER encontrada: ¡AUTOCOMPLETE FUNCIONARÁ!")
else:
    print(f"   ❌ GUEBER NO encontrada: Autocomplete seguirá fallando")

# Comparar con la lógica original (simulada)
print(f"\n🔄 COMPARACIÓN con lógica original:")
print("-" * 38)

# Simular lógica original de CompanyFilterMixin
all_companies = Company.objects.all()
user_companies_session = []  # Sesión típicamente vacía

if yolanda.is_superuser:
    original_qs = all_companies
    print(f"   👑 Superuser: Todas las empresas ({all_companies.count()})")
else:
    if user_companies_session and user_companies_session != 'all':
        original_qs = all_companies.filter(id__in=user_companies_session)
        print(f"   📊 Sesión con IDs: {user_companies_session}")
    else:
        original_qs = all_companies.none()
        print(f"   📊 Sesión vacía: Queryset.none()")

print(f"   📋 Lógica original: {[c.trade_name for c in original_qs]}")
print(f"   📋 Lógica corregida: {[c.trade_name for c in queryset]}")

# Verificar que el autocomplete field está configurado
print(f"\n⚙️  VERIFICACIÓN DE CONFIGURACIÓN:")
print("-" * 37)

# Verificar search_fields
search_fields = getattr(company_admin, 'search_fields', [])
print(f"   🔍 search_fields: {search_fields}")
if 'trade_name' in search_fields:
    print(f"   ✅ 'trade_name' en search_fields (necesario para autocomplete)")
else:
    print(f"   ⚠️  'trade_name' NO en search_fields (podría afectar autocomplete)")

# Simulación de búsqueda autocomplete
print(f"\n🔍 SIMULACIÓN BÚSQUEDA 'GUEBER':")
print("-" * 34)

if 'trade_name' in search_fields:
    # Simular búsqueda con Q objects
    from django.db.models import Q
    
    search_term = 'GUEBER'
    search_qs = queryset
    
    # Aplicar filtros de búsqueda como lo haría Django admin
    for field in search_fields:
        if field == 'trade_name':
            search_qs = search_qs.filter(Q(trade_name__icontains=search_term))
        elif field == 'legal_name':
            search_qs = search_qs.filter(Q(legal_name__icontains=search_term))
        # etc.
    
    results = list(search_qs)
    print(f"   🎯 Término: '{search_term}'")
    print(f"   📋 Resultados: {[c.trade_name for c in results]}")
    
    if results:
        print(f"   ✅ ¡AUTOCOMPLETE ENCONTRARÁ GUEBER!")
    else:
        print(f"   ❌ Autocomplete no encontrará nada")
else:
    print(f"   ⚠️  Sin search_fields, verificación parcial")

print(f"\n🎯 RESULTADO FINAL:")
print("-" * 19)
if queryset.filter(trade_name='GUEBER').exists():
    print(f"   ✅ ¡PROBLEMA RESUELTO!")
    print(f"   ✅ CompanyAdmin autocomplete funcionará correctamente")
    print(f"   ✅ Usuario Yolanda podrá ver empresa GUEBER")
else:
    print(f"   ❌ Problema persiste")
    print(f"   ❌ Necesita revisión adicional")

print(f"\n📋 RESUMEN TÉCNICO:")
print("-" * 20)
print(f"   🔧 Cambio: get_queryset() usa CompanyUser directo")
print(f"   🚫 Evita: Dependencia de request.session['user_companies']")
print(f"   ✅ Resultado: Consistencia con otros módulos (Banking, etc.)")
print(f"   🎯 Status: Autocomplete debería funcionar ahora")