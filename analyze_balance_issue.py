#!/usr/bin/env python3
"""
Script para analizar por qué el balance aparece como desbalanceado
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

def analyze_balance_issue():
    """Analizar por qué el balance aparece como desbalanceado"""
    
    print("🔍 ANÁLISIS DEL BALANCE DESBALANCEADO")
    print("=" * 50)
    
    # Obtener empresas
    companies = Company.objects.all()
    company_ids = companies.values_list('id', flat=True)
    
    print(f"📊 EMPRESAS ANALIZADAS: {companies.count()}")
    for company in companies:
        print(f"   - {company.trade_name}")
    print()
    
    # === ANÁLISIS DE ASIENTOS CONTABILIZADOS ===
    print("📝 ASIENTOS CONTABILIZADOS (POSTED):")
    
    posted_entries = JournalEntry.objects.filter(
        company__in=company_ids, 
        state='posted'
    ).order_by('number')
    
    print(f"Total de asientos contabilizados: {posted_entries.count()}")
    
    total_debit_all = Decimal('0.00')
    total_credit_all = Decimal('0.00')
    
    for entry in posted_entries:
        print(f"\n--- Asiento {entry.number} ---")
        print(f"Fecha: {entry.date}")
        print(f"Descripción: {entry.description}")
        print(f"Total Débito: ${entry.total_debit}")
        print(f"Total Crédito: ${entry.total_credit}")
        print(f"Balanceado: {'✅' if entry.is_balanced else '❌'}")
        
        # Mostrar líneas del asiento
        lines = JournalEntryLine.objects.filter(journal_entry=entry)
        for line in lines:
            account_code = line.account.code if line.account else "Sin cuenta"
            print(f"  {account_code} | {line.description[:30]:30} | Deb: ${line.debit:8.2f} | Cred: ${line.credit:8.2f}")
        
        total_debit_all += entry.total_debit
        total_credit_all += entry.total_credit
    
    print(f"\n📊 TOTALES GENERALES:")
    print(f"Total Débitos: ${total_debit_all}")
    print(f"Total Créditos: ${total_credit_all}")
    print(f"Diferencia: ${abs(total_debit_all - total_credit_all)}")
    
    # === ANÁLISIS POR TIPO DE CUENTA ===
    print(f"\n⚖️ ANÁLISIS POR TIPO DE CUENTA:")
    
    # Activos (1.x)
    activos_lines = JournalEntryLine.objects.filter(
        journal_entry__company__in=company_ids,
        journal_entry__state='posted',
        account__code__startswith='1'
    )
    
    activos_debit = activos_lines.aggregate(total=Sum('debit'))['total'] or Decimal('0.00')
    activos_credit = activos_lines.aggregate(total=Sum('credit'))['total'] or Decimal('0.00')
    activos_saldo = activos_debit - activos_credit
    
    print(f"\n💰 ACTIVOS (1.x):")
    print(f"Débitos: ${activos_debit}")
    print(f"Créditos: ${activos_credit}")
    print(f"Saldo neto: ${activos_saldo}")
    
    # Mostrar cuentas de activos con movimiento
    activos_accounts = ChartOfAccounts.objects.filter(
        company__in=company_ids, 
        code__startswith='1'
    )
    
    for account in activos_accounts:
        account_lines = activos_lines.filter(account=account)
        if account_lines.exists():
            account_debit = account_lines.aggregate(total=Sum('debit'))['total'] or Decimal('0.00')
            account_credit = account_lines.aggregate(total=Sum('credit'))['total'] or Decimal('0.00')
            account_balance = account_debit - account_credit
            print(f"  {account.code} - {account.name}: ${account_balance}")
    
    # Pasivos (2.x)
    pasivos_lines = JournalEntryLine.objects.filter(
        journal_entry__company__in=company_ids,
        journal_entry__state='posted',
        account__code__startswith='2'
    )
    
    pasivos_debit = pasivos_lines.aggregate(total=Sum('debit'))['total'] or Decimal('0.00')
    pasivos_credit = pasivos_lines.aggregate(total=Sum('credit'))['total'] or Decimal('0.00')
    pasivos_saldo = pasivos_credit - pasivos_debit
    
    print(f"\n🔴 PASIVOS (2.x):")
    print(f"Débitos: ${pasivos_debit}")
    print(f"Créditos: ${pasivos_credit}")
    print(f"Saldo neto: ${pasivos_saldo}")
    
    # Mostrar cuentas de pasivos con movimiento
    pasivos_accounts = ChartOfAccounts.objects.filter(
        company__in=company_ids, 
        code__startswith='2'
    )
    
    for account in pasivos_accounts:
        account_lines = pasivos_lines.filter(account=account)
        if account_lines.exists():
            account_debit = account_lines.aggregate(total=Sum('debit'))['total'] or Decimal('0.00')
            account_credit = account_lines.aggregate(total=Sum('credit'))['total'] or Decimal('0.00')
            account_balance = account_credit - account_debit
            print(f"  {account.code} - {account.name}: ${account_balance}")
    
    # Patrimonio (3.x)
    patrimonio_lines = JournalEntryLine.objects.filter(
        journal_entry__company__in=company_ids,
        journal_entry__state='posted',
        account__code__startswith='3'
    )
    
    patrimonio_debit = patrimonio_lines.aggregate(total=Sum('debit'))['total'] or Decimal('0.00')
    patrimonio_credit = patrimonio_lines.aggregate(total=Sum('credit'))['total'] or Decimal('0.00')
    patrimonio_saldo = patrimonio_credit - patrimonio_debit
    
    print(f"\n🔵 PATRIMONIO (3.x):")
    print(f"Débitos: ${patrimonio_debit}")
    print(f"Créditos: ${patrimonio_credit}")
    print(f"Saldo neto: ${patrimonio_saldo}")
    
    # Mostrar cuentas de patrimonio con movimiento
    patrimonio_accounts = ChartOfAccounts.objects.filter(
        company__in=company_ids, 
        code__startswith='3'
    )
    
    for account in patrimonio_accounts:
        account_lines = patrimonio_lines.filter(account=account)
        if account_lines.exists():
            account_debit = account_lines.aggregate(total=Sum('debit'))['total'] or Decimal('0.00')
            account_credit = account_lines.aggregate(total=Sum('credit'))['total'] or Decimal('0.00')
            account_balance = account_credit - account_debit
            print(f"  {account.code} - {account.name}: ${account_balance}")
    
    # === VERIFICACIÓN DE LA ECUACIÓN CONTABLE ===
    print(f"\n📊 ECUACIÓN CONTABLE:")
    print(f"Activos = Pasivos + Patrimonio")
    print(f"${activos_saldo} = ${pasivos_saldo} + ${patrimonio_saldo}")
    print(f"${activos_saldo} = ${pasivos_saldo + patrimonio_saldo}")
    
    diferencia = activos_saldo - (pasivos_saldo + patrimonio_saldo)
    print(f"Diferencia: ${diferencia}")
    
    if abs(diferencia) < Decimal('0.01'):
        print("✅ BALANCE CORRECTO")
    else:
        print("❌ BALANCE DESBALANCEADO")
        
        print(f"\n🔍 POSIBLES CAUSAS DEL DESBALANCE:")
        
        if patrimonio_saldo == Decimal('0.00'):
            print("1. ❌ PATRIMONIO EN CERO:")
            print("   - No hay cuentas de patrimonio registradas con movimiento")
            print("   - Faltan asientos de capital inicial o utilidades retenidas")
            print("   - Recomendación: Crear asiento de capital inicial")
        
        if abs(diferencia) == activos_saldo:
            print("2. ❌ SOLO HAY ACTIVOS:")
            print("   - Todos los movimientos están en cuentas de activos")
            print("   - Falta el origen de los recursos (pasivos o patrimonio)")
        
        if posted_entries.count() < JournalEntry.objects.filter(company__in=company_ids).count():
            draft_count = JournalEntry.objects.filter(company__in=company_ids, state='draft').count()
            print(f"3. ⚠️  ASIENTOS PENDIENTES:")
            print(f"   - Hay {draft_count} asientos en borrador sin contabilizar")
            print(f"   - Estos podrían contener las partidas faltantes")
        
        print(f"\n💡 RECOMENDACIONES:")
        print("1. Crear asiento de capital inicial para balancear")
        print("2. Contabilizar asientos pendientes en borrador")
        print("3. Verificar que cada asiento individual esté balanceado")
        print("4. Revisar la clasificación de cuentas (1.x, 2.x, 3.x)")

if __name__ == "__main__":
    try:
        analyze_balance_issue()
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        import traceback
        traceback.print_exc()