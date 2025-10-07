#!/usr/bin/env python
"""
Debug: Verificar datos que JavaScript debería recibir
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from apps.banking.models import BankAccount
from apps.companies.models import Company
import json

def debug_invoice_data():
    """Verificar los datos exactos que JavaScript debería recibir"""
    
    print("🔍 DEBUG: Datos para JavaScript")
    print("=" * 35)
    
    # Buscar la factura más reciente con transferencia
    invoice = Invoice.objects.filter(
        payment_form__name__icontains='transferencia'
    ).order_by('-id').first()
    
    if not invoice:
        print("❌ No hay facturas con transferencia")
        return
    
    print(f"📄 FACTURA ANALIZADA: #{invoice.number} (ID: {invoice.id})")
    print(f"   💳 Método de pago: {invoice.payment_form}")
    print(f"   🏦 Account (Django): {invoice.account.id if invoice.account else 'N/A'}")
    print(f"   💬 bank_observations: '{invoice.bank_observations[:100]}...' (length: {len(invoice.bank_observations)})")
    
    # Obtener cuentas bancarias disponibles para la empresa
    company = invoice.company
    bank_accounts = BankAccount.objects.filter(
        company=company,
        is_active=True
    ).select_related('bank', 'chart_account')
    
    print(f"\n🏛️ CUENTAS BANCARIAS DISPONIBLES PARA JAVASCRIPT:")
    print("-" * 50)
    
    for bank in bank_accounts:
        is_match = bank.chart_account and bank.chart_account.id == invoice.account.id if invoice.account else False
        match_indicator = " ← DEBE ESTAR SELECCIONADA" if is_match else ""
        
        print(f"   💳 BankAccount ID: {bank.id}{match_indicator}")
        print(f"      🏛️ Banco: {bank.bank.short_name}")
        print(f"      🔗 Chart Account ID: {bank.chart_account.id if bank.chart_account else 'N/A'}")
        print(f"      📋 Número: ****{bank.account_number[-4:] if bank.account_number else 'N/A'}")
        print(f"      📊 Tipo: {bank.get_account_type_display()}")
        print(f"      🎯 ¿Coincide?: {'✅ SÍ' if is_match else '❌ No'}")
        print("")
    
    # Simular datos JSON que JavaScript recibiría
    bank_accounts_data = []
    for bank in bank_accounts:
        bank_data = {
            'id': bank.id,
            'bank_short_name': bank.bank.short_name,
            'account_number': bank.account_number,
            'account_type_display': bank.get_account_type_display(),
            'chart_account_id': bank.chart_account.id if bank.chart_account else None,
            'chart_account_code': bank.chart_account.code if bank.chart_account else None,
            'chart_account_name': bank.chart_account.name if bank.chart_account else None,
        }
        bank_accounts_data.append(bank_data)
    
    print(f"📤 JSON QUE JAVASCRIPT RECIBIRÍA:")
    print("-" * 33)
    print(json.dumps(bank_accounts_data, indent=2, ensure_ascii=False))
    
    # Verificar qué opción debería estar seleccionada
    if invoice.account:
        target_chart_id = invoice.account.id
        matching_bank = bank_accounts.filter(chart_account_id=target_chart_id).first()
        
        print(f"\n🎯 VERIFICACIÓN DE COINCIDENCIA:")
        print(f"   🔍 Django field 'account' tiene ID: {target_chart_id}")
        print(f"   🔍 JavaScript debe buscar: option con dataset.chartAccountId == {target_chart_id}")
        
        if matching_bank:
            print(f"   ✅ ENCONTRADA: BankAccount ID {matching_bank.id}")
            print(f"   ✅ Selector debe pre-seleccionar: {matching_bank.bank.short_name} - ****{matching_bank.account_number[-4:] if matching_bank.account_number else 'N/A'}")
            print(f"   ✅ JavaScript debe asignar: bankSelect.value = '{matching_bank.id}'")
        else:
            print(f"   ❌ NO ENCONTRADA: No hay BankAccount con chart_account_id = {target_chart_id}")
    else:
        print(f"\n⚠️ La factura no tiene campo 'account' asignado")

if __name__ == "__main__":
    debug_invoice_data()