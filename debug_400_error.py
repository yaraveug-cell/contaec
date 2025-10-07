"""
Script para diagnosticar el error 400 en la conciliación
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

def debug_400_error():
    """Diagnosticar por qué la conciliación retorna 400"""
    
    print("🐛 DIAGNÓSTICO ERROR 400")
    print("="*40)
    
    client = Client()
    yolanda = User.objects.get(email='yolismarlen@gmail.com')
    client.force_login(yolanda)
    
    # Probar con diferentes parámetros
    test_cases = [
        {'url': '/banking/conciliacion/', 'desc': 'Sin parámetros'},
        {'url': '/banking/conciliacion/?bank_account=3', 'desc': 'Solo bank_account'},
        {'url': '/banking/conciliacion/?bank_account=3&extracto=', 'desc': 'bank_account + extracto vacío'},
    ]
    
    for case in test_cases:
        print(f"\n📝 {case['desc']}:")
        print(f"   URL: {case['url']}")
        
        response = client.get(case['url'])
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            # Mostrar contenido del error
            content = response.content.decode()[:500]
            print(f"   Error content: {content}")
        else:
            print(f"   ✅ Éxito")

if __name__ == "__main__":
    debug_400_error()