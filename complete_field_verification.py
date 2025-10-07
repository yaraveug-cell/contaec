#!/usr/bin/env python
"""
VERIFICACION COMPLETA: Test de todos los campos de factura
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from apps.companies.models import PaymentMethod
from apps.accounting.models import ChartOfAccounts

print("🔍 VERIFICACION COMPLETA: Sistema de guardado de facturas")
print("=" * 65)

# 1. Estado actual del sistema
print("1. 📊 ESTADO ACTUAL DEL SISTEMA:")
print("-" * 40)

total_invoices = Invoice.objects.count()
print(f"📋 Total facturas en sistema: {total_invoices}")

if total_invoices > 0:
    latest_invoice = Invoice.objects.latest('created_at')
    print(f"✅ Última factura: ID {latest_invoice.id} ({latest_invoice.created_at})")
else:
    print("❌ No hay facturas en el sistema")

# 2. Análisis de las últimas 5 facturas
print(f"\n2. 🔍 ANÁLISIS ÚLTIMAS 5 FACTURAS:")
print("-" * 40)

recent_invoices = Invoice.objects.all().order_by('-created_at')[:5]

for i, invoice in enumerate(recent_invoices, 1):
    print(f"\n📋 Factura {i}: ID {invoice.id}")
    print(f"   Empresa: {invoice.company}")
    print(f"   Fecha: {invoice.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar forma de pago
    if invoice.payment_form:
        print(f"   💳 Forma de pago: {invoice.payment_form.name} (ID: {invoice.payment_form.id})")
        payment_status = "✅"
    else:
        print(f"   💳 Forma de pago: ❌ NO GUARDADA")
        payment_status = "❌"
    
    # Verificar cuenta
    if invoice.account:
        print(f"   🏦 Cuenta: {invoice.account.code} - {invoice.account.name}")
        account_status = "✅"
        
        # Verificar coherencia con forma de pago
        if invoice.payment_form and invoice.payment_form.parent_account:
            parent_code = invoice.payment_form.parent_account.code.rstrip('.')
            account_code = invoice.account.code
            is_coherent = account_code.startswith(parent_code + '.') and account_code != parent_code
            coherence_status = "✅" if is_coherent else "⚠️"
            print(f"      Coherencia: {coherence_status} {'Correcta' if is_coherent else 'Inconsistente'}")
        else:
            print(f"      Coherencia: ⚪ No verificable")
    else:
        print(f"   🏦 Cuenta: ❌ NO GUARDADA")
        account_status = "❌"
    
    # Verificar transfer detail
    if invoice.transfer_detail:
        print(f"   📄 Transfer Detail: '{invoice.transfer_detail}'")
        transfer_status = "✅"
        
        # Verificar si es apropiado
        if invoice.payment_form and invoice.payment_form.name == 'Transferencia':
            print(f"      Estado: ✅ Apropiado (es Transferencia)")
        else:
            print(f"      Estado: ⚠️ Presente sin ser Transferencia")
    else:
        print(f"   📄 Transfer Detail: ⚪ Vacío")
        transfer_status = "⚪"
    
    # Resumen de la factura
    status_summary = f"{payment_status}{account_status}{transfer_status}"
    print(f"   📊 Estado: {status_summary}")

# 3. Verificar configuraciones del sistema
print(f"\n3. ⚙️ CONFIGURACIONES DEL SISTEMA:")
print("-" * 40)

payment_methods = PaymentMethod.objects.all()
print(f"💳 Métodos de pago configurados: {payment_methods.count()}")

for method in payment_methods:
    print(f"   {method.id}: {method.name}")
    if method.parent_account:
        print(f"      → Cuenta padre: {method.parent_account.code} - {method.parent_account.name}")
    else:
        print(f"      → ❌ Sin cuenta padre configurada")

accounts = ChartOfAccounts.objects.all().count()
print(f"🏦 Total cuentas disponibles: {accounts}")

# 4. Test de consistencia
print(f"\n4. 🧪 TEST DE CONSISTENCIA:")
print("-" * 30)

consistency_issues = []

# Verificar facturas con forma de pago pero sin cuenta
missing_accounts = Invoice.objects.filter(payment_form__isnull=False, account__isnull=True).count()
if missing_accounts > 0:
    consistency_issues.append(f"❌ {missing_accounts} factura(s) con forma de pago pero sin cuenta")

# Verificar facturas con cuenta pero sin forma de pago
missing_payment = Invoice.objects.filter(payment_form__isnull=True, account__isnull=False).count()
if missing_payment > 0:
    consistency_issues.append(f"❌ {missing_payment} factura(s) con cuenta pero sin forma de pago")

# Verificar transfer detail sin transferencia
wrong_transfer_detail = Invoice.objects.filter(
    transfer_detail__isnull=False
).exclude(
    payment_form__name='Transferencia'
).exclude(
    transfer_detail=''
).count()
if wrong_transfer_detail > 0:
    consistency_issues.append(f"⚠️ {wrong_transfer_detail} factura(s) con transfer detail sin ser Transferencia")

if consistency_issues:
    print("❌ PROBLEMAS DE CONSISTENCIA ENCONTRADOS:")
    for issue in consistency_issues:
        print(f"   {issue}")
else:
    print("✅ NO SE ENCONTRARON PROBLEMAS DE CONSISTENCIA")

print(f"\n5. 📋 RESUMEN FINAL:")
print("-" * 25)

if total_invoices > 0:
    complete_invoices = Invoice.objects.filter(
        payment_form__isnull=False,
        account__isnull=False
    ).count()
    
    percentage = (complete_invoices / total_invoices) * 100
    
    print(f"📊 Facturas completas: {complete_invoices}/{total_invoices} ({percentage:.1f}%)")
    
    if percentage >= 90:
        print("🎉 ¡EXCELENTE! El sistema está guardando correctamente")
    elif percentage >= 70:
        print("👍 BUENO: La mayoría de facturas se guardan correctamente")
    else:
        print("⚠️ PROBLEMAS: Muchas facturas incompletas")
        
else:
    print("🆕 Sistema nuevo - crear facturas para verificar")

print(f"\n🏁 Verificación completa finalizada")
print(f"💡 Para test en vivo: http://127.0.0.1:8000/admin/invoicing/invoice/add/")