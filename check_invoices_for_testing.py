#!/usr/bin/env python3
"""
Verificar facturas existentes para probar modo edición
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append('.')
django.setup()

def check_existing_invoices():
    """Verificar facturas existentes para testing"""
    
    from apps.invoicing.models import Invoice
    
    print("📋 VERIFICACIÓN DE FACTURAS EXISTENTES")
    print("=" * 50)
    
    # Obtener facturas existentes
    invoices = Invoice.objects.all().order_by('-created_at')
    
    print(f"💼 Total de facturas: {invoices.count()}")
    
    if invoices.exists():
        print(f"\n📄 FACTURAS DISPONIBLES PARA TESTING:")
        
        for i, invoice in enumerate(invoices[:5], 1):  # Mostrar primeras 5
            print(f"   {i}. ID: {invoice.id}")
            print(f"      Número: {invoice.number}")
            print(f"      Cliente: {invoice.customer.trade_name}")
            print(f"      Fecha: {invoice.date}")
            print(f"      Total: ${invoice.total}")
            print(f"      URL de edición: /admin/invoicing/invoice/{invoice.id}/change/")
            print()
        
        if invoices.count() > 5:
            print(f"   ... y {invoices.count() - 5} facturas más")
        
        print(f"🧪 URLS PARA TESTING:")
        print(f"   📝 Crear factura: http://127.0.0.1:8000/admin/invoicing/invoice/add/")
        print(f"   ✏️ Editar factura: http://127.0.0.1:8000/admin/invoicing/invoice/{invoices.first().id}/change/")
        
        print(f"\n✅ INSTRUCCIONES:")
        print(f"   1. Ve a la URL de CREAR para probar que Totales esté oculto")
        print(f"   2. Ve a la URL de EDITAR para probar que Totales sea visible")
        print(f"   3. Ejecuta test_totals_visibility.js en ambas páginas")
        
    else:
        print(f"\n⚠️ NO HAY FACTURAS EXISTENTES")
        print(f"   📝 Necesitas crear al menos una factura para probar modo edición")
        print(f"   🔗 Ve a: http://127.0.0.1:8000/admin/invoicing/invoice/add/")
        print(f"   💡 Crea una factura con líneas para tener datos de prueba")

if __name__ == '__main__':
    try:
        check_existing_invoices()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()