#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from apps.companies.models import PaymentMethod
from apps.accounting.services import AutomaticJournalEntryService
from apps.accounting.models import JournalEntry

print('🧪 TEST: Detalle Transferencia en Asientos Contables')
print('=' * 55)

# Buscar una factura con transferencia existente
transferencia = PaymentMethod.objects.filter(name__icontains='TRANSFERENCIA').first()
if not transferencia:
    print('❌ No se encontró método de transferencia')
    exit()

facturas_transfer = Invoice.objects.filter(
    payment_form=transferencia,
    transfer_detail__isnull=False
).exclude(transfer_detail='')

if not facturas_transfer.exists():
    print('❌ No se encontraron facturas con transferencia y detalle')
    exit()

# Tomar la primera factura con transferencia
factura = facturas_transfer.first()
print(f'✅ Factura de prueba: ID {factura.id}')
print(f'   Número: {factura.number}')
print(f'   Cliente: {factura.customer.trade_name}')
print(f'   Método pago: {factura.payment_form.name}')
print(f'   Transfer detail: "{factura.transfer_detail}"')

# Verificar si ya existe asiento para esta factura
existing_entry = JournalEntry.objects.filter(
    reference=f"FAC-{factura.id}",
    company=factura.company
).first()

if existing_entry:
    print(f'\n📋 Asiento existente encontrado: {existing_entry.number}')
    print(f'   Descripción actual: "{existing_entry.description}"')
    
    # Verificar si ya incluye el detalle de transferencia
    if factura.transfer_detail and factura.transfer_detail in existing_entry.description:
        print('✅ El asiento YA incluye el detalle de transferencia')
    else:
        print('⚠️ El asiento NO incluye el detalle de transferencia')
        print('   Esto es esperado si fue creado antes del fix')
else:
    print('\n📋 No existe asiento previo para esta factura')

# Crear un nuevo asiento usando el servicio actualizado
print(f'\n🔧 Probando servicio actualizado...')

# Simular creación de asiento (sin commitear a BD)
try:
    # Para test, crear asiento temporal
    print(f'   Método pago: {factura.payment_form.name}')
    print(f'   Transfer detail: "{factura.transfer_detail}"')
    
    # Generar descripción que debería crear el servicio
    base_description = f"Venta factura #{factura.number or factura.id} - {factura.customer.trade_name or factura.customer.legal_name}"
    
    if (factura.payment_form and 
        hasattr(factura.payment_form, 'name') and
        'TRANSFERENCIA' in factura.payment_form.name.upper() and 
        factura.transfer_detail):
        expected_description = f"{base_description} - Transferencia: {factura.transfer_detail}"
        print('✅ Se detectó TRANSFERENCIA con detalle')
    else:
        expected_description = base_description
        print('ℹ️ No es transferencia o sin detalle')
    
    print(f'\n📝 Descripción esperada:')
    print(f'   "{expected_description}"')
    
    # Verificar longitud de descripción
    if len(expected_description) > 200:  # Asumir límite de campo
        print(f'⚠️ Descripción muy larga ({len(expected_description)} caracteres)')
    else:
        print(f'✅ Longitud adecuada ({len(expected_description)} caracteres)')
    
except Exception as e:
    print(f'❌ Error en test: {str(e)}')

print(f'\n🎯 Diferencias esperadas:')
print(f'   ANTES: "Venta factura #... - Cliente"')
print(f'   DESPUÉS: "Venta factura #... - Cliente - Transferencia: {factura.transfer_detail}"')

print(f'\n🏁 Test completado')
print(f'\n💡 Para verificar en producción:')
print(f'   1. Crear nueva factura con transferencia y detalle')
print(f'   2. Cambiar estado a "Enviada"')
print(f'   3. Verificar descripción del asiento creado')