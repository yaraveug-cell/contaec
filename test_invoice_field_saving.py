#!/usr/bin/env python
"""
Script de diagnóstico para verificar el guardado de campos de factura
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice, Customer
from apps.companies.models import Company, PaymentMethod
from apps.accounting.models import ChartOfAccounts
from apps.users.models import User
from decimal import Decimal

def diagnose_invoice_field_saving():
    """Diagnosticar el guardado de campos de factura"""
    print("🔍 DIAGNÓSTICO: Guardado de campos de factura")
    print("=" * 60)
    
    # Verificar facturas recientes
    recent_invoices = Invoice.objects.all().order_by('-id')[:5]
    
    print(f"📄 FACTURAS RECIENTES ({recent_invoices.count()}):")
    print("-" * 60)
    
    for invoice in recent_invoices:
        print(f"\n💼 Factura ID: {invoice.id}")
        print(f"   Número: {invoice.number}")
        print(f"   Cliente: {invoice.customer.trade_name}")
        print(f"   Empresa: {invoice.company.trade_name}")
        print(f"   📝 Forma de Pago: {invoice.payment_form}")
        print(f"   🏦 Cuenta: {invoice.account}")
        print(f"   📋 Transfer Detail: '{invoice.transfer_detail}'")
        print(f"   📊 Estado: {invoice.status}")
        print(f"   💰 Total: ${invoice.total}")
    
    # Verificar datos disponibles
    print(f"\n📊 DATOS DISPONIBLES EN EL SISTEMA:")
    print("-" * 60)
    
    payment_methods = PaymentMethod.objects.all()
    print(f"✅ Métodos de Pago ({payment_methods.count()}):")
    for pm in payment_methods:
        print(f"   - ID {pm.id}: {pm.name} ({'Activo' if pm.is_active else 'Inactivo'})")
    
    accounts = ChartOfAccounts.objects.filter(accepts_movement=True)[:10]
    print(f"\n✅ Cuentas Disponibles ({accounts.count()}):")
    for acc in accounts:
        print(f"   - ID {acc.id}: {acc.code} - {acc.name}")
    
    # Test de creación de factura
    print(f"\n🧪 TEST: Crear factura con todos los campos")
    print("-" * 60)
    
    try:
        # Obtener datos necesarios
        gueber = Company.objects.filter(trade_name__icontains='GUEBER').first()
        customer = Customer.objects.filter(company=gueber).first()
        user = User.objects.first()
        payment_method = PaymentMethod.objects.first()
        account = ChartOfAccounts.objects.filter(accepts_movement=True).first()
        
        if not all([gueber, customer, user, payment_method, account]):
            print("❌ ERROR: Faltan datos para crear factura de prueba")
            return
        
        # Crear factura con todos los campos
        test_invoice = Invoice.objects.create(
            company=gueber,
            customer=customer,
            date='2024-01-15',
            status='DRAFT',
            payment_form=payment_method,
            account=account,
            transfer_detail='Transferencia de prueba - Test diagnóstico',
            created_by=user
        )
        
        print(f"✅ Factura creada - ID: {test_invoice.id}")
        print(f"   📝 Forma de Pago guardada: {test_invoice.payment_form}")
        print(f"   🏦 Cuenta guardada: {test_invoice.account}")
        print(f"   📋 Transfer Detail guardado: '{test_invoice.transfer_detail}'")
        
        # Verificar recarga desde BD
        reloaded_invoice = Invoice.objects.get(pk=test_invoice.pk)
        print(f"\n🔄 VERIFICACIÓN DESPUÉS DE RECARGAR:")
        print(f"   📝 Forma de Pago: {reloaded_invoice.payment_form}")
        print(f"   🏦 Cuenta: {reloaded_invoice.account}")
        print(f"   📋 Transfer Detail: '{reloaded_invoice.transfer_detail}'")
        
        # Test de edición
        print(f"\n📝 TEST: Editar campos de la factura")
        print("-" * 40)
        
        # Cambiar campos
        new_payment_method = PaymentMethod.objects.exclude(pk=payment_method.pk).first()
        new_account = ChartOfAccounts.objects.filter(accepts_movement=True).exclude(pk=account.pk).first()
        
        if new_payment_method and new_account:
            original_payment = reloaded_invoice.payment_form
            original_account = reloaded_invoice.account
            original_detail = reloaded_invoice.transfer_detail
            
            reloaded_invoice.payment_form = new_payment_method
            reloaded_invoice.account = new_account
            reloaded_invoice.transfer_detail = 'Nuevo detalle editado'
            reloaded_invoice.save()
            
            # Verificar cambios
            updated_invoice = Invoice.objects.get(pk=test_invoice.pk)
            print(f"   📝 Forma de Pago: {original_payment} → {updated_invoice.payment_form}")
            print(f"   🏦 Cuenta: {original_account} → {updated_invoice.account}")
            print(f"   📋 Transfer Detail: '{original_detail}' → '{updated_invoice.transfer_detail}'")
            
            if (updated_invoice.payment_form == new_payment_method and 
                updated_invoice.account == new_account and
                updated_invoice.transfer_detail == 'Nuevo detalle editado'):
                print("✅ TODOS LOS CAMPOS SE GUARDARON CORRECTAMENTE")
            else:
                print("❌ ALGUNOS CAMPOS NO SE GUARDARON")
        
        # Limpiar
        test_invoice.delete()
        print(f"\n🧹 Factura de prueba eliminada")
        
    except Exception as e:
        print(f"❌ ERROR en test: {e}")
    
    print(f"\n🏁 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 60)
    print("🔍 Campos verificados:")
    print("   - payment_form (Forma de Pago)")
    print("   - account (Cuenta)")  
    print("   - transfer_detail (Detalle Transferencia)")
    print("\n💡 Si algún campo no se guarda, el problema puede estar en:")
    print("   1. Admin JavaScript no enviando datos correctamente")
    print("   2. Método calculate_totals() sobrescribiendo campos")
    print("   3. Validación de formulario rechazando valores")

if __name__ == "__main__":
    diagnose_invoice_field_saving()