#!/usr/bin/env python
"""
Script para probar y depurar el desglose dinámico de IVA
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.invoicing.models import Invoice, InvoiceLine
from apps.inventory.models import Product
from apps.companies.models import Company
from django.contrib.auth.models import User

def test_tax_breakdown():
    """Probar el cálculo de desglose de IVA"""
    print("=== PRUEBA DE DESGLOSE DINÁMICO DE IVA ===")
    
    # Buscar una factura existente
    invoices = Invoice.objects.all()[:3]
    
    if not invoices:
        print("❌ No se encontraron facturas para probar")
        return
    
    for invoice in invoices:
        print(f"\n📋 FACTURA #{invoice.number} - {invoice.customer_name}")
        print(f"   Empresa: {invoice.company.name}")
        print(f"   Líneas: {invoice.lines.count()}")
        
        # Probar el método get_tax_breakdown
        try:
            breakdown = invoice.get_tax_breakdown()
            print(f"   ✅ get_tax_breakdown() ejecutado correctamente")
            print(f"   📊 Breakdown: {breakdown}")
            
            if breakdown:
                for rate, data in breakdown.items():
                    print(f"      IVA {rate}%: Base ${data['base']:.2f}, Impuesto ${data['tax']:.2f}")
            else:
                print("      Sin impuestos")
                
        except Exception as e:
            print(f"   ❌ Error en get_tax_breakdown(): {e}")
            import traceback
            traceback.print_exc()
        
        # Probar el método del admin
        try:
            from apps.invoicing.admin import InvoiceAdmin
            admin = InvoiceAdmin(Invoice, None)
            display_result = admin.tax_breakdown_display(invoice)
            print(f"   ✅ tax_breakdown_display() ejecutado")
            print(f"   📺 HTML generado: {len(str(display_result))} caracteres")
            if "Error" in str(display_result):
                print(f"   ⚠️  Contiene error: {display_result}")
            
        except Exception as e:
            print(f"   ❌ Error en tax_breakdown_display(): {e}")
            import traceback
            traceback.print_exc()

def test_invoice_lines():
    """Probar líneas de factura específicas"""
    print("\n=== ANÁLISIS DE LÍNEAS DE FACTURA ===")
    
    lines = InvoiceLine.objects.select_related('invoice', 'product')[:5]
    
    for line in lines:
        print(f"\n📦 LÍNEA: {line.product.name if line.product else 'Sin producto'}")
        print(f"   Factura: #{line.invoice.number}")
        print(f"   Cantidad: {line.quantity}")
        print(f"   Precio unitario: ${line.unit_price}")
        print(f"   Descuento: {line.discount}%")
        print(f"   IVA Rate: {line.iva_rate}%")
        
        # Calcular manualmente
        subtotal = line.quantity * line.unit_price
        discount_amount = subtotal * (line.discount / 100)
        net = subtotal - discount_amount
        tax = net * (line.iva_rate / 100)
        total = net + tax
        
        print(f"   📊 Cálculo manual:")
        print(f"      Subtotal: ${subtotal:.2f}")
        print(f"      Descuento: ${discount_amount:.2f}")
        print(f"      Neto: ${net:.2f}")
        print(f"      IVA: ${tax:.2f}")
        print(f"      Total: ${total:.2f}")
        print(f"   📋 Total en DB: ${line.line_total}")

if __name__ == "__main__":
    print("Iniciando pruebas de desglose de IVA...")
    test_tax_breakdown()
    test_invoice_lines()
    print("\n✅ Pruebas completadas")