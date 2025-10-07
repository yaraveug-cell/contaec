#!/usr/bin/env python
"""
TEST: Verificación específica del guardado de campos de factura
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from apps.companies.models import PaymentMethod
from apps.accounting.models import ChartOfAccounts

print("🧪 TEST: Guardado de campos de factura")
print("=" * 50)

# 1. Verificar la última factura creada
print("1. 📋 Verificando última factura:")
print("-" * 30)

try:
    latest_invoice = Invoice.objects.latest('created_at')
    print(f"✅ Última factura: ID {latest_invoice.id}")
    print(f"   Creada: {latest_invoice.created_at}")
    print(f"   Empresa: {latest_invoice.company}")
    print(f"   Cliente: {latest_invoice.customer}")
    
    # Verificar campos específicos
    print(f"\n📊 Campos a verificar:")
    print(f"   Forma de pago: {latest_invoice.payment_form}")
    if latest_invoice.payment_form:
        print(f"      ID: {latest_invoice.payment_form.id}")
        print(f"      Nombre: {latest_invoice.payment_form.name}")
    
    print(f"   Cuenta: {latest_invoice.account}")
    if latest_invoice.account:
        print(f"      ID: {latest_invoice.account.id}")
        print(f"      Código: {latest_invoice.account.code}")
        print(f"      Nombre: {latest_invoice.account.name}")
    
    print(f"   Transfer Detail: '{latest_invoice.transfer_detail}'")
    
    # Validar lógica de guardado
    print(f"\n✅ VALIDACIONES:")
    print("-" * 20)
    
    if latest_invoice.payment_form:
        print(f"✅ Forma de pago guardada correctamente")
        
        # Verificar coherencia de la cuenta
        if latest_invoice.account:
            parent_account = latest_invoice.payment_form.parent_account
            if parent_account:
                account_code = latest_invoice.account.code
                parent_code = parent_account.code.rstrip('.')
                
                is_child = account_code.startswith(parent_code + '.') and account_code != parent_code
                
                if is_child:
                    print(f"✅ Cuenta coherente con forma de pago")
                else:
                    print(f"⚠️  Cuenta NO coherente con forma de pago")
                    print(f"      Cuenta: {account_code}")
                    print(f"      Padre esperado: {parent_code}")
            else:
                print(f"⚠️  Forma de pago sin cuenta padre configurada")
        else:
            print(f"❌ Cuenta NO guardada")
    else:
        print(f"❌ Forma de pago NO guardada")
    
    if latest_invoice.payment_form and latest_invoice.payment_form.name == 'Transferencia':
        if latest_invoice.transfer_detail:
            print(f"✅ Transfer Detail guardado para Transferencia")
        else:
            print(f"⚠️  Transfer Detail vacío para Transferencia")
    elif latest_invoice.transfer_detail:
        print(f"⚠️  Transfer Detail presente sin ser Transferencia")
    else:
        print(f"✅ Transfer Detail apropiado para {latest_invoice.payment_form.name if latest_invoice.payment_form else 'Sin forma de pago'}")

except Invoice.DoesNotExist:
    print("❌ No hay facturas en el sistema")

print(f"\n2. 🧪 Instrucciones para test manual:")
print("-" * 35)
print("1. Ve al admin: http://127.0.0.1:8000/admin/invoicing/invoice/add/")
print("2. Selecciona empresa: GUEBER")
print("3. Selecciona cliente: cualquiera")
print("4. Prueba cada forma de pago:")
print("   - Efectivo → debería mostrar CAJA GENERAL")
print("   - Crédito → debería mostrar CLIENTE CREDITO AUTORIZADO 1")
print("   - Transferencia → debería mostrar BANCO INTERNACIONAL/PICHINCHA + campo detalle")
print("5. Llena el campo detalle transferencia si aparece")
print("6. Guarda la factura")
print("7. Ejecuta este script nuevamente para verificar")

print(f"\n🏁 Test completado")
print("💡 El monitor en el otro terminal mostrará los cambios en tiempo real")