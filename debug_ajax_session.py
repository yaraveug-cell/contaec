"""
Script para probar el AJAX endpoint con sesión de usuario
"""
import os
import django
import sys
from django.test import Client

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def test_ajax_with_session():
    """Probar AJAX con sesión real como lo haría el navegador"""
    
    print("🌐 PRUEBA AJAX CON SESIÓN - Usuario Yolanda")
    print("="*60)
    
    # Crear cliente de prueba
    client = Client()
    
    # 1. Login como Yolanda
    yolanda = User.objects.get(email='yolismarlen@gmail.com')
    client.force_login(yolanda)
    
    print(f"👤 Usuario logueado: {yolanda.email}")
    
    # 2. Primero acceder a la página principal para establecer sesión
    print("\n📄 Accediendo a página de conciliación...")
    main_response = client.get('/banking/conciliacion/')
    print(f"   Status: {main_response.status_code}")
    
    if main_response.status_code != 200:
        print(f"❌ Error accediendo a conciliación: {main_response.status_code}")
        return
    
    # 3. Ahora probar el AJAX
    print("\n🔗 Probando AJAX endpoint...")
    ajax_url = '/banking/conciliacion/ajax/?action=get_extractos&bank_account_id=3'
    ajax_response = client.get(ajax_url)
    
    print(f"   URL: {ajax_url}")
    print(f"   Status: {ajax_response.status_code}")
    
    if ajax_response.status_code == 200:
        try:
            content = ajax_response.json()
            print(f"   ✅ Respuesta JSON: {content}")
            
            if 'extractos' in content and len(content['extractos']) > 0:
                print(f"   🎉 ¡AJAX funcionando! Extractos encontrados: {len(content['extractos'])}")
            else:
                print(f"   ⚠️  AJAX funciona pero no retorna extractos")
                
        except Exception as e:
            print(f"   ❌ Error parseando JSON: {e}")
            print(f"   Raw content: {ajax_response.content}")
    else:
        print(f"   ❌ AJAX falló con status {ajax_response.status_code}")
        if hasattr(ajax_response, 'content'):
            print(f"   Content: {ajax_response.content.decode()[:500]}")
    
    # 4. Probar diferentes cuentas bancarias
    print(f"\n🔄 Probando otras cuentas bancarias...")
    for account_id in [1, 2, 3]:
        test_url = f'/banking/conciliacion/ajax/?action=get_extractos&bank_account_id={account_id}'
        test_response = client.get(test_url)
        
        if test_response.status_code == 200:
            try:
                data = test_response.json()
                count = len(data.get('extractos', []))
                print(f"   Cuenta {account_id}: {count} extractos")
            except:
                print(f"   Cuenta {account_id}: Error en JSON")
        else:
            print(f"   Cuenta {account_id}: Error {test_response.status_code}")

if __name__ == "__main__":
    test_ajax_with_session()