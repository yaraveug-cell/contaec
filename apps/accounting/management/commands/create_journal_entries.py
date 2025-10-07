"""
Comando de gestión para crear asientos contables automáticos
desde facturas existentes que estén en estado 'sent' pero no tengan asiento
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from apps.invoicing.models import Invoice
from apps.accounting.models import JournalEntry
from apps.accounting.services import AutomaticJournalEntryService


class Command(BaseCommand):
    help = 'Crea asientos contables para facturas enviadas que no los tengan'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--invoice-id',
            type=int,
            help='ID específico de factura a procesar'
        )
        
        parser.add_argument(
            '--company-id',
            type=int,
            help='Procesar solo facturas de una empresa específica'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar qué se procesaría sin crear asientos'
        )
        
        parser.add_argument(
            '--status',
            type=str,
            default='sent',
            help='Estado de facturas a procesar (default: sent)'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando procesamiento de facturas para asientos contables...')
        )
        
        # Construir queryset base
        queryset = Invoice.objects.filter(status=options['status'])
        
        # Filtros opcionales
        if options['invoice_id']:
            queryset = queryset.filter(id=options['invoice_id'])
            
        if options['company_id']:
            queryset = queryset.filter(company_id=options['company_id'])
        
        # Excluir facturas que ya tienen asiento
        existing_references = JournalEntry.objects.filter(
            reference__startswith='FAC-'
        ).values_list('reference', flat=True)
        
        existing_invoice_ids = [
            int(ref.replace('FAC-', '')) 
            for ref in existing_references 
            if ref.replace('FAC-', '').isdigit()
        ]
        
        if not options['invoice_id']:  # Solo excluir si no es una factura específica
            queryset = queryset.exclude(id__in=existing_invoice_ids)
        
        # Seleccionar datos relacionados para optimizar consultas
        queryset = queryset.select_related(
            'company', 'customer', 'account', 'payment_form', 'created_by'
        ).prefetch_related('lines')
        
        # Estadísticas
        total_count = queryset.count()
        processed = 0
        created = 0
        errors = 0
        skipped = 0
        
        self.stdout.write(f"📊 Facturas encontradas para procesar: {total_count}")
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('🔍 Modo DRY-RUN: Solo mostrando qué se procesaría...')
            )
        
        # Procesar cada factura
        for invoice in queryset:
            processed += 1
            
            self.stdout.write(f"\n[{processed}/{total_count}] Procesando factura #{invoice.id}...")
            
            # Mostrar información de la factura
            self.stdout.write(f"   📄 Empresa: {invoice.company.legal_name}")
            self.stdout.write(f"   👤 Cliente: {invoice.customer.trade_name or invoice.customer.legal_name}")
            self.stdout.write(f"   💰 Total: ${invoice.total}")
            self.stdout.write(f"   📊 Cuenta: {invoice.account.code if invoice.account else 'N/A'}")
            
            # Validar datos antes de procesar
            if not self._validate_invoice_for_processing(invoice):
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f"   ❌ Factura {invoice.id} tiene datos incompletos")
                )
                continue
            
            # Verificar si ya existe asiento (doble verificación)
            if invoice.id in existing_invoice_ids:
                skipped += 1
                existing_entry = JournalEntry.objects.filter(
                    reference=f'FAC-{invoice.id}'
                ).first()
                self.stdout.write(
                    self.style.WARNING(f"   ⚠️ Ya existe asiento #{existing_entry.number if existing_entry else 'N/A'}")
                )
                continue
            
            if options['dry_run']:
                self.stdout.write(
                    self.style.SUCCESS(f"   ✅ Se crearía asiento para factura #{invoice.id}")
                )
                created += 1
                continue
            
            # Crear asiento contable
            try:
                journal_entry, was_created = AutomaticJournalEntryService.create_journal_entry_from_invoice(invoice)
                
                if was_created and journal_entry:
                    created += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"   ✅ Asiento #{journal_entry.number} creado exitosamente")
                    )
                    
                    # Mostrar desglose del asiento
                    self.stdout.write(f"      📝 Total Débito: ${journal_entry.total_debit}")
                    self.stdout.write(f"      📝 Total Crédito: ${journal_entry.total_credit}")
                    self.stdout.write(f"      📝 Balanceado: {'✅' if journal_entry.is_balanced else '❌'}")
                    
                elif journal_entry and not was_created:
                    skipped += 1
                    self.stdout.write(
                        self.style.WARNING(f"   ⚠️ Asiento ya existía: #{journal_entry.number}")
                    )
                else:
                    errors += 1
                    self.stdout.write(
                        self.style.ERROR(f"   ❌ No se pudo crear asiento")
                    )
                    
            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f"   ❌ Error: {str(e)}")
                )
        
        # Resumen final
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS("📊 RESUMEN FINAL:"))
        self.stdout.write(f"   📄 Facturas procesadas: {processed}")
        self.stdout.write(f"   ✅ Asientos creados: {created}")
        self.stdout.write(f"   ⚠️ Omitidas (ya tenían asiento): {skipped}")
        self.stdout.write(f"   ❌ Errores: {errors}")
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING("\n🔍 Fue una simulación. Para ejecutar realmente, omite --dry-run")
            )
        
        # Código de salida
        if errors > 0:
            self.stdout.write(
                self.style.ERROR(f"\n⚠️ Se completó con {errors} errores")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"\n🎉 Procesamiento completado exitosamente")
            )
    
    def _validate_invoice_for_processing(self, invoice):
        """Valida que la factura tenga los datos necesarios"""
        required_fields = [
            ('company', invoice.company),
            ('customer', invoice.customer),
            ('account', invoice.account),
            ('payment_form', invoice.payment_form),
        ]
        
        for field_name, field_value in required_fields:
            if field_value is None:
                self.stdout.write(f"      ❌ Campo requerido faltante: {field_name}")
                return False
        
        if invoice.total <= 0:
            self.stdout.write(f"      ❌ Total debe ser mayor a 0: {invoice.total}")
            return False
        
        if not invoice.lines.exists():
            self.stdout.write(f"      ❌ Factura sin líneas de detalle")
            return False
            
        return True