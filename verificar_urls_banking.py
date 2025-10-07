"""
Script simple para verificar URLs de reportes bancarios
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.urls import reverse_lazy, reverse
from django.core.management import execute_from_command_line

def test_urls():
    """Probar las URLs"""
    
    print("🔗 VERIFICANDO URLs DE REPORTES BANCARIOS")
    print("-" * 50)
    
    urls_to_test = [
        ('banking:reportes_index', 'Índice de Reportes'),
        ('banking:estado_conciliacion', 'Estado de Conciliación'),
        ('banking:diferencias_no_conciliadas', 'Diferencias No Conciliadas'),
        ('banking:extracto_conciliacion_mensual', 'Extracto Mensual'),
        ('banking:conciliacion', 'Conciliación Manual'),
    ]
    
    for url_name, description in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"   ✅ {description}: {url}")
        except Exception as e:
            print(f"   ❌ {description}: Error - {e}")
    
    print(f"\n🌐 URLs de Acceso:")
    print(f"   • http://127.0.0.1:8000/banking/reportes/ - Índice Principal")
    print(f"   • http://127.0.0.1:8000/banking/reportes/estado-conciliacion/ - Estado por Cuenta")
    print(f"   • http://127.0.0.1:8000/banking/reportes/diferencias/ - Diferencias")
    print(f"   • http://127.0.0.1:8000/banking/reportes/extracto-mensual/ - Extracto Mensual")


if __name__ == "__main__":
    test_urls()