#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.invoicing.models import Invoice

def test_simple():
    print("=== Prueba simple del desglose de IVA ===")
    
    # Obtener primera factura
    invoice = Invoice.objects.first()
    
    if not invoice:
        print("No hay facturas")
        return
    
    print(f"Factura ID: {invoice.id}")
    print(f"Numero: {invoice.number}")
    print(f"Empresa: {invoice.company.trade_name}")
    print(f"Lineas: {invoice.lines.count()}")
    
    # Probar get_tax_breakdown
    try:
        breakdown = invoice.get_tax_breakdown()
        print("Breakdown exitoso:", breakdown)
    except Exception as e:
        print("Error en breakdown:", e)
        import traceback
        traceback.print_exc()
    
    # Probar admin display
    try:
        from apps.invoicing.admin import InvoiceAdmin
        admin = InvoiceAdmin(Invoice, None)
        result = admin.tax_breakdown_display(invoice)
        print("Display result:", result)
    except Exception as e:
        print("Error en display:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple()