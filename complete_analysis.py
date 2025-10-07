#!/usr/bin/env python
"""
Análisis completo de la factura ID 99 para debug
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from apps.banking.models import BankAccount
from apps.accounting.models import ChartOfAccounts

def complete_analysis():
    """Análisis completo de la discrepancia"""
    
    print("🕵️ ANÁLISIS COMPLETO: Factura vs JavaScript")
    print("=" * 45)
    
    try:
        # 1. Verificar factura
        invoice = Invoice.objects.get(id=99)
        print(f"📄 FACTURA ID 99:")
        print(f"   Número: {invoice.number}")
        print(f"   Account ID: {invoice.account.id if invoice.account else 'NULL'}")
        print(f"   Account Código: {invoice.account.code if invoice.account else 'NULL'}")
        print(f"   Account Nombre: {invoice.account.name if invoice.account else 'NULL'}")
        print(f"   Método pago: {invoice.payment_form}")
        print(f"   Empresa: {invoice.company}")
        
        # 2. Verificar todas las cuentas contables bancarias disponibles
        print(f"\n🏦 CUENTAS CONTABLES BANCARIAS DE LA EMPRESA:")
        chart_accounts = ChartOfAccounts.objects.filter(
            company=invoice.company,
            aux_type='bank'
        ).order_by('code')
        
        for acc in chart_accounts:
            is_selected = acc.id == invoice.account.id if invoice.account else False
            marker = " ← SELECCIONADA EN FACTURA" if is_selected else ""
            print(f"   {acc.id}: {acc.code} - {acc.name}{marker}")
        
        # 3. Verificar cuentas bancarias (BankAccount)
        print(f"\n🏛️ CUENTAS BANCARIAS (BankAccount):")
        bank_accounts = BankAccount.objects.filter(
            company=invoice.company,
            is_active=True
        )
        
        for bank in bank_accounts:
            chart_id = bank.chart_account.id if bank.chart_account else None
            matches_invoice = chart_id == invoice.account.id if invoice.account else False
            marker = " ← DEBE APARECER SELECCIONADA" if matches_invoice else ""
            
            print(f"   BankAccount ID: {bank.id}")
            print(f"     Chart Account: {chart_id} ({bank.chart_account.code if bank.chart_account else 'N/A'})")
            print(f"     Banco: {bank.bank.short_name}")
            print(f"     Coincide: {'✅ SÍ' if matches_invoice else '❌ No'}{marker}")
        
        # 4. Simular lo que JavaScript debería ver
        print(f"\n💻 SIMULACIÓN JAVASCRIPT:")
        if invoice.account:
            target_id = invoice.account.id
            print(f"   Django campo 'account': {target_id}")
            
            matching_bank = bank_accounts.filter(chart_account_id=target_id).first()
            if matching_bank:
                print(f"   ✅ JavaScript DEBE encontrar:")
                print(f"      BankAccount ID: {matching_bank.id}")
                print(f"      Texto mostrado: {matching_bank.bank.short_name} - ****{matching_bank.account_number[-4:] if matching_bank.account_number else 'N/A'}")
                print(f"      dataset.chartAccountId: {matching_bank.chart_account.id}")
            else:
                print(f"   ❌ JavaScript NO encontrará coincidencia")
                print(f"      Buscando chartAccountId == {target_id}")
                print(f"      Disponibles: {[b.chart_account.id for b in bank_accounts if b.chart_account]}")
        
        # 5. Verificar el problema específico de los logs
        print(f"\n🔍 ANÁLISIS DEL LOG DE ERROR:")
        print(f"   Log reportó: 'Django account = 38'")
        print(f"   BD muestra: 'account = {invoice.account.id if invoice.account else 'NULL'}'")
        
        if invoice.account and invoice.account.id != 38:
            print(f"   ⚠️ DISCREPANCIA DETECTADA!")
            print(f"      Posibles causas:")
            print(f"      1. Caché del navegador")
            print(f"      2. Múltiples campos con ID 'id_account'")
            print(f"      3. JavaScript leyendo campo equivocado")
            print(f"      4. Factura actualizada pero página no recargada")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    complete_analysis()