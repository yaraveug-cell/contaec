#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Migracion de Datos: Actualizar Net Payable en Facturas Existentes
Corrige el problema de compatibilidad hacia atras con facturas existentes
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
from apps.companies.models import Company

def migrate_existing_invoices():
    """Actualizar net_payable para facturas existentes sin retenciones"""
    print("=== MIGRACION: Actualizando Net Payable en Facturas Existentes ===")
    
    company = Company.objects.filter(trade_name__icontains='GUEBER').first()
    if not company:
        company = Company.objects.first()
    
    if not company:
        print("X No hay empresas en el sistema")
        return
    
    print(f">> Empresa: {company.trade_name}")
    
    # Buscar facturas con net_payable = 0 pero total > 0
    problematic_invoices = PurchaseInvoice.objects.filter(
        company=company,
        total__gt=0,
        net_payable=0
    )
    
    print(f">> Facturas a corregir: {problematic_invoices.count()}")
    
    corrected_count = 0
    for invoice in problematic_invoices:
        old_net_payable = invoice.net_payable
        old_total_retentions = invoice.total_retentions
        
        # Recalcular totales (esto actualizará net_payable)
        invoice.calculate_totals()
        
        # Refrescar desde BD para obtener valores actualizados
        invoice.refresh_from_db()
        
        print(f"  Factura {invoice.internal_number}:")
        print(f"    Total: ${invoice.total}")
        print(f"    Retenciones: ${old_total_retentions} -> ${invoice.total_retentions}")
        print(f"    Net Payable: ${old_net_payable} -> ${invoice.net_payable}")
        
        corrected_count += 1
    
    print(f"\n✓ {corrected_count} facturas corregidas")
    print("✓ Net payable actualizado para compatibilidad hacia atras")

if __name__ == "__main__":
    migrate_existing_invoices()