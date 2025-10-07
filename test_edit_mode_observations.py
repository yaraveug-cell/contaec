#!/usr/bin/env python
"""
Prueba: Verificar carga de observaciones en modo edición
Crear una factura con observaciones y verificar que se vean al editarla
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
from decimal import Decimal
import time

def test_edit_mode_observations():
    """Probar que las observaciones se muestren en modo edición"""
    
    print("🧪 PRUEBA: Observaciones bancarias en modo edición")
    print("=" * 50)
    
    # Obtener datos necesarios
    company = Company.objects.first()
    if not company:
        print("❌ No hay empresas configuradas")
        return False
    
    customer = Customer.objects.filter(company=company).first()
    if not customer:
        print("❌ No hay clientes configurados")
        return False
    
    transfer_method = PaymentMethod.objects.filter(
        name__icontains='transferencia',
        is_active=True
    ).first()
    
    if not transfer_method:
        print("❌ No hay método 'Transferencia' configurado")
        return False
    
    bank_account = ChartOfAccounts.objects.filter(
        company=company,
        aux_type='bank',
        accepts_movement=True
    ).first()
    
    if not bank_account:
        print("❌ No hay cuentas bancarias configuradas")
        return False
    
    User = get_user_model()
    test_user = User.objects.first()
    
    if not test_user:
        print("❌ No hay usuarios configurados")
        return False
    
    print(f"✅ Configuración lista:")
    print(f"   🏢 Empresa: {company.trade_name}")
    print(f"   👤 Cliente: {customer.trade_name}")
    print(f"   💳 Método: {transfer_method.name}")
    print(f"   🏦 Cuenta: {bank_account.code} - {bank_account.name}")
    
    # Crear factura con observaciones específicas
    test_observations = "PRUEBA EDICIÓN: Transferencia Banco Pichincha - Cuenta 2110-1543-21 - Referencia ABC123 - Cliente VIP"
    test_number = f"EDIT-TEST-{int(time.time())}"
    
    print(f"\n📝 Creando factura de prueba:")
    print(f"   📄 Número: {test_number}")
    print(f"   💬 Observaciones: {test_observations}")
    
    try:
        # Crear factura completa
        test_invoice = Invoice.objects.create(
            company=company,
            customer=customer,
            number=test_number,
            payment_form=transfer_method,
            account=bank_account,
            created_by=test_user,
            bank_observations=test_observations,
            transfer_detail="",  # Dejarlo vacío para que use bank_observations
            status='draft'
        )
        
        print(f"✅ Factura creada con ID: {test_invoice.id}")
        
        # Verificar que se guardó correctamente
        test_invoice.refresh_from_db()
        print(f"\n📊 Datos guardados:")
        print(f"   💬 bank_observations: '{test_invoice.bank_observations}'")
        print(f"   📝 transfer_detail: '{test_invoice.transfer_detail}'")
        print(f"   💳 payment_form: {test_invoice.payment_form}")
        print(f"   🏦 account: {test_invoice.account}")
        
        # Verificar que los campos estén presentes para JavaScript
        has_bank_obs = bool(test_invoice.bank_observations and test_invoice.bank_observations.strip())
        account_matches = test_invoice.account == bank_account
        payment_is_transfer = test_invoice.payment_form == transfer_method
        
        print(f"\n🔍 Verificaciones:")
        print(f"   ✅ Tiene observaciones: {'✓' if has_bank_obs else '✗'}")
        print(f"   ✅ Cuenta correcta: {'✓' if account_matches else '✗'}")
        print(f"   ✅ Método transferencia: {'✓' if payment_is_transfer else '✗'}")
        
        if has_bank_obs and account_matches and payment_is_transfer:
            print(f"\n🎯 RESULTADO: ✅ FACTURA LISTA PARA EDICIÓN")
            print(f"   🔗 URL de edición: /admin/invoicing/invoice/{test_invoice.id}/change/")
            print(f"   💬 JavaScript debería cargar: '{test_observations}'")
            print(f"   🏦 JavaScript debería pre-seleccionar: {bank_account.code} - {bank_account.name}")
            
            # Mantener la factura por un momento para que se pueda probar manualmente
            print(f"\n⏰ La factura se mantendrá por 30 segundos para prueba manual...")
            print(f"   🌐 Abrir en navegador: http://localhost:8000/admin/invoicing/invoice/{test_invoice.id}/change/")
            print(f"   🔍 Verificar que:")
            print(f"     - Se muestre 'Transferencia' seleccionada")
            print(f"     - Se oculte el campo 'Cuenta' tradicional")
            print(f"     - Se muestre el selector bancario unificado")
            print(f"     - Se carguen las observaciones en el textarea")
            print(f"     - Se pre-seleccione la cuenta bancaria correcta")
            
            import time as sleep_time
            sleep_time.sleep(30)
            
            # Limpiar
            test_invoice.delete()
            print(f"\n🗑️ Factura de prueba eliminada")
            
            return True
        else:
            print(f"\n❌ FALLÓ: Datos no se guardaron correctamente")
            test_invoice.delete()
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_edit_mode_observations()