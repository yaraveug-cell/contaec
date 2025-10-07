"""
Script para diagnosticar el filtrado de transacciones y extractos
"""
import os
import django
import sys
from django.test import Client
from urllib.parse import urlencode

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.banking.models import BankTransaction, ExtractoBancarioDetalle

User = get_user_model()

def debug_filtrado_completo():
    """Diagnosticar el filtrado completo con banco + extracto"""
    
    print("🔍 DIAGNÓSTICO FILTRADO BANCO + EXTRACTO")
    print("="*60)
    
    client = Client()
    yolanda = User.objects.get(email='yolismarlen@gmail.com')
    client.force_login(yolanda)
    
    # Parámetros del test
    test_cases = [
        {
            'name': 'Solo banco (cuenta 3)',
            'params': {'bank_account': '3'}
        },
        {
            'name': 'Banco + extracto',
            'params': {'bank_account': '3', 'extracto': '1'}
        },
        {
            'name': 'Con fechas',
            'params': {
                'bank_account': '3', 
                'extracto': '1',
                'fecha_desde': '2025-09-01',
                'fecha_hasta': '2025-10-10'
            }
        }
    ]
    
    for case in test_cases:
        print(f"\n📋 Test: {case['name']}")
        print(f"   Parámetros: {case['params']}")
        
        # Hacer request
        url = '/banking/conciliacion/?' + urlencode(case['params'])
        print(f"   URL: {url}")
        
        try:
            response = client.get(url, SERVER_NAME='localhost')
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.content.decode()
                
                # Buscar indicadores de contenido
                if 'Movimientos del Sistema' in content:
                    print("   ✅ Sección 'Movimientos del Sistema' encontrada")
                    
                    # Contar filas de transacciones (buscar checkboxes)
                    transaction_checkboxes = content.count('name="reconcile_transactions"')
                    print(f"   📊 Transacciones del sistema: {transaction_checkboxes}")
                else:
                    print("   ❌ Sección 'Movimientos del Sistema' NO encontrada")
                
                if 'Extracto Bancario' in content:
                    print("   ✅ Sección 'Extracto Bancario' encontrada")
                    
                    # Contar filas del extracto
                    extracto_checkboxes = content.count('name="reconcile_extracto_items"')
                    print(f"   📊 Items del extracto: {extracto_checkboxes}")
                else:
                    print("   ❌ Sección 'Extracto Bancario' NO encontrada")
                
                # Buscar mensajes de error o vacío
                if 'No hay movimientos para mostrar' in content:
                    print("   ⚠️  Mensaje: 'No hay movimientos para mostrar'")
                
                if 'No hay items del extracto para mostrar' in content:
                    print("   ⚠️  Mensaje: 'No hay items del extracto para mostrar'")
                
                if 'Selecciona un extracto bancario para ver' in content:
                    print("   ℹ️  Mensaje: 'Selecciona un extracto bancario'")
                    
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Verificar datos raw en la base de datos
    print(f"\n📊 DATOS EN BASE DE DATOS:")
    
    # Transacciones para cuenta 3
    transactions = BankTransaction.objects.filter(bank_account_id=3)
    print(f"   Transacciones cuenta 3: {transactions.count()}")
    if transactions.exists():
        for t in transactions:
            print(f"     - {t.transaction_date}: {t.description} (${t.signed_amount})")
    
    # Items del extracto 1
    extracto_items = ExtractoBancarioDetalle.objects.filter(extracto_id=1)
    print(f"   Items extracto 1: {extracto_items.count()}")
    if extracto_items.exists():
        for item in extracto_items:
            print(f"     - {item.fecha}: {item.descripcion} (${item.monto})")

if __name__ == "__main__":
    debug_filtrado_completo()