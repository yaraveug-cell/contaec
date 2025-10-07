#!/usr/bin/env python
"""
Script para verificar que todas las URLs de reportes funcionan correctamente
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.urls import reverse

def test_urls():
    """Prueba todas las URLs de reportes"""
    print("🔍 Verificando URLs de Reportes de Conciliación Bancaria\n")
    
    try:
        # URLs a probar
        urls_to_test = [
            ('banking:reportes_index', 'Índice de Reportes'),
            ('banking:estado_conciliacion', 'Estado de Conciliación por Cuenta'),
            ('banking:diferencias_no_conciliadas', 'Diferencias No Conciliadas'),
            ('banking:extracto_conciliacion_mensual', 'Extracto de Conciliación Mensual'),
        ]
        
        # Probar cada URL
        for url_name, descripcion in urls_to_test:
            try:
                url = reverse(url_name)
                print(f"📋 {descripcion}")
                print(f"   URL: {url}")
                print(f"   ✅ URL resuelta correctamente")
                
            except Exception as e:
                print(f"   ❌ Error resolviendo URL: {str(e)}")
                return False
        
        print(f"\n🎉 ¡Todas las {len(urls_to_test)} URLs se resolvieron correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_urls()
    if success:
        print("\n✅ VERIFICACIÓN COMPLETA: Todos los reportes están configurados correctamente")
    else:
        print("\n❌ VERIFICACIÓN FALLIDA: Hay problemas en la configuración")