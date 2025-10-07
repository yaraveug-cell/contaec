"""
Test directo para simular el navegador con Yolanda
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

def test_browser_simulation():
    """Simular exactamente lo que hace el navegador"""
    
    print("🌐 SIMULACIÓN EXACTA DEL NAVEGADOR")
    print("="*50)
    
    client = Client()
    yolanda = User.objects.get(email='yolismarlen@gmail.com')
    client.force_login(yolanda)
    
    # Test exacto como en el navegador
    url = '/banking/conciliacion/?bank_account=3&extracto=1&fecha_desde=&fecha_hasta='
    print(f"📡 URL: {url}")
    
    response = client.get(url, SERVER_NAME='localhost')
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode()
        
        # Buscar específicamente la variable extracto_items en el contexto
        print(f"\n🔍 ANÁLISIS DEL CONTEXTO:")
        
        # Verificar si hay badge con número de extractos
        import re
        badge_match = re.search(r'<span class="badge bg-info ms-2">(\d+)</span>', content)
        if badge_match:
            count = badge_match.group(1)
            print(f"   ✅ Badge extractos encontrado: {count} items")
        else:
            print(f"   ❌ Badge extractos NO encontrado")
        
        # Buscar checkboxes de extracto
        extracto_checkboxes = content.count('name="reconcile_extracto_items"')
        print(f"   📊 Checkboxes de extracto: {extracto_checkboxes}")
        
        # Buscar tabla de extractos
        if 'id="check-all-extracto"' in content:
            print(f"   ✅ Checkbox 'Seleccionar todos extracto' encontrado")
        else:
            print(f"   ❌ Checkbox 'Seleccionar todos extracto' NO encontrado")
        
        # Buscar el loop del extracto
        if '{% for item in extracto_items %}' in content or 'extr_' in content:
            print(f"   ✅ Loop de extracto items detectado")
        else:
            print(f"   ❌ Loop de extracto items NO detectado")
        
        # Buscar mensajes específicos
        if 'No hay items del extracto para mostrar' in content:
            print(f"   ⚠️  Mensaje: 'No hay items del extracto para mostrar'")
        elif 'Selecciona un extracto bancario para ver' in content:
            print(f"   ⚠️  Mensaje: 'Selecciona un extracto bancario'")
        
        # Contar filas de la tabla de extracto
        tbody_extracto_count = 0
        lines = content.split('\n')
        in_extracto_tbody = False
        for line in lines:
            if 'extracto-checkbox' in line:
                tbody_extracto_count += 1
        
        print(f"   📊 Filas reales de extracto en HTML: {tbody_extracto_count}")
        
        # Imprimir fragmento específico de la sección del extracto
        print(f"\n📄 FRAGMENTO HTML SECCIÓN EXTRACTO:")
        start = content.find('Extracto Bancario')
        if start > -1:
            end = content.find('</div>', start + 500)  # Buscar cierre
            fragment = content[start:end+6] if end > -1 else content[start:start+800]
            print(f"   {fragment[:500]}...")
    
    else:
        print(f"❌ Error HTTP: {response.status_code}")

if __name__ == "__main__":
    test_browser_simulation()