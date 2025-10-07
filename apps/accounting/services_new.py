"""
Servicio para creación automática de asientos contables desde facturas
Cumple con normativa contable ecuatoriana
"""

from decimal import Decimal
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.accounting.models import JournalEntry, JournalEntryLine, ChartOfAccounts

User = get_user_model()


class AutomaticJournalEntryService:
    """
    Servicio para crear asientos contables automáticos desde facturas
    """
    
    # Mapeo de cuentas IVA por tarifa
    IVA_ACCOUNTS_MAPPING = {
        15.0: '2.1.01.01.03.01',  # IVA COBRADO EN VENTAS 15%
        5.0: '2.1.01.01.03.02',   # IVA COBRADO EN VENTAS 5%
        0.0: None                  # Sin IVA
    }
    
    @classmethod
    def create_journal_entry_from_invoice(cls, invoice):
        """
        Crea asiento contable automático desde una factura
        Solo se ejecuta cuando la factura cambia a estado 'sent'
        
        Retorna: (JournalEntry, bool) - (asiento_creado, fue_creado)
        """
        try:
            # Verificar si ya existe asiento para esta factura
            existing_entry = JournalEntry.objects.filter(
                reference=f"FAC-{invoice.id}",
                company=invoice.company
            ).first()
            
            if existing_entry:
                print(f"⚠️ Ya existe asiento para factura {invoice.id}: {existing_entry.id}")
                return existing_entry, False
            
            # Verificar que la factura tenga datos necesarios
            if not cls._validate_invoice_data(invoice):
                print(f"❌ Datos de factura {invoice.id} incompletos para asiento")
                return None, False
            
            # Crear asiento con transacción para atomicidad
            with transaction.atomic():
                journal_entry = cls._create_journal_entry_header(invoice)
                cls._create_debit_line(journal_entry, invoice)
                cls._create_credit_lines(journal_entry, invoice)
                
                # NUEVO: Crear líneas de inventario y costo de ventas
                cls._create_inventory_cost_lines(journal_entry, invoice)
                
                # Recalcular totales
                journal_entry.calculate_totals()
                
                print(f"✅ Asiento contable creado: {journal_entry.number} para factura {invoice.id}")
                return journal_entry, True
                
        except Exception as e:
            print(f"❌ Error creando asiento para factura {invoice.id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, False
    
    @classmethod
    def _validate_invoice_data(cls, invoice):
        """Valida que la factura tenga todos los datos necesarios"""
        required_fields = [
            invoice.company,
            invoice.customer, 
            invoice.account,
            invoice.payment_form,
            invoice.subtotal,
            invoice.total
        ]
        
        if not all(field is not None for field in required_fields):
            print(f"❌ Campos requeridos faltantes en factura {invoice.id}")
            return False
            
        if invoice.total <= 0:
            print(f"❌ Total de factura {invoice.id} debe ser mayor a 0")
            return False
            
        return True
    
    @classmethod
    def _create_journal_entry_header(cls, invoice):
        """Crea el encabezado del asiento contable"""
        # Descripción base del asiento
        base_description = f"Venta factura #{invoice.number or invoice.id} - {invoice.customer.trade_name or invoice.customer.legal_name}"
        
        # Agregar detalle de transferencia si existe
        if (invoice.payment_form and 
            hasattr(invoice.payment_form, 'name') and
            'TRANSFERENCIA' in invoice.payment_form.name.upper() and 
            invoice.transfer_detail):
            description = f"{base_description} - Transferencia: {invoice.transfer_detail}"
        else:
            description = base_description
        
        return JournalEntry.objects.create(
            company=invoice.company,
            date=invoice.date,
            reference=f"FAC-{invoice.id}",
            description=description,
            created_by=invoice.created_by or User.objects.filter(is_superuser=True).first()
        )
    
    @classmethod
    def _create_debit_line(cls, journal_entry, invoice):
        """Crea las líneas DEBE según forma de pago y retenciones del cliente"""
        # La cuenta DEBE principal es la cuenta seleccionada en la factura
        # (Caja, Banco, o Cuenta por Cobrar según forma de pago)
        debit_account = invoice.account
        
        # Determinar descripción según tipo de cuenta
        payment_type = cls._get_payment_type_description(invoice.payment_form.name)
        
        # Calcular monto neto después de retenciones (si aplica)
        net_amount = invoice.total
        retention_amounts = {'iva_retention': Decimal('0.00'), 'ir_retention': Decimal('0.00')}
        
        if invoice.customer.retention_agent:
            # Calcular retenciones
            retention_amounts = invoice.customer.calculate_retention_amounts(
                invoice.subtotal, 
                invoice.tax_amount
            )
            net_amount = invoice.total - retention_amounts['iva_retention'] - retention_amounts['ir_retention']
        
        # Crear línea DEBE principal (monto neto)
        JournalEntryLine.objects.create(
            journal_entry=journal_entry,
            account=debit_account,
            description=f"{payment_type} - Factura {invoice.number or invoice.id}",
            debit=net_amount,
            credit=Decimal('0.00'),
            document_type='FACTURA',
            document_number=invoice.number or str(invoice.id),
            document_date=invoice.date,
            auxiliary_code=invoice.customer.identification,
            auxiliary_name=invoice.customer.trade_name or invoice.customer.legal_name
        )
        
        print(f"📝 Línea DEBE principal: {debit_account.code} - ${net_amount}")
        
        # Crear líneas DEBE de retenciones (si aplica)
        if invoice.customer.retention_agent:
            cls._create_retention_debit_lines(journal_entry, invoice, retention_amounts)
    
    @classmethod
    def _create_retention_debit_lines(cls, journal_entry, invoice, retention_amounts):
        """Crea las líneas DEBE para retenciones del cliente agente de retención"""
        # Línea DEBE: Retención IVA por Cobrar
        if retention_amounts['iva_retention'] > 0:
            # Obtener la tarifa de IVA principal de la factura para buscar cuenta específica
            main_iva_rate = cls._get_main_iva_rate_from_invoice(invoice)
            iva_retention_account = cls._get_iva_retention_receivable_account(invoice.company, main_iva_rate)
            if iva_retention_account:
                rates = invoice.customer.get_retention_rates()
                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=iva_retention_account,
                    description=f"Retención IVA {rates['iva_retention']}% por cobrar - {invoice.customer.trade_name}",
                    debit=retention_amounts['iva_retention'],
                    credit=Decimal('0.00'),
                    document_type='RETENCION',
                    document_number=invoice.number or str(invoice.id),
                    document_date=invoice.date,
                    auxiliary_code=invoice.customer.identification,
                    auxiliary_name=invoice.customer.trade_name or invoice.customer.legal_name
                )
                print(f"📝 Línea DEBE Retención IVA: {iva_retention_account.code} - ${retention_amounts['iva_retention']}")
            else:
                print(f"⚠️ No se encontró cuenta 'Retención IVA por Cobrar' para empresa {invoice.company.id}")
        
        # Línea DEBE: Retención IR por Cobrar  
        if retention_amounts['ir_retention'] > 0:
            ir_retention_account = cls._get_ir_retention_receivable_account(invoice.company)
            if ir_retention_account:
                rates = invoice.customer.get_retention_rates()
                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=ir_retention_account,
                    description=f"Retención IR {rates['ir_retention']}% por cobrar - {invoice.customer.trade_name}",
                    debit=retention_amounts['ir_retention'],
                    credit=Decimal('0.00'),
                    document_type='RETENCION',
                    document_number=invoice.number or str(invoice.id),
                    document_date=invoice.date,
                    auxiliary_code=invoice.customer.identification,
                    auxiliary_name=invoice.customer.trade_name or invoice.customer.legal_name
                )
                print(f"📝 Línea DEBE Retención IR: {ir_retention_account.code} - ${retention_amounts['ir_retention']}")
            else:
                print(f"⚠️ No se encontró cuenta 'Retención IR por Cobrar' para empresa {invoice.company.id}")
    
    @classmethod
    def _create_credit_lines(cls, journal_entry, invoice):
        """
        Crea las líneas HABER (Ventas + IVA) con soporte ESTRATEGIA B
        COMPATIBLE: Mantiene funcionalidad existente + mejoras inteligentes
        """
        # Calcular totales por tarifa de IVA (sin cambios)
        iva_breakdown = cls._calculate_iva_breakdown(invoice)
        
        # ========================================
        # ESTRATEGIA B: VENTAS POR CUENTA INTELIGENTE
        # ========================================
        
        # Agrupar subtotales por cuenta de ventas según productos
        sales_by_account = cls._group_sales_by_account(invoice)
        
        if sales_by_account:
            # NUEVO: Crear una línea HABER por cada cuenta de ventas diferente
            for account, amount in sales_by_account.items():
                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=account,
                    description=f"Ventas {account.name} - Factura {invoice.number or invoice.id}",
                    debit=Decimal('0.00'),
                    credit=amount,
                    document_type='FACTURA',
                    document_number=invoice.number or str(invoice.id),
                    document_date=invoice.date,
                    auxiliary_code=invoice.customer.identification,
                    auxiliary_name=invoice.customer.trade_name or invoice.customer.legal_name
                )
                print(f"📝 Línea HABER Ventas ({account.code}): ${amount}")
        else:
            # FALLBACK: Comportamiento original si no hay productos o configuración
            sales_account = cls._get_sales_account(invoice.company)
            if sales_account:
                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=sales_account,
                    description=f"Ventas - Factura {invoice.number or invoice.id}",
                    debit=Decimal('0.00'),
                    credit=invoice.subtotal,
                    document_type='FACTURA',
                    document_number=invoice.number or str(invoice.id),
                    document_date=invoice.date,
                    auxiliary_code=invoice.customer.identification,
                    auxiliary_name=invoice.customer.trade_name or invoice.customer.legal_name
                )
                print(f"📝 Línea HABER Ventas (fallback): {sales_account.code} - ${invoice.subtotal}")
            else:
                print(f"⚠️ No se encontró cuenta de ventas para empresa {invoice.company.id}")
        
        # ========================================  
        # IVA: Mejorado para manejar facturas sin líneas
        # ========================================
        
        # Si no hay desglose de IVA desde líneas, usar el IVA total de la factura
        if not iva_breakdown and invoice.tax_amount > 0:
            main_iva_rate = cls._get_main_iva_rate_from_invoice(invoice)
            iva_breakdown = {main_iva_rate: invoice.tax_amount}
            print(f"📝 IVA calculado desde total de factura: {main_iva_rate}% = ${invoice.tax_amount}")
        
        for iva_rate, iva_amount in iva_breakdown.items():
            if iva_amount > 0 and iva_rate > 0:
                iva_account = cls._get_iva_account(invoice.company, iva_rate)
                if iva_account:
                    JournalEntryLine.objects.create(
                        journal_entry=journal_entry,
                        account=iva_account,
                        description=f"IVA {iva_rate}% - Factura {invoice.number or invoice.id}",
                        debit=Decimal('0.00'),
                        credit=iva_amount,
                        document_type='FACTURA',
                        document_number=invoice.number or str(invoice.id),
                        document_date=invoice.date,
                        auxiliary_code=invoice.customer.identification,
                        auxiliary_name=invoice.customer.trade_name or invoice.customer.legal_name
                    )
                    print(f"📝 Línea HABER IVA {iva_rate}%: {iva_account.code} - ${iva_amount}")
                else:
                    print(f"⚠️ No se encontró cuenta IVA {iva_rate}% para empresa {invoice.company.id}")
    
    @classmethod
    def _create_inventory_cost_lines(cls, journal_entry, invoice):
        """Crea líneas de asiento para costo de ventas e inventario"""
        # Solo procesar facturas con productos que manejan inventario
        inventory_lines = invoice.lines.filter(product__manages_inventory=True)
        
        if not inventory_lines.exists():
            print(f"ℹ️ Factura {invoice.id} sin productos de inventario - omitiendo líneas de costo")
            return
        
        # Calcular costo total por categoría/cuenta
        cost_by_account = {}
        inventory_by_account = {}
        
        for line in inventory_lines:
            product = line.product
            line_cost = line.quantity * product.cost_price
            
            if line_cost <= 0:
                print(f"⚠️ Producto {product.code} sin costo configurado - omitiendo")
                continue
            
            # Obtener cuentas efectivas del producto
            cost_account = product.get_effective_cost_account()
            inventory_account = product.get_effective_inventory_account()
            
            if not cost_account or not cost_account.accepts_movement:
                print(f"❌ Cuenta de costo no válida para producto {product.code}")
                continue
                
            if not inventory_account or not inventory_account.accepts_movement:
                print(f"❌ Cuenta de inventario no válida para producto {product.code}")
                continue
            
            # Acumular por cuenta
            if cost_account not in cost_by_account:
                cost_by_account[cost_account] = Decimal('0.00')
            cost_by_account[cost_account] += line_cost
            
            if inventory_account not in inventory_by_account:
                inventory_by_account[inventory_account] = Decimal('0.00')
            inventory_by_account[inventory_account] += line_cost
            
            print(f"📦 {product.code}: Qty={line.quantity} x Costo=${product.cost_price} = ${line_cost}")
        
        # Crear líneas DEBE para costo de ventas
        for cost_account, total_cost in cost_by_account.items():
            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=cost_account,
                description=f"Costo mercadería vendida - Factura {invoice.number or invoice.id}",
                debit=total_cost,
                credit=Decimal('0.00'),
                document_type='FACTURA',
                document_number=invoice.number or str(invoice.id),
                document_date=invoice.date,
                auxiliary_code=invoice.customer.identification,
                auxiliary_name=invoice.customer.trade_name or invoice.customer.legal_name
            )
            print(f"📝 Línea DEBE Costo: {cost_account.code} - ${total_cost}")
        
        # Crear líneas HABER para reducción de inventario
        for inventory_account, total_inventory in inventory_by_account.items():
            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=inventory_account,
                description=f"Reducción inventario por venta - Factura {invoice.number or invoice.id}",
                debit=Decimal('0.00'),
                credit=total_inventory,
                document_type='FACTURA',
                document_number=invoice.number or str(invoice.id),
                document_date=invoice.date,
                auxiliary_code=invoice.customer.identification,
                auxiliary_name=invoice.customer.trade_name or invoice.customer.legal_name
            )
            print(f"📝 Línea HABER Inventario: {inventory_account.code} - ${total_inventory}")
        
        total_cost_amount = sum(cost_by_account.values())
        total_inventory_amount = sum(inventory_by_account.values())
        
        print(f"💰 Total costo registrado: ${total_cost_amount}")
        print(f"📦 Total inventario reducido: ${total_inventory_amount}")
        
        if total_cost_amount != total_inventory_amount:
            print(f"⚠️ Advertencia: Costo ({total_cost_amount}) != Inventario ({total_inventory_amount})")
    
    # [CONTINUARÁ CON EL RESTO DE MÉTODOS...]