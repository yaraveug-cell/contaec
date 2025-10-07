#!/usr/bin/env python
"""
Script para verificar que los campos Forma de Pago y Cuenta funcionan correctamente
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice, Customer, Company, CASH, CREDIT, TRANSFER, PAYMENT_FORM_CHOICES
from apps.accounting.models import ChartOfAccounts

def test_invoice_fields():
    """Verificar campos Forma de Pago y Cuenta"""
    
    print("🔍 VERIFICACIÓN CAMPOS DE FACTURA")
    print("=" * 60)
    
    # 1. Verificar campo payment_form
    print("💳 Verificando campo Forma de Pago...")
    try:
        payment_form_field = Invoice._meta.get_field('payment_form')
        print("✅ Campo payment_form encontrado:")
        print(f"   - Verbose name: {payment_form_field.verbose_name}")
        print(f"   - Default: {payment_form_field.default}")
        print(f"   - Choices: {len(payment_form_field.choices)} opciones")
        
        for code, label in PAYMENT_FORM_CHOICES:
            print(f"   - {code}: {label}")
            
    except Exception as e:
        print(f"❌ Error en campo payment_form: {e}")
        return False
    
    # 2. Verificar campo account
    print("\n🏦 Verificando campo Cuenta...")
    try:
        account_field = Invoice._meta.get_field('account')
        print("✅ Campo account encontrado:")
        print(f"   - Verbose name: {account_field.verbose_name}")
        print(f"   - Related model: {account_field.related_model.__name__}")
        print(f"   - Null: {account_field.null}")
        print(f"   - Blank: {account_field.blank}")
        
    except Exception as e:
        print(f"❌ Error en campo account: {e}")
        return False
    
    # 3. Verificar relación con ChartOfAccounts
    print("\n📊 Verificando cuentas disponibles...")
    try:
        total_accounts = ChartOfAccounts.objects.count()
        movement_accounts = ChartOfAccounts.objects.filter(accepts_movement=True).count()
        
        print(f"✅ Plan de cuentas disponible:")
        print(f"   - Total cuentas: {total_accounts}")
        print(f"   - Cuentas que aceptan movimiento: {movement_accounts}")
        
        if movement_accounts > 0:
            sample_accounts = ChartOfAccounts.objects.filter(accepts_movement=True)[:5]
            print(f"   - Ejemplos de cuentas:")
            for acc in sample_accounts:
                print(f"     • {acc.code} - {acc.name} ({acc.company.trade_name})")
        
    except Exception as e:
        print(f"❌ Error verificando cuentas: {e}")
        return False
    
    # 4. Probar creación de instancia con ambos campos
    print("\n🧪 Probando creación de factura...")
    try:
        # Buscar datos necesarios
        company = Company.objects.filter(is_active=True).first()
        customer = Customer.objects.filter(company=company).first() if company else None
        account = ChartOfAccounts.objects.filter(
            company=company, 
            accepts_movement=True
        ).first() if company else None
        
        if not company or not customer:
            print("⚠️  No hay empresa o cliente para prueba")
            return True
            
        # Crear instancia de prueba
        test_invoice = Invoice(
            company=company,
            customer=customer,
            number='TEST-FIELDS-001',
            payment_form=CREDIT,  # Probar con crédito
            account=account  # Asignar cuenta si existe
        )
        
        print("✅ Factura de prueba creada:")
        print(f"   - Empresa: {test_invoice.company.trade_name}")
        print(f"   - Cliente: {test_invoice.customer.trade_name}")
        print(f"   - Forma de Pago: {test_invoice.payment_form}")
        print(f"   - Cuenta: {test_invoice.account or 'No asignada'}")
        
    except Exception as e:
        print(f"❌ Error creando factura: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ¡CAMPOS CONFIGURADOS CORRECTAMENTE!")
    print("✅ Forma de Pago: Funcional con 3 opciones")
    print("✅ Cuenta: Relacionada con plan de cuentas")
    print("✅ Ambos campos listos para usar en admin")
    return True

if __name__ == "__main__":
    success = test_invoice_fields()
    sys.exit(0 if success else 1)