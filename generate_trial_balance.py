#!/usr/bin/env python
"""
Script para generar Balance de Comprobación completo
Uso: python generate_trial_balance.py [company_id] [start_date] [end_date]
"""
import os
import sys
import django
from datetime import datetime, date
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import ChartOfAccounts, JournalEntryLine, JournalEntry
from apps.companies.models import Company


def format_currency(amount):
    """Formatear monto como moneda"""
    if amount == 0:
        return ""
    return f"${amount:,.2f}"


def generate_trial_balance_report(company_id=None, start_date=None, end_date=None):
    """Generar reporte completo de Balance de Comprobación"""
    
    # Obtener empresa
    if company_id:
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            print(f"❌ Error: Empresa con ID {company_id} no encontrada")
            return
    else:
        # Usar primera empresa activa
        company = Company.objects.filter(is_active=True).first()
        if not company:
            print("❌ Error: No hay empresas activas")
            return
    
    # Fechas
    if end_date is None:
        end_date = date.today()
    elif isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    if start_date and isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    print("\n" + "="*80)
    print("                    BALANCE DE COMPROBACIÓN")
    print("="*80)
    print(f"Empresa: {company.legal_name}")
    print(f"RUC: {company.ruc}")
    
    if start_date:
        print(f"Período: Del {start_date.strftime('%d/%m/%Y')} al {end_date.strftime('%d/%m/%Y')}")
    else:
        print(f"Período: Al {end_date.strftime('%d/%m/%Y')}")
    
    print("="*80)
    
    # Encabezados de la tabla
    print(f"{'Código':<12} {'Cuenta':<30} {'Saldo Inicial':<24} {'Movimientos Período':<24} {'Saldo Final':<24}")
    print(f"{'':<12} {'':<30} {'Débito':<12}{'Crédito':<12} {'Débito':<12}{'Crédito':<12} {'Débito':<12}{'Crédito':<12}")
    print("-"*130)
    
    # Obtener todas las cuentas con movimientos
    accounts_with_movement = []
    
    # Filtro base para asientos contabilizados
    base_filter = {
        'journal_entry__company': company,
        'journal_entry__state': 'posted'
    }
    
    if end_date:
        base_filter['journal_entry__date__lte'] = end_date
    
    # Obtener todas las cuentas que tienen movimientos
    account_ids = JournalEntryLine.objects.filter(**base_filter).values_list('account_id', flat=True).distinct()
    accounts = ChartOfAccounts.objects.filter(id__in=account_ids, company=company).order_by('code')
    
    total_initial_debit = Decimal('0.00')
    total_initial_credit = Decimal('0.00')
    total_period_debit = Decimal('0.00')
    total_period_credit = Decimal('0.00')
    total_final_debit = Decimal('0.00')
    total_final_credit = Decimal('0.00')
    
    for account in accounts:
        # Saldo inicial
        initial_debit = Decimal('0.00')
        initial_credit = Decimal('0.00')
        
        if start_date:
            initial_movements = JournalEntryLine.objects.filter(
                account=account,
                journal_entry__company=company,
                journal_entry__date__lt=start_date,
                journal_entry__state='posted'
            ).aggregate(
                debit_sum=django.db.models.Sum('debit'),
                credit_sum=django.db.models.Sum('credit')
            )
            
            initial_debit_total = initial_movements['debit_sum'] or Decimal('0.00')
            initial_credit_total = initial_movements['credit_sum'] or Decimal('0.00')
            
            # Balance inicial según naturaleza de la cuenta
            if account.account_type.code in ['ASSET', 'EXPENSE']:
                balance = initial_debit_total - initial_credit_total
                if balance >= 0:
                    initial_debit = balance
                else:
                    initial_credit = abs(balance)
            else:
                balance = initial_credit_total - initial_debit_total
                if balance >= 0:
                    initial_credit = balance
                else:
                    initial_debit = abs(balance)
        
        # Movimientos del período
        period_filter = {
            'account': account,
            'journal_entry__company': company,
            'journal_entry__state': 'posted'
        }
        
        if start_date:
            period_filter['journal_entry__date__gte'] = start_date
        if end_date:
            period_filter['journal_entry__date__lte'] = end_date
        
        period_movements = JournalEntryLine.objects.filter(**period_filter).aggregate(
            debit_sum=django.db.models.Sum('debit'),
            credit_sum=django.db.models.Sum('credit')
        )
        
        period_debit = period_movements['debit_sum'] or Decimal('0.00')
        period_credit = period_movements['credit_sum'] or Decimal('0.00')
        
        # Saldo final
        final_debit_total = initial_debit + period_debit
        final_credit_total = initial_credit + period_credit
        
        # Saldo final neto
        if account.account_type.code in ['ASSET', 'EXPENSE']:
            final_balance = final_debit_total - final_credit_total
            if final_balance >= 0:
                final_debit = final_balance
                final_credit = Decimal('0.00')
            else:
                final_debit = Decimal('0.00')
                final_credit = abs(final_balance)
        else:
            final_balance = final_credit_total - final_debit_total
            if final_balance >= 0:
                final_credit = final_balance
                final_debit = Decimal('0.00')
            else:
                final_credit = Decimal('0.00')
                final_debit = abs(final_balance)
        
        # Solo mostrar cuentas con movimiento
        if (initial_debit + initial_credit + period_debit + period_credit + 
            final_debit + final_credit) > 0:
            
            # Imprimir la línea de la cuenta
            account_name = account.name[:28] if len(account.name) > 28 else account.name
            
            print(f"{account.code:<12} {account_name:<30} "
                  f"{format_currency(initial_debit):<12}{format_currency(initial_credit):<12} "
                  f"{format_currency(period_debit):<12}{format_currency(period_credit):<12} "
                  f"{format_currency(final_debit):<12}{format_currency(final_credit):<12}")
            
            # Sumar a totales
            total_initial_debit += initial_debit
            total_initial_credit += initial_credit
            total_period_debit += period_debit
            total_period_credit += period_credit
            total_final_debit += final_debit
            total_final_credit += final_credit
    
    # Imprimir totales
    print("-"*130)
    print(f"{'TOTALES':<42} "
          f"{format_currency(total_initial_debit):<12}{format_currency(total_initial_credit):<12} "
          f"{format_currency(total_period_debit):<12}{format_currency(total_period_credit):<12} "
          f"{format_currency(total_final_debit):<12}{format_currency(total_final_credit):<12}")
    
    print("="*130)
    
    # Verificar balance
    print("\n📊 VERIFICACIÓN DEL BALANCE:")
    
    initial_balanced = abs(total_initial_debit - total_initial_credit) < 0.01
    period_balanced = abs(total_period_debit - total_period_credit) < 0.01
    final_balanced = abs(total_final_debit - total_final_credit) < 0.01
    
    print(f"• Saldo Inicial: {'✅ CUADRADO' if initial_balanced else '❌ DESCUADRADO'}")
    if not initial_balanced:
        print(f"  Diferencia: ${abs(total_initial_debit - total_initial_credit):,.2f}")
    
    print(f"• Movimientos del Período: {'✅ CUADRADO' if period_balanced else '❌ DESCUADRADO'}")
    if not period_balanced:
        print(f"  Diferencia: ${abs(total_period_debit - total_period_credit):,.2f}")
    
    print(f"• Saldo Final: {'✅ CUADRADO' if final_balanced else '❌ DESCUADRADO'}")
    if not final_balanced:
        print(f"  Diferencia: ${abs(total_final_debit - total_final_credit):,.2f}")
    
    # Estadísticas adicionales
    print(f"\n📈 ESTADÍSTICAS:")
    print(f"• Total de cuentas con movimientos: {len(accounts)}")
    print(f"• Total de asientos contabilizados: {JournalEntry.objects.filter(company=company, state='posted').count()}")
    
    if final_balanced:
        print(f"\n🎉 ¡EL BALANCE ESTÁ PERFECTAMENTE CUADRADO!")
    else:
        print(f"\n⚠️  Hay diferencias en el balance. Revisar asientos contables.")
    
    print("\n" + "="*80)


def main():
    """Función principal"""
    print("🧮 Generador de Balance de Comprobación - ContaEC")
    
    # Parsear argumentos
    company_id = None
    start_date = None
    end_date = None
    
    if len(sys.argv) > 1:
        company_id = int(sys.argv[1])
    if len(sys.argv) > 2:
        start_date = sys.argv[2]
    if len(sys.argv) > 3:
        end_date = sys.argv[3]
    
    # Mostrar empresas disponibles si no se especifica una
    if not company_id:
        print("\n📁 Empresas disponibles:")
        companies = Company.objects.filter(is_active=True)
        if companies:
            for i, company in enumerate(companies, 1):
                print(f"{company.id:2d}. {company.trade_name} ({company.ruc})")
        else:
            print("❌ No hay empresas activas")
            return
    
    # Generar el reporte
    try:
        generate_trial_balance_report(company_id, start_date, end_date)
    except Exception as e:
        print(f"❌ Error generando el reporte: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()