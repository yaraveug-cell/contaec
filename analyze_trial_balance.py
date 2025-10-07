#!/usr/bin/env python3
"""
Script para analizar el balance de comprobación y encontrar descuadres
Versión: 1.0
Fecha: 2025-10-02
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import JournalEntry, JournalEntryLine, ChartOfAccounts
from apps.companies.models import Company
from django.db.models import Sum
from decimal import Decimal

def analyze_trial_balance():
    """Analizar balance de comprobación para encontrar descuadres"""
    
    print("🔍 ANÁLISIS DEL BALANCE DE COMPROBACIÓN")
    print("=" * 50)
    
    companies = Company.objects.all()
    
    for company in companies:
        print(f"\n🏢 EMPRESA: {company.trade_name}")
        print("-" * 40)
        
        # === 1. VERIFICAR ASIENTOS INDIVIDUALES ===
        print("\n📝 VERIFICANDO ASIENTOS INDIVIDUALES:")
        
        entries = JournalEntry.objects.filter(company=company).order_by('number')
        total_unbalanced = 0
        unbalanced_entries = []
        
        for entry in entries:
            lines = JournalEntryLine.objects.filter(journal_entry=entry)
            
            # Calcular totales reales de las líneas
            actual_debit = sum(line.debit for line in lines)
            actual_credit = sum(line.credit for line in lines)
            
            # Comparar con totales almacenados
            stored_debit = entry.total_debit
            stored_credit = entry.total_credit
            
            # Verificar balance interno del asiento
            difference = actual_debit - actual_credit
            
            status = "✅" if abs(difference) < Decimal('0.01') else "❌"
            
            print(f"   {entry.number} | {status} | Deb: ${actual_debit:8.2f} | Cred: ${actual_credit:8.2f} | Diff: ${difference:8.2f}")
            
            if abs(difference) >= Decimal('0.01'):
                total_unbalanced += abs(difference)
                unbalanced_entries.append({
                    'number': entry.number,
                    'debit': actual_debit,
                    'credit': actual_credit,
                    'difference': difference,
                    'description': entry.description
                })
                
                # Mostrar líneas del asiento problemático
                print(f"      LÍNEAS DEL ASIENTO {entry.number}:")
                for line in lines:
                    account_code = line.account.code if line.account else "Sin cuenta"
                    print(f"         {account_code} | {line.description[:25]:25} | ${line.debit:8.2f} | ${line.credit:8.2f}")
        
        print(f"\n   📊 RESUMEN DE ASIENTOS:")
        print(f"   Total asientos: {entries.count()}")
        print(f"   Asientos desbalanceados: {len(unbalanced_entries)}")
        print(f"   Monto total descuadrado: ${total_unbalanced}")
        
        # === 2. BALANCE DE COMPROBACIÓN GENERAL ===
        print(f"\n⚖️ BALANCE DE COMPROBACIÓN GENERAL:")
        
        # Obtener todas las cuentas con movimiento
        accounts_with_movement = ChartOfAccounts.objects.filter(
            company=company,
            journalentryline__journal_entry__company=company
        ).distinct().order_by('code')
        
        total_debit_balance = Decimal('0.00')
        total_credit_balance = Decimal('0.00')
        
        print(f"   {'CUENTA':15} | {'NOMBRE':30} | {'DÉBITO':>12} | {'CRÉDITO':>12} | {'SALDO':>12}")
        print(f"   {'-'*15}|{'-'*31}|{'-'*13}|{'-'*14}|{'-'*13}")
        
        for account in accounts_with_movement:
            # Sumar todos los movimientos de esta cuenta
            lines = JournalEntryLine.objects.filter(
                account=account,
                journal_entry__company=company,
                journal_entry__state='posted'  # Solo asientos contabilizados
            )
            
            account_debit = sum(line.debit for line in lines)
            account_credit = sum(line.credit for line in lines)
            
            # Calcular saldo según naturaleza de la cuenta
            if account.code.startswith('1') or account.code.startswith('5'):  # Activos y Gastos
                saldo = account_debit - account_credit
                if saldo > 0:
                    total_debit_balance += saldo
            else:  # Pasivos, Patrimonio, Ingresos
                saldo = account_credit - account_debit
                if saldo > 0:
                    total_credit_balance += saldo
            
            # Mostrar solo cuentas con movimiento
            if account_debit > 0 or account_credit > 0:
                saldo_display = abs(saldo)
                print(f"   {account.code:15} | {account.name[:30]:30} | ${account_debit:>11.2f} | ${account_credit:>11.2f} | ${saldo_display:>11.2f}")
        
        # === 3. TOTALES DEL BALANCE DE COMPROBACIÓN ===
        print(f"   {'-'*15}|{'-'*31}|{'-'*13}|{'-'*14}|{'-'*13}")
        print(f"   {'TOTALES':15} | {' ':30} | ${total_debit_balance:>11.2f} | ${total_credit_balance:>11.2f} | ${abs(total_debit_balance - total_credit_balance):>11.2f}")
        
        # Verificar si el balance de comprobación cuadra
        balance_difference = total_debit_balance - total_credit_balance
        
        print(f"\n   📊 RESULTADO DEL BALANCE DE COMPROBACIÓN:")
        print(f"   Total saldos deudores: ${total_debit_balance}")
        print(f"   Total saldos acreedores: ${total_credit_balance}")
        print(f"   Diferencia: ${balance_difference}")
        
        if abs(balance_difference) < Decimal('0.01'):
            print(f"   ✅ BALANCE DE COMPROBACIÓN CUADRADO")
        else:
            print(f"   ❌ BALANCE DE COMPROBACIÓN DESCUADRADO")
            
            # === 4. DIAGNÓSTICO DEL DESCUADRE ===
            print(f"\n🔍 DIAGNÓSTICO DEL DESCUADRE:")
            
            if len(unbalanced_entries) > 0:
                print(f"   1. ❌ ASIENTOS DESBALANCEADOS DETECTADOS:")
                for entry in unbalanced_entries:
                    print(f"      - Asiento {entry['number']}: Diferencia ${entry['difference']}")
                    print(f"        {entry['description'][:50]}")
            
            # Verificar asientos incompletos (solo una línea)
            incomplete_entries = []
            for entry in entries:
                lines_count = JournalEntryLine.objects.filter(journal_entry=entry).count()
                if lines_count == 1:
                    incomplete_entries.append(entry)
            
            if incomplete_entries:
                print(f"   2. ⚠️ ASIENTOS INCOMPLETOS (SOLO UNA LÍNEA):")
                for entry in incomplete_entries:
                    print(f"      - Asiento {entry.number}: Solo {JournalEntryLine.objects.filter(journal_entry=entry).count()} línea(s)")
            
            # Verificar asientos sin líneas
            empty_entries = entries.filter(lines__isnull=True)
            if empty_entries.exists():
                print(f"   3. ❌ ASIENTOS SIN LÍNEAS:")
                for entry in empty_entries:
                    print(f"      - Asiento {entry.number}: Sin movimientos")
            
            # Verificar problema del asiento de capital
            capital_entry = entries.filter(description__icontains='capital inicial').first()
            if capital_entry:
                print(f"   4. 🔍 VERIFICANDO ASIENTO DE CAPITAL:")
                capital_lines = JournalEntryLine.objects.filter(journal_entry=capital_entry)
                print(f"      - Asiento {capital_entry.number} tiene {capital_lines.count()} línea(s)")
                
                if capital_lines.count() == 1:
                    line = capital_lines.first()
                    print(f"      - ❌ PROBLEMA: Solo tiene crédito de ${line.credit}, falta el débito")
                    print(f"      - 💡 SOLUCIÓN: Agregar línea de débito por ${line.credit} en cuenta de activos")

if __name__ == "__main__":
    try:
        analyze_trial_balance()
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        import traceback
        traceback.print_exc()