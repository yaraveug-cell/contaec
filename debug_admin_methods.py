#!/usr/bin/env python3
"""
Debug: Verificar métodos de la clase InvoiceAdmin
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append('.')
django.setup()

def debug_admin_methods():
    """Verificar que los métodos existan en InvoiceAdmin"""
    from apps.invoicing.admin import InvoiceAdmin
    from apps.invoicing.models import Invoice
    from django.contrib.admin.sites import AdminSite
    
    print("🔍 DEBUGGER DE MÉTODOS - InvoiceAdmin")
    print("=" * 50)
    
    # Crear instancia correctamente
    admin_site = AdminSite()
    admin_instance = InvoiceAdmin(Invoice, admin_site)
    
    print("✅ Instancia creada exitosamente")
    
    # Verificar métodos requeridos
    methods_to_check = [
        'get_urls',
        'company_payment_methods_view', 
        'payment_method_accounts_view'
    ]
    
    print("\n🔍 Verificando métodos:")
    for method_name in methods_to_check:
        has_method = hasattr(admin_instance, method_name)
        callable_method = callable(getattr(admin_instance, method_name, None))
        
        status = "✅" if has_method and callable_method else "❌"
        print(f"   {status} {method_name}: {'Existe y es callable' if has_method and callable_method else 'NO ENCONTRADO'}")
    
    # Listar todos los métodos de la clase
    print("\n📋 Todos los métodos disponibles:")
    all_methods = [method for method in dir(admin_instance) if not method.startswith('_')]
    for i, method in enumerate(sorted(all_methods), 1):
        print(f"   {i:2d}. {method}")

if __name__ == '__main__':
    try:
        debug_admin_methods()
        print("\n🎉 Debug completado sin errores")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()