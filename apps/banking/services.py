"""
Servicio de Integración Bancaria
Manejo cuidadoso de la creación de movimientos bancarios desde facturas
"""

from decimal import Decimal
from django.utils import timezone
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class BankingIntegrationService:
    """
    Servicio para integrar movimientos bancarios con facturas
    Diseño defensivo para no afectar funcionalidades existentes
    """
    
    @classmethod
    def create_bank_transaction_from_invoice(cls, invoice, journal_entry):
        """
        Crea movimiento bancario automáticamente desde factura
        
        Args:
            invoice: Instancia de Invoice
            journal_entry: Instancia de JournalEntry ya creado
            
        Returns:
            BankTransaction creado o None si no aplica
            
        Raises:
            No debe lanzar excepciones que interrumpan el flujo principal
        """
        try:
            # Importación tardía para evitar dependencias circulares
            from apps.banking.models import BankAccount, BankTransaction
            
            # Validación 1: Verificar que es transferencia
            if not cls._is_bank_transfer(invoice):
                logger.info(f"Factura {invoice.id} no es transferencia bancaria - no se crea BankTransaction")
                return None
            
            # Validación 2: Verificar que hay cuenta seleccionada
            if not invoice.account:
                logger.warning(f"Factura {invoice.id} sin cuenta contable - no se puede crear BankTransaction")
                return None
            
            # Validación 3: Buscar BankAccount vinculado
            try:
                bank_account = BankAccount.objects.get(
                    chart_account=invoice.account,
                    is_active=True
                )
            except BankAccount.DoesNotExist:
                logger.info(f"Cuenta contable {invoice.account.code} sin BankAccount vinculado - no se crea movimiento")
                return None
            except BankAccount.MultipleObjectsReturned:
                logger.error(f"Múltiples BankAccounts para cuenta {invoice.account.code} - usando el primero")
                bank_account = BankAccount.objects.filter(
                    chart_account=invoice.account,
                    is_active=True
                ).first()
            
            # Validación 4: Verificar que no existe ya una transacción para esta factura
            reference = f"FAC-{invoice.id}"
            existing_transaction = BankTransaction.objects.filter(
                reference=reference,
                bank_account=bank_account
            ).first()
            
            if existing_transaction:
                logger.warning(f"Ya existe BankTransaction {existing_transaction.id} para factura {invoice.id}")
                return existing_transaction
            
            # Calcular monto neto (después de retenciones si aplica)
            net_amount = cls._calculate_net_amount(invoice)
            
            # Crear descripción detallada
            description = cls._build_transaction_description(invoice)
            
            # Crear movimiento bancario con transacción para atomicidad
            with transaction.atomic():
                bank_transaction = BankTransaction.objects.create(
                    bank_account=bank_account,
                    transaction_date=invoice.date,
                    value_date=invoice.date,  # Misma fecha por defecto
                    transaction_type='credit',  # Ingreso al banco por venta
                    amount=net_amount,
                    description=description,
                    reference=reference,
                    journal_entry=journal_entry,
                    is_reconciled=False  # Pendiente de conciliación
                )
            
            logger.info(f"✅ BankTransaction {bank_transaction.id} creado para factura {invoice.id}")
            return bank_transaction
            
        except ImportError:
            logger.warning("Módulo banking no disponible - no se puede crear BankTransaction")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al crear BankTransaction para factura {invoice.id}: {str(e)}")
            # No re-lanzar la excepción para no interrumpir el flujo principal
            return None
    
    @classmethod
    def _is_bank_transfer(cls, invoice):
        """Verifica si la factura es pago por transferencia bancaria"""
        if not invoice.payment_form:
            return False
        
        payment_name = invoice.payment_form.name.upper()
        return 'TRANSFERENCIA' in payment_name or 'TRANSFER' in payment_name
    
    @classmethod
    def _calculate_net_amount(cls, invoice):
        """
        Calcula el monto neto que ingresa al banco
        Considera retenciones si el cliente es agente de retención
        """
        base_amount = invoice.total or Decimal('0.00')
        
        # Si el cliente es agente de retención, restar retenciones
        if hasattr(invoice, 'customer') and invoice.customer and invoice.customer.retention_agent:
            try:
                retention_amounts = invoice.customer.calculate_retention_amounts(
                    invoice.subtotal or Decimal('0.00'), 
                    invoice.tax_amount or Decimal('0.00')
                )
                iva_retention = retention_amounts.get('iva_retention', Decimal('0.00'))
                ir_retention = retention_amounts.get('ir_retention', Decimal('0.00'))
                
                net_amount = base_amount - iva_retention - ir_retention
                logger.info(f"Factura {invoice.id}: Total ${base_amount}, Retenciones ${iva_retention + ir_retention}, Neto ${net_amount}")
                return net_amount
            except Exception as e:
                logger.warning(f"Error calculando retenciones para factura {invoice.id}: {str(e)}")
        
        return base_amount
    
    @classmethod
    def _build_transaction_description(cls, invoice):
        """Construye descripción detallada del movimiento bancario"""
        base_desc = f"Ingreso por venta - Factura #{invoice.number or invoice.id}"
        
        if invoice.customer:
            customer_name = invoice.customer.trade_name or invoice.customer.legal_name or "Cliente"
            base_desc += f" - {customer_name}"
        
        # Agregar observaciones de transferencia si existen
        if hasattr(invoice, 'bank_observations') and invoice.bank_observations:
            # Limitar longitud para no exceder límites de campo
            obs_preview = invoice.bank_observations[:100]
            if len(invoice.bank_observations) > 100:
                obs_preview += "..."
            base_desc += f" - {obs_preview}"
        
        return base_desc
    
    @classmethod
    def reverse_bank_transaction(cls, invoice):
        """
        Reversa movimiento bancario cuando se anula una factura
        
        Args:
            invoice: Factura anulada
            
        Returns:
            BankTransaction de reversión o None
        """
        try:
            from apps.banking.models import BankTransaction
            
            # Buscar transacción original
            reference = f"FAC-{invoice.id}"
            original_transaction = BankTransaction.objects.filter(
                reference=reference
            ).first()
            
            if not original_transaction:
                logger.info(f"No hay BankTransaction que reversar para factura {invoice.id}")
                return None
            
            # Verificar que no existe ya una reversión
            reverse_reference = f"REV-{reference}"
            existing_reverse = BankTransaction.objects.filter(
                reference=reverse_reference
            ).first()
            
            if existing_reverse:
                logger.warning(f"Ya existe reversión {existing_reverse.id} para factura {invoice.id}")
                return existing_reverse
            
            # Crear transacción de reversión
            with transaction.atomic():
                reverse_transaction = BankTransaction.objects.create(
                    bank_account=original_transaction.bank_account,
                    transaction_date=timezone.now().date(),
                    value_date=timezone.now().date(),
                    transaction_type='debit',  # Salida del banco (reversión)
                    amount=original_transaction.amount,
                    description=f"Reversión - {original_transaction.description}",
                    reference=reverse_reference,
                    journal_entry=None,  # Se vinculará con asiento de reversión si existe
                    is_reconciled=False
                )
            
            logger.info(f"✅ BankTransaction de reversión {reverse_transaction.id} creado para factura {invoice.id}")
            return reverse_transaction
            
        except ImportError:
            logger.warning("Módulo banking no disponible para reversión")
            return None
        except Exception as e:
            logger.error(f"Error al reversar BankTransaction para factura {invoice.id}: {str(e)}")
            return None
    
    @classmethod
    def create_bank_transaction_from_journal_line(cls, journal_line, journal_entry):
        """
        Crear movimiento bancario desde línea de asiento manual contabilizado
        
        Args:
            journal_line: Instancia de JournalEntryLine con account.aux_type='bank'
            journal_entry: Instancia de JournalEntry padre
            
        Returns:
            BankTransaction creado o None si no aplica
        """
        try:
            from apps.banking.models import BankAccount, BankTransaction
            
            # Validación 1: Verificar que es cuenta bancaria
            if not journal_line.account or journal_line.account.aux_type != 'bank':
                logger.info(f"Línea {journal_line.id} no es cuenta bancaria - no se crea BankTransaction")
                return None
            
            # Validación 2: Verificar que hay monto válido
            if journal_line.debit == 0 and journal_line.credit == 0:
                logger.info(f"Línea {journal_line.id} sin monto - no se crea BankTransaction")
                return None
            
            # Validación 3: Buscar BankAccount vinculada
            bank_account = BankAccount.objects.filter(
                chart_account=journal_line.account,
                company=journal_entry.company,
                is_active=True
            ).first()
            
            if not bank_account:
                logger.warning(f"No se encontró BankAccount activa para cuenta {journal_line.account.code}")
                return None
            
            # Validación 4: Verificar que no existe ya un movimiento para esta línea
            existing_reference = f"AST-{journal_entry.number}-L{journal_line.id}"
            existing_transaction = BankTransaction.objects.filter(
                reference=existing_reference,
                bank_account=bank_account
            ).first()
            
            if existing_transaction:
                logger.info(f"Ya existe BankTransaction para línea {journal_line.id}: {existing_transaction.id}")
                return existing_transaction
            
            # Determinar tipo de transacción y monto
            # CORRECCIÓN: Para cuentas bancarias (activo), la lógica contable es:
            # DEBE = aumenta activo = dinero ENTRA al banco = 'credit' bancario
            # HABER = disminuye activo = dinero SALE del banco = 'debit' bancario
            if journal_line.debit > 0:
                transaction_type = 'credit'  # Ingreso al banco (debe contable = ingreso de dinero)
                amount = journal_line.debit
                description_prefix = "Ingreso bancario"
            else:
                transaction_type = 'debit'   # Egreso del banco (haber contable = salida de dinero)
                amount = journal_line.credit
                description_prefix = "Salida bancaria"
            
            # Construir descripción detallada
            description = cls._build_manual_journal_description(
                journal_entry, journal_line, description_prefix
            )
            
            # Crear movimiento bancario
            bank_transaction = BankTransaction.objects.create(
                bank_account=bank_account,
                transaction_date=journal_entry.date,
                value_date=journal_entry.date,
                transaction_type=transaction_type,
                amount=amount,
                description=description,
                reference=existing_reference,  # AST-{number}-L{line_id}
                # Vincular con asiento si el modelo lo permite
                **cls._get_journal_entry_relation(journal_entry),
                is_reconciled=False
            )
            
            logger.info(f"BankTransaction {bank_transaction.id} creado para línea manual {journal_line.id}")
            return bank_transaction
            
        except Exception as e:
            logger.error(f"Error creando BankTransaction para línea manual {journal_line.id}: {e}")
            return None
    
    @classmethod
    def _build_manual_journal_description(cls, journal_entry, journal_line, prefix):
        """Construir descripción detallada para movimiento bancario desde asiento manual"""
        parts = [prefix]
        
        # Agregar descripción del asiento
        if journal_entry.description:
            parts.append(f"- {journal_entry.description}")
        
        # Agregar descripción específica de la línea
        if journal_line.description and journal_line.description != journal_entry.description:
            parts.append(f"- {journal_line.description}")
        
        # Agregar referencia del asiento
        if journal_entry.reference:
            parts.append(f"- Ref: {journal_entry.reference}")
        
        # Agregar origen
        parts.append(f"- Asiento #{journal_entry.number}")
        
        return " ".join(parts)
    
    @classmethod
    def _get_journal_entry_relation(cls, journal_entry):
        """Obtener relación con journal_entry según estructura del modelo BankTransaction"""
        try:
            from apps.banking.models import BankTransaction
            
            # Verificar si el modelo tiene campo journal_entry
            if hasattr(BankTransaction, 'journal_entry'):
                return {'journal_entry': journal_entry}
            else:
                return {}
                
        except Exception:
            return {}