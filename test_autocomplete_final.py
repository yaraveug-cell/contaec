#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.companies.models import Company

User = get_user_model()

print("🌐 TEST FINAL: Simulación completa del autocomplete")
print("=" * 52)

# Crear cliente de test
client = Client()

# Login como Yolanda
yolanda = User.objects.get(username='Yolanda')
login_success = client.force_login(yolanda)

print(f"👤 Usuario logueado: {yolanda.username}")

# Simular request de autocomplete
url = '/admin/companies/company/autocomplete/'
params = {'term': 'GUEBER'}

print(f"\n🔗 Testing URL: {url}?term=GUEBER")
print("-" * 45)

response = client.get(url, params)

print(f"📊 Status Code: {response.status_code}")
print(f"📄 Content-Type: {response.get('Content-Type', 'N/A')}")

if response.status_code == 200:
    print(f"✅ Respuesta exitosa!")
    
    # Django autocomplete devuelve JSON
    if 'application/json' in response.get('Content-Type', ''):
        import json
        try:
            data = json.loads(response.content.decode('utf-8'))
            print(f"📋 Datos JSON:")
            print(f"   results: {data.get('results', [])}")
            
            if data.get('results'):
                print(f"✅ ¡AUTOCOMPLETE FUNCIONA!")
                print(f"🎯 La empresa aparece en el resultado")
            else:
                print(f"❌ Sin resultados en JSON")
        except json.JSONDecodeError:
            print(f"❌ Respuesta no es JSON válido")
            print(f"📄 Contenido: {response.content[:200]}")
    else:
        print(f"📄 Contenido (primeros 500 chars):")
        print(f"   {response.content[:500]}")
        
elif response.status_code == 403:
    print(f"❌ Forbidden (403) - Problema de permisos")
    print(f"🔧 Verificar que los permisos están bien aplicados")
    
elif response.status_code == 404:
    print(f"❌ Not Found (404) - URL no encontrada")
    print(f"🔧 Verificar configuración de URLs")
    
else:
    print(f"❌ Error {response.status_code}")
    print(f"📄 Contenido: {response.content[:200]}")

# Verificar URL patterns
print(f"\n🛣️ VERIFICACIÓN DE URLs:")
print("-" * 25)
from django.urls import reverse
try:
    autocomplete_url = reverse('admin:companies_company_autocomplete')
    print(f"✅ URL autocomplete encontrada: {autocomplete_url}")
except:
    print(f"❌ URL autocomplete NO encontrada")
    print(f"🔧 Verificar que CompanyAdmin esté registrado correctamente")

print(f"\n🎯 RESUMEN:")
print("-" * 11)
if response.status_code == 200:
    print(f"✅ El backend funciona correctamente")
    print(f"🌐 Prueba en el navegador en: http://127.0.0.1:8000/admin/banking/bankaccount/add/")
    print(f"💡 Si no funciona en el navegador: Ctrl+F5 (limpiar caché)")
else:
    print(f"❌ Hay un problema en el backend")
    print(f"🔧 Revisar configuración y permisos")