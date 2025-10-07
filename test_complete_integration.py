#!/usr/bin/env python3
"""
Script de prueba para la integración completa:
Filtro en Cascada + Asiento Contable + Movimiento Bancario
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def main():
    print("🧪 PRUEBA DE INTEGRACIÓN COMPLETA")
    print("=" * 60)
    
    from apps.invoicing.models import Invoice
    from apps.accounting.models import JournalEntry
    from apps.banking.models import BankTransaction
    from apps.companies.models import PaymentMethod
    
    # Verificar factura de prueba
    try:
        invoice = Invoice.objects.get(id=99)
        print(f"📄 Factura de prueba: {invoice.number}")
        print(f"   Estado: {invoice.status}")
        print(f"   Forma de pago: {invoice.payment_form}")
        print(f"   Cuenta: {invoice.account}")
        print(f"   Total: ${invoice.total}")
        print()
        
        # Verificar asientos contables
        journal_entries = JournalEntry.objects.filter(reference=f"FAC-{invoice.id}")
        print(f"📊 Asientos contables relacionados: {journal_entries.count()}")
        for entry in journal_entries:
            print(f"   ├─ #{entry.number} - {entry.date} - {entry.description}")
        
        # Verificar movimientos bancarios
        bank_transactions = BankTransaction.objects.filter(reference=f"FAC-{invoice.id}")
        print(f"🏦 Movimientos bancarios relacionados: {bank_transactions.count()}")
        for transaction in bank_transactions:
            print(f"   ├─ {transaction.bank_account.bank.short_name} - ${transaction.amount} - {transaction.transaction_type}")
        
        print()
        
    except Invoice.DoesNotExist:
        print("❌ Factura de prueba ID 99 no encontrada")
        return
    
    # Prueba del filtro en cascada
    print("🔄 PRUEBA DEL FILTRO EN CASCADA:")
    print("-" * 40)
    
    payment_methods = PaymentMethod.objects.all()
    for method in payment_methods:
        print(f"💳 {method.name}:")
        if method.parent_account:
            print(f"   └─ Cuenta padre: {method.parent_account.code}")
            
            # Simular endpoint AJAX
            from apps.accounting.models import ChartOfAccounts
            from apps.companies.models import Company
            
            gueber = Company.objects.get(trade_name="GUEBER")
            parent_code = method.parent_account.code
            child_accounts = ChartOfAccounts.objects.filter(
                company=gueber,
                code__startswith=parent_code,
                accepts_movement=True
            ).exclude(code=parent_code)
            
            print(f"   └─ Cuentas disponibles: {child_accounts.count()}")
            for account in child_accounts:
                print(f"      ├─ {account.code} - {account.name}")
        else:
            print(f"   └─ Sin cuenta padre configurada")
        print()
    
    # Verificar integración bancaria disponible
    print("🏦 ESTADO DE INTEGRACIÓN BANCARIA:")
    print("-" * 40)
    
    from apps.banking.models import BankAccount
    
    # Verificar cuentas con integración
    bank_accounts = BankAccount.objects.filter(
        chart_account__isnull=False,
        is_active=True
    )
    
    print(f"✅ Cuentas bancarias con integración contable: {bank_accounts.count()}")
    for bank_acc in bank_accounts:
        print(f"   ├─ {bank_acc.bank.short_name} - {bank_acc.account_number}")
        print(f"   └─ Vinculado con: {bank_acc.chart_account.code} - {bank_acc.chart_account.name}")
    
    print()
    
    # Instrucciones de prueba
    print("📋 PASOS PARA PROBAR LA INTEGRACIÓN COMPLETA:")
    print("-" * 50)
    print("""
    1. Abrir: http://localhost:8000/admin/invoicing/invoice/add/
    
    2. Completar datos básicos:
       - Empresa: GUEBER
       - Cliente: Cualquier cliente
       - Fecha: Hoy
    
    3. Probar filtro en cascada:
       - Seleccionar "Transferencia" en Forma de Pago
       - Verificar que campo Cuenta se filtra a solo bancos
       - Seleccionar "1.1.02.02 - BANCO PICHINCHA"
    
    4. Completar factura:
       - Agregar líneas de productos
       - Guardar factura (estado: draft)
    
    5. Cambiar estado a "Enviada" (sent):
       - Debe crear asiento contable automáticamente
       - Debe crear movimiento bancario (si cuenta tiene BankAccount)
       - Verificar mensajes de confirmación
    
    6. Verificar resultados:
       - Revisar asiento en: /admin/accounting/journalentry/
       - Revisar movimiento en: /admin/banking/banktransaction/
    
    ⚠️ NOTA: Solo funcionará con cuentas que tengan BankAccount vinculado
    """)

if __name__ == '__main__':
    main()