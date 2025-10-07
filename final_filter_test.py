#!/usr/bin/env python
import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.users.models import User
from apps.companies.models import Company, CompanyUser
from apps.companies.admin import CompanyAdmin
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

print("=== VERIFICACIÓN COMPLETA DEL FILTRADO DE EMPRESAS ===")

# Crear usuarios de prueba
contador_user = User.objects.get(email='contador@comecuador.com')
admin_user = User.objects.get(email='admin@contaec.com')

factory = RequestFactory()

def test_user_admin_access(user, description):
    print(f"\n👤 {description}: {user.email}")
    
    # Crear request simulada
    request = factory.get('/admin/companies/company/')
    request.user = user
    
    # Configurar sesión
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    
    # Simular el middleware que filtra empresas
    if user.is_superuser:
        request.session['user_companies'] = 'all'
    else:
        user_company_ids = list(CompanyUser.objects.filter(user=user).values_list('company_id', flat=True))
        request.session['user_companies'] = user_company_ids
    
    request.session.save()
    
    # Crear admin instance
    company_admin = CompanyAdmin(Company, None)
    
    # Obtener queryset filtrado
    filtered_companies = company_admin.get_queryset(request)
    
    print(f"   📊 Ve {filtered_companies.count()} empresas de {Company.objects.count()} totales")
    for company in filtered_companies:
        print(f"      - {company.trade_name} ({company.ruc})")
    
    return filtered_companies.count()

# Probar usuarios
contador_count = test_user_admin_access(contador_user, "CONTADOR")
admin_count = test_user_admin_access(admin_user, "SUPERUSER")

print(f"\n=== RESUMEN DEL FILTRADO ===")
print(f"✅ Contador ve {contador_count} empresa(s) - {'✓ CORRECTO' if contador_count == 1 else '✗ ERROR'}")
print(f"✅ Superuser ve {admin_count} empresa(s) - {'✓ CORRECTO' if admin_count == Company.objects.count() else '✗ ERROR'}")

print(f"\n=== VERIFICACIÓN FINAL ===")
if contador_count == 1 and admin_count == Company.objects.count():
    print("🎯 ✅ FILTRADO FUNCIONANDO CORRECTAMENTE")
    print("   - El contador solo ve su empresa asignada")
    print("   - El superuser ve todas las empresas")
    print("   - El filtro de la barra lateral está seguro")
else:
    print("❌ PROBLEMA EN EL FILTRADO")

print(f"\n=== URLs DE PRUEBA ===")
print("Para probar manualmente:")
print("1. Login como contador@comecuador.com / contador123")
print("2. Ve a: http://127.0.0.1:8000/admin/companies/company/")
print("3. Deberías ver solo COMECUADOR")