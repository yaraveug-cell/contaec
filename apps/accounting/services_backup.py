"""
Servicio para creación automática de asientos                      # Crear asiento con transacción para atomicidad
            with transaction.atomic():
                journal_entry = cls._create_journal_entry_header(invoice)
                cls._create_debit_line(journal_entry, invoice)
                cls._create_credit_lines(journal_entry, invoice)
                
                # NUEVO: Crear líneas de inventario y costo de ventas
                cls._create_inventory_cost_lines(journal_entry, invoice)
                
                # Recalcular totales
                journal_entry.calculate_totals()r asiento con transacción para atomicidad
            with transaction.atomic():
                journal_entry = cls._create_journal_entry_header(invoice)
                cls._create_debit_line(journal_entry, invoice)
                cls._create_credit_lines(journal_entry, invoice)
                
                # NUEVO: Crear líneas de inventario y costo de ventas
                cls._create_inventory_cost_lines(journal_entry, invoice)
                
                # Recalcular totales
                journal_entry.calculate_totals()es desde facturas
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
    def _calculate_iva_breakdown(cls, invoice):
        """Calcula el desglose de IVA por tarifa desde las líneas de factura"""
        iva_breakdown = {15.0: Decimal('0.00'), 5.0: Decimal('0.00'), 0.0: Decimal('0.00')}
        
        for line in invoice.lines.all():
            # Calcular subtotal de la línea
            subtotal_line = (line.quantity * line.unit_price * (Decimal('1') - line.discount/Decimal('100')))
            # Calcular IVA de la línea
            iva_amount = subtotal_line * (line.iva_rate / Decimal('100'))
            
            if line.iva_rate in iva_breakdown:
                iva_breakdown[line.iva_rate] += iva_amount
            else:
                # Si hay una tarifa no contemplada, agregarla
                iva_breakdown[line.iva_rate] = iva_amount
        
        # Limpiar valores cero
        return {rate: amount for rate, amount in iva_breakdown.items() if amount > 0}
    
    @classmethod
    def _get_sales_account(cls, company):
        """Obtiene la cuenta de ventas para la empresa con configuración flexible"""
        # PRIORIDAD 1: Buscar en configuración por defecto de empresa
        try:
            from apps.companies.models import CompanyAccountDefaults
            defaults = CompanyAccountDefaults.objects.select_related('default_sales_account').get(
                company=company
            )
            if defaults.default_sales_account:
                print(f"✅ Cuenta ventas desde configuración por defecto: {defaults.default_sales_account.code}")
                return defaults.default_sales_account
        except CompanyAccountDefaults.DoesNotExist:
            pass
        
        # PRIORIDAD 2: Buscar cuenta con código 4 (fallback)
        account = ChartOfAccounts.objects.filter(
            company=company,
            code__startswith='4',
            accepts_movement=True
        ).first()
        
        if account:
            print(f"✅ Cuenta ventas desde código 4: {account.code}")
            return account
        
        print(f"⚠️ No se encontró cuenta de ventas para empresa {company.id}")
        return None
    
    @classmethod
    def _get_iva_account(cls, company, iva_rate):
        """Obtiene la cuenta de IVA según la tarifa - Primero desde configuración, luego fallback"""
        # Intentar obtener desde configuración de empresa
        try:
            from apps.companies.models import CompanyTaxAccountMapping
            mapping = CompanyTaxAccountMapping.objects.select_related('account').get(
                company=company, 
                tax_rate=iva_rate
            )
            print(f"✅ Cuenta IVA {iva_rate}% desde configuración: {mapping.account.code}")
            return mapping.account
        except CompanyTaxAccountMapping.DoesNotExist:
            print(f"⚠️ No hay configuración específica para IVA {iva_rate}%, usando mapeo por defecto")
        
        # Fallback al mapeo hardcodeado
        account_code = cls.IVA_ACCOUNTS_MAPPING.get(iva_rate)
        if not account_code:
            print(f"❌ No se encontró mapeo para tarifa IVA {iva_rate}%")
            return None
            
        return ChartOfAccounts.objects.filter(
            company=company,
            code=account_code,
            accepts_movement=True
        ).first()
    
    @classmethod
    def _get_iva_retention_receivable_account(cls, company, tax_rate=None):
        """Obtiene la cuenta 'Retención IVA por Cobrar' para ventas con configuración flexible"""
        # PRIORIDAD 1: Buscar en mapeo específico por tarifa de IVA
        if tax_rate is not None:
            try:
                from apps.companies.models import CompanyTaxAccountMapping
                mapping = CompanyTaxAccountMapping.objects.select_related('retention_account').get(
                    company=company,
                    tax_rate=tax_rate,
                    retention_account__isnull=False
                )
                if mapping.retention_account:
                    print(f"✅ Cuenta retención IVA desde mapeo específico {tax_rate}%: {mapping.retention_account.code}")
                    return mapping.retention_account
            except CompanyTaxAccountMapping.DoesNotExist:
                pass
        
        # PRIORIDAD 2: Buscar en configuración por defecto de empresa
        try:
            from apps.companies.models import CompanyAccountDefaults
            defaults = CompanyAccountDefaults.objects.select_related('iva_retention_receivable_account').get(
                company=company
            )
            if defaults.iva_retention_receivable_account:
                print(f"✅ Cuenta retención IVA desde configuración por defecto: {defaults.iva_retention_receivable_account.code}")
                return defaults.iva_retention_receivable_account
        except CompanyAccountDefaults.DoesNotExist:
            pass
        
        # PRIORIDAD 3: Buscar cuenta específica creada anteriormente (GUEBER)
        account = ChartOfAccounts.objects.filter(
            company=company,
            code='1.1.05.05',
            accepts_movement=True
        ).first()
        
        if account:
            print(f"✅ Cuenta retención IVA desde código específico: {account.code}")
            return account
            
        # PRIORIDAD 4: Buscar cuenta con códigos típicos para retención IVA por cobrar
        account_codes = ['1.1.02.06', '1.1.02.06.01', '11020601', '1.1.05.05']
        
        for code in account_codes:
            account = ChartOfAccounts.objects.filter(
                company=company,
                code__icontains=code,
                accepts_movement=True
            ).first()
            if account:
                print(f"✅ Cuenta retención IVA desde código típico {code}: {account.code}")
                return account
        
        # PRIORIDAD 5: Buscar por nombre si no se encuentra por código
        account = ChartOfAccounts.objects.filter(
            company=company,
            name__icontains='retención iva por cobrar',
            accepts_movement=True
        ).first()
        
        if account:
            print(f"✅ Cuenta retención IVA desde nombre: {account.code}")
            return account
        
        print(f"⚠️ No se encontró cuenta de retención IVA por cobrar para empresa {company.id}")
        return None
    
    @classmethod
    def _get_ir_retention_receivable_account(cls, company):
        """Obtiene la cuenta 'Retención IR por Cobrar' para ventas con configuración flexible"""
        # PRIORIDAD 1: Buscar en configuración por defecto de empresa
        try:
            from apps.companies.models import CompanyAccountDefaults
            defaults = CompanyAccountDefaults.objects.select_related('ir_retention_receivable_account').get(
                company=company
            )
            if defaults.ir_retention_receivable_account:
                print(f"✅ Cuenta retención IR desde configuración por defecto: {defaults.ir_retention_receivable_account.code}")
                return defaults.ir_retention_receivable_account
        except CompanyAccountDefaults.DoesNotExist:
            pass
        
        # PRIORIDAD 2: Buscar cuenta específica creada anteriormente (GUEBER)
        account = ChartOfAccounts.objects.filter(
            company=company,
            code='1.1.05.06',
            accepts_movement=True
        ).first()
        
        if account:
            print(f"✅ Cuenta retención IR desde código específico: {account.code}")
            return account
            
        # PRIORIDAD 3: Buscar cuenta con códigos típicos para retención IR por cobrar
        account_codes = ['1.1.02.07', '1.1.02.07.01', '11020701', '1.1.05.06']
        
        for code in account_codes:
            account = ChartOfAccounts.objects.filter(
                company=company,
                code__icontains=code,
                accepts_movement=True
            ).first()
            if account:
                print(f"✅ Cuenta retención IR desde código típico {code}: {account.code}")
                return account
        
        # PRIORIDAD 4: Buscar por nombre si no se encuentra por código
        account = ChartOfAccounts.objects.filter(
            company=company,
            name__icontains='retención renta por cobrar',
            accepts_movement=True
        ).first()
        
        if account:
            print(f"✅ Cuenta retención IR desde nombre: {account.code}")
            return account
        
        print(f"⚠️ No se encontró cuenta de retención IR por cobrar para empresa {company.id}")
        return None
    
    @classmethod
    def _get_main_iva_rate_from_invoice(cls, invoice):
        """Obtiene la tarifa de IVA principal de la factura"""
        # Si hay líneas de factura, usar la tarifa más común
        if hasattr(invoice, 'lines') and invoice.lines.exists():
            rates = invoice.lines.values_list('iva_rate', flat=True)
            # Retornar la tarifa más frecuente
            rate_counts = {}
            for rate in rates:
                rate_counts[float(rate)] = rate_counts.get(float(rate), 0) + 1
            if rate_counts:
                return max(rate_counts, key=rate_counts.get)
        
        # Fallback: calcular desde el total si no hay líneas
        if invoice.tax_amount > 0 and invoice.subtotal > 0:
            calculated_rate = (invoice.tax_amount / invoice.subtotal * 100).quantize(Decimal('0.01'))
            return float(calculated_rate)
        
        # Fallback final: 15% (tarifa más común en Ecuador)
        return 15.0
    
    @classmethod
    def _group_sales_by_account(cls, invoice):
        """
        ESTRATEGIA B: Agrupa subtotales de ventas por cuenta contable inteligente
        
        Returns:
            dict: {ChartOfAccounts: Decimal} - Monto por cuenta de ventas
        """
        sales_by_account = {}
        
        # Procesar cada línea de la factura
        for line in invoice.lines.all():
            try:
                # Calcular subtotal de la línea (sin IVA)
                line_subtotal = line.quantity * line.unit_price
                discount_amount = line_subtotal * (line.discount / 100)
                line_net = line_subtotal - discount_amount
                
                # Obtener cuenta de ventas efectiva del producto  
                sales_account = line.product.get_effective_sales_account()
                
                if sales_account:
                    # Agrupar por cuenta
                    if sales_account in sales_by_account:
                        sales_by_account[sales_account] += line_net
                    else:
                        sales_by_account[sales_account] = line_net
                    
                    print(f"🏷️ Producto {line.product.code} → Cuenta {sales_account.code}: ${line_net}")
                else:
                    print(f"⚠️ Sin cuenta de ventas para producto {line.product.code}")
                    
            except Exception as e:
                print(f"❌ Error procesando línea de producto {line.product.code if line.product else 'N/A'}: {e}")
                # Continuar con siguiente línea sin interrumpir el proceso
                continue
        
        return sales_by_account
    
    @classmethod
    def _get_payment_type_description(cls, payment_method_name):
        """Obtiene descripción del tipo de pago"""
        payment_method_lower = payment_method_name.lower()
        
        if 'efectivo' in payment_method_lower:
            return 'Cobro en efectivo'
        elif 'credito' in payment_method_lower or 'crédito' in payment_method_lower:
            return 'Venta a crédito'
        elif 'transferencia' in payment_method_lower:
            return 'Cobro por transferencia'
        else:
            return f'Cobro {payment_method_name}'
    
    @classmethod
    def reverse_journal_entry(cls, invoice):
        """
        Crea asiento de reversión al anular factura
        
        Retorna: (JournalEntry, bool) - (asiento_reversión, fue_creado)
        """
        try:
            # Buscar asiento original
            original_entry = JournalEntry.objects.filter(
                reference=f"FAC-{invoice.id}",
                company=invoice.company
            ).first()
            
            if not original_entry:
                print(f"⚠️ No se encontró asiento original para factura {invoice.id}")
                return None, False
            
            # Verificar si ya existe reversión
            existing_reversal = JournalEntry.objects.filter(
                reference=f"REV-FAC-{invoice.id}",
                company=invoice.company
            ).first()
            
            if existing_reversal:
                print(f"⚠️ Ya existe reversión para factura {invoice.id}: {existing_reversal.id}")
                return existing_reversal, False
            
            # Crear asiento de reversión
            with transaction.atomic():
                reverse_entry = JournalEntry.objects.create(
                    company=invoice.company,
                    date=timezone.now().date(),
                    reference=f"REV-FAC-{invoice.id}",
                    description=f"Reversión factura #{invoice.number or invoice.id} - {invoice.customer.trade_name or invoice.customer.legal_name}",
                    created_by=invoice.created_by or User.objects.filter(is_superuser=True).first()
                )
                
                # Crear líneas inversas (intercambiar DEBE/HABER)
                for line in original_entry.lines.all():
                    JournalEntryLine.objects.create(
                        journal_entry=reverse_entry,
                        account=line.account,
                        description=f"REV - {line.description}",
                        debit=line.credit,  # Invertir DEBE/HABER
                        credit=line.debit,
                        document_type='REVERSA',
                        document_number=f"REV-{invoice.number or invoice.id}",
                        document_date=timezone.now().date(),
                        auxiliary_code=line.auxiliary_code,
                        auxiliary_name=line.auxiliary_name
                    )
                
                # Recalcular totales
                reverse_entry.calculate_totals()
                
                print(f"✅ Asiento de reversión creado: {reverse_entry.number}")
                return reverse_entry, True
                
        except Exception as e:
            print(f"❌ Error creando reversión para factura {invoice.id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, False
    
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