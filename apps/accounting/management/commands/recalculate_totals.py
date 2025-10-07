from django.core.management.base import BaseCommand
from apps.accounting.models import JournalEntry

class Command(BaseCommand):
    help = 'Recalcular totales de débito y crédito en todos los asientos contables'
    
    def handle(self, *args, **options):
        self.stdout.write('Iniciando recálculo de totales...')
        
        entries = JournalEntry.objects.all()
        total_entries = entries.count()
        
        if total_entries == 0:
            self.stdout.write(self.style.WARNING('No hay asientos contables para procesar'))
            return
        
        updated_count = 0
        for i, entry in enumerate(entries):
            # Mostrar progreso cada 10 entradas
            if (i + 1) % 10 == 0:
                self.stdout.write(f'Procesando {i + 1}/{total_entries}...')
            
            old_debit = entry.total_debit
            old_credit = entry.total_credit
            
            # Recalcular totales
            entry.calculate_totals()
            
            # Solo guardar si hay cambios
            if entry.total_debit != old_debit or entry.total_credit != old_credit:
                entry.save(update_fields=['total_debit', 'total_credit'])
                updated_count += 1
                
                self.stdout.write(
                    f'Asiento {entry.number}: '
                    f'Débito: {old_debit} → {entry.total_debit}, '
                    f'Crédito: {old_credit} → {entry.total_credit}'
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Proceso completado. {updated_count} de {total_entries} asientos actualizados.'
            )
        )