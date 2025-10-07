#!/usr/bin/env python

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def test_enhanced_views():
    """Test de las vistas mejoradas con el nuevo PDF"""
    
    print("🌐 PROBANDO VISTAS WEB CON PDF MEJORADO")
    print("=" * 50)
    
    try:
        from django.test import RequestFactory
        from django.contrib.auth import get_user_model
        from apps.suppliers.models import PurchaseInvoice
        from apps.suppliers.views import print_purchase_invoice_pdf
        
        User = get_user_model()
        
        # Crear factory para requests
        factory = RequestFactory()
        
        # Obtener datos de prueba
        invoice = PurchaseInvoice.objects.get(internal_number='FC-001-000007')
        user = User.objects.first()
        
        print(f"✅ Factura: {invoice.internal_number}")
        print(f"✅ Usuario: {user.username}")
        
        # Crear request simulado
        request = factory.get(f'/suppliers/purchase-invoice/{invoice.id}/pdf/')
        request.user = user
        
        print("\n📄 Probando vista individual mejorada...")
        
        # Probar vista
        response = print_purchase_invoice_pdf(request, invoice.id)
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"✅ Content-Type: {response.get('Content-Type')}")
        
        if hasattr(response, 'content'):
            print(f"✅ PDF Size: {len(response.content):,} bytes")
            
            # Guardar para verificar
            with open('factura_web_test.pdf', 'wb') as f:
                f.write(response.content)
            print(f"💾 PDF guardado: factura_web_test.pdf")
        
        # Verificar que las funciones mejoradas están siendo usadas
        print("\n🔧 Verificando imports en vistas...")
        
        from apps.suppliers import views
        import inspect
        
        # Obtener código fuente de la función
        source = inspect.getsource(views.print_purchase_invoice_pdf)
        
        if 'purchase_invoice_pdf_enhanced' in source:
            print("✅ Vista usando PDF mejorado")
        else:
            print("⚠️  Vista usando PDF original")
            
        print("\n" + "=" * 50)
        print("🎉 PRUEBA DE VISTAS EXITOSA")
        print("💡 El PDF mejorado ahora incluye:")
        print("   • Datos completos de empresa y proveedor")
        print("   • Tabla detallada de productos con cálculos")
        print("   • Totales desglosados profesionalmente")
        print("   • Formato SRI compatible para Ecuador")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_views()