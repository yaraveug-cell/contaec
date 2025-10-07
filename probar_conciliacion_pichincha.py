"""
Probar conciliación específicamente con PICHINCHA
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.banking.models import BankAccount, ExtractoBancario

def probar_conciliacion_pichincha():
    """Probar conciliación con PICHINCHA específicamente"""
    
    print("🧪 PRUEBA CONCILIACIÓN PICHINCHA")
    print("="*50)
    
    # Obtener datos PICHINCHA
    try:
        cuenta_pichincha = BankAccount.objects.get(account_number='2201109377')
        extracto_pichincha = ExtractoBancario.objects.filter(bank_account=cuenta_pichincha, status='processed').first()
        
        if not extracto_pichincha:
            print("❌ No hay extracto PICHINCHA procesado")
            return
        
        print(f"✅ Cuenta PICHINCHA: ID {cuenta_pichincha.id}")
        print(f"✅ Extracto PICHINCHA: ID {extracto_pichincha.id}")
        print(f"📊 Status: {extracto_pichincha.status}")
        print(f"📋 Detalles: {extracto_pichincha.detalles.count()}")
        
        # Simular request a conciliación con PICHINCHA
        client = Client()
        
        # Login como admin
        User = get_user_model()
        user = User.objects.filter(is_superuser=True).first()
        if user:
            client.force_login(user)
        
        # Request con PICHINCHA
        url = f'/banking/conciliacion/?bank_account={cuenta_pichincha.id}&extracto={extracto_pichincha.id}'
        print(f"📡 URL PICHINCHA: {url}")
        
        response = client.get(url)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Buscar extractos en dropdown
            print(f"\n🔍 ANÁLISIS EXTRACTO DROPDOWN:")
            import re
            
            # Buscar opciones del dropdown extracto
            extracto_pattern = r'<option value="(\d+)"[^>]*>(.*?)</option>'
            extracto_matches = re.findall(extracto_pattern, content)
            
            for value, text in extracto_matches:
                print(f"   📋 Opción {value}: {text.strip()}")
                if value == str(extracto_pichincha.id):
                    print(f"   🎯 ¡PICHINCHA ENCONTRADO!")
            
            # Buscar badge de extractos
            badge_pattern = r'<span[^>]*class="[^"]*badge[^"]*"[^>]*>(\d+)</span>'
            badge_matches = re.findall(badge_pattern, content)
            
            print(f"\n📊 BADGES ENCONTRADOS:")
            for badge in badge_matches:
                print(f"   🏷️ Badge: {badge}")
            
            # Buscar tabla de extractos
            print(f"\n🔍 TABLA EXTRACTOS:")
            if 'id="transaction-table-extracto"' in content:
                print(f"   ✅ Tabla de extracto encontrada")
                
                # Contar checkboxes de extracto
                checkbox_extracto_count = content.count('name="extracto_items"')
                print(f"   📊 Checkboxes extracto: {checkbox_extracto_count}")
                
                if checkbox_extracto_count > 0:
                    print(f"   🎉 ¡EXTRACTOS PICHINCHA VISIBLES!")
                else:
                    print(f"   ❌ No hay checkboxes de extracto visible")
            else:
                print(f"   ❌ Tabla de extracto no encontrada")
            
            # Test AJAX endpoint específico
            print(f"\n📡 TEST AJAX ENDPOINT:")
            ajax_url = f'/banking/conciliacion/ajax/?bank_account={cuenta_pichincha.id}'
            ajax_response = client.get(ajax_url)
            print(f"   📊 AJAX Status: {ajax_response.status_code}")
            
            if ajax_response.status_code == 200:
                import json
                ajax_data = json.loads(ajax_response.content)
                extractos = ajax_data.get('extractos', [])
                print(f"   📊 AJAX Extractos: {len(extractos)}")
                
                for extracto_data in extractos:
                    print(f"   📋 {extracto_data['value']}: {extracto_data['text']}")
        
        else:
            print(f"❌ Error en request: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    probar_conciliacion_pichincha()