# Migración personalizada para cambio de payment_form de CharField a ForeignKey
from django.db import migrations, models
import django.db.models.deletion

def migrate_payment_form_to_fk(apps, schema_editor):
    """Migrar datos de CharField a ForeignKey"""
    Invoice = apps.get_model('invoicing', 'Invoice')
    PaymentMethod = apps.get_model('companies', 'PaymentMethod')
    
    # Mapear valores antiguos a métodos de pago
    payment_form_mapping = {
        'EFECTIVO': 'Efectivo',
        'CREDITO': 'Crédito',
        'TRANSFERENCIA': 'Transferencia'
    }
    
    # Obtener métodos de pago existentes
    payment_methods = {}
    for pm in PaymentMethod.objects.all():
        payment_methods[pm.name] = pm
    
    print(f"Migrando {Invoice.objects.count()} facturas...")
    
    # Migrar cada factura
    migrated_count = 0
    for invoice in Invoice.objects.all():
        old_value = getattr(invoice, 'payment_form_old', None)
        if old_value:
            new_name = payment_form_mapping.get(old_value)
            if new_name and new_name in payment_methods:
                invoice.payment_form_new = payment_methods[new_name]
                invoice.save(update_fields=['payment_form_new'])
                migrated_count += 1
                print(f"  Factura {invoice.id}: {old_value} -> {new_name}")
    
    print(f"Migradas {migrated_count} facturas exitosamente")

def reverse_migrate_payment_form_to_fk(apps, schema_editor):
    """Migración inversa"""
    Invoice = apps.get_model('invoicing', 'Invoice')
    
    reverse_mapping = {
        'Efectivo': 'EFECTIVO',
        'Crédito': 'CREDITO', 
        'Transferencia': 'TRANSFERENCIA'
    }
    
    for invoice in Invoice.objects.select_related('payment_form_new').all():
        if invoice.payment_form_new:
            old_value = reverse_mapping.get(invoice.payment_form_new.name, 'EFECTIVO')
            invoice.payment_form_old = old_value
            invoice.save(update_fields=['payment_form_old'])

class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0002_paymentmethod_company_payment_method'),
        ('invoicing', '0010_invoice_account'),
    ]

    operations = [
        # Paso 1: Renombrar campo original
        migrations.RenameField(
            model_name='invoice',
            old_name='payment_form',
            new_name='payment_form_old',
        ),
        
        # Paso 2: Agregar nuevo campo ForeignKey
        migrations.AddField(
            model_name='invoice',
            name='payment_form_new',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to='companies.paymentmethod',
                verbose_name='Forma de Pago'
            ),
        ),
        
        # Paso 3: Migrar datos
        migrations.RunPython(
            migrate_payment_form_to_fk,
            reverse_migrate_payment_form_to_fk
        ),
        
        # Paso 4: Eliminar campo antiguo
        migrations.RemoveField(
            model_name='invoice',
            name='payment_form_old',
        ),
        
        # Paso 5: Renombrar nuevo campo al nombre original
        migrations.RenameField(
            model_name='invoice',
            old_name='payment_form_new',
            new_name='payment_form',
        ),
    ]