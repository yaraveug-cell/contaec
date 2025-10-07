#!/usr/bin/env python3
"""
Verificar qué factura corresponde a la referencia FAC-101
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def main():
    print("🔍 ANÁLISIS DE REFERENCIA FAC-101")
    print("=" * 50)
    
    from apps.invoicing.models import Invoice
    from apps.banking.models import BankTransaction
    from apps.accounting.models import JournalEntry
    
    try:
        # Buscar factura con ID 101
        invoice = Invoice.objects.get(id=101)
        print(f"📄 FACTURA ID 101:")
        print(f"   Número: {invoice.number}")
        print(f"   Cliente: {invoice.customer}")
        print(f"   Fecha: {invoice.date}")
        print(f"   Estado: {invoice.status}")
        print(f"   Forma de pago: {invoice.payment_form}")
        print(f"   Cuenta: {invoice.account}")
        print(f"   Total: ${invoice.total}")
        print(f"   Creada: {invoice.created_at}")
        print()
        
        # Buscar movimiento bancario relacionado
        bank_transactions = BankTransaction.objects.filter(reference="FAC-101")
        print(f"🏦 MOVIMIENTOS BANCARIOS CON REFERENCIA FAC-101: {bank_transactions.count()}")
        for tx in bank_transactions:
            print(f"   ├─ ID: {tx.id}")
            print(f"   ├─ Banco: {tx.bank_account.bank.short_name}")
            print(f"   ├─ Cuenta: {tx.bank_account.account_number}")
            print(f"   ├─ Fecha: {tx.transaction_date}")
            print(f"   ├─ Tipo: {tx.transaction_type}")
            print(f"   ├─ Monto: ${tx.amount}")
            print(f"   ├─ Descripción: {tx.description}")
            print(f"   ├─ Referencia: {tx.reference}")
            print(f"   └─ Asiento vinculado: {tx.journal_entry}")
        print()
        
        # Buscar asiento contable relacionado  
        journal_entries = JournalEntry.objects.filter(reference="FAC-101")
        print(f"📊 ASIENTOS CONTABLES CON REFERENCIA FAC-101: {journal_entries.count()}")
        for entry in journal_entries:
            print(f"   ├─ ID: {entry.id}")
            print(f"   ├─ Número: {entry.number}")
            print(f"   ├─ Fecha: {entry.date}")
            print(f"   ├─ Descripción: {entry.description}")
            print(f"   └─ Referencia: {entry.reference}")
        print()
        
    except Invoice.DoesNotExist:
        print("❌ No existe factura con ID 101")
        
        # Verificar si hay movimientos bancarios huérfanos
        bank_transactions = BankTransaction.objects.filter(reference="FAC-101")
        if bank_transactions.exists():
            print("⚠️ PERO SÍ existe movimiento bancario con referencia FAC-101:")
            for tx in bank_transactions:
                print(f"   ├─ Movimiento ID: {tx.id}")
                print(f"   ├─ Fecha: {tx.transaction_date}")
                print(f"   ├─ Monto: ${tx.amount}")
                print(f"   └─ Descripción: {tx.description}")
    
    # Explicación del sistema de referencias
    print("📋 EXPLICACIÓN DEL SISTEMA DE REFERENCIAS:")
    print("-" * 50)
    print("""
    FORMATO DE REFERENCIA: FAC-{invoice.id}
    
    EJEMPLO:
    - Factura ID: 101
    - Referencia generada: "FAC-101"
    
    PROPÓSITO:
    1. 🔗 Vinculación: Conecta movimiento bancario con factura específica
    2. 🔍 Trazabilidad: Permite rastrear origen del movimiento
    3. 🚫 Duplicados: Previene crear múltiples movimientos para misma factura
    4. 🏦 Conciliación: Facilita conciliación bancaria automática
    5. 📊 Auditoría: Rastrea transacciones para reportes y auditorías
    
    DONDE SE USA:
    - apps/banking/services.py línea 66: reference = f"FAC-{invoice.id}"
    - BankTransaction.reference = "FAC-101"
    - JournalEntry.reference = "FAC-101"  
    
    FLUJO:
    1. Se crea/modifica factura ID 101
    2. Se cambia estado a "Enviada" 
    3. Se crea asiento contable con reference="FAC-101"
    4. Se crea movimiento bancario con reference="FAC-101"
    5. Ambos quedan vinculados por la referencia común
    """)

if __name__ == '__main__':
    main()