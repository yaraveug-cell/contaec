"""
Comando para probar la numeración automática de facturas
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.companies.models import Company
from apps.invoicing.models import Customer, Invoice
from apps.inventory.models import Product
from decimal import Decimal
import datetime


class Command(BaseCommand):
    help = 'Prueba la numeración automática de facturas ecuatorianas'

    def add_arguments(self, parser):
        parser.add_argument('--company-id', type=int, help='ID de la empresa')

    def handle(self, *args, **options):
        company_id = options.get('company_id')
        
        if company_id:
            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Empresa con ID {company_id} no encontrada')
                )
                return
        else:
            company = Company.objects.first()
            if not company:
                self.stdout.write(
                    self.style.ERROR('No hay empresas registradas')
                )
                return

        self.stdout.write(f'Probando numeración para: {company.trade_name}')
        self.stdout.write(f'RUC: {company.ruc}')
        self.stdout.write(f'Establecimiento: {company.establishment_code}')
        self.stdout.write(f'Punto de emisión: {company.emission_point}')
        
        # Obtener o crear un cliente de prueba
        customer, created = Customer.objects.get_or_create(
            company=company,
            identification='1234567890001',
            defaults={
                'customer_type': Customer.JURIDICAL,
                'trade_name': 'Cliente de Prueba S.A.',
                'legal_name': 'Cliente de Prueba Sociedad Anónima',
                'email': 'cliente@prueba.com',
                'address': 'Av. Amazonas y Naciones Unidas',
                'credit_limit': Decimal('5000.00'),
                'payment_terms': 30,
            }
        )
        
        if created:
            self.stdout.write(f'Cliente creado: {customer.trade_name}')
        else:
            self.stdout.write(f'Cliente existente: {customer.trade_name}')

        # Crear factura de prueba
        try:
            invoice = Invoice(
                company=company,
                customer=customer,
                date=timezone.now().date(),
                due_date=timezone.now().date() + datetime.timedelta(days=30),
                status=Invoice.DRAFT,
                created_by_id=1  # Asumiendo que existe usuario con ID 1
            )
            
            # No asignar número manualmente - se generará automáticamente
            self.stdout.write('Generando número de factura...')
            
            invoice.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Factura creada exitosamente: {invoice.number}'
                )
            )
            
            # Mostrar información del secuencial
            from apps.companies.models import CompanySettings
            settings = CompanySettings.objects.get(company=company)
            
            self.stdout.write(f'Próximo secuencial: {settings.invoice_sequential}')
            
            # Crear otra factura para verificar incremento
            invoice2 = Invoice(
                company=company,
                customer=customer,
                date=timezone.now().date(),
                due_date=timezone.now().date() + datetime.timedelta(days=15),
                status=Invoice.DRAFT,
                created_by_id=1
            )
            
            invoice2.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Segunda factura creada: {invoice2.number}'
                )
            )
            
            # Verificar formato
            parts = invoice.number.split('-')
            if len(parts) == 3:
                establishment, emission, sequential = parts
                self.stdout.write(f'Establecimiento: {establishment} (3 dígitos)')
                self.stdout.write(f'Punto emisión: {emission} (3 dígitos)')  
                self.stdout.write(f'Secuencial: {sequential} (9 dígitos)')
                
                if (len(establishment) == 3 and 
                    len(emission) == 3 and 
                    len(sequential) == 9):
                    self.stdout.write(
                        self.style.SUCCESS(
                            '✅ Formato correcto según normativa ecuatoriana'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            '❌ Formato incorrecto'
                        )
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        '❌ Formato de número inválido'
                    )
                )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al crear factura: {str(e)}')
            )