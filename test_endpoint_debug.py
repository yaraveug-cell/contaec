#!/usr/bin/env python
"""
TEST: Verificación directa del endpoint con debugging
"""

import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

print("🔍 TEST: Endpoint payment-method-accounts (DEBUG)")
print("=" * 50)

# Test del endpoint usando el servidor real
url = "http://127.0.0.1:8000/admin/invoicing/invoice/payment-method-accounts/"

headers = {
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    print(f"📡 Haciendo petición a: {url}")
    
    response = requests.get(url, headers=headers)
    
    print(f"📊 Status code: {response.status_code}")
    print(f"📄 Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
    print(f"📏 Content-Length: {len(response.content)} bytes")
    
    print(f"\n📋 Raw content (primeros 1000 chars):")
    print(f"{response.text[:1000]}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"\n✅ JSON válido!")
            print(f"📊 Tipo: {type(data)}")
            print(f"📊 Keys: {list(data.keys()) if isinstance(data, dict) else 'No es dict'}")
            
            for method_id, config in data.items():
                print(f"\n   ID: {method_id}")
                print(f"   Config: {config}")
                
        except Exception as json_error:
            print(f"❌ Error parseando JSON: {json_error}")
    
except requests.exceptions.ConnectionError:
    print("❌ Error de conexión. ¿Está el servidor Django ejecutándose?")
    
except Exception as e:
    print(f"❌ Error inesperado: {e}")

print("\n🏁 Test completado")