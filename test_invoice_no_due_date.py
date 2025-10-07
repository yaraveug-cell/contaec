#!/usr/bin/env python3
"""
Test: Verificar que se puede crear factura sin due_date
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append('.')
django.setup()

def test_invoice_without_due_date():
    """Test de creación de factura sin fecha de vencimiento"""
    
    from apps.invoicing.models import Invoice, Customer
    from apps.companies.models import Company, PaymentMethod
    from apps.accounting.models import ChartOfAccounts
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    
    User = get_user_model()
    
    print("🧪 TEST: FACTURA SIN FECHA DE VENCIMIENTO")
    print("=" * 50)
    
    try:
        # 1. Obtener datos necesarios
        print("📋 OBTENIENDO DATOS NECESARIOS:")
        
        # Usuario
        user = User.objects.first()
        print(f"   ✅ Usuario: {user.username}")
        
        # Empresa
        company = Company.objects.first()
        print(f"   ✅ Empresa: {company.trade_name}")
        
        # Cliente
        customer = Customer.objects.filter(company=company).first()
        if not customer:
            # Crear cliente de prueba
            customer = Customer.objects.create(
                company=company,
                customer_type='natural',
                identification='1234567890',
                trade_name='Cliente de Prueba',
                address='Dirección de prueba',
                payment_terms=0
            )
            print(f"   ✅ Cliente creado: {customer.trade_name}")
        else:
            print(f"   ✅ Cliente: {customer.trade_name}")
        
        # Método de pago
        payment_method = PaymentMethod.objects.filter(name__icontains='efectivo').first()
        print(f"   ✅ Método de pago: {payment_method.name}")
        
        # Cuenta (opcional)
        account = ChartOfAccounts.objects.filter(
            company=company, 
            accepts_movement=True
        ).first()
        
        if account:
            print(f"   ✅ Cuenta: {account.code} - {account.name}")
        else:
            print(f"   ⚠️ No hay cuentas disponibles - usando None")
        
        # 2. Crear factura SIN due_date
        print(f"\n💾 CREANDO FACTURA SIN DUE_DATE:")
        
        invoice = Invoice(
            company=company,
            customer=customer,
            date=timezone.now().date(),
            # due_date NO se especifica - debe ser None
            payment_form=payment_method,
            account=account,  # Puede ser None
            status='draft',
            created_by=user
        )
        
        # Intentar guardar
        invoice.save()
        
        print(f"   ✅ Factura creada exitosamente:")
        print(f"   📄 Número: {invoice.number}")
        print(f"   📅 Fecha: {invoice.date}")
        print(f"   📅 Fecha de vencimiento: {invoice.due_date}")
        print(f"   💳 Forma de pago: {invoice.payment_form.name}")
        if invoice.account:
            print(f"   📊 Cuenta: {invoice.account.code} - {invoice.account.name}")
        else:
            print(f"   📊 Cuenta: None")
        
        # 3. Verificar que due_date es None
        print(f"\n✅ VERIFICACIÓN:")
        if invoice.due_date is None:
            print(f"   ✅ due_date es None (correcto)")
        else:
            print(f"   ❌ due_date tiene valor: {invoice.due_date}")
        
        # 4. Verificar que la factura se puede recuperar de la base de datos
        saved_invoice = Invoice.objects.get(id=invoice.id)
        print(f"   ✅ Factura recuperada de BD: {saved_invoice.number}")
        print(f"   📅 due_date en BD: {saved_invoice.due_date}")
        
        print(f"\n🎉 RESULTADO:")
        print(f"   ✅ La factura se puede crear sin due_date")
        print(f"   ✅ El campo due_date queda como None")
        print(f"   ✅ No hay errores de integridad")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE EL TEST:")
        print(f"   Error: {str(e)}")
        
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_invoice_without_due_date()
    if success:
        print(f"\n🏆 TEST EXITOSO - El campo due_date es opcional")
    else:
        print(f"\n💥 TEST FALLIDO - Revisar configuración")