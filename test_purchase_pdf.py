#!/usr/bin/env python

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.suppliers.models import PurchaseInvoice

def test_pdf_generation():
    """Probar generación de PDF de facturas de compra"""
    
    print("=== PRUEBA DE GENERACIÓN PDF FACTURAS DE COMPRA ===")
    
    # Obtener una factura de compra existente
    invoice = PurchaseInvoice.objects.first()
    
    if not invoice:
        print("❌ No hay facturas de compra en el sistema")
        return
    
    print(f"📋 Factura encontrada: {invoice.internal_number}")
    print(f"   Proveedor: {invoice.supplier.trade_name}")
    print(f"   Fecha: {invoice.date}")
    print(f"   Total: ${invoice.total}")
    
    try:
        # Importar y probar el generador
        from apps.suppliers.purchase_invoice_pdf import generate_purchase_invoice_pdf
        
        print("🔄 Generando PDF...")
        pdf_buffer = generate_purchase_invoice_pdf(invoice)
        
        print(f"✅ PDF generado exitosamente")
        print(f"   Tamaño: {len(pdf_buffer.read())} bytes")
        
        print("📄 Prueba completada - PDF funciona correctamente")
        
    except Exception as e:
        print(f"❌ Error al generar PDF: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation()