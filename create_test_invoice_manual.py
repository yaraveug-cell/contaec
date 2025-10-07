#!/usr/bin/env python
"""
Crear factura permanente para probar observaciones bancarias en edición
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
from django.contrib.auth import get_user_model
import time

def create_test_invoice_for_editing():
    """Crear factura permanente para probar en navegador"""
    
    # Obtener datos necesarios
    company = Company.objects.first()
    customer = Customer.objects.filter(company=company).first()
    
    transfer_method = PaymentMethod.objects.filter(
        name__icontains='transferencia',
        is_active=True
    ).first()
    
    bank_account = ChartOfAccounts.objects.filter(
        company=company,
        aux_type='bank',
        accepts_movement=True
    ).first()
    
    User = get_user_model()
    test_user = User.objects.first()
    
    # Observaciones detalladas para la prueba
    test_observations = """TRANSFERENCIA INTERBANCARIA
Banco: Pichincha
Cuenta: 2110-1543-21  
Referencia: TXN-ABC123
Cliente: VIP Gold
Motivo: Pago factura productos varios
Fecha: 06/10/2025
Autorizado por: Gerencia"""
    
    test_number = f"MANUAL-TEST-{int(time.time())}"
    
    # Crear factura
    test_invoice = Invoice.objects.create(
        company=company,
        customer=customer,
        number=test_number,
        payment_form=transfer_method,
        account=bank_account,
        created_by=test_user,
        bank_observations=test_observations,
        transfer_detail="",  # Vacío para usar bank_observations
        status='draft'
    )
    
    print("🏦 FACTURA CREADA PARA PRUEBA MANUAL")
    print("=" * 40)
    print(f"📄 ID: {test_invoice.id}")
    print(f"📄 Número: {test_invoice.number}")
    print(f"💳 Método: {test_invoice.payment_form}")
    print(f"🏦 Cuenta: {test_invoice.account}")
    print(f"💬 Observaciones:")
    print(test_observations)
    print("")
    print("🌐 URLs para probar:")
    print(f"   📝 Editar: http://localhost:8000/admin/invoicing/invoice/{test_invoice.id}/change/")
    print(f"   📋 Lista: http://localhost:8000/admin/invoicing/invoice/")
    print("")
    print("🔍 Al abrir la URL de edición, verificar:")
    print("   ✅ Campo 'Forma de pago' muestra 'Transferencia'")
    print("   ✅ Campo 'Cuenta' tradicional está OCULTO")
    print("   ✅ Aparece selector 'Cuenta Bancaria' con cuenta pre-seleccionada")
    print("   ✅ Aparece campo 'Observaciones' con texto cargado")
    print("   ✅ Observaciones se sincronizan al editarlas")
    print("")
    print("⚠️  IMPORTANTE: Esta factura NO se eliminará automáticamente")
    print(f"    Elimínala manualmente cuando termines: ID {test_invoice.id}")
    
    return test_invoice.id

if __name__ == "__main__":
    invoice_id = create_test_invoice_for_editing()