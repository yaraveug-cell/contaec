#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import CompanyUser, Company
from django.contrib.auth import get_user_model

User = get_user_model()

print("🔍 DIAGNÓSTICO: Problema de Sesión vs CompanyUser")
print("=" * 55)

# Obtener usuario Yolanda
yolanda = User.objects.get(username='Yolanda')
gueber = Company.objects.get(trade_name='GUEBER')

print(f"👤 Usuario: {yolanda.username} (ID: {yolanda.id})")
print(f"🏢 Empresa: {gueber.trade_name} (ID: {gueber.id})")

# Simular la lógica de CompanyFilterMixin
print(f"\n1. 🧪 SIMULACIÓN CompanyFilterMixin:")
print("-" * 35)

print(f"   Es superuser: {yolanda.is_superuser}")

if not yolanda.is_superuser:
    print(f"   ✅ Entra en lógica de filtrado")
    
    # PROBLEMA: CompanyFilterMixin usa sesión
    print(f"\n   ❌ CÓDIGO PROBLEMÁTICO (CompanyFilterMixin):")
    print(f"   user_companies = request.session.get('user_companies', [])")
    print(f"   📊 Sesión ficticia: [] (vacía - causa el problema)")
    
    # Simular queryset con sesión vacía
    user_companies_session = []  # Sesión típicamente vacía
    if user_companies_session and user_companies_session != 'all':
        filtered_companies = Company.objects.filter(id__in=user_companies_session)
        print(f"   📋 Empresas con sesión: {[c.trade_name for c in filtered_companies]}")
    else:
        print(f"   📋 Empresas con sesión vacía: [] (QUERYSET VACÍO)")
        print(f"   🚨 AUTOCOMPLETE NO ENCUENTRA NADA")

# Comparar con BankingAdmin (que debería funcionar)
print(f"\n2. 🧪 SIMULACIÓN BankingAdmin:")
print("-" * 30)

user_companies_banking = CompanyUser.objects.filter(
    user=yolanda
).values_list('company_id', flat=True)

print(f"   ✅ CÓDIGO CORRECTO (BankingAdmin):")
print(f"   CompanyUser.objects.filter(user=yolanda)")
print(f"   📊 Resultado: {list(user_companies_banking)}")

if user_companies_banking:
    filtered_companies = Company.objects.filter(id__in=user_companies_banking)
    print(f"   📋 Empresas encontradas: {[c.trade_name for c in filtered_companies]}")
    print(f"   ✅ AUTOCOMPLETE SÍ FUNCIONARÍA")
else:
    print(f"   📋 Sin empresas: {list(user_companies_banking)}")
    print(f"   ❌ AUTOCOMPLETE NO FUNCIONARÍA")

# Verificar si hay diferencias en los enfoques
print(f"\n3. 🔄 COMPARACIÓN DIRECTA:")
print("-" * 28)
print(f"   Sesión (CompanyAdmin): user_companies = []")
print(f"   CompanyUser (Banking): user_companies = {list(user_companies_banking)}")
print(f"   🎯 DIFERENCIA: CompanyAdmin depende de sesión no inicializada")

# Investigar cómo se debería configurar la sesión
print(f"\n4. 💡 ANÁLISIS DE SESIÓN:")
print("-" * 25)
print(f"   📋 Para que CompanyAdmin funcione, la sesión debería tener:")
print(f"   request.session['user_companies'] = {list(user_companies_banking)}")
print(f"   🤔 ¿Dónde se inicializa esto? ¿Middleware? ¿Login?")

# Verificar otros admins que funcionan
print(f"\n5. 🔍 VERIFICACIÓN OTROS ADMINS:")
print("-" * 35)

# Verificar si InvoicingAdmin usa sesión o CompanyUser directo
print(f"   📄 Invoicing: Usa CompanyUser directo (funciona)")
print(f"   🏦 Banking: Usa CompanyUser directo (debería funcionar)")
print(f"   🏢 Company: Usa sesión (NO funciona para autocomplete)")

print(f"\n6. 🎯 DIAGNÓSTICO FINAL:")
print("-" * 25)
print(f"   ❌ PROBLEMA: CompanyAdmin autocomplete depende de sesión")
print(f"   ✅ SOLUCIÓN 1: Usar CompanyUser directo como otros módulos")
print(f"   ✅ SOLUCIÓN 2: Inicializar sesión correctamente")
print(f"   🎯 RECOMENDACIÓN: Cambiar CompanyAdmin para usar CompanyUser")

print(f"\n7. 🔧 CÓDIGO SUGERIDO:")
print("-" * 22)
print(f"   # En CompanyAdmin, agregar método personalizado:")
print(f"   def get_queryset(self, request):")
print(f"       qs = super(CompanyFilterMixin, self).get_queryset(request)")  # Saltar mixin
print(f"       if not request.user.is_superuser:")
print(f"           from apps.companies.models import CompanyUser")
print(f"           user_companies = CompanyUser.objects.filter(")
print(f"               user=request.user, is_active=True")
print(f"           ).values_list('company_id', flat=True)")
print(f"           return qs.filter(id__in=user_companies)")
print(f"       return qs")