from django.core.management.base import BaseCommand
from apps.invoicing.models import InvoiceLine, Invoice
from decimal import Decimal

class Command(BaseCommand):
    help = 'Recalcula todos los totales de líneas de factura existentes'
    
    def handle(self, *args, **options):
        self.stdout.write('Iniciando recálculo de totales de líneas de factura...')
        
        # Obtener todas las líneas de factura
        lines = InvoiceLine.objects.all()
        updated_lines = 0
        updated_invoices = set()
        
        for line in lines:
            # Calcular nuevo total
            old_total = line.line_total
            new_total = line.calculate_line_total()
            
            if old_total != new_total:
                line.line_total = new_total
                line.save(update_fields=['line_total'])
                updated_lines += 1
                updated_invoices.add(line.invoice.id)
                
                self.stdout.write(
                    f'Línea {line.id}: {old_total} -> {new_total}'
                )
        
        # Recalcular totales de facturas afectadas
        for invoice_id in updated_invoices:
            invoice = Invoice.objects.get(id=invoice_id)
            invoice.calculate_totals()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Recálculo completado: {updated_lines} líneas actualizadas, '
                f'{len(updated_invoices)} facturas recalculadas'
            )
        )