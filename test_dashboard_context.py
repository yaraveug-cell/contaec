#!/usr/bin/env python
import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.users.models import User
from apps.companies.models import Company, CompanyUser
from django.test import RequestFactory
from contaec.views import dashboard_view

# Simular una request para el usuario contador
factory = RequestFactory()
contador_user = User.objects.get(email='contador@comecuador.com')

# Crear una request simulada
request = factory.get('/dashboard/')
request.user = contador_user
request.session = {}

print("=== VERIFICACIÓN DEL CONTEXTO DEL DASHBOARD ===")

# Llamar a la vista dashboard
try:
    from django.contrib.sessions.middleware import SessionMiddleware
    from django.contrib.messages.middleware import MessageMiddleware
    
    # Procesar middleware
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    request.session.save()
    
    # Obtener el contexto que se envía al template
    response = dashboard_view(request)
    
    print("✅ Vista ejecutada correctamente")
    
    # Verificar las empresas en el contexto
    if hasattr(response, 'context_data'):
        context = response.context_data
        if 'user_companies' in context:
            print(f"\n📊 user_companies: {context['user_companies'].count()} empresas")
            for uc in context['user_companies']:
                print(f"   - {uc.company.trade_name}")
        
        if 'all_companies' in context:
            print(f"\n🏢 all_companies: {context['all_companies'].count()} empresas")
            for company in context['all_companies']:
                print(f"   - {company.trade_name}")
                
        if 'available_companies' in context:
            print(f"\n🎯 available_companies: {context['available_companies'].count()} empresas")
            for company in context['available_companies']:
                print(f"   - {company.trade_name}")
    else:
        print("❌ No se pudo obtener el contexto")
        
except Exception as e:
    print(f"❌ Error al ejecutar la vista: {e}")
    
print("\n=== VERIFICACIÓN DIRECTA DE FILTRADO ===")

# Verificar directamente qué ve el contador
if contador_user.is_superuser:
    print("🔓 Usuario es superuser - ve todas las empresas")
    available_companies = Company.objects.all()
else:
    print("🔒 Usuario normal - filtrado aplicado")
    user_companies = CompanyUser.objects.filter(user=contador_user).select_related('company')
    company_ids = user_companies.values_list('company_id', flat=True)
    available_companies = Company.objects.filter(id__in=company_ids)

print(f"\n✅ Empresas disponibles para {contador_user.email}:")
for company in available_companies:
    print(f"   - {company.trade_name} ({company.ruc})")

print(f"\n📈 Total empresas que debería ver: {available_companies.count()}")
print(f"📈 Total empresas en el sistema: {Company.objects.count()}")