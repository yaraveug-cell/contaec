#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from apps.companies.models import PaymentMethod
from apps.accounting.services import AutomaticJournalEntryService
from apps.accounting.models import JournalEntry

print('🧪 PRUEBA: Usar Factura Existente para Probar Detalle Transferencia')
print('=' * 65)

# Buscar factura existente con transferencia
transferencia = PaymentMethod.objects.filter(name__icontains='TRANSFERENCIA').first()
factura_existente = Invoice.objects.filter(
    payment_form=transferencia,
    transfer_detail__isnull=False,
    total__gt=0
).exclude(transfer_detail='').first()

if not factura_existente:
    print('❌ No se encontró factura existente con transferencia y total > 0')
    exit()

print(f'✅ Factura encontrada:')
print(f'   ID: {factura_existente.id}')
print(f'   Número: {factura_existente.number}')
print(f'   Cliente: {factura_existente.customer.trade_name}')
print(f'   Transfer Detail: "{factura_existente.transfer_detail}"')
print(f'   Total: ${factura_existente.total}')
print(f'   Estado actual: {factura_existente.status}')

# Verificar si ya tiene asiento
existing_entry = JournalEntry.objects.filter(
    reference=f"FAC-{factura_existente.id}",
    company=factura_existente.company
).first()

if existing_entry:
    print(f'\n📋 Asiento existente:')
    print(f'   Número: {existing_entry.number}')
    print(f'   Descripción ACTUAL: "{existing_entry.description}"')
    
    if factura_existente.transfer_detail in existing_entry.description:
        print('✅ Ya incluye detalle de transferencia')
    else:
        print('❌ NO incluye detalle de transferencia (asiento creado antes del fix)')
        
        # Mostrar cómo se vería con el nuevo código
        base_description = f"Venta factura #{factura_existente.number or factura_existente.id} - {factura_existente.customer.trade_name or factura_existente.customer.legal_name}"
        new_description = f"{base_description} - Transferencia: {factura_existente.transfer_detail}"
        
        print(f'\n📝 Con el FIX se vería así:')
        print(f'   "{new_description}"')

# Crear un nuevo asiento usando el código actualizado (simulación)
print(f'\n🔧 Simulando creación de NUEVO asiento con código actualizado:')

# Eliminar asiento existente temporalmente para probar
if existing_entry:
    print(f'   Eliminando asiento existente {existing_entry.number} para prueba...')
    existing_entry.delete()

# Crear nuevo asiento
try:
    journal_entry, created = AutomaticJournalEntryService.create_journal_entry_from_invoice(factura_existente)
    
    if created and journal_entry:
        print(f'✅ ¡NUEVO asiento creado exitosamente!')
        print(f'   ID: {journal_entry.id}')
        print(f'   Número: {journal_entry.number}')
        print(f'   📝 DESCRIPCIÓN NUEVA: "{journal_entry.description}"')
        
        # Verificar si incluye el detalle de transferencia
        if factura_existente.transfer_detail in journal_entry.description:
            print(f'\n🎉 ¡ÉXITO COMPLETO! El detalle de transferencia SÍ está incluido')
            print(f'   ✅ Detalle encontrado: "{factura_existente.transfer_detail}"')
            
            # Mostrar diferencia
            base_part = journal_entry.description.split(' - Transferencia:')[0]
            transfer_part = f"Transferencia: {factura_existente.transfer_detail}"
            
            print(f'\n📊 Análisis de la descripción:')
            print(f'   Parte base: "{base_part}"')
            print(f'   Parte agregada: "- {transfer_part}"')
        else:
            print(f'\n❌ ERROR: El detalle de transferencia NO está en la descripción')
            
        # Mostrar líneas del asiento
        lines = journal_entry.journalentryline_set.all()
        print(f'\n📊 Líneas del asiento ({lines.count()}):')
        for i, line in enumerate(lines, 1):
            print(f'   {i}. {line.account.code} - {line.account.name}')
            print(f'      DEBE: ${line.debit} | HABER: ${line.credit}')
            
    else:
        print(f'❌ Error: No se pudo crear el asiento')
        
except Exception as e:
    print(f'❌ Error creando asiento: {str(e)}')
    import traceback
    traceback.print_exc()

print(f'\n🌐 Para ver en admin:')
print(f'   Factura: /admin/invoicing/invoice/{factura_existente.id}/change/')
if 'journal_entry' in locals() and journal_entry:
    print(f'   Nuevo Asiento: /admin/accounting/journalentry/{journal_entry.id}/change/')

print(f'\n🏁 Prueba completada')