"""
Comando para eliminar transacciones de empresa GUEBER manteniendo estructura base.

Elimina:
- Asientos contables y sus líneas
- Facturas de venta y sus líneas  
- Facturas de compra y sus líneas
- Transacciones bancarias
- Extractos bancarios
- Movimientos de inventario

Conserva:
- Usuarios y permisos
- Plan de cuentas
- Maestros (clientes, proveedores, productos)
- Configuraciones de empresa
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from apps.companies.models import Company
import json
import os
from datetime import datetime


class Command(BaseCommand):
    help = 'Elimina transacciones de GUEBER manteniendo estructura base'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la eliminación sin realizar cambios reales',
        )
        parser.add_argument(
            '--backup',
            action='store_true', 
            help='Genera backup antes de eliminar',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirma que desea proceder con la eliminación',
        )
        parser.add_argument(
            '--company',
            type=str,
            default='GUEBER',
            help='Nombre comercial de la empresa (default: GUEBER)',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.backup = options['backup']
        self.confirm = options['confirm']
        self.company_name = options['company']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🧹 LIMPIEZA DE TRANSACCIONES - {self.company_name.upper()}\n'
            )
        )
        
        try:
            # Paso 1: Identificar empresa
            company = self._get_company()
            
            # Paso 2: Análisis previo
            analysis = self._analyze_data(company)
            
            # Paso 3: Mostrar plan de eliminación
            self._show_deletion_plan(analysis)
            
            # Paso 4: Confirmaciones
            if not self._get_confirmations():
                self.stdout.write(self.style.WARNING('❌ Operación cancelada'))
                return
                
            # Paso 5: Backup opcional
            if self.backup:
                self._create_backup(company, analysis)
            
            # Paso 6: Ejecutar eliminación
            if self.dry_run:
                self.stdout.write(
                    self.style.WARNING('\n🔍 SIMULACIÓN - No se realizarán cambios\n')
                )
            else:
                self._execute_deletion(company, analysis)
                
            # Paso 7: Reporte final
            self._final_report(company)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Error durante la operación: {str(e)}')
            )
            raise CommandError(f'Falló la eliminación: {str(e)}')

    def _get_company(self):
        """Identificar y validar empresa objetivo"""
        self.stdout.write('🔍 Buscando empresa...')
        
        company = Company.objects.filter(
            trade_name__icontains=self.company_name
        ).first()
        
        if not company:
            company = Company.objects.filter(
                legal_name__icontains=self.company_name
            ).first()
            
        if not company:
            raise CommandError(
                f'❌ Empresa "{self.company_name}" no encontrada'
            )
            
        self.stdout.write(
            self.style.SUCCESS(f'✅ Empresa encontrada: {company.trade_name}')
        )
        self.stdout.write(f'   📋 Razón Social: {company.legal_name}')
        self.stdout.write(f'   🆔 RUC: {company.ruc}')
        self.stdout.write(f'   🔑 ID: {company.id}')
        
        return company

    def _analyze_data(self, company):
        """Analizar datos a eliminar"""
        self.stdout.write('\n📊 Analizando transacciones...')
        
        analysis = {
            'company': company,
            'models': [],
            'total_records': 0
        }
        
        # Definir modelos a verificar
        models_config = [
            {
                'name': 'Asientos Contables',
                'module': 'apps.accounting.models',
                'model': 'JournalEntry',
                'filter_field': 'company',
                'priority': 1
            },
            {
                'name': 'Líneas de Asiento',
                'module': 'apps.accounting.models', 
                'model': 'JournalEntryLine',
                'filter_field': 'journal_entry__company',
                'priority': 2
            },
            {
                'name': 'Facturas de Venta',
                'module': 'apps.invoicing.models',
                'model': 'Invoice', 
                'filter_field': 'company',
                'priority': 3
            },
            {
                'name': 'Líneas Factura Venta',
                'module': 'apps.invoicing.models',
                'model': 'InvoiceLine',
                'filter_field': 'invoice__company', 
                'priority': 4
            },
            {
                'name': 'Facturas de Compra',
                'module': 'apps.suppliers.models',
                'model': 'PurchaseInvoice',
                'filter_field': 'company',
                'priority': 5
            },
            {
                'name': 'Líneas Factura Compra',
                'module': 'apps.suppliers.models',
                'model': 'PurchaseInvoiceLine',
                'filter_field': 'purchase_invoice__company',
                'priority': 6
            },
            {
                'name': 'Transacciones Bancarias',
                'module': 'apps.banking.models',
                'model': 'BankTransaction',
                'filter_field': 'bank_account__company',
                'priority': 7
            },
            {
                'name': 'Extractos Bancarios', 
                'module': 'apps.banking.models',
                'model': 'ExtractoBancario',
                'filter_field': 'bank_account__company',
                'priority': 8
            }
        ]
        
        # Analizar cada modelo
        for model_config in models_config:
            try:
                module = __import__(model_config['module'], fromlist=[model_config['model']])
                model = getattr(module, model_config['model'])
                
                # Contar registros
                filter_kwargs = {model_config['filter_field']: company}
                count = model.objects.filter(**filter_kwargs).count()
                
                if count > 0:
                    analysis['models'].append({
                        'name': model_config['name'],
                        'model': model,
                        'count': count,
                        'filter_field': model_config['filter_field'],
                        'priority': model_config['priority']
                    })
                    analysis['total_records'] += count
                    
                    self.stdout.write(
                        f'   📄 {model_config["name"]}: {count} registros'
                    )
                else:
                    self.stdout.write(
                        f'   ✓ {model_config["name"]}: sin registros'
                    )
                    
            except (ImportError, AttributeError):
                self.stdout.write(
                    f'   ⚠️  {model_config["name"]}: modelo no disponible'
                )
                
        return analysis

    def _show_deletion_plan(self, analysis):
        """Mostrar plan detallado de eliminación"""
        self.stdout.write('\n📋 PLAN DE ELIMINACIÓN:')
        self.stdout.write('=' * 60)
        
        if not analysis['models']:
            self.stdout.write(
                self.style.SUCCESS('✅ No hay transacciones para eliminar')
            )
            return
            
        # Ordenar por prioridad (eliminar dependientes primero)
        sorted_models = sorted(
            analysis['models'], 
            key=lambda x: -x['priority']  # Mayor prioridad primero
        )
        
        for i, model_info in enumerate(sorted_models, 1):
            self.stdout.write(
                f'{i:2d}. 🗑️  {model_info["name"]}: '
                f'{model_info["count"]} registros'
            )
            
        self.stdout.write('=' * 60)
        self.stdout.write(
            f'📊 TOTAL A ELIMINAR: {analysis["total_records"]} registros'
        )
        
        # Advertencias
        self.stdout.write('\n⚠️  ADVERTENCIAS:')
        self.stdout.write('   • Esta operación NO se puede deshacer')
        self.stdout.write('   • Se eliminarán TODAS las transacciones de GUEBER')
        self.stdout.write('   • Los maestros (clientes, proveedores, productos) se mantienen')
        self.stdout.write('   • El plan de cuentas se mantiene')
        self.stdout.write('   • Los usuarios y permisos se mantienen')

    def _get_confirmations(self):
        """Obtener confirmaciones del usuario"""
        if self.dry_run:
            return True
            
        if not self.confirm:
            self.stdout.write('\n❌ Debe usar --confirm para proceder')
            self.stdout.write('   Ejemplo: python manage.py reset_gueber_transactions --confirm')
            return False
            
        return True

    def _create_backup(self, company, analysis):
        """Crear backup de los datos a eliminar"""
        self.stdout.write('\n💾 Creando backup...')
        
        backup_dir = f'backups/gueber_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        os.makedirs(backup_dir, exist_ok=True)
        
        for model_info in analysis['models']:
            model = model_info['model']
            filter_kwargs = {model_info['filter_field']: company}
            
            # Exportar a JSON
            records = list(model.objects.filter(**filter_kwargs).values())
            
            backup_file = f'{backup_dir}/{model._meta.label_lower}.json'
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2, default=str, ensure_ascii=False)
                
            self.stdout.write(f'   💾 {model_info["name"]}: {backup_file}')
            
        self.stdout.write(
            self.style.SUCCESS(f'✅ Backup creado en: {backup_dir}')
        )

    def _execute_deletion(self, company, analysis):
        """Ejecutar eliminación con transacción"""
        self.stdout.write('\n🗑️  Ejecutando eliminación...')
        
        if not analysis['models']:
            self.stdout.write(
                self.style.SUCCESS('✅ No hay registros para eliminar')
            )
            return
            
        with transaction.atomic():
            # Eliminar en orden de dependencias (prioridad descendente)
            sorted_models = sorted(
                analysis['models'],
                key=lambda x: -x['priority']
            )
            
            deleted_counts = {}
            
            for model_info in sorted_models:
                model = model_info['model']
                filter_kwargs = {model_info['filter_field']: company}
                
                # Eliminar registros
                queryset = model.objects.filter(**filter_kwargs)
                count, details = queryset.delete()
                
                deleted_counts[model_info['name']] = count
                
                self.stdout.write(
                    f'   ✅ {model_info["name"]}: {count} eliminados'
                )
                
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n🎉 Eliminación completada exitosamente'
                )
            )

    def _final_report(self, company):
        """Generar reporte final"""
        self.stdout.write('\n📋 REPORTE FINAL:')
        self.stdout.write('=' * 50)
        
        # Verificar que no quedan transacciones
        final_analysis = self._analyze_data(company)
        
        if final_analysis['total_records'] == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ ÉXITO: No quedan transacciones en {company.trade_name}'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  ATENCIÓN: Quedan {final_analysis["total_records"]} registros'
                )
            )
            
        self.stdout.write('=' * 50)
        self.stdout.write(f'🕐 Completado: {timezone.now()}')
        
        if not self.dry_run:
            self.stdout.write(
                '\n💡 La empresa GUEBER está lista para operaciones nuevas'
            )