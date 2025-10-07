"""
Probar acceso al dashboard con nuevos módulos bancarios
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
from apps.core.permissions import get_available_modules

def probar_dashboard_bancario():
    """Probar dashboard con módulos bancarios"""
    
    print("🏦 PRUEBA DASHBOARD CON MÓDULOS BANCARIOS")
    print("="*60)
    
    User = get_user_model()
    
    # Obtener usuario con acceso a empresas
    user = User.objects.filter(is_superuser=True).first()
    
    if not user:
        print("❌ No se encontró usuario superuser")
        return
    
    print(f"👤 Usuario: {user.username}")
    
    # Verificar módulos disponibles
    modules = get_available_modules(user)
    
    print(f"\n📊 MÓDULOS DISPONIBLES:")
    banking_modules = []
    
    for module in modules:
        print(f"   - {module['icon']} {module['name']}: {module['description']}")
        if 'bank' in module['name'].lower() or 'bancari' in module['name'].lower():
            banking_modules.append(module)
    
    print(f"\n🏦 MÓDULOS BANCARIOS ESPECÍFICOS:")
    for module in banking_modules:
        print(f"   ✅ {module['icon']} {module['name']}")
        print(f"      📍 URL: {module['url']}")
        print(f"      📝 {module['description']}")
        print()
    
    # Probar acceso al dashboard
    print(f"🌐 PROBANDO ACCESO AL DASHBOARD:")
    
    try:
        client = Client()
        client.force_login(user)
        
        response = client.get('/')
        
        print(f"   - Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Dashboard accesible")
            
            # Verificar contenido bancario
            content = response.content.decode('utf-8')
            
            banking_keywords = [
                'Gestión Bancaria',
                'Conciliación Bancaria', 
                'Extractos Bancarios',
                'Cuentas Bancarias',
                'banking/conciliacion',
                'banking/extractobancario'
            ]
            
            found_keywords = []
            for keyword in banking_keywords:
                if keyword in content:
                    found_keywords.append(keyword)
            
            print(f"   📊 Keywords bancarios encontrados: {len(found_keywords)}/{len(banking_keywords)}")
            for keyword in found_keywords:
                print(f"      ✅ {keyword}")
            
            missing = [k for k in banking_keywords if k not in found_keywords]
            if missing:
                print(f"   ❌ Keywords faltantes:")
                for keyword in missing:
                    print(f"      - {keyword}")
        else:
            print(f"   ❌ Error accediendo al dashboard")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Probar acceso directo a conciliación
    print(f"\n🔄 PROBANDO ACCESO DIRECTO A CONCILIACIÓN:")
    
    try:
        response = client.get('/banking/conciliacion/')
        print(f"   - Status conciliación: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Conciliación accesible")
        elif response.status_code == 302:
            print(f"   🔄 Redirección (normal para vista con parámetros)")
        else:
            print(f"   ⚠️  Status inesperado")
    
    except Exception as e:
        print(f"   ❌ Error accediendo a conciliación: {e}")

if __name__ == "__main__":
    probar_dashboard_bancario()