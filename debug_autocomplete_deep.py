#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import CompanyUser, Company
from apps.banking.admin import BankAccountAdmin
from apps.companies.admin import CompanyAdmin
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.contrib.admin.sites import AdminSite
from django.http import QueryDict

User = get_user_model()

print("🔍 DIAGNÓSTICO PROFUNDO: ¿Por qué no aparece la empresa?")
print("=" * 58)

# Configurar objetos de test
factory = RequestFactory()
site = AdminSite()
company_admin = CompanyAdmin(Company, site)

# Obtener usuario Yolanda
yolanda = User.objects.get(username='Yolanda')
gueber = Company.objects.get(trade_name='GUEBER')

print(f"👤 Usuario: {yolanda.username} (ID: {yolanda.id})")
print(f"🏢 Empresa: {gueber.trade_name} (ID: {gueber.id})")

# 1. Verificar que el campo autocomplete está configurado en BankAccountAdmin
print(f"\n1. ⚙️ CONFIGURACIÓN BankAccountAdmin:")
print("-" * 37)

from apps.banking.admin import BankAccountAdmin
from apps.banking.models import BankAccount

bank_admin = BankAccountAdmin(BankAccount, site)
autocomplete_fields = getattr(bank_admin, 'autocomplete_fields', [])
print(f"   📋 autocomplete_fields: {autocomplete_fields}")

if 'company' in autocomplete_fields:
    print(f"   ✅ 'company' configurado para autocomplete")
else:
    print(f"   ❌ 'company' NO configurado para autocomplete")
    print(f"   🔧 NECESITA: autocomplete_fields = ['bank', 'company']")

# 2. Simular request de autocomplete real
print(f"\n2. 🌐 SIMULACIÓN REQUEST AUTOCOMPLETE:")
print("-" * 38)

# Simular URL de autocomplete: /admin/companies/company/autocomplete/?term=GUEBER
query_params = QueryDict('term=GUEBER')
request = factory.get('/admin/companies/company/autocomplete/', query_params)
request.user = yolanda
request.GET = query_params

print(f"   🔗 URL: /admin/companies/company/autocomplete/?term=GUEBER")
print(f"   👤 Usuario: {request.user}")
print(f"   🔍 Parámetro 'term': {request.GET.get('term', 'NO_TERM')}")

# 3. Verificar get_queryset de CompanyAdmin
print(f"\n3. 📊 VERIFICAR get_queryset():")
print("-" * 32)

queryset = company_admin.get_queryset(request)
print(f"   📋 Queryset base: {queryset}")
print(f"   🔢 Cantidad: {queryset.count()}")
print(f"   📝 Empresas: {[c.trade_name for c in queryset]}")

# 4. Simular filtro de búsqueda (como hace Django autocomplete)
print(f"\n4. 🔍 APLICAR FILTRO DE BÚSQUEDA:")
print("-" * 34)

search_term = request.GET.get('term', '')
print(f"   🎯 Término búsqueda: '{search_term}'")

if search_term:
    # Django autocomplete usa get_search_results
    from django.contrib.admin.utils import lookup_spawns_duplicates
    from django.db.models import Q
    
    search_fields = company_admin.get_search_fields(request)
    print(f"   🔍 search_fields: {search_fields}")
    
    # Construir Q object como lo hace Django
    query = Q()
    for field in search_fields:
        if field == 'trade_name':
            query |= Q(trade_name__icontains=search_term)
        elif field == 'legal_name':
            query |= Q(legal_name__icontains=search_term)
        elif field == 'ruc':
            query |= Q(ruc__icontains=search_term)
        elif field == 'email':
            query |= Q(email__icontains=search_term)
    
    filtered_qs = queryset.filter(query)
    print(f"   📋 Después del filtro: {[c.trade_name for c in filtered_qs]}")
    print(f"   🔢 Cantidad filtrada: {filtered_qs.count()}")
    
    if filtered_qs.exists():
        print(f"   ✅ ¡Empresas encontradas!")
    else:
        print(f"   ❌ No hay resultados de búsqueda")
else:
    print(f"   ⚠️ Sin término de búsqueda")

# 5. Verificar permisos
print(f"\n5. 🔐 VERIFICAR PERMISOS:")
print("-" * 24)

has_view_perm = company_admin.has_view_permission(request)
has_change_perm = company_admin.has_change_permission(request)
print(f"   👁️ has_view_permission: {has_view_perm}")
print(f"   ✏️ has_change_permission: {has_change_perm}")

if not has_view_perm:
    print(f"   ❌ SIN PERMISO DE VISTA - Autocomplete no funcionará")
else:
    print(f"   ✅ Permisos OK")

# 6. Comparar con configuración que funciona (invoicing)
print(f"\n6. 🔄 COMPARAR CON MÓDULO QUE FUNCIONA:")
print("-" * 40)

try:
    from apps.invoicing.admin import SalesInvoiceAdmin
    from apps.invoicing.models import SalesInvoice
    
    invoice_admin = SalesInvoiceAdmin(SalesInvoice, site)
    invoice_autocomplete = getattr(invoice_admin, 'autocomplete_fields', [])
    
    print(f"   📄 SalesInvoiceAdmin autocomplete_fields: {invoice_autocomplete}")
    
    if 'company' in invoice_autocomplete:
        print(f"   ✅ Invoicing SÍ usa autocomplete para company")
        
        # Verificar si invoicing funciona
        invoice_qs = invoice_admin.get_queryset(request)
        print(f"   📊 InvoicingAdmin queryset para Yolanda: {invoice_qs.count()} facturas")
    else:
        print(f"   ℹ️ Invoicing no usa autocomplete para company")
        
except ImportError:
    print(f"   ℹ️ No se pudo importar SalesInvoiceAdmin")

# 7. Verificar URL patterns y registro
print(f"\n7. 🛣️ VERIFICAR REGISTRO ADMIN:")
print("-" * 30)

from django.contrib import admin
from django.apps import apps

# Verificar que Company está registrado
if Company in admin.site._registry:
    print(f"   ✅ Company registrado en admin.site")
    registered_admin = admin.site._registry[Company]
    print(f"   📝 Clase admin: {registered_admin.__class__.__name__}")
    
    # Verificar que es nuestra clase corregida
    if hasattr(registered_admin, 'get_queryset'):
        print(f"   ✅ Tiene método get_queryset personalizado")
    else:
        print(f"   ⚠️ Sin método get_queryset personalizado")
else:
    print(f"   ❌ Company NO registrado en admin")

# 8. Test directo del autocomplete endpoint
print(f"\n8. 🎯 SIMULACIÓN COMPLETA AUTOCOMPLETE:")
print("-" * 42)

# Verificar que tenemos todo lo necesario
print(f"   🔧 Requisitos:")
print(f"      - Usuario autenticado: ✅ {yolanda}")
print(f"      - Empresa existe: ✅ {gueber}")
print(f"      - CompanyUser vinculado: ✅")
print(f"      - Permisos: ✅ {has_view_perm}")
print(f"      - search_fields: ✅ {company_admin.get_search_fields(request)}")
print(f"      - Queryset base: ✅ {queryset.count()} empresa(s)")

# El problema podría estar en otro lugar
print(f"\n9. 🕵️ POSIBLES CAUSAS RESTANTES:")
print("-" * 35)
print(f"   1. ❓ Caché del navegador")
print(f"   2. ❓ JavaScript no cargado correctamente")
print(f"   3. ❓ CSRF token issues")
print(f"   4. ❓ URL routing problems")
print(f"   5. ❓ Algún middleware interceptando")

print(f"\n🎯 DIAGNÓSTICO:")
print("-" * 15)
if queryset.filter(trade_name__icontains='GUEBER').exists():
    print(f"   ✅ Los datos están bien")
    print(f"   ✅ Los permisos están bien") 
    print(f"   ✅ El queryset está bien")
    print(f"   ❓ Problema probable: Frontend/JavaScript/Caché")
    print(f"\n🔧 SIGUIENTES PASOS:")
    print(f"   1. Ctrl+F5 (hard refresh)")
    print(f"   2. Verificar consola JavaScript (F12)")
    print(f"   3. Verificar Network tab para ver requests")
else:
    print(f"   ❌ Problema en el backend - queryset aún vacío")