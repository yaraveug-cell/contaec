#!/usr/bin/env python
"""
Corregir factura ID 99 para que coincida con la cuenta bancaria disponible
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from apps.banking.models import BankAccount
from apps.accounting.models import ChartOfAccounts

def fix_invoice_account():
    """Corregir la cuenta de la factura para que coincida"""
    
    print("🔧 CORRECCIÓN: Sincronizar factura con cuenta bancaria")
    print("=" * 52)
    
    try:
        # Obtener la factura ID 99
        invoice = Invoice.objects.get(id=99)
        print(f"📄 Factura encontrada: #{invoice.number}")
        print(f"   💳 Método actual: {invoice.payment_form}")
        print(f"   🏦 Cuenta actual: {invoice.account.id if invoice.account else 'N/A'} - {invoice.account if invoice.account else 'N/A'}")
        
        # Obtener la cuenta bancaria disponible
        bank_account = BankAccount.objects.filter(
            company=invoice.company,
            is_active=True
        ).first()
        
        if not bank_account:
            print("❌ No hay cuentas bancarias disponibles")
            return False
            
        chart_account = bank_account.chart_account
        if not chart_account:
            print("❌ La cuenta bancaria no tiene cuenta contable asociada")
            return False
        
        print(f"\n🎯 CORRECCIÓN NECESARIA:")
        print(f"   🔄 Cambiar de: {invoice.account.id if invoice.account else 'N/A'}")
        print(f"   ➡️ Cambiar a: {chart_account.id}")
        print(f"   🏛️ Banco: {bank_account.bank.short_name}")
        print(f"   📋 Código: {chart_account.code}")
        
        # Actualizar la factura
        invoice.account = chart_account
        invoice.save()
        
        print(f"\n✅ FACTURA ACTUALIZADA:")
        print(f"   📄 ID: {invoice.id}")
        print(f"   🏦 Nueva cuenta: {invoice.account.id} - {invoice.account}")
        
        print(f"\n🔍 VERIFICACIÓN JAVASCRIPT:")
        print(f"   ✅ Django field 'account' ahora tiene: {invoice.account.id}")
        print(f"   ✅ JavaScript debe buscar chartAccountId == {invoice.account.id}")
        print(f"   ✅ Debe encontrar BankAccount ID: {bank_account.id}")
        print(f"   ✅ Debe pre-seleccionar: {bank_account.bank.short_name} - ****{bank_account.account_number[-4:] if bank_account.account_number else 'N/A'}")
        
        print(f"\n🌐 PROBAR NUEVAMENTE:")
        print(f"   http://localhost:8000/admin/invoicing/invoice/{invoice.id}/change/")
        print(f"   🔄 Recargar página (F5) para ver los cambios")
        
        return True
        
    except Invoice.DoesNotExist:
        print("❌ Factura ID 99 no encontrada")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    fix_invoice_account()