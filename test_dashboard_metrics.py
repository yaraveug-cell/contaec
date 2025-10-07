#!/usr/bin/env python3
"""
Script para probar las métricas financieras del dashboard
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

from django.contrib.auth import get_user_model
from apps.accounting.models import JournalEntry, JournalEntryLine, ChartOfAccounts
from apps.invoicing.models import Invoice
from apps.companies.models import Company
from django.db.models import Sum, Count
from decimal import Decimal

User = get_user_model()

def test_financial_metrics():
    """Probar el cálculo de métricas financieras del dashboard"""
    
    print("🔍 PRUEBA DE MÉTRICAS FINANCIERAS DEL DASHBOARD")
    print("=" * 55)
    
    # Obtener todas las empresas para el cálculo
    companies = Company.objects.all()
    company_ids = companies.values_list('id', flat=True)
    
    print(f"📊 EMPRESAS INCLUIDAS: {companies.count()}")
    for company in companies:
        print(f"   - {company.trade_name} (RUC: {company.ruc})")
    print()
    
    # === MÉTRICAS DE ASIENTOS CONTABLES ===
    print("📝 ASIENTOS CONTABLES:")
    
    total_entries = JournalEntry.objects.filter(company__in=company_ids).count()
    draft_entries = JournalEntry.objects.filter(company__in=company_ids, state='draft').count()
    posted_entries = JournalEntry.objects.filter(company__in=company_ids, state='posted').count()
    cancelled_entries = JournalEntry.objects.filter(company__in=company_ids, state='cancelled').count()
    
    print(f"   Total de asientos: {total_entries}")
    print(f"   Borradores: {draft_entries}")
    print(f"   Contabilizados: {posted_entries}")
    print(f"   Anulados: {cancelled_entries}")
    
    posted_rate = round((posted_entries / total_entries * 100) if total_entries > 0 else 0, 1)
    print(f"   Tasa de contabilización: {posted_rate}%")
    print()
    
    # === MÉTRICAS DE FACTURAS ===
    print("🧾 FACTURAS:")
    
    total_invoices = Invoice.objects.filter(company__in=company_ids).count()
    draft_invoices = Invoice.objects.filter(company__in=company_ids, status='draft').count()
    sent_invoices = Invoice.objects.filter(company__in=company_ids, status='sent').count()
    paid_invoices = Invoice.objects.filter(company__in=company_ids, status='paid').count()
    cancelled_invoices = Invoice.objects.filter(company__in=company_ids, status='cancelled').count()
    
    print(f"   Total de facturas: {total_invoices}")
    print(f"   Borradores: {draft_invoices}")
    print(f"   Enviadas: {sent_invoices}")
    print(f"   Pagadas: {paid_invoices}")
    print(f"   Anuladas: {cancelled_invoices}")
    
    collection_rate = round((paid_invoices / total_invoices * 100) if total_invoices > 0 else 0, 1)
    print(f"   Tasa de cobro: {collection_rate}%")
    
    # Ingresos del mes (facturas pagadas)
    from django.utils import timezone
    today = timezone.now().date()
    first_day_month = today.replace(day=1)
    
    monthly_income = Invoice.objects.filter(
        company__in=company_ids,
        status='paid',
        created_at__date__gte=first_day_month
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    print(f"   Ingresos del mes: ${monthly_income}")
    print()
    
    # === BALANCE BÁSICO ===
    print("⚖️ BALANCE GENERAL BÁSICO:")
    
    try:
        # Activos (código 1.x)
        activos_query = JournalEntryLine.objects.filter(
            journal_entry__company__in=company_ids,
            journal_entry__state='posted',
            account__code__startswith='1'
        ).aggregate(
            debit_total=Sum('debit'),
            credit_total=Sum('credit')
        )
        
        # Pasivos (código 2.x)
        pasivos_query = JournalEntryLine.objects.filter(
            journal_entry__company__in=company_ids,
            journal_entry__state='posted',
            account__code__startswith='2'
        ).aggregate(
            debit_total=Sum('debit'),
            credit_total=Sum('credit')
        )
        
        # Patrimonio (código 3.x)
        patrimonio_query = JournalEntryLine.objects.filter(
            journal_entry__company__in=company_ids,
            journal_entry__state='posted',
            account__code__startswith='3'
        ).aggregate(
            debit_total=Sum('debit'),
            credit_total=Sum('credit')
        )
        
        # Calcular saldos netos
        activos_debit = activos_query['debit_total'] or Decimal('0.00')
        activos_credit = activos_query['credit_total'] or Decimal('0.00')
        activos_saldo = activos_debit - activos_credit
        
        pasivos_debit = pasivos_query['debit_total'] or Decimal('0.00')
        pasivos_credit = pasivos_query['credit_total'] or Decimal('0.00')
        pasivos_saldo = pasivos_credit - pasivos_debit
        
        patrimonio_debit = patrimonio_query['debit_total'] or Decimal('0.00')
        patrimonio_credit = patrimonio_query['credit_total'] or Decimal('0.00')
        patrimonio_saldo = patrimonio_credit - patrimonio_debit
        
        print(f"   Activos: ${activos_saldo}")
        print(f"   Pasivos: ${pasivos_saldo}")
        print(f"   Patrimonio: ${patrimonio_saldo}")
        
        # Verificar balance
        balance_difference = abs(activos_saldo - (pasivos_saldo + patrimonio_saldo))
        is_balanced = balance_difference < Decimal('0.01')
        
        print(f"   Diferencia: ${balance_difference}")
        print(f"   Estado: {'✅ Balanceado' if is_balanced else '❌ Desbalanceado'}")
        
    except Exception as e:
        print(f"   ❌ Error calculando balance: {e}")
    
    print()
    
    # === ESTRUCTURA DEL PLAN DE CUENTAS ===
    print("📋 PLAN DE CUENTAS:")
    
    total_accounts = ChartOfAccounts.objects.filter(company__in=company_ids).count()
    activos_accounts = ChartOfAccounts.objects.filter(company__in=company_ids, code__startswith='1').count()
    pasivos_accounts = ChartOfAccounts.objects.filter(company__in=company_ids, code__startswith='2').count()
    patrimonio_accounts = ChartOfAccounts.objects.filter(company__in=company_ids, code__startswith='3').count()
    ingresos_accounts = ChartOfAccounts.objects.filter(company__in=company_ids, code__startswith='4').count()
    gastos_accounts = ChartOfAccounts.objects.filter(company__in=company_ids, code__startswith='5').count()
    
    print(f"   Total de cuentas: {total_accounts}")
    print(f"   Activos (1.x): {activos_accounts} cuentas")
    print(f"   Pasivos (2.x): {pasivos_accounts} cuentas")
    print(f"   Patrimonio (3.x): {patrimonio_accounts} cuentas")
    print(f"   Ingresos (4.x): {ingresos_accounts} cuentas")
    print(f"   Gastos (5.x): {gastos_accounts} cuentas")
    print()
    
    # === KPIs CALCULADOS ===
    print("📈 KPIs PRINCIPALES:")
    print(f"   Total facturas: {total_invoices}")
    print(f"   Ingresos mensuales: ${monthly_income}")
    print(f"   Asientos pendientes: {draft_entries}")
    print(f"   Balance saludable: {'Sí' if is_balanced else 'No'}")
    print(f"   Tasa de cobro: {collection_rate}%")
    print(f"   Tasa de contabilización: {posted_rate}%")
    
    print("\n✅ MÉTRICAS CALCULADAS EXITOSAMENTE")
    print("🌐 Dashboard disponible en: http://localhost:8000/dashboard/")

if __name__ == "__main__":
    try:
        test_financial_metrics()
    except Exception as e:
        print(f"❌ Error ejecutando pruebas: {e}")
        import traceback
        traceback.print_exc()