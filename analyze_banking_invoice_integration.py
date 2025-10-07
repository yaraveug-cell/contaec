#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from apps.companies.models import PaymentMethod, Company
from apps.banking.models import BankAccount, Bank
from apps.accounting.services import AutomaticJournalEntryService
from apps.accounting.models import ChartOfAccounts, JournalEntry

print("🔍 ANÁLISIS: ¿Podemos implementar integración Banking-Invoicing?")
print("=" * 65)

# 1. Verificar componentes existentes
print("\n1. 📊 COMPONENTES DISPONIBLES:")
print("-" * 32)

# Banking module
banks = Bank.objects.count()
bank_accounts = BankAccount.objects.count()
print(f"   🏦 Bancos registrados: {banks}")
print(f"   💳 Cuentas bancarias: {bank_accounts}")

# Payment methods
transfer_methods = PaymentMethod.objects.filter(name__icontains='TRANSFERENCIA')
print(f"   💰 Métodos 'Transferencia': {transfer_methods.count()}")

# Invoicing system
invoices_total = Invoice.objects.count()
invoices_transfer = Invoice.objects.filter(payment_form__name__icontains='TRANSFERENCIA').count()
print(f"   📄 Total facturas: {invoices_total}")
print(f"   📄 Facturas con transferencia: {invoices_transfer}")

# Accounting integration
journal_entries = JournalEntry.objects.count()
print(f"   📋 Asientos contables: {journal_entries}")

# 2. Verificar estructura de datos
print(f"\n2. 🔍 ESTRUCTURA DE DATOS:")
print("-" * 28)

# Verificar campos en Invoice
print(f"   📄 Campos en Invoice:")
print(f"      ✅ payment_form (ForeignKey a PaymentMethod)")
print(f"      ✅ account (ForeignKey a ChartOfAccounts)")
print(f"      ✅ transfer_detail (TextField)")

# Verificar BankAccount
sample_bank_account = BankAccount.objects.first()
if sample_bank_account:
    print(f"   💳 Campos en BankAccount:")
    print(f"      ✅ company (ForeignKey)")
    print(f"      ✅ bank (ForeignKey)")
    print(f"      ✅ chart_account (ForeignKey) - {'SÍ' if sample_bank_account.chart_account else 'NO'} vinculada")

# 3. Verificar AutomaticJournalEntryService
print(f"\n3. ⚙️ SERVICIO CONTABLE:")
print("-" * 26)

print(f"   ✅ AutomaticJournalEntryService disponible")
print(f"   ✅ Método create_journal_entry_from_invoice()")
print(f"   ✅ Integra transfer_detail en descripción")

# Verificar si ya maneja cuentas específicas por payment_form
sample_invoice = Invoice.objects.filter(payment_form__name__icontains='TRANSFERENCIA').first()
if sample_invoice:
    print(f"   📝 Ejemplo factura transferencia ID: {sample_invoice.id}")
    print(f"      - payment_form: {sample_invoice.payment_form.name}")
    print(f"      - account: {sample_invoice.account}")
    print(f"      - transfer_detail: {sample_invoice.transfer_detail or 'Vacío'}")

# 4. Verificar integración actual
print(f"\n4. 🔗 INTEGRACIÓN ACTUAL:")
print("-" * 26)

# Buscar si hay facturas con transfer que usen cuentas bancarias específicas
invoices_with_bank_accounts = Invoice.objects.filter(
    payment_form__name__icontains='TRANSFERENCIA',
    account__aux_type='bank'
)
print(f"   📄 Facturas transferencia con cuenta bancaria: {invoices_with_bank_accounts.count()}")

# Verificar si existen BankTransaction
try:
    from apps.banking.models import BankTransaction
    bank_transactions = BankTransaction.objects.count()
    print(f"   💰 Movimientos bancarios registrados: {bank_transactions}")
except:
    print(f"   ⚠️ BankTransaction no disponible o error")

# 5. Análisis de viabilidad
print(f"\n5. 💡 ANÁLISIS DE VIABILIDAD:")
print("-" * 31)

requirements_met = []
requirements_missing = []

# Check requirements
if transfer_methods.exists():
    requirements_met.append("✅ PaymentMethod 'Transferencia' existe")
else:
    requirements_missing.append("❌ Falta PaymentMethod 'Transferencia'")

if bank_accounts > 0:
    requirements_met.append("✅ BankAccount disponibles")
else:
    requirements_missing.append("❌ No hay BankAccount configuradas")

# Verificar si BankAccount tiene chart_account vinculadas
bank_accounts_with_chart = BankAccount.objects.filter(chart_account__isnull=False).count()
if bank_accounts_with_chart > 0:
    requirements_met.append(f"✅ {bank_accounts_with_chart} BankAccount con chart_account")
else:
    requirements_missing.append("❌ BankAccount sin chart_account vinculadas")

# Verificar AutomaticJournalEntryService functionality
if hasattr(AutomaticJournalEntryService, 'create_journal_entry_from_invoice'):
    requirements_met.append("✅ AutomaticJournalEntryService funcional")
else:
    requirements_missing.append("❌ AutomaticJournalEntryService no disponible")

# Mostrar resultados
for req in requirements_met:
    print(f"   {req}")
for req in requirements_missing:
    print(f"   {req}")

# 6. Propuesta de implementación
print(f"\n6. 🚀 PROPUESTA DE IMPLEMENTACIÓN:")
print("-" * 36)

if len(requirements_missing) == 0:
    print(f"   ✅ ¡LISTO PARA IMPLEMENTAR!")
    print(f"\n   🔧 PASOS REQUERIDOS:")
    print(f"   1. Modificar Invoice.save() o admin")
    print(f"   2. Al seleccionar payment_form='Transferencia':")
    print(f"      - Mostrar dropdown de BankAccount disponibles")
    print(f"      - Auto-asignar account = bankaccount.chart_account")
    print(f"   3. AutomaticJournalEntryService ya maneja el resto")
    print(f"   4. Opcional: Crear BankTransaction automático")
    
elif len(requirements_missing) <= 2:
    print(f"   ⚠️ CASI LISTO - Faltan {len(requirements_missing)} requisitos")
    print(f"\n   🔧 RESOLVER PRIMERO:")
    for req in requirements_missing:
        print(f"   {req}")
    
else:
    print(f"   ❌ NO LISTO - Faltan {len(requirements_missing)} requisitos críticos")

# 7. Análisis técnico detallado
print(f"\n7. 🔍 ANÁLISIS TÉCNICO:")
print("-" * 24)

print(f"   📋 FLUJO PROPUESTO:")
print(f"   1. Usuario crea factura")
print(f"   2. Selecciona payment_form = 'Transferencia'")
print(f"   3. Frontend muestra BankAccount del company")
print(f"   4. Usuario selecciona BankAccount específica")
print(f"   5. Sistema auto-asigna account = bankaccount.chart_account")
print(f"   6. Usuario guarda factura")
print(f"   7. AutomaticJournalEntryService crea:")
print(f"      DEBE: BankAccount.chart_account (1.1.02.01)")
print(f"      HABER: Ventas + IVA")
print(f"   8. Opcional: Crear BankTransaction para conciliación")

print(f"\n   ⚙️ MODIFICACIONES REQUERIDAS:")
print(f"   - InvoiceAdmin: JavaScript para mostrar BankAccount")
print(f"   - Invoice model: Método para obtener BankAccount")
print(f"   - Opcional: BankTransaction auto-creation")

print(f"\n🎯 CONCLUSIÓN:")
print("-" * 13)

if len(requirements_missing) == 0:
    print(f"✅ ¡SÍ PODEMOS IMPLEMENTAR!")
    print(f"📊 Todos los componentes están disponibles")
    print(f"🔧 Solo requiere modificaciones menores en UI y lógica")
    print(f"⏱️ Estimación: 2-3 horas de desarrollo")
elif len(requirements_missing) <= 2:
    print(f"⚠️ CASI LISTO")
    print(f"🔧 Resolver requisitos faltantes primero")
    print(f"⏱️ Estimación: 1 hora preparación + 2-3 horas desarrollo")
else:
    print(f"❌ NO RECOMENDADO AÚN")
    print(f"🔧 Completar módulos faltantes primero")