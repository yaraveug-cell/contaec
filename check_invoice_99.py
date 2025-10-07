#!/usr/bin/env python
"""
Verificar estado completo de factura ID 99 para diagnóstico
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice

def check_invoice_99():
    """Verificar datos de la factura ID 99"""
    
    try:
        invoice = Invoice.objects.get(id=99)
        
        print("📄 FACTURA ID 99 - ESTADO ACTUAL:")
        print("=" * 40)
        print(f"Número: {invoice.number}")
        print(f"Método de pago: {invoice.payment_form}")
        print(f"Cuenta (account): {invoice.account}")
        print(f"Account ID: {invoice.account.id if invoice.account else 'NULL'}")
        print(f"Bank observations: '{invoice.bank_observations}'")
        print(f"Transfer detail: '{invoice.transfer_detail}'")
        print(f"Status: {invoice.status}")
        
        print(f"\n🔍 ANÁLISIS:")
        print(f"Tiene observaciones: {'✓' if invoice.bank_observations else '✗'}")
        print(f"Longitud observaciones: {len(invoice.bank_observations) if invoice.bank_observations else 0}")
        print(f"Es transferencia: {'✓' if 'transferencia' in invoice.payment_form.name.lower() else '✗'}")
        
        if invoice.bank_observations:
            print(f"\n📝 CONTENIDO DE OBSERVACIONES:")
            print(f"'{invoice.bank_observations}'")
        
        print(f"\n🌐 RECARGA LA PÁGINA:")
        print(f"http://localhost:8000/admin/invoicing/invoice/{invoice.id}/change/")
        
    except Invoice.DoesNotExist:
        print("❌ Factura ID 99 no existe")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_invoice_99()