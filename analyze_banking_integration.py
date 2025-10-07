#!/usr/bin/env python3
"""
ANÁLISIS DE INTEGRACIÓN: Cuenta Bancaria → Asiento Contable + Movimiento Bancario
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def main():
    print("🔍 ANÁLISIS DE INTEGRACIÓN BANCARIA")
    print("=" * 70)
    
    # 1. Estado Actual del Sistema
    print("\n📋 1. ESTADO ACTUAL DEL SISTEMA:")
    print("-" * 50)
    
    from apps.accounting.models import ChartOfAccounts
    from apps.companies.models import Company
    
    try:
        from apps.banking.models import BankAccount, BankTransaction
        banking_available = True
        print("✅ Módulo Banking disponible")
    except ImportError:
        banking_available = False
        print("❌ Módulo Banking NO disponible")
    
    # Verificar cuentas bancarias en Chart of Accounts
    gueber = Company.objects.get(trade_name="GUEBER")
    bank_accounts = ChartOfAccounts.objects.filter(
        company=gueber,
        code__startswith="1.1.02",  # BANCOS
        accepts_movement=True
    ).order_by('code')
    
    print(f"\n🏦 Cuentas bancarias contables en {gueber.trade_name}:")
    for account in bank_accounts:
        print(f"   📊 {account.code} - {account.name} (ID: {account.id})")
        
        if banking_available:
            # Verificar si tiene BankAccount vinculado
            try:
                bank_account = BankAccount.objects.get(chart_account=account)
                print(f"      └─ ✅ Vinculado con: {bank_account.bank.name} - {bank_account.account_number}")
            except BankAccount.DoesNotExist:
                print(f"      └─ ❌ Sin BankAccount vinculado")
    
    # 2. Flujo Actual de Asientos Contables
    print(f"\n💼 2. FLUJO ACTUAL DE ASIENTOS CONTABLES:")
    print("-" * 50)
    print("""
    ESTADO ACTUAL (apps/accounting/services.py):
    
    1. AutomaticJournalEntryService.create_journal_entry_from_invoice()
    2. _create_debit_line() - Usa invoice.account (ChartOfAccounts seleccionado)
    3. _create_credit_lines() - Crea líneas de ventas e IVA
    4. Descripción incluye bank_observations si es transferencia
    
    PROBLEMA: No se crea movimiento bancario automático
    """)
    
    # 3. Integración Necesaria
    print(f"\n🎯 3. INTEGRACIÓN NECESARIA:")
    print("-" * 50)
    print("""
    CUANDO: Usuario selecciona "Transferencia" y cuenta bancaria específica
    
    DEBE SUCEDER:
    
    A. ASIENTO CONTABLE (YA EXISTE):
       ✅ DEBE: Cuenta bancaria seleccionada (ej: 1.1.02.02 - BANCO PICHINCHA)
       ✅ HABER: Cuenta de ventas + IVA
       ✅ Descripción con bank_observations
    
    B. MOVIMIENTO BANCARIO (NUEVO):
       🆕 Crear BankTransaction automáticamente
       🆕 Vincular con JournalEntry
       🆕 Tipo: 'credit' (ingreso al banco)
       🆕 Monto: invoice.total (neto después de retenciones)
    """)
    
    # 4. Implementación Propuesta
    print(f"\n🔧 4. IMPLEMENTACIÓN PROPUESTA:")
    print("-" * 50)
    print("""
    OPCIÓN 1: Extender AutomaticJournalEntryService
    ──────────────────────────────────────────────
    
    Archivo: apps/accounting/services.py
    
    Método nuevo: _create_bank_transaction_if_applicable()
    
    Lógica:
    1. Verificar si invoice.payment_form es "Transferencia"
    2. Verificar si invoice.account tiene BankAccount vinculado
    3. Crear BankTransaction con:
       - bank_account = BankAccount relacionado
       - transaction_type = 'credit' 
       - amount = monto neto de factura
       - description = f"Ingreso por venta - Factura #{invoice.number}"
       - reference = f"FAC-{invoice.number}"
       - journal_entry = asiento creado
    
    OPCIÓN 2: Crear servicio independiente
    ──────────────────────────────────────
    
    Archivo: apps/banking/services.py (nuevo)
    
    Clase: BankingIntegrationService
    
    Método: create_bank_transaction_from_invoice()
    """)
    
    # 5. Puntos de integración
    print(f"\n🔗 5. PUNTOS DE INTEGRACIÓN:")
    print("-" * 50)
    print("""
    LLAMADA DESDE: apps/invoicing/admin.py
    
    En _handle_journal_entry_creation():
    
    # Después de crear el asiento contable
    if created and journal_entry:
        # NUEVO: Crear movimiento bancario si aplica
        try:
            bank_transaction = BankingIntegrationService.create_bank_transaction_from_invoice(
                invoice, journal_entry
            )
            if bank_transaction:
                messages.success(request, f"💳 Movimiento bancario creado: {bank_transaction.reference}")
        except Exception as e:
            messages.warning(request, f"⚠️ Asiento creado pero error en movimiento bancario: {e}")
    """)
    
    # 6. Validaciones necesarias
    print(f"\n✅ 6. VALIDACIONES NECESARIAS:")
    print("-" * 50)
    print("""
    ANTES DE CREAR MOVIMIENTO BANCARIO:
    
    1. ✓ invoice.payment_form existe y es "Transferencia"
    2. ✓ invoice.account existe (ChartOfAccounts)
    3. ✓ Existe BankAccount con chart_account = invoice.account
    4. ✓ BankAccount está activo (is_active=True)
    5. ✓ No existe ya un BankTransaction para esta factura
    
    MANEJO DE ERRORES:
    - Si no hay BankAccount vinculado: Warning, no error crítico
    - Si hay error: Asiento se crea igual, solo se registra warning
    """)
    
    # 7. Verificar facturas de prueba
    if banking_available:
        print(f"\n🧪 7. VERIFICACIÓN CON FACTURA DE PRUEBA:")
        print("-" * 50)
        
        from apps.invoicing.models import Invoice
        
        try:
            test_invoice = Invoice.objects.get(id=99)
            print(f"📄 Factura #{test_invoice.number}")
            print(f"   Forma de pago: {test_invoice.payment_form}")
            print(f"   Cuenta: {test_invoice.account}")
            print(f"   Total: ${test_invoice.total}")
            
            if test_invoice.account:
                try:
                    related_bank_account = BankAccount.objects.get(chart_account=test_invoice.account)
                    print(f"   ✅ BankAccount vinculado: {related_bank_account.bank.name}")
                    print(f"   📋 Número cuenta: {related_bank_account.account_number}")
                    
                    # Verificar si ya tiene transacciones
                    existing_transactions = BankTransaction.objects.filter(
                        reference=f"FAC-{test_invoice.id}"
                    )
                    print(f"   📊 Transacciones existentes: {existing_transactions.count()}")
                    
                except BankAccount.DoesNotExist:
                    print(f"   ❌ Sin BankAccount vinculado - NO se puede crear movimiento bancario")
                    
        except Invoice.DoesNotExist:
            print("❌ Factura de prueba no encontrada")

if __name__ == '__main__':
    main()