#!/usr/bin/env python3
"""
Script para probar el filtrado dinámico en vivo del sistema de facturas
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

import requests
import json
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

def test_live_endpoints():
    """Probar endpoints AJAX en vivo"""
    print("=" * 60)
    print("🧪 PROBANDO ENDPOINTS AJAX EN VIVO")
    print("=" * 60)
    
    # Crear cliente de prueba
    client = Client()
    
    # Obtener un usuario admin para la sesión
    User = get_user_model()
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if not admin_user:
        print("❌ No se encontró usuario administrador")
        return False
    
    # Iniciar sesión
    client.force_login(admin_user)
    
    # Probar endpoint de métodos de pago por empresa
    print("\n1. Probando endpoint: company-payment-methods/")
    try:
        response = client.get(
            '/admin/invoicing/invoice/company-payment-methods/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Respuesta exitosa: {len(data)} empresas configuradas")
            for company_id, config in data.items():
                print(f"      - Empresa {company_id}: {config['company_name']} → {config['name']}")
        else:
            print(f"   ❌ Error: {response.content}")
            
    except Exception as e:
        print(f"   ❌ Error en endpoint company-payment-methods: {e}")
    
    # Probar endpoint de cuentas por método de pago
    print("\n2. Probando endpoint: payment-method-accounts/")
    try:
        response = client.get(
            '/admin/invoicing/invoice/payment-method-accounts/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Respuesta exitosa: {len(data)} métodos de pago configurados")
            for method_id, config in data.items():
                parent = config['parent_account']
                print(f"      - Método {method_id} ({config['method_name']}): Cuenta Padre {parent['code']} - {parent['name']}")
        else:
            print(f"   ❌ Error: {response.content}")
            
    except Exception as e:
        print(f"   ❌ Error en endpoint payment-method-accounts: {e}")
    
    print("\n" + "=" * 60)
    return True

def verify_javascript_loading():
    """Verificar que el JavaScript se esté cargando correctamente"""
    print("📄 VERIFICANDO CARGA DE JAVASCRIPT")
    print("=" * 60)
    
    # Verificar que el archivo JavaScript existe
    js_file = "static/admin/js/integrated_payment_account_handler.js"
    if os.path.exists(js_file):
        print("✅ Archivo JavaScript encontrado")
        
        # Leer contenido y verificar funciones clave
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        key_functions = [
            'IntegratedPaymentAccountHandler',
            'handleCompanyChange',
            'handlePaymentFormChange', 
            'filterChildAccounts',
            'isChildAccount'
        ]
        
        for func in key_functions:
            if func in content:
                print(f"   ✅ Función encontrada: {func}")
            else:
                print(f"   ❌ Función faltante: {func}")
    else:
        print(f"❌ Archivo JavaScript no encontrado: {js_file}")

def test_admin_page_access():
    """Probar acceso a página de administración de facturas"""
    print("\n🌐 VERIFICANDO ACCESO A PÁGINA ADMIN")
    print("=" * 60)
    
    client = Client()
    User = get_user_model()
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if admin_user:
        client.force_login(admin_user)
        
        # Probar acceso a lista de facturas
        try:
            response = client.get('/admin/invoicing/invoice/')
            print(f"Lista de facturas - Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Acceso exitoso a lista de facturas")
            else:
                print(f"   ❌ Error accediendo a lista: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Probar acceso a formulario de añadir factura
        try:
            response = client.get('/admin/invoicing/invoice/add/')
            print(f"Añadir factura - Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Acceso exitoso a formulario de nueva factura")
                
                # Verificar que el JavaScript está en la respuesta
                content = response.content.decode('utf-8')
                if 'integrated_payment_account_handler.js' in content:
                    print("   ✅ JavaScript integrado encontrado en página")
                else:
                    print("   ⚠️  JavaScript integrado no encontrado en página")
            else:
                print(f"   ❌ Error accediendo a formulario: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE FILTRADO DINÁMICO EN VIVO")
    print("Servidor debe estar ejecutándose en http://127.0.0.1:8000/")
    
    # Verificar configuración de datos
    from apps.companies.models import Company, PaymentMethod
    from apps.accounting.models import ChartOfAccounts
    
    companies = Company.objects.filter(payment_method__isnull=False).count()
    payment_methods = PaymentMethod.objects.filter(is_active=True).count()
    accounts = ChartOfAccounts.objects.filter(accepts_movement=True).count()
    
    print(f"\n📊 ESTADO DE DATOS:")
    print(f"   - Empresas con método de pago: {companies}")
    print(f"   - Métodos de pago activos: {payment_methods}")
    print(f"   - Cuentas que aceptan movimiento: {accounts}")
    
    if companies == 0:
        print("⚠️  ADVERTENCIA: No hay empresas configuradas con métodos de pago")
    
    # Ejecutar pruebas
    verify_javascript_loading()
    test_live_endpoints()
    test_admin_page_access()
    
    print("\n🎯 INSTRUCCIONES PARA PROBAR MANUALMENTE:")
    print("1. Abrir: http://127.0.0.1:8000/admin/")
    print("2. Iniciar sesión como administrador")
    print("3. Ir a: Invoicing > Invoices > Add Invoice")
    print("4. Seleccionar una empresa en el campo 'Company'")
    print("5. Observar que 'Forma de Pago' se actualiza automáticamente")
    print("6. Verificar que el campo 'Cuenta' muestra solo cuentas hijas")
    print("7. Cambiar la forma de pago y observar filtrado dinámico de cuentas")
    
    print("\n✅ PRUEBAS COMPLETADAS")