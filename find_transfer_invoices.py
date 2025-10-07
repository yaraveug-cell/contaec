#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from apps.companies.models import PaymentMethod

# Buscar método de transferencia
transferencia = PaymentMethod.objects.filter(name__icontains='TRANSFERENCIA').first()
if transferencia:
    print(f'Método transferencia ID: {transferencia.id}')
    
    # Buscar facturas con transferencia y detalle
    facturas = Invoice.objects.filter(payment_form=transferencia, transfer_detail__isnull=False).exclude(transfer_detail='')
    print(f'Facturas con transferencia y detalle: {facturas.count()}')
    
    for f in facturas[:3]:
        print(f'  Factura {f.id}: {f.number} - Detalle: "{f.transfer_detail}"')
        print(f'    URL: /admin/invoicing/invoice/{f.id}/change/')
else:
    print('No se encontró método de transferencia')

# También mostrar las últimas 3 facturas
print('\nÚltimas 3 facturas:')
for f in Invoice.objects.all().order_by('-id')[:3]:
    print(f'  Factura {f.id}: {f.number} - Pago: {f.payment_form} - Detalle: "{f.transfer_detail}"')
    print(f'    URL: /admin/invoicing/invoice/{f.id}/change/')