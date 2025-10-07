#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from apps.companies.models import PaymentMethod
from datetime import datetime, timedelta

print('🔍 DEBUG: Facturas Nuevas vs Guardadas - Transfer Detail')
print('=' * 60)

# Buscar método de transferencia
transferencia = PaymentMethod.objects.filter(name__icontains='TRANSFERENCIA').first()
if not transferencia:
    print('❌ No se encontró método de transferencia')
    exit()

print(f'✅ Método transferencia ID: {transferencia.id}')

# Obtener facturas con transferencia
facturas_transfer = Invoice.objects.filter(payment_form=transferencia).order_by('-id')

print(f'\n📊 Total facturas con transferencia: {facturas_transfer.count()}')

# Analizar últimas 5 facturas
print('\n🔍 Análisis de las últimas 5 facturas con transferencia:')
print('-' * 80)

for i, factura in enumerate(facturas_transfer[:5], 1):
    print(f'\n{i}. Factura ID: {factura.id} | Número: {factura.number}')
    print(f'   Creada: {factura.created_at}')
    print(f'   Actualizada: {factura.updated_at}')
    print(f'   Payment Form ID: {factura.payment_form_id}')
    print(f'   Transfer Detail: "{factura.transfer_detail}"')
    print(f'   Transfer Detail (repr): {repr(factura.transfer_detail)}')
    print(f'   Transfer Detail (len): {len(factura.transfer_detail or "")}')
    print(f'   Transfer Detail (bool): {bool(factura.transfer_detail)}')
    
    # Verificar si es reciente (última hora)
    ahora = datetime.now()
    if hasattr(factura.created_at, 'replace'):
        # Es datetime aware, hacer comparación correcta
        desde_creacion = ahora.replace(tzinfo=factura.created_at.tzinfo) - factura.created_at
    else:
        # Es datetime naive
        desde_creacion = ahora - factura.created_at
        
    minutos = desde_creacion.total_seconds() / 60
    
    if minutos < 60:
        print(f'   🕐 RECIENTE: Creada hace {minutos:.1f} minutos')
    else:
        horas = minutos / 60
        if horas < 24:
            print(f'   🕑 Creada hace {horas:.1f} horas')
        else:
            dias = horas / 24
            print(f'   📅 Creada hace {dias:.1f} días')

# Buscar facturas muy recientes sin transfer_detail
print(f'\n🚨 Facturas recientes con transferencia SIN detalle:')
print('-' * 50)

facturas_sin_detalle_null = facturas_transfer.filter(transfer_detail__isnull=True)
facturas_sin_detalle_empty = facturas_transfer.filter(transfer_detail='')

print(f'   Facturas con transfer_detail NULL: {facturas_sin_detalle_null.count()}')
print(f'   Facturas con transfer_detail vacío: {facturas_sin_detalle_empty.count()}')

# Mostrar ejemplos
for factura in facturas_sin_detalle_null[:2]:
    print(f'     NULL: Factura {factura.id}: {factura.number}')
for factura in facturas_sin_detalle_empty[:2]:
    print(f'     VACÍO: Factura {factura.id}: {factura.number}')

# Verificar el campo transfer_detail en el modelo
print(f'\n🔍 Verificando campo transfer_detail en el modelo:')
print('-' * 50)

# Obtener información del campo
field_info = Invoice._meta.get_field('transfer_detail')
print(f'   Tipo de campo: {type(field_info).__name__}')
print(f'   Null permitido: {field_info.null}')
print(f'   Blank permitido: {field_info.blank}')
if hasattr(field_info, 'max_length'):
    print(f'   Max length: {field_info.max_length}')
if hasattr(field_info, 'default'):
    print(f'   Default: {field_info.default}')

print('\n🏁 Análisis completado')