#!/usr/bin/env python
"""
DEBUG: Verificar datos de factura en modo edición
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice

print("🔍 DEBUG: Problema en modo edición de facturas")
print("=" * 55)

# Buscar la última factura con Transferencia
try:
    transferencia_invoice = Invoice.objects.filter(
        payment_form__name='Transferencia'
    ).latest('created_at')
    
    print(f"🎯 Factura encontrada para test:")
    print(f"   ID: {transferencia_invoice.id}")
    print(f"   Empresa: {transferencia_invoice.company}")
    print(f"   Cliente: {transferencia_invoice.customer}")
    print(f"   Forma de pago: {transferencia_invoice.payment_form.name} (ID: {transferencia_invoice.payment_form.id})")
    print(f"   Cuenta: {transferencia_invoice.account.code} - {transferencia_invoice.account.name}")
    print(f"   Transfer Detail: '{transferencia_invoice.transfer_detail}'")
    print(f"   Creada: {transferencia_invoice.created_at}")
    
    edit_url = f"http://127.0.0.1:8000/admin/invoicing/invoice/{transferencia_invoice.id}/change/"
    print(f"\n📝 URL para editar:")
    print(f"   {edit_url}")
    
    print(f"\n🔍 PROBLEMA IDENTIFICADO:")
    print("   El JavaScript está aplicando valores por defecto")
    print("   en lugar de respetar los valores existentes")
    
    print(f"\n💡 SOLUCIÓN NECESARIA:")
    print("   1. Detectar si estamos en modo EDICIÓN vs CREACIÓN")
    print("   2. No aplicar defaults si ya hay valores guardados")
    print("   3. Cargar transfer_detail si la forma de pago es Transferencia")
    
except Invoice.DoesNotExist:
    print("❌ No se encontró factura con Transferencia")

print(f"\n🏁 Análisis completado")