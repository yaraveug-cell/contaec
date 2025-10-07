#!/usr/bin/env python
"""
Script de diagnóstico para verificar el sistema de filtrado
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

import requests
from django.test import Client
from django.contrib.auth import get_user_model
from apps.companies.models import Company, CompanyUser

User = get_user_model()

def test_endpoints():
    """Probar endpoints AJAX"""
    
    print("🔍 DIAGNÓSTICO DEL SISTEMA DE FILTRADO")
    print("=" * 60)
    
    # 1. Verificar que el servidor esté corriendo
    print("🌐 Probando conexión al servidor...")
    try:
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        print(f"✅ Servidor responde: Status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Servidor no responde: {e}")
        return False
    
    # 2. Crear cliente de prueba
    print("\n👤 Configurando cliente de prueba...")
    client = Client()
    
    # Obtener un usuario admin
    try:
        admin_user = User.objects.filter(is_staff=True, is_superuser=True).first()
        if not admin_user:
            print("❌ No hay usuarios admin disponibles")
            return False
        
        print(f"✅ Usuario admin encontrado: {admin_user.username}")
        
        # Forzar login del usuario
        client.force_login(admin_user)
        
    except Exception as e:
        print(f"❌ Error configurando usuario: {e}")
        return False
    
    # 3. Probar endpoint de cuentas de caja
    print("\n💰 Probando endpoint de cuentas de caja...")
    try:
        response = client.get('/api/v1/invoicing/ajax/cash-accounts/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Respuesta exitosa: {len(data.get('accounts', []))} cuentas")
            
            for account in data.get('accounts', [])[:3]:
                print(f"   • {account['code']} - {account['name']}")
        else:
            print(f"   ❌ Error: {response.content.decode()}")
            
    except Exception as e:
        print(f"   ❌ Error en endpoint caja: {e}")
    
    # 4. Probar endpoint de todas las cuentas
    print("\n🏦 Probando endpoint de todas las cuentas...")
    try:
        response = client.get('/api/v1/invoicing/ajax/all-accounts/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Respuesta exitosa: {len(data.get('accounts', []))} cuentas")
            
            for account in data.get('accounts', [])[:3]:
                print(f"   • {account['code']} - {account['name']}")
        else:
            print(f"   ❌ Error: {response.content.decode()}")
            
    except Exception as e:
        print(f"   ❌ Error en endpoint todas: {e}")
    
    # 5. Verificar archivos estáticos
    print("\n📁 Verificando archivos JavaScript...")
    js_file = 'static/admin/js/payment_form_handler.js'
    if os.path.exists(js_file):
        print(f"   ✅ {js_file} existe")
        
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'PaymentFormHandler' in content:
                print("   ✅ Clase PaymentFormHandler encontrada")
            if 'ajax/cash-accounts' in content:
                print("   ✅ URLs de endpoints configuradas")
    else:
        print(f"   ❌ {js_file} no encontrado")
    
    print("\n" + "=" * 60)
    print("📊 DIAGNÓSTICO COMPLETADO")
    
    return True

if __name__ == "__main__":
    success = test_endpoints()
    sys.exit(0 if success else 1)