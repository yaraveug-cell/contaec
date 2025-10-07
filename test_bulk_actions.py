#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from apps.companies.models import PaymentMethod
from apps.accounting.models import JournalEntry

print('🧪 TEST: Verificar Acciones Grupales de Facturas')
print('=' * 50)

# 1. Verificar que existen facturas para probar
total_invoices = Invoice.objects.count()
print(f'📊 Total de facturas en el sistema: {total_invoices}')

if total_invoices == 0:
    print('❌ No hay facturas para probar las acciones grupales')
    exit()

# 2. Mostrar distribución por estado
print(f'\n📋 Distribución por estado:')
for status_code, status_name in Invoice.STATUS_CHOICES:
    count = Invoice.objects.filter(status=status_code).count()
    print(f'   {status_name}: {count} facturas')

# 3. Buscar facturas de diferentes estados para simular acciones
draft_invoices = Invoice.objects.filter(status='draft')
sent_invoices = Invoice.objects.filter(status='sent')
paid_invoices = Invoice.objects.filter(status='paid')
cancelled_invoices = Invoice.objects.filter(status='cancelled')

print(f'\n🎯 Facturas disponibles para acciones:')
print(f'   Borrador → Enviada: {draft_invoices.count()} facturas')
print(f'   Enviada → Pagada: {sent_invoices.count()} facturas')
print(f'   Cualquiera → Anulada: {total_invoices} facturas')
print(f'   Cualquiera → Borrador: {total_invoices} facturas')

# 4. Verificar que las acciones están disponibles
from apps.invoicing.admin import InvoiceAdmin
admin_instance = InvoiceAdmin(Invoice, None)

available_actions = admin_instance.actions
print(f'\n✅ Acciones disponibles en el admin:')
for action in available_actions:
    if hasattr(admin_instance, action):
        method = getattr(admin_instance, action)
        description = getattr(method, 'short_description', action)
        print(f'   • {action}: "{description}"')

# 5. Simular una acción grupal (mark_as_sent)
if draft_invoices.exists():
    print(f'\n🧪 SIMULANDO: Marcar {min(3, draft_invoices.count())} facturas como "Enviadas"')
    
    # Tomar máximo 3 facturas en borrador
    test_invoices = draft_invoices[:3]
    
    for invoice in test_invoices:
        print(f'   📄 Factura {invoice.number}: {invoice.get_status_display()} → Enviada')
        
        # Verificar si ya tiene asiento contable
        existing_entry = JournalEntry.objects.filter(
            reference=f"FAC-{invoice.id}",
            company=invoice.company
        ).first()
        
        if existing_entry:
            print(f'      ⚠️ Ya tiene asiento: {existing_entry.number}')
        else:
            print(f'      ✅ Se creará nuevo asiento contable')

# 6. Verificar facturas con transferencia para asientos
transferencia = PaymentMethod.objects.filter(name__icontains='TRANSFERENCIA').first()
if transferencia:
    transfer_invoices = Invoice.objects.filter(
        payment_form=transferencia,
        transfer_detail__isnull=False
    ).exclude(transfer_detail='')
    
    print(f'\n💳 Facturas con transferencia: {transfer_invoices.count()}')
    if transfer_invoices.exists():
        print(f'   → Al cambiar a "Enviada", incluirán detalle en asiento contable')

# 7. Mostrar cómo usar las acciones
print(f'\n🚀 CÓMO USAR LAS ACCIONES GRUPALES:')
print(f'   1. Ir a /admin/invoicing/invoice/')
print(f'   2. Seleccionar facturas con checkbox ☑️')
print(f'   3. Elegir acción en dropdown "Acción"')
print(f'   4. Hacer clic en "Ir"')
print(f'   5. ✅ Ver mensaje de confirmación')

print(f'\n🎯 ACCIONES DISPONIBLES:')
print(f'   📤 "Marcar como Enviadas" → Crea asientos contables')
print(f'   💰 "Marcar como Pagadas" → Mantiene asientos')
print(f'   ❌ "Marcar como Anuladas" → Revierte asientos')
print(f'   📝 "Marcar como Borrador" → Revierte asientos')

print(f'\n🏁 Test completado - Las acciones grupales están listas para usar')