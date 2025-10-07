#!/usr/bin/env python

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def examine_invoice_data():
    """Examinar datos completos de la factura"""
    
    from apps.suppliers.models import PurchaseInvoice, PurchaseInvoiceLine
    
    invoice = PurchaseInvoice.objects.get(internal_number='FC-001-000007')
    
    print('=== DATOS COMPLETOS FACTURA ===')
    print(f'Número: {invoice.internal_number}')
    print(f'Proveedor: {invoice.supplier.trade_name}')
    print(f'Razón Social: {invoice.supplier.legal_name}')
    print(f'RUC: {invoice.supplier.identification}')
    print(f'Fecha: {invoice.date}')
    print(f'Subtotal: ${invoice.subtotal}')
    print(f'IVA: ${invoice.tax_amount}')
    print(f'Total: ${invoice.total}')
    print(f'Observaciones: {invoice.notes}')
    print(f'Estado: {invoice.status}')
    print(f'Empresa: {invoice.company.trade_name if invoice.company else "Sin empresa"}')
    print(f'Forma de pago: {invoice.payment_form.name if invoice.payment_form else "Sin forma de pago"}')
    print()
    
    print('=== LÍNEAS DE FACTURA ===')
    lines = PurchaseInvoiceLine.objects.filter(purchase_invoice=invoice)
    print(f'Total líneas: {lines.count()}')
    
    for i, line in enumerate(lines, 1):
        print(f'Línea {i}:')
        print(f'  Producto: {line.product.name if line.product else "Sin producto"}')
        print(f'  Descripción: {line.description if hasattr(line, "description") else "N/A"}')
        print(f'  Cantidad: {line.quantity}')
        print(f'  Costo unitario: ${line.unit_cost}')
        subtotal = line.quantity * line.unit_cost
        print(f'  Subtotal calculado: ${subtotal}')
        iva = subtotal * (line.iva_rate / 100)
        print(f'  IVA calculado ({line.iva_rate}%): ${iva}')
        total = subtotal + iva
        print(f'  Total calculado: ${total}')
        print()

if __name__ == "__main__":
    examine_invoice_data()