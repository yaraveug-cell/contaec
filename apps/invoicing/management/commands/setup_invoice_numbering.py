"""
Comando para configurar numeración de facturas en empresas
"""
from django.core.management.base import BaseCommand
from apps.companies.models import Company, CompanySettings


class Command(BaseCommand):
    help = 'Configura la numeración de facturas según normativa ecuatoriana'

    def add_arguments(self, parser):
        parser.add_argument('--company-id', type=int, help='ID específico de empresa')
        parser.add_argument('--reset-sequential', action='store_true', help='Reiniciar secuencial a 1')

    def handle(self, *args, **options):
        company_id = options.get('company_id')
        reset_sequential = options.get('reset_sequential', False)
        
        if company_id:
            companies = Company.objects.filter(id=company_id)
            if not companies.exists():
                self.stdout.write(
                    self.style.ERROR(f'Empresa con ID {company_id} no encontrada')
                )
                return
        else:
            companies = Company.objects.all()

        if not companies.exists():
            self.stdout.write(
                self.style.ERROR('No hay empresas registradas')
            )
            return

        for company in companies:
            self.stdout.write(f'\n=== Configurando {company.trade_name} ===')
            self.stdout.write(f'RUC: {company.ruc}')
            
            # Verificar códigos de establecimiento y punto de emisión
            if not company.establishment_code:
                company.establishment_code = '001'
                self.stdout.write('✓ Código de establecimiento establecido: 001')
            else:
                self.stdout.write(f'✓ Código de establecimiento: {company.establishment_code}')
                
            if not company.emission_point:
                company.emission_point = '001'
                self.stdout.write('✓ Punto de emisión establecido: 001')
            else:
                self.stdout.write(f'✓ Punto de emisión: {company.emission_point}')
            
            company.save()
            
            # Crear o actualizar configuraciones
            settings, created = CompanySettings.objects.get_or_create(
                company=company,
                defaults={
                    'invoice_sequential': 1,
                    'credit_note_sequential': 1,
                    'debit_note_sequential': 1,
                    'withholding_sequential': 1,
                }
            )
            
            if created:
                self.stdout.write('✓ Configuración de secuenciales creada')
            else:
                if reset_sequential:
                    settings.invoice_sequential = 1
                    settings.credit_note_sequential = 1
                    settings.debit_note_sequential = 1
                    settings.withholding_sequential = 1
                    settings.save()
                    self.stdout.write('✓ Secuenciales reiniciados')
                else:
                    self.stdout.write('✓ Configuración existente mantenida')
            
            self.stdout.write(f'✓ Próximo número de factura será: {company.establishment_code}-{company.emission_point}-{str(settings.invoice_sequential).zfill(9)}')
            
            # Mostrar configuración actual
            self.stdout.write(f'  - Facturas: {settings.invoice_sequential}')
            self.stdout.write(f'  - Notas de crédito: {settings.credit_note_sequential}')
            self.stdout.write(f'  - Notas de débito: {settings.debit_note_sequential}')
            self.stdout.write(f'  - Retenciones: {settings.withholding_sequential}')

        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Configuración completada para {companies.count()} empresa(s)')
        )