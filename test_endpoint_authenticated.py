#!/usr/bin/env python
"""
TEST: Endpoint usando Django test client (con autenticación)
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.companies.models import PaymentMethod

print("🔍 TEST: Endpoint payment-method-accounts (autenticado)")
print("=" * 60)

# Crear client con sesión
client = Client()

# Buscar un usuario admin para autenticación
User = get_user_model()
try:
    admin_user = User.objects.filter(is_staff=True).first()
    if admin_user:
        print(f"👤 Usando usuario: {admin_user.username}")
        client.force_login(admin_user)
    else:
        print("❌ No se encontró usuario admin")
        exit()
except Exception as e:
    print(f"❌ Error obteniendo usuario: {e}")
    exit()

# Test del endpoint
url = "/admin/invoicing/invoice/payment-method-accounts/"
print(f"📡 Haciendo petición autenticada a: {url}")

try:
    response = client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    
    print(f"📊 Status code: {response.status_code}")
    print(f"📄 Content-Type: {response.get('Content-Type', 'No especificado')}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Endpoint funcionando correctamente!")
        print(f"📋 Datos recibidos ({len(data)} métodos):")
        
        for method_id, config in data.items():
            print(f"\n   📋 ID: {method_id}")
            print(f"      Método: {config['method_name']}")
            if 'parent_account' in config:
                parent = config['parent_account']
                print(f"      Cuenta padre: {parent['code']} - {parent['name']}")
                print(f"      ID cuenta: {parent['id']}")
                
        # Verificar específicamente Transferencia
        transferencia_found = False
        for method_id, config in data.items():
            if config['method_name'] == 'Transferencia':
                transferencia_found = True
                print(f"\n🏦 CONFIGURACIÓN TRANSFERENCIA:")
                print(f"   ID método: {method_id}")
                parent = config['parent_account']
                print(f"   Cuenta padre: {parent['code']} - {parent['name']}")
                print(f"   Código: '{parent['code']}'")
                break
                
        if not transferencia_found:
            print("\n❌ Transferencia no encontrada en la respuesta")
    
    else:
        print(f"❌ Error {response.status_code}")
        print(f"Response: {response.content.decode()[:500]}...")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n🏁 Test completado")