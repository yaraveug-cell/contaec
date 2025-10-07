#!/usr/bin/env python
import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from apps.companies.models import PaymentMethod, Company
from apps.invoicing.models import Customer
from apps.accounting.services import AutomaticJournalEntryService
from apps.accounting.models import JournalEntry

print('🧪 PRUEBA REAL: Crear Factura y Asiento con Detalle Transferencia')
print('=' * 65)

# Obtener datos necesarios
transferencia = PaymentMethod.objects.filter(name__icontains='TRANSFERENCIA').first()
company = Company.objects.first()
customer = Customer.objects.first()

if not all([transferencia, company, customer]):
    print('❌ Faltan datos necesarios')
    exit()

print(f'✅ Datos listos:')
print(f'   Empresa: {company.trade_name}')
print(f'   Cliente: {customer.trade_name}')
print(f'   Método: {transferencia.name}')

# Buscar una cuenta disponible
from apps.accounting.models import ChartOfAccounts
account = ChartOfAccounts.objects.filter(
    accepts_movement=True
).first()

if not account:
    print('❌ No se encontró cuenta disponible')
    exit()

# Usar la empresa de la cuenta encontrada
company = account.company

print(f'   Cuenta: {account.code} - {account.name}')

# Crear nueva factura de prueba
nueva_factura = Invoice.objects.create(
    company=company,
    customer=customer,
    account=account,  # ← CAMPO FALTANTE AGREGADO
    payment_form=transferencia,
    transfer_detail='PRUEBA: Banco Pacífico - Cuenta 12345678 - Referencia ABC123',
    status='draft',  # Empezar en borrador
    created_by_id=1,
    subtotal=Decimal('100.00'),
    tax_amount=Decimal('15.00'),
    total=Decimal('115.00')
)

print(f'\n✅ Factura creada:')
print(f'   ID: {nueva_factura.id}')
print(f'   Número: {nueva_factura.number}')
print(f'   Transfer Detail: "{nueva_factura.transfer_detail}"')
print(f'   Estado inicial: {nueva_factura.status}')
print(f'   Subtotal: {nueva_factura.subtotal}')
print(f'   Tax amount: {nueva_factura.tax_amount}')
print(f'   Total: {nueva_factura.total}')

# Cambiar estado a 'sent' para activar creación de asiento
print(f'\n🔧 Cambiando estado a "sent" para crear asiento...')
nueva_factura.status = 'sent'
nueva_factura.save()

# Crear asiento usando el servicio actualizado
print(f'\n📋 Creando asiento contable...')
try:
    journal_entry, created = AutomaticJournalEntryService.create_journal_entry_from_invoice(nueva_factura)
    
    if created and journal_entry:
        print(f'✅ Asiento creado exitosamente!')
        print(f'   ID: {journal_entry.id}')
        print(f'   Número: {journal_entry.number}')
        print(f'   Fecha: {journal_entry.date}')
        print(f'   Referencia: {journal_entry.reference}')
        print(f'   📝 DESCRIPCIÓN: "{journal_entry.description}"')
        
        # Verificar si incluye el detalle de transferencia
        if nueva_factura.transfer_detail in journal_entry.description:
            print(f'\n🎉 ¡ÉXITO! El detalle de transferencia SÍ está incluido en el asiento')
            print(f'   Detalle encontrado: "{nueva_factura.transfer_detail}"')
        else:
            print(f'\n❌ ERROR: El detalle de transferencia NO está en la descripción')
            
        # Mostrar líneas del asiento
        lines = journal_entry.journalentryline_set.all()
        print(f'\n📊 Líneas del asiento ({lines.count()}):')
        for i, line in enumerate(lines, 1):
            print(f'   {i}. {line.account.code} - {line.account.name}')
            print(f'      DEBE: ${line.debit} | HABER: ${line.credit}')
            print(f'      Descripción: "{line.description}"')
            
    elif journal_entry and not created:
        print(f'⚠️ Ya existía asiento: {journal_entry.number}')
        print(f'   Descripción: "{journal_entry.description}"')
    else:
        print(f'❌ Error: No se pudo crear el asiento')
        
except Exception as e:
    print(f'❌ Error creando asiento: {str(e)}')
    import traceback
    traceback.print_exc()

print(f'\n🌐 Para ver en admin:')
print(f'   Factura: /admin/invoicing/invoice/{nueva_factura.id}/change/')
if 'journal_entry' in locals() and journal_entry:
    print(f'   Asiento: /admin/accounting/journalentry/{journal_entry.id}/change/')

print(f'\n🏁 Prueba completada')