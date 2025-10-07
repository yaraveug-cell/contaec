#!/usr/bin/env python

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def test_enhanced_pdf():
    """Test del generador PDF mejorado"""
    
    print("🚀 PROBANDO GENERADOR PDF MEJORADO")
    print("=" * 45)
    
    try:
        from apps.suppliers.models import PurchaseInvoice
        from apps.suppliers.purchase_invoice_pdf_enhanced import generate_purchase_invoice_pdf_enhanced
        
        # Obtener factura de prueba
        invoice = PurchaseInvoice.objects.get(internal_number='FC-001-000007')
        print(f"✅ Factura encontrada: {invoice.internal_number}")
        
        # Generar PDF mejorado
        print("📄 Generando PDF mejorado...")
        pdf_buffer = generate_purchase_invoice_pdf_enhanced(invoice)
        pdf_size = len(pdf_buffer.read())
        
        print(f"✅ PDF generado exitosamente!")
        print(f"📊 Tamaño: {pdf_size:,} bytes")
        
        # Guardar archivo para verificar
        with open('factura_mejorada_test.pdf', 'wb') as f:
            pdf_buffer.seek(0)
            f.write(pdf_buffer.read())
        
        print(f"💾 Archivo guardado: factura_mejorada_test.pdf")
        
        print("\n" + "=" * 45)
        print("🎉 PRUEBA EXITOSA")
        print("El PDF mejorado incluye:")
        print("• Datos completos de la empresa")  
        print("• Información detallada del proveedor")
        print("• Tabla completa de productos")
        print("• Cálculos de IVA por línea")
        print("• Totales desglosados")
        print("• Formato profesional")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_pdf()