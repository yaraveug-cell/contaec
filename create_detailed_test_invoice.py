#!/usr/bin/env python
"""
Crear factura específica para verificar pre-selección de cuenta bancaria
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from apps.companies.models import Company, PaymentMethod
from apps.accounting.models import ChartOfAccounts
from apps.invoicing.models import Customer
from apps.banking.models import BankAccount
from django.contrib.auth import get_user_model
import time

def create_detailed_test_invoice():
    """Crear factura con información detallada para debug"""
    
    print("🔍 ANÁLISIS DETALLADO PARA PRE-SELECCIÓN")
    print("=" * 45)
    
    # Obtener datos
    company = Company.objects.first()
    customer = Customer.objects.filter(company=company).first()
    
    transfer_method = PaymentMethod.objects.filter(
        name__icontains='transferencia',
        is_active=True
    ).first()
    
    User = get_user_model()
    test_user = User.objects.first()
    
    # Buscar cuentas contables de tipo bancario
    chart_accounts = ChartOfAccounts.objects.filter(
        company=company,
        aux_type='bank',
        accepts_movement=True
    )
    
    print(f"\n📊 CUENTAS CONTABLES BANCARIAS DISPONIBLES:")
    print("-" * 42)
    for acc in chart_accounts:
        print(f"   🏦 ID: {acc.id} | Código: {acc.code} | Nombre: {acc.name}")
    
    # Buscar cuentas bancarias vinculadas
    bank_accounts = BankAccount.objects.filter(
        company=company,
        is_active=True
    )
    
    print(f"\n🏛️ CUENTAS BANCARIAS (BankAccount) DISPONIBLES:")
    print("-" * 47)
    for bank in bank_accounts:
        print(f"   💳 ID: {bank.id} | Banco: {bank.bank.short_name}")
        print(f"      🔗 Chart Account ID: {bank.chart_account.id if bank.chart_account else 'N/A'}")
        print(f"      📋 Número: ****{bank.account_number[-4:] if bank.account_number else 'N/A'}")
        print(f"      📊 Tipo: {bank.get_account_type_display()}")
        print("")
    
    # Seleccionar la primera cuenta bancaria disponible
    bank_account = bank_accounts.first()
    if not bank_account:
        print("❌ No hay cuentas bancarias configuradas")
        return None
    
    chart_account = bank_account.chart_account
    if not chart_account:
        print("❌ La cuenta bancaria no tiene cuenta contable asociada")
        return None
    
    print(f"✅ CUENTA SELECCIONADA PARA LA PRUEBA:")
    print(f"   💳 BankAccount ID: {bank_account.id}")
    print(f"   🏦 Chart Account ID: {chart_account.id}")
    print(f"   📋 Código: {chart_account.code}")
    print(f"   🏛️ Banco: {bank_account.bank.short_name}")
    
    # Crear observaciones específicas
    test_observations = f"""PRUEBA PRE-SELECCIÓN CUENTA BANCARIA
===========================================
Banco: {bank_account.bank.short_name}
Cuenta: ****{bank_account.account_number[-4:] if bank_account.account_number else 'N/A'}
Código contable: {chart_account.code}
Chart Account ID: {chart_account.id}
Bank Account ID: {bank_account.id}

VERIFICAR:
✓ Selector muestra cuenta pre-seleccionada
✓ NO muestra "Seleccionar cuenta bancaria"
✓ Observaciones se cargan correctamente
✓ JavaScript hace match correcto por chart_account_id"""
    
    test_number = f"PRESEL-TEST-{int(time.time())}"
    
    # Crear factura con cuenta específica
    test_invoice = Invoice.objects.create(
        company=company,
        customer=customer,
        number=test_number,
        payment_form=transfer_method,
        account=chart_account,  # ← Clave: usar chart_account, no bank_account
        created_by=test_user,
        bank_observations=test_observations,
        status='draft'
    )
    
    print(f"\n✅ FACTURA CREADA:")
    print(f"   📄 ID: {test_invoice.id}")
    print(f"   📄 Número: {test_invoice.number}")
    print(f"   💳 Método: {test_invoice.payment_form}")
    print(f"   🏦 Account (Chart): {test_invoice.account.id} - {test_invoice.account.code}")
    
    print(f"\n🌐 URL PARA PROBAR:")
    print(f"   http://localhost:8000/admin/invoicing/invoice/{test_invoice.id}/change/")
    
    print(f"\n🔍 VERIFICACIONES JAVASCRIPT:")
    print(f"   1. Campo 'Cuenta' Django tiene valor: {chart_account.id}")
    print(f"   2. JavaScript debe buscar option con dataset.chartAccountId == {chart_account.id}")
    print(f"   3. JavaScript debe encontrar BankAccount ID: {bank_account.id}")
    print(f"   4. Selector debe mostrar: {bank_account.bank.short_name} - ****{bank_account.account_number[-4:] if bank_account.account_number else 'N/A'}")
    
    print(f"\n⚠️  IMPORTANTE: Factura NO se eliminará automáticamente")
    print(f"    Para eliminar: ID {test_invoice.id}")
    
    return test_invoice.id

if __name__ == "__main__":
    invoice_id = create_detailed_test_invoice()