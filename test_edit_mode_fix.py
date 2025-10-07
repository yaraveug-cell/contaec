#!/usr/bin/env python
"""
TEST: Verificación del fix de modo edición
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice

print("🔧 TEST: Fix del modo edición v5.3")
print("=" * 40)

# Buscar facturas para test
transferencia_invoices = Invoice.objects.filter(
    payment_form__name='Transferencia'
).order_by('-created_at')[:3]

efectivo_invoices = Invoice.objects.filter(
    payment_form__name='Efectivo'
).order_by('-created_at')[:2]

print("🎯 FACTURAS PARA TEST:")
print("-" * 25)

print("\n📋 Facturas con TRANSFERENCIA:")
for invoice in transferencia_invoices:
    edit_url = f"http://127.0.0.1:8000/admin/invoicing/invoice/{invoice.id}/change/"
    print(f"   ID {invoice.id}: {invoice.payment_form.name} → {invoice.account.code}")
    print(f"      Transfer Detail: '{invoice.transfer_detail}'")
    print(f"      URL: {edit_url}")

print("\n💰 Facturas con EFECTIVO:")
for invoice in efectivo_invoices:
    edit_url = f"http://127.0.0.1:8000/admin/invoicing/invoice/{invoice.id}/change/"
    print(f"   ID {invoice.id}: {invoice.payment_form.name} → {invoice.account.code}")
    print(f"      URL: {edit_url}")

print(f"\n🧪 INSTRUCCIONES PARA VERIFICAR EL FIX:")
print("-" * 45)
print("1. Abre una de las facturas de Transferencia en modo edición")
print("2. ANTES del fix: Se abría con 'Efectivo' seleccionado")
print("3. DESPUÉS del fix: Debería abrirse con 'Transferencia' seleccionada")
print("4. El campo 'Transfer Detail' debe mostrarse automáticamente")
print("5. El campo debe contener el valor guardado")

print(f"\n🔍 EN LA CONSOLA DEL NAVEGADOR DEBERÍAS VER:")
print("-" * 50)
print("✅ IntegratedPaymentAccountHandler: v5.3 (EDIT MODE FIXED)")
print("✅ 📝 ¿Modo edición?: true - URL: .../change/")
print("✅ 📝 Modo EDICIÓN detectado: Respetando valores existentes")
print("✅ 💳 Aplicando filtrado para valor existente: 3")

print(f"\n❌ NO DEBERÍAS VER:")
print("-" * 20)
print("❌ 🆕 Modo CREACIÓN: Aplicando valor por defecto: Efectivo")
print("❌ ✅ Estableciendo Efectivo como forma de pago por defecto")

print(f"\n🏁 Test preparado - Verifica en el navegador")