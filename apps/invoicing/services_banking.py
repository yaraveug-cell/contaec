"""
Servicio para integración Banking-Invoicing
Crea movimientos bancarios automáticos cuando se facturan transferencias
"""

from decimal import Decimal
from django.db import transaction
from django.utils import timezone


class BankingInvoiceService:
    """
    Servicio para manejar la integración entre facturas y movimientos bancarios
    """
    
    @classmethod
    def create_bank_transaction_from_invoice(cls, invoice, bank_account_id=None):
        """
        Crear movimiento bancario automático desde factura de venta con transferencia
        
        Args:
            invoice: Instancia de Invoice
            bank_account_id: ID de BankAccount (opcional, se puede inferir)
            
        Returns:
            tuple: (BankTransaction, created: bool)
        """
        try:
            # Verificar si el módulo banking está disponible
            from apps.banking.models import BankAccount, BankTransaction
        except ImportError:
            print("⚠️ Módulo Banking no disponible, saltando creación de BankTransaction")
            return None, False
            
        # Validar que es factura de transferencia
        if not cls._is_transfer_invoice(invoice):
            print(f"ℹ️ Factura {invoice.id} no es transferencia, saltando BankTransaction")
            return None, False
            
        # Verificar si ya existe movimiento bancario para esta factura
        existing_transaction = cls._get_existing_transaction(invoice)
        if existing_transaction:
            print(f"⚠️ Ya existe BankTransaction {existing_transaction.id} para factura {invoice.id}")
            return existing_transaction, False
            
        # Obtener cuenta bancaria
        bank_account = cls._get_bank_account(invoice, bank_account_id)
        if not bank_account:
            print(f"❌ No se pudo determinar cuenta bancaria para factura {invoice.id}")
            return None, False
            
        # Crear movimiento bancario
        try:
            with transaction.atomic():
                bank_transaction = BankTransaction.objects.create(
                    bank_account=bank_account,
                    transaction_date=invoice.date,
                    value_date=invoice.date,  # Por defecto, misma fecha
                    transaction_type='credit',  # Ingreso por venta
                    amount=invoice.total,
                    description=cls._build_transaction_description(invoice),
                    reference=cls._build_transaction_reference(invoice),
                    # Vincular con asiento contable si existe
                    journal_entry=cls._get_related_journal_entry(invoice),
                    is_reconciled=False  # Por defecto no conciliado
                )
                
                print(f"✅ BankTransaction {bank_transaction.id} creado para factura {invoice.id}")
                return bank_transaction, True
                
        except Exception as e:
            print(f"❌ Error creando BankTransaction para factura {invoice.id}: {e}")
            return None, False
    
    @classmethod
    def _is_transfer_invoice(cls, invoice):
        """Verificar si la factura es de transferencia"""
        if not invoice.payment_form:
            return False
        return 'transferencia' in invoice.payment_form.name.lower()
    
    @classmethod
    def _get_existing_transaction(cls, invoice):
        """Buscar movimiento bancario existente para la factura"""
        try:
            from apps.banking.models import BankTransaction
            
            # Buscar por referencia que contenga el ID de la factura
            reference_patterns = [
                f"FAC-{invoice.id}",
                f"Factura {invoice.number}" if invoice.number else None,
                str(invoice.id)
            ]
            
            for pattern in reference_patterns:
                if pattern:
                    transaction_qs = BankTransaction.objects.filter(
                        reference__icontains=pattern,
                        amount=invoice.total
                    )
                    if transaction_qs.exists():
                        return transaction_qs.first()
            
            # Buscar por journal_entry vinculado
            journal_entry = cls._get_related_journal_entry(invoice)
            if journal_entry:
                transaction_qs = BankTransaction.objects.filter(
                    journal_entry=journal_entry
                )
                if transaction_qs.exists():
                    return transaction_qs.first()
                    
        except Exception as e:
            print(f"⚠️ Error buscando BankTransaction existente: {e}")
            
        return None
    
    @classmethod
    def _get_bank_account(cls, invoice, bank_account_id=None):
        """Obtener cuenta bancaria para el movimiento"""
        try:
            from apps.banking.models import BankAccount
            
            # Opción 1: BankAccount específica proporcionada
            if bank_account_id:
                try:
                    return BankAccount.objects.get(
                        id=bank_account_id,
                        company=invoice.company,
                        is_active=True
                    )
                except BankAccount.DoesNotExist:
                    print(f"⚠️ BankAccount {bank_account_id} no encontrada o no activa")
            
            # Opción 2: Inferir desde cuenta contable de la factura
            if invoice.account and hasattr(invoice.account, 'aux_type'):
                if invoice.account.aux_type == 'bank':
                    # Buscar BankAccount que use esta chart_account
                    bank_account_qs = BankAccount.objects.filter(
                        chart_account=invoice.account,
                        company=invoice.company,
                        is_active=True
                    )
                    if bank_account_qs.exists():
                        return bank_account_qs.first()
            
            # Opción 3: Primera cuenta bancaria disponible de la empresa
            bank_account_qs = BankAccount.objects.filter(
                company=invoice.company,
                is_active=True
            ).order_by('id')
            
            if bank_account_qs.exists():
                print(f"ℹ️ Usando primera cuenta bancaria disponible para empresa {invoice.company}")
                return bank_account_qs.first()
                
        except Exception as e:
            print(f"❌ Error obteniendo BankAccount: {e}")
            
        return None
    
    @classmethod
    def _build_transaction_description(cls, invoice):
        """Construir descripción del movimiento bancario"""
        base_desc = f"Venta - Factura {invoice.number or invoice.id}"
        
        if invoice.customer:
            customer_name = invoice.customer.trade_name or invoice.customer.legal_name
            base_desc += f" - {customer_name}"
        
        # Agregar observaciones bancarias si existen (priorizar bank_observations sobre transfer_detail)
        transfer_info = getattr(invoice, 'bank_observations', '') or getattr(invoice, 'transfer_detail', '')
        if transfer_info:
            transfer_detail = transfer_info[:100]  # Limitar longitud
            base_desc += f" - {transfer_detail}"
            
        return base_desc
    
    @classmethod
    def _build_transaction_reference(cls, invoice):
        """Construir referencia del movimiento bancario"""
        if invoice.number:
            return f"FAC-{invoice.number}"
        return f"FAC-{invoice.id}"
    
    @classmethod
    def _get_related_journal_entry(cls, invoice):
        """Obtener asiento contable relacionado con la factura"""
        try:
            from apps.accounting.models import JournalEntry
            
            # Buscar por referencia
            reference_patterns = [
                f"FAC-{invoice.id}",
                f"Factura {invoice.number}" if invoice.number else None
            ]
            
            for pattern in reference_patterns:
                if pattern:
                    journal_qs = JournalEntry.objects.filter(
                        reference__icontains=pattern,
                        company=invoice.company
                    )
                    if journal_qs.exists():
                        return journal_qs.first()
                        
        except Exception as e:
            print(f"⚠️ Error buscando JournalEntry: {e}")
            
        return None
    
    @classmethod
    def reverse_bank_transaction(cls, invoice):
        """Reversar/anular movimiento bancario de una factura anulada"""
        try:
            from apps.banking.models import BankTransaction
            
            # Buscar movimiento bancario existente
            existing_transaction = cls._get_existing_transaction(invoice)
            if not existing_transaction:
                print(f"ℹ️ No hay BankTransaction para reversar en factura {invoice.id}")
                return None, False
            
            # Crear movimiento de reverso
            with transaction.atomic():
                reverse_transaction = BankTransaction.objects.create(
                    bank_account=existing_transaction.bank_account,
                    transaction_date=timezone.now().date(),
                    value_date=timezone.now().date(),
                    transaction_type='debit',  # Salida por anulación
                    amount=existing_transaction.amount,
                    description=f"REVERSO - {existing_transaction.description}",
                    reference=f"REV-{existing_transaction.reference}",
                    journal_entry=None,  # Se vinculará con asiento de reverso si existe
                    is_reconciled=False
                )
                
                print(f"✅ BankTransaction de reverso {reverse_transaction.id} creado")
                return reverse_transaction, True
                
        except Exception as e:
            print(f"❌ Error creando reverso BankTransaction: {e}")
            return None, False
    
    @classmethod
    def sync_bank_transaction_with_journal_entry(cls, invoice, journal_entry):
        """Sincronizar BankTransaction existente con JournalEntry creado"""
        try:
            from apps.banking.models import BankTransaction
            
            existing_transaction = cls._get_existing_transaction(invoice)
            if existing_transaction and not existing_transaction.journal_entry:
                existing_transaction.journal_entry = journal_entry
                existing_transaction.save(update_fields=['journal_entry'])
                print(f"✅ BankTransaction {existing_transaction.id} vinculado con JournalEntry {journal_entry.id}")
                return True
                
        except Exception as e:
            print(f"⚠️ Error sincronizando BankTransaction con JournalEntry: {e}")
            
        return False