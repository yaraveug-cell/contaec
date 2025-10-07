#!/usr/bin/env python
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from apps.companies.models import PaymentMethod, Company
from apps.invoicing.models import Customer

print('🧪 TEST: Crear factura nueva con transferencia')
print('=' * 50)

# Obtener datos necesarios
transferencia = PaymentMethod.objects.filter(name__icontains='TRANSFERENCIA').first()
company = Company.objects.first()
customer = Customer.objects.first()

if not all([transferencia, company, customer]):
    print('❌ Faltan datos necesarios')
    exit()

print(f'✅ Método transferencia: {transferencia.name} (ID: {transferencia.id})')
print(f'✅ Empresa: {company.trade_name} (ID: {company.id})')
print(f'✅ Cliente: {customer.trade_name} (ID: {customer.id})')

# Crear nueva factura
nueva_factura = Invoice.objects.create(
    company=company,
    customer=customer,
    payment_form=transferencia,
    transfer_detail='TEST: Factura nueva con detalle de transferencia - Banco Ejemplo 123456',
    status='DRAFT',
    created_by_id=1  # Asumiendo que existe un usuario con ID 1
)

print(f'\n✅ Nueva factura creada:')
print(f'   ID: {nueva_factura.id}')
print(f'   Número: {nueva_factura.number}')
print(f'   Transfer Detail: "{nueva_factura.transfer_detail}"')
print(f'   URL para editar: /admin/invoicing/invoice/{nueva_factura.id}/change/')

# Verificar que se guardó correctamente
factura_verificacion = Invoice.objects.get(id=nueva_factura.id)
print(f'\n🔍 Verificación desde BD:')
print(f'   Transfer Detail: "{factura_verificacion.transfer_detail}"')
print(f'   Payment Form: {factura_verificacion.payment_form.name}')

print(f'\n🌐 Para probar en navegador:')
print(f'   http://127.0.0.1:8000/admin/invoicing/invoice/{nueva_factura.id}/change/')

print('\n🏁 Test completado')