"""
Script para crear datos de prueba para la conciliación bancaria
"""

import os
import django
import sys
from decimal import Decimal
from datetime import date, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.companies.models import Company
from apps.banking.models import Bank, BankAccount, BankTransaction, ExtractoBancario, ExtractoBancarioDetalle

User = get_user_model()

def crear_datos_prueba():
    """Crear datos de prueba para conciliación bancaria"""
    
    print("🏦 Creando datos de prueba para conciliación bancaria...")
    
    # 1. Obtener empresa existente
    company = Company.objects.first()
    if not company:
        print("❌ No se encontró ninguna empresa. Crear una empresa primero.")
        return
    
    print(f"✅ Usando empresa: {company.trade_name}")
    
    # 2. Crear banco si no existe
    bank, created = Bank.objects.get_or_create(
        sbs_code='0001',
        defaults={
            'name': 'Banco del Pacífico S.A.',
            'short_name': 'Banco Pacífico',
            'swift_code': 'PACIECGQ',
            'website': 'https://www.bancodelpacifico.com',
            'phone': '1700 627 234'
        }
    )
    
    if created:
        print(f"✅ Banco creado: {bank.name}")
    else:
        print(f"✅ Banco existente: {bank.name}")
    
    # 3. Crear cuenta bancaria
    bank_account, created = BankAccount.objects.get_or_create(
        company=company,
        bank=bank,
        account_number='2100123456',
        defaults={
            'account_type': 'checking',
            'currency': 'USD',
            'initial_balance': Decimal('5000.00'),
            'opening_date': date.today() - timedelta(days=365),
            'contact_person': 'Juan Pérez',
            'notes': 'Cuenta principal para operaciones corrientes'
        }
    )
    
    if created:
        print(f"✅ Cuenta bancaria creada: {bank_account}")
    else:
        print(f"✅ Cuenta bancaria existente: {bank_account}")
    
    # 4. Crear transacciones del sistema
    print("\n💰 Creando transacciones del sistema...")
    
    transacciones = [
        {
            'transaction_date': date.today() - timedelta(days=10),
            'transaction_type': 'credit',
            'amount': Decimal('1500.00'),
            'description': 'Depósito por venta de mercadería',
            'reference': 'DEP001'
        },
        {
            'transaction_date': date.today() - timedelta(days=9),
            'transaction_type': 'debit',
            'amount': Decimal('350.00'),
            'description': 'Pago a proveedor ABC',
            'reference': 'PAG001'
        },
        {
            'transaction_date': date.today() - timedelta(days=8),
            'transaction_type': 'credit',
            'amount': Decimal('2200.00'),
            'description': 'Transferencia recibida cliente XYZ',
            'reference': 'TRF001'
        },
        {
            'transaction_date': date.today() - timedelta(days=7),
            'transaction_type': 'fee',
            'amount': Decimal('12.50'),
            'description': 'Comisión por mantenimiento de cuenta',
            'reference': 'COM001'
        },
        {
            'transaction_date': date.today() - timedelta(days=5),
            'transaction_type': 'debit',
            'amount': Decimal('800.00'),
            'description': 'Pago de servicios básicos',
            'reference': 'SRV001'
        }
    ]
    
    for trans_data in transacciones:
        transaction, created = BankTransaction.objects.get_or_create(
            bank_account=bank_account,
            transaction_date=trans_data['transaction_date'],
            reference=trans_data['reference'],
            defaults=trans_data
        )
        
        if created:
            print(f"   ✅ Transacción: {transaction.description} - ${transaction.signed_amount}")
    
    # 5. Crear extracto bancario
    print("\n📄 Creando extracto bancario...")
    
    period_start = date.today() - timedelta(days=15)
    period_end = date.today() - timedelta(days=1)
    
    extracto, created = ExtractoBancario.objects.get_or_create(
        bank_account=bank_account,
        period_start=period_start,
        period_end=period_end,
        defaults={
            'initial_balance': Decimal('5000.00'),
            'final_balance': Decimal('7537.50'),
            'status': 'processed',
            'notes': 'Extracto de prueba para conciliación'
        }
    )
    
    if created:
        print(f"✅ Extracto creado: {extracto}")
    else:
        print(f"✅ Extracto existente: {extracto}")
    
    # 6. Crear detalles del extracto (algunos coinciden, otros no)
    print("\n📋 Creando detalles del extracto...")
    
    detalles_extracto = [
        {
            'fecha': date.today() - timedelta(days=10),
            'descripcion': 'DEPOSITO VENTANILLA',
            'referencia': 'DEP001',
            'credito': Decimal('1500.00'),
            'saldo': Decimal('6500.00')
        },
        {
            'fecha': date.today() - timedelta(days=9),
            'descripcion': 'PAGO PROVEEDOR ABC',
            'referencia': 'PAG001',
            'debito': Decimal('350.00'),
            'saldo': Decimal('6150.00')
        },
        {
            'fecha': date.today() - timedelta(days=8),
            'descripcion': 'TRF CLIENTE XYZ',
            'referencia': 'TRF001',
            'credito': Decimal('2200.00'),
            'saldo': Decimal('8350.00')
        },
        {
            'fecha': date.today() - timedelta(days=7),
            'descripcion': 'COMISION MANTENIMIENTO',
            'referencia': 'COM001',
            'debito': Decimal('12.50'),
            'saldo': Decimal('8337.50')
        },
        {
            'fecha': date.today() - timedelta(days=6),
            'descripcion': 'INTERES GANADO',
            'referencia': 'INT001',
            'credito': Decimal('25.00'),
            'saldo': Decimal('8362.50')
        },
        {
            'fecha': date.today() - timedelta(days=5),
            'descripcion': 'PAGO SERVICIOS BASICOS',
            'referencia': 'SRV001',
            'debito': Decimal('800.00'),
            'saldo': Decimal('7562.50')
        },
        {
            'fecha': date.today() - timedelta(days=4),
            'descripcion': 'COMISION TRANSFERENCIA',
            'referencia': 'COM002',
            'debito': Decimal('25.00'),
            'saldo': Decimal('7537.50')
        }
    ]
    
    for detalle_data in detalles_extracto:
        detalle, created = ExtractoBancarioDetalle.objects.get_or_create(
            extracto=extracto,
            fecha=detalle_data['fecha'],
            referencia=detalle_data['referencia'],
            defaults=detalle_data
        )
        
        if created:
            tipo = 'Crédito' if detalle_data.get('credito') else 'Débito'
            monto = detalle_data.get('credito', detalle_data.get('debito'))
            print(f"   ✅ {tipo}: {detalle_data['descripcion']} - ${monto}")
    
    print("\n🎉 ¡Datos de prueba creados exitosamente!")
    print("\n📊 Resumen:")
    print(f"   • Banco: {bank.name}")
    print(f"   • Cuenta: {bank_account.account_number}")
    print(f"   • Transacciones del sistema: {BankTransaction.objects.filter(bank_account=bank_account).count()}")
    print(f"   • Detalles del extracto: {ExtractoBancarioDetalle.objects.filter(extracto=extracto).count()}")
    print(f"\n🔗 Accede a la conciliación en: http://localhost:8000/banking/conciliacion/")

if __name__ == "__main__":
    crear_datos_prueba()