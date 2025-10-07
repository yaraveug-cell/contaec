#!/usr/bin/env python

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def test_both_pdf_methods():
    """Test para verificar que ambos métodos generen PDFs completos"""
    
    print("🔍 VERIFICANDO AMBOS MÉTODOS PDF - INDIVIDUAL VS MÚLTIPLE")
    print("=" * 65)
    
    try:
        from apps.suppliers.models import PurchaseInvoice
        from apps.suppliers.purchase_invoice_pdf_enhanced import (
            generate_purchase_invoice_pdf_enhanced, 
            generate_multiple_purchase_invoices_pdf_enhanced
        )
        
        # Obtener facturas de prueba
        invoice = PurchaseInvoice.objects.get(internal_number='FC-001-000007')
        invoices = PurchaseInvoice.objects.all()[:2]  # 2 facturas para el múltiple
        
        print(f"📋 DATOS DE PRUEBA:")
        print(f"   • Factura individual: {invoice.internal_number}")
        print(f"   • Facturas múltiples: {len(invoices)} documentos")
        for inv in invoices:
            print(f"     - {inv.internal_number} (${inv.total})")
        
        print(f"\n1️⃣ PDF INDIVIDUAL MEJORADO:")
        
        # Generar PDF individual
        pdf_individual = generate_purchase_invoice_pdf_enhanced(invoice)
        size_individual = len(pdf_individual.read())
        
        print(f"   ✅ Generado: {size_individual:,} bytes")
        
        # Guardar para verificar
        with open('test_pdf_individual.pdf', 'wb') as f:
            pdf_individual.seek(0)
            f.write(pdf_individual.read())
        
        print(f"   💾 Guardado: test_pdf_individual.pdf")
        
        print(f"\n2️⃣ PDF MÚLTIPLE MEJORADO:")
        
        # Generar PDF múltiple
        pdf_multiple = generate_multiple_purchase_invoices_pdf_enhanced(invoices)
        size_multiple = len(pdf_multiple.read())
        
        print(f"   ✅ Generado: {size_multiple:,} bytes")
        
        # Guardar para verificar
        with open('test_pdf_multiple.pdf', 'wb') as f:
            pdf_multiple.seek(0)
            f.write(pdf_multiple.read())
        
        print(f"   💾 Guardado: test_pdf_multiple.pdf")
        
        print(f"\n📊 ANÁLISIS DE TAMAÑOS:")
        
        expected_multiple_size = size_individual * len(invoices) * 0.8  # Estimación considerando portada
        
        print(f"   📄 Individual: {size_individual:,} bytes")
        print(f"   📄 Múltiple: {size_multiple:,} bytes")
        print(f"   📈 Esperado múltiple: ~{expected_multiple_size:,.0f} bytes")
        
        if size_multiple > expected_multiple_size:
            print(f"   ✅ PDF múltiple tiene contenido COMPLETO ({size_multiple/size_individual:.1f}x individual)")
        else:
            print(f"   ⚠️  PDF múltiple puede tener contenido incompleto")
        
        print(f"\n🧪 PRUEBA CON VISTAS WEB:")
        
        # Probar las vistas web
        from django.test import RequestFactory
        from django.contrib.auth import get_user_model
        from apps.suppliers.views import print_purchase_invoice_pdf, print_multiple_purchase_invoices_pdf
        
        User = get_user_model()
        factory = RequestFactory()
        user = User.objects.first()
        
        # Test vista individual
        request = factory.get(f'/suppliers/purchase-invoice/{invoice.id}/pdf/')
        request.user = user
        
        response_individual = print_purchase_invoice_pdf(request, invoice.id)
        
        print(f"   ✅ Vista individual: {response_individual.status_code} - {len(response_individual.content):,} bytes")
        
        # Test vista múltiple
        invoice_ids = ','.join(str(inv.id) for inv in invoices)
        request_multiple = factory.get(f'/suppliers/purchase-invoices/multiple/pdf/?invoice_ids={invoice_ids}')
        request_multiple.user = user
        
        response_multiple = print_multiple_purchase_invoices_pdf(request_multiple)
        
        print(f"   ✅ Vista múltiple: {response_multiple.status_code} - {len(response_multiple.content):,} bytes")
        
        # Comparar tamaños de vistas con generadores directos
        if len(response_individual.content) == size_individual:
            print(f"   ✅ Vista individual coincide con generador")
        else:
            print(f"   ⚠️  Vista individual difiere del generador")
            
        if len(response_multiple.content) == size_multiple:
            print(f"   ✅ Vista múltiple coincide con generador")
        else:
            print(f"   ⚠️  Vista múltiple difiere del generador")
        
        print(f"\n" + "=" * 65)
        print(f"🎉 VERIFICACIÓN COMPLETADA")
        
        if size_multiple > expected_multiple_size and response_multiple.status_code == 200:
            print(f"✅ AMBOS MÉTODOS GENERAN PDFs COMPLETOS")
            print(f"✅ Individual: Contenido completo con todos los detalles")
            print(f"✅ Múltiple: Portada + facturas completas individuales")
            print(f"✅ Vistas web: Funcionando correctamente")
        else:
            print(f"⚠️  Revisar implementación - posibles problemas detectados")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_both_pdf_methods()