#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug: Analizar Asientos Contables con Retenciones
Identificar por que los asientos estan desbalanceados
"""

import os
import sys
import django
from decimal import Decimal

# Configurar Django
sys.path.append('c:/contaec')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.suppliers.models import PurchaseInvoice
from apps.accounting.models import JournalEntry, JournalEntryLine
from apps.companies.models import Company

def debug_journal_entry_balance():
    """Analizar balance de asientos con retenciones"""
    print("=== DEBUG: Balance de Asientos con Retenciones ===")
    
    company = Company.objects.filter(trade_name__icontains='GUEBER').first()
    
    # Buscar factura con retenciones
    invoice = PurchaseInvoice.objects.filter(
        company=company,
        total_retentions__gt=0
    ).first()
    
    if not invoice:
        print("X No hay facturas con retenciones")
        return
    
    print(f">> Factura: {invoice.internal_number}")
    print(f"   Subtotal: ${invoice.subtotal}")
    print(f"   IVA: ${invoice.tax_amount}")
    print(f"   Total Bruto: ${invoice.total}")
    print(f"   Retencion IVA: ${invoice.iva_retention_amount}")
    print(f"   Retencion IR: ${invoice.ir_retention_amount}")
    print(f"   Total Retenciones: ${invoice.total_retentions}")
    print(f"   Neto a Pagar: ${invoice.net_payable}")
    
    # Buscar asiento contable
    journal_entry = JournalEntry.objects.filter(
        reference__icontains=invoice.internal_number,
        company=company
    ).first()
    
    if not journal_entry:
        print("X No se encontro asiento contable")
        return
    
    print(f"\n>> Asiento: {journal_entry.number}")
    print("   Lineas del asiento:")
    
    total_debit = Decimal('0.00')
    total_credit = Decimal('0.00')
    
    for line in journal_entry.lines.all():
        print(f"   - {line.account.code} {line.account.name}")
        print(f"     Debito: ${line.debit}")
        print(f"     Credito: ${line.credit}")
        print(f"     Descripcion: {line.description}")
        
        total_debit += line.debit
        total_credit += line.credit
    
    print(f"\n   Total Debitos: ${total_debit}")
    print(f"   Total Creditos: ${total_credit}")
    print(f"   Diferencia: ${total_debit - total_credit}")
    print(f"   Balanceado: {journal_entry.is_balanced}")
    
    # Verificar que debe registrar
    print(f"\n>> Lo que DEBERIA registrar:")
    print(f"   DEBITO - Gasto/Inventario: ${invoice.subtotal}")
    print(f"   DEBITO - IVA por Cobrar: ${invoice.tax_amount}")
    print(f"   CREDITO - Cuentas por Pagar: ${invoice.net_payable}")
    print(f"   CREDITO - Retencion IVA: ${invoice.iva_retention_amount}")
    print(f"   CREDITO - Retencion IR: ${invoice.ir_retention_amount}")
    
    expected_debits = invoice.subtotal + invoice.tax_amount
    expected_credits = invoice.net_payable + invoice.total_retentions
    
    print(f"\n   Total Debitos Esperados: ${expected_debits}")
    print(f"   Total Creditos Esperados: ${expected_credits}")
    print(f"   Balance Esperado: ${expected_debits - expected_credits}")

if __name__ == "__main__":
    debug_journal_entry_balance()