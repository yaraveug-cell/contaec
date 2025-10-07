"""
Probar enlaces de botones en conciliación bancaria
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
from django.urls import reverse

def probar_enlaces_conciliacion():
    """Probar enlaces de botones en conciliación"""
    
    print("🔗 PRUEBA DE ENLACES DE CONCILIACIÓN")
    print("="*50)
    
    User = get_user_model()
    user = User.objects.filter(is_superuser=True).first()
    
    if not user:
        print("❌ No se encontró usuario superuser")
        return
    
    print(f"👤 Usuario: {user.username}")
    
    # URLs que deberían funcionar
    urls_to_test = [
        ('admin:banking_extractobancario_add', 'Subir Extracto'),
        ('admin:banking_extractobancario_changelist', 'Historial de Extractos'),
        ('admin:banking_bankaccount_changelist', 'Cuentas Bancarias'),
    ]
    
    print(f"\n🧪 PROBANDO URLs DE ADMIN:")
    
    client = Client()
    client.force_login(user)
    
    for url_name, description in urls_to_test:
        try:
            url = reverse(url_name)
            response = client.get(url)
            
            print(f"   📍 {description}:")
            print(f"      URL: {url}")
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"      ✅ Accesible")
            elif response.status_code == 302:
                print(f"      🔄 Redirección (puede ser normal)")
            else:
                print(f"      ❌ Error")
                
        except Exception as e:
            print(f"   ❌ Error con {description}: {e}")
    
    # Probar la página de conciliación con los nuevos enlaces
    print(f"\n🌐 PROBANDO PÁGINA DE CONCILIACIÓN:")
    
    try:
        response = client.get('/banking/conciliacion/')
        print(f"   - Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Buscar los enlaces actualizados
            enlaces_esperados = [
                'admin/banking/extractobancario/add/',
                'admin/banking/extractobancario/',
                'Subir Extracto',
                'Historial'
            ]
            
            print(f"   📋 Verificando enlaces en HTML:")
            for enlace in enlaces_esperados:
                if enlace in content:
                    print(f"      ✅ {enlace}")
                else:
                    print(f"      ❌ {enlace} (no encontrado)")
        
        elif response.status_code == 302:
            print(f"   🔄 Redirección (normal para vista sin parámetros)")
        else:
            print(f"   ❌ Error de acceso")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Información adicional útil
    print(f"\n📚 INFORMACIÓN ÚTIL:")
    print(f"   🔗 Enlaces corregidos:")
    print(f"      - Subir Extracto: /admin/banking/extractobancario/add/")
    print(f"      - Historial: /admin/banking/extractobancario/")
    print(f"   ✨ Características:")
    print(f"      - Se abren en nueva pestaña (target='_blank')")
    print(f"      - Usan URLs de Django Admin")
    print(f"      - Mantienen iconos y estilos originales")

if __name__ == "__main__":
    probar_enlaces_conciliacion()