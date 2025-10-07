#!/usr/bin/env python

import os
import sys
import django
from io import StringIO

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def test_pdf_urls_direct():
    """Test directo de URLs PDF sin autenticación"""
    
    print("=== TEST DIRECTO URLs PDF ===")
    
    try:
        from django.test import Client, RequestFactory
        from django.contrib.auth import get_user_model
        from apps.suppliers.models import PurchaseInvoice
        from apps.suppliers.views import print_purchase_invoice_pdf, print_multiple_purchase_invoices_pdf
        
        User = get_user_model()
        
        # Crear factory para requests
        factory = RequestFactory()
        
        print("\n1️⃣ CREANDO REQUEST SIMULADO:")
        
        # Obtener factura de prueba
        invoice = PurchaseInvoice.objects.first()
        if not invoice:
            print("   ❌ No hay facturas para probar")
            return
            
        print(f"   ✅ Factura de prueba: {invoice.internal_number}")
        
        # Crear request simulado
        request = factory.get(f'/suppliers/purchase-invoice/{invoice.id}/pdf/')
        
        # Obtener usuario de prueba
        user = User.objects.first()
        if not user:
            print("   ❌ No hay usuarios para probar")
            return
            
        print(f"   ✅ Usuario de prueba: {user.username}")
        request.user = user
        
        print("\n2️⃣ PROBANDO VISTA INDIVIDUAL:")
        try:
            response = print_purchase_invoice_pdf(request, invoice.id)
            print(f"   ✅ Vista individual: Status {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Content-Type: {response.get('Content-Type', 'N/A')}")
                if hasattr(response, 'content'):
                    print(f"   ✅ Tamaño PDF: {len(response.content)} bytes")
        except Exception as e:
            print(f"   ❌ Error en vista individual: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n3️⃣ PROBANDO VISTA MÚLTIPLE:")
        try:
            # Crear request POST para múltiples
            post_data = {
                'invoice_ids': [str(invoice.id)]
            }
            request_multiple = factory.post('/suppliers/purchase-invoices/multiple/pdf/', post_data)
            request_multiple.user = user
            
            response = print_multiple_purchase_invoices_pdf(request_multiple)
            print(f"   ✅ Vista múltiple: Status {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Content-Type: {response.get('Content-Type', 'N/A')}")
                if hasattr(response, 'content'):
                    print(f"   ✅ Tamaño PDF: {len(response.content)} bytes")
        except Exception as e:
            print(f"   ❌ Error en vista múltiple: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n4️⃣ VERIFICANDO RESOLUCIÓN URLs:")
        try:
            from django.urls import reverse, resolve
            
            # Probar reverse lookup
            url_individual = reverse('suppliers:print_purchase_invoice_pdf', args=[invoice.id])
            print(f"   ✅ URL individual: {url_individual}")
            
            url_multiple = reverse('suppliers:print_multiple_purchase_invoices_pdf')
            print(f"   ✅ URL múltiple: {url_multiple}")
            
            # Probar resolve
            resolved_individual = resolve(url_individual)
            print(f"   ✅ Función individual: {resolved_individual.func.__name__}")
            
            resolved_multiple = resolve(url_multiple) 
            print(f"   ✅ Función múltiple: {resolved_multiple.func.__name__}")
            
        except Exception as e:
            print(f"   ❌ Error resolviendo URLs: {e}")
        
        print("\n5️⃣ VERIFICANDO CONFIGURACIÓN COMPLETA:")
        
        # Verificar settings
        from django.conf import settings
        print(f"   ✅ DEBUG: {settings.DEBUG}")
        print(f"   ✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        
        # Verificar middlewares de autenticación
        auth_middlewares = [m for m in settings.MIDDLEWARE if 'auth' in m.lower()]
        print(f"   ✅ Auth middlewares: {len(auth_middlewares)}")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*50)
    print("✅ TEST URLS COMPLETADO")

if __name__ == "__main__":
    test_pdf_urls_direct()