#!/usr/bin/env python3
"""
Script para completar el asiento de capital inicial con la línea de débito faltante
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import JournalEntry, JournalEntryLine, ChartOfAccounts
from decimal import Decimal
from django.db import transaction

def complete_capital_entry():
    """Completar el asiento de capital inicial agregando la línea de débito faltante"""
    
    print("🔧 COMPLETANDO ASIENTO DE CAPITAL INICIAL")
    print("=" * 45)
    
    # Buscar el asiento de capital inicial
    capital_entry = JournalEntry.objects.filter(
        description__icontains='capital inicial'
    ).first()
    
    if not capital_entry:
        print("❌ No se encontró asiento de capital inicial")
        return
    
    print(f"📋 Asiento encontrado: {capital_entry.number}")
    print(f"    Descripción: {capital_entry.description}")
    
    # Verificar líneas existentes
    existing_lines = JournalEntryLine.objects.filter(journal_entry=capital_entry)
    print(f"    Líneas existentes: {existing_lines.count()}")
    
    if existing_lines.count() != 1:
        print("⚠️ El asiento no tiene exactamente 1 línea, verificar manualmente")
        return
    
    credit_line = existing_lines.first()
    credit_amount = credit_line.credit
    
    print(f"    Línea existente: CRÉDITO ${credit_amount} en {credit_line.account.code}")
    
    if credit_amount <= 0:
        print("❌ La línea de crédito no tiene monto válido")
        return
    
    try:
        with transaction.atomic():
            # Buscar cuenta de caja para el débito
            company = capital_entry.company
            
            # Buscar cuenta de caja existente
            cash_account = ChartOfAccounts.objects.filter(
                company=company,
                code='1.1.01.01'  # CAJA GENERAL
            ).first()
            
            if not cash_account:
                print("❌ No se encontró cuenta de caja")
                return
            
            print(f"    Cuenta de débito: {cash_account.code} - {cash_account.name}")
            
            # Crear línea de débito faltante
            JournalEntryLine.objects.create(
                journal_entry=capital_entry,
                account=cash_account,
                description=f"Capital inicial - Aporte en efectivo",
                debit=credit_amount,
                credit=Decimal('0.00')
            )
            
            # Actualizar totales del asiento
            capital_entry.total_debit = credit_amount
            capital_entry.total_credit = credit_amount
            capital_entry.save()
            
            print(f"✅ Línea de débito agregada exitosamente")
            print(f"    DÉBITO: {cash_account.code} ${credit_amount}")
            
            # Verificar balance del asiento
            new_lines = JournalEntryLine.objects.filter(journal_entry=capital_entry)
            total_debit = sum(line.debit for line in new_lines)
            total_credit = sum(line.credit for line in new_lines)
            
            print(f"\n📊 VERIFICACIÓN:")
            print(f"    Total débito: ${total_debit}")
            print(f"    Total crédito: ${total_credit}")
            print(f"    Diferencia: ${total_debit - total_credit}")
            
            if abs(total_debit - total_credit) < Decimal('0.01'):
                print(f"    ✅ Asiento ahora está balanceado")
            else:
                print(f"    ❌ Asiento sigue desbalanceado")
                
    except Exception as e:
        print(f"❌ Error completando asiento: {e}")
        return
    
    print(f"\n🎉 ASIENTO COMPLETADO EXITOSAMENTE")
    print(f"🔄 El balance de comprobación debería estar ahora cuadrado")

if __name__ == "__main__":
    try:
        complete_capital_entry()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()