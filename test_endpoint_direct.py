#!/usr/bin/env python
"""
TEST: Verificación directa del endpoint payment-method-accounts
"""

import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

print("🔍 TEST: Endpoint payment-method-accounts")
print("=" * 50)

# Test del endpoint usando el servidor real
url = "http://127.0.0.1:8000/admin/invoicing/invoice/payment-method-accounts/"

headers = {
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    print(f"📡 Haciendo petición a: {url}")
    print(f"🔧 Headers: {headers}")
    
    response = requests.get(url, headers=headers)
    
    print(f"📊 Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Endpoint funcionando correctamente!")
        print(f"📋 Datos recibidos:")
        
        for method_id, config in data.items():
            print(f"\n   ID: {method_id}")
            print(f"   Método: {config['method_name']}")
            if 'parent_account' in config:
                parent = config['parent_account']
                print(f"   Cuenta padre: {parent['code']} - {parent['name']}")
                print(f"   ID cuenta: {parent['id']}")
            
    else:
        print(f"❌ Error {response.status_code}")
        print(f"📄 Response: {response.text[:500]}...")

except requests.exceptions.ConnectionError:
    print("❌ Error de conexión. ¿Está el servidor Django ejecutándose?")
    print("💡 Ejecuta: python manage.py runserver")
    
except Exception as e:
    print(f"❌ Error inesperado: {e}")

print("\n🏁 Test completado")