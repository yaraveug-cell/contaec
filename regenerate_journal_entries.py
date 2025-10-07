#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Regeneracion: Asientos Contables con Retenciones
Regenera asientos para facturas que tienen retenciones pero asientos incompletos
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
from apps.accounting.models import JournalEntry
from apps.companies.models import Company

def regenerate_journal_entries_with_retentions():
    """Regenerar asientos contables con retenciones"""
    print("=== REGENERACION: Asientos Contables con Retenciones ===")
    
    company = Company.objects.filter(trade_name__icontains='GUEBER').first()
    
    # Buscar facturas con retenciones
    invoices_with_retentions = PurchaseInvoice.objects.filter(
        company=company,
        total_retentions__gt=0,
        status='validated'
    )
    
    print(f">> Facturas con retenciones a procesar: {invoices_with_retentions.count()}")
    
    for invoice in invoices_with_retentions:
        print(f"\n>> Procesando Factura: {invoice.internal_number}")
        print(f"   Total: ${invoice.total}")
        print(f"   Retenciones: ${invoice.total_retentions}")
        print(f"   Neto a Pagar: ${invoice.net_payable}")
        
        # Buscar asiento existente
        existing_entry = JournalEntry.objects.filter(
            reference__icontains=invoice.internal_number,
            company=company
        ).first()
        
        if existing_entry:
            print(f"   >> Asiento existente: {existing_entry.number} ({existing_entry.lines.count()} lineas)")
            print(f"      Balance: {existing_entry.is_balanced}")
            
            # Si el asiento no esta balanceado o tiene menos lineas de las necesarias
            expected_lines = 3  # Al menos: Gasto/Inventario + Cuentas por Pagar + (Retenciones si aplican)
            if invoice.total_retentions > 0:
                expected_lines += 2  # +IVA por Cobrar +Retenciones
                if invoice.iva_retention_amount > 0 and invoice.ir_retention_amount > 0:
                    expected_lines += 1  # Separar retenciones IVA e IR
            
            if not existing_entry.is_balanced or existing_entry.lines.count() < 4:
                print(f"   >> Eliminando asiento incompleto...")
                existing_entry.delete()
                
                print(f"   >> Creando nuevo asiento con retenciones...")
                new_entry = invoice.create_journal_entry()
                
                if new_entry:
                    print(f"   ✓ Nuevo asiento: {new_entry.number} ({new_entry.lines.count()} lineas)")
                    print(f"     Balance: {new_entry.is_balanced}")
                else:
                    print(f"   X Error creando asiento")
            else:
                print(f"   ✓ Asiento correcto, no requiere cambios")
        else:
            print(f"   >> Creando asiento desde cero...")
            new_entry = invoice.create_journal_entry()
            
            if new_entry:
                print(f"   ✓ Asiento creado: {new_entry.number} ({new_entry.lines.count()} lineas)")
                print(f"     Balance: {new_entry.is_balanced}")
            else:
                print(f"   X Error creando asiento")

if __name__ == "__main__":
    regenerate_journal_entries_with_retentions()