#!/usr/bin/env python
"""
DEBUG: Verificar cómo Django renderiza el campo transfer_detail
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from django.forms.models import model_to_dict

print("🔍 DEBUG: Campo transfer_detail en Django")
print("=" * 50)

# Buscar factura con transfer_detail
invoice = Invoice.objects.filter(
    transfer_detail__isnull=False
).exclude(
    transfer_detail=''
).first()

if invoice:
    print(f"🎯 Factura encontrada:")
    print(f"   ID: {invoice.id}")
    print(f"   Transfer Detail: '{invoice.transfer_detail}'")
    
    # Verificar el modelo serializado
    invoice_dict = model_to_dict(invoice)
    print(f"\n📋 Datos del modelo:")
    for key, value in invoice_dict.items():
        if 'transfer' in key.lower():
            print(f"   {key}: {value}")
    
    print(f"\n🌐 URL de edición:")
    edit_url = f"http://127.0.0.1:8000/admin/invoicing/invoice/{invoice.id}/change/"
    print(f"   {edit_url}")
    
    print(f"\n💡 EN EL NAVEGADOR, BUSCAR:")
    print("1. Campo con ID 'id_transfer_detail'")
    print("2. Campo con name 'transfer_detail'") 
    print("3. Inspeccionar el HTML del formulario")
    print("4. Verificar window.invoiceData en la consola")
    
    print(f"\n🔧 JAVASCRIPT PARA CONSOLA DEL NAVEGADOR:")
    print("// Buscar campo Django")
    print("const djangoField = document.getElementById('id_transfer_detail');")
    print("console.log('Campo Django:', djangoField);")
    print("console.log('Valor Django:', djangoField?.value);")
    print("")
    print("// Buscar todos los campos relacionados")
    print("const allFields = document.querySelectorAll('[name*=\"transfer\"], [id*=\"transfer\"]');")
    print("console.log('Todos los campos transfer:', allFields);")
    print("")
    print("// Verificar invoiceData")
    print("console.log('Invoice Data:', window.invoiceData);")
    
else:
    print("❌ No se encontró factura con transfer_detail")

print(f"\n🏁 Debug completado")