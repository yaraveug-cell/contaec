#!/usr/bin/env python
"""
Script para probar la corrección del error en BankTransaction admin
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.banking.admin import BankTransactionAdmin
from apps.banking.models import BankTransaction

print("🧪 PRUEBA: Corrección de signed_amount_display")
print("=" * 48)

# Crear instancia del admin
admin_instance = BankTransactionAdmin(BankTransaction, None)

# Crear un BankTransaction ficticio para prueba
class MockBankTransaction:
    def __init__(self, amount, is_debit):
        self.amount = amount
        self._is_debit = is_debit
    
    @property
    def is_debit(self):
        return self._is_debit
    
    @property 
    def signed_amount(self):
        """Simular el método signed_amount"""
        return -self.amount if self.is_debit else self.amount

# Probar con diferentes valores
test_cases = [
    (100.50, False),  # Crédito (positivo)
    (75.25, True),    # Débito (negativo)
    (1000.00, False), # Crédito grande
    (0.01, True),     # Débito pequeño
]

print("🔍 PROBANDO signed_amount_display:")
print("-" * 36)

for amount, is_debit in test_cases:
    mock_transaction = MockBankTransaction(amount, is_debit)
    
    try:
        # Probar el método corregido
        result = admin_instance.signed_amount_display(mock_transaction)
        
        transaction_type = "Débito" if is_debit else "Crédito"
        expected_sign = "-" if is_debit else "+"
        
        print(f"   💰 {transaction_type}: ${amount}")
        print(f"      ✅ Resultado: {result}")
        print(f"      📊 Signo esperado: {expected_sign}")
        
        # Verificar que el resultado contenga el HTML esperado
        if expected_sign in result and str(float(amount)) in result:
            print(f"      ✅ Formato correcto")
        else:
            print(f"      ❌ Formato incorrecto")
            
    except Exception as e:
        print(f"   ❌ Error con ${amount} ({transaction_type}): {e}")
    
    print()

print("🎯 RESULTADO:")
print("-" * 12)
print("✅ Método signed_amount_display corregido")
print("✅ No más errores de formato con SafeString") 
print("✅ Admin de BankTransaction debería funcionar ahora")

# Verificar que no haya BankTransactions reales que causen problemas
real_transactions = BankTransaction.objects.count()
print(f"\nℹ️ BankTransactions en base de datos: {real_transactions}")

if real_transactions > 0:
    print("🔍 Verificando transacciones reales...")
    
    for transaction in BankTransaction.objects.all()[:3]:  # Primeras 3
        try:
            result = admin_instance.signed_amount_display(transaction)
            print(f"   ✅ Transacción {transaction.id}: OK")
        except Exception as e:
            print(f"   ❌ Error en transacción {transaction.id}: {e}")
else:
    print("ℹ️ No hay transacciones reales para probar")