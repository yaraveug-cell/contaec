from django.db import models, transaction
from decimal import Decimal
from django.utils import timezone
from apps.core.models import BaseModel
from apps.companies.models import Company
from django.contrib.auth import get_user_model

User = get_user_model()


class Supplier(BaseModel):
    """Proveedores del sistema"""
    NATURAL = 'natural'
    JURIDICAL = 'juridical'
    
    SUPPLIER_TYPE_CHOICES = [
        (NATURAL, 'Persona Natural'),
        (JURIDICAL, 'Persona Jurídica'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa')
    supplier_type = models.CharField(
        max_length=10, 
        choices=SUPPLIER_TYPE_CHOICES, 
        verbose_name='Tipo de proveedor'
    )
    
    # Información básica
    identification = models.CharField(max_length=13, verbose_name='Cédula/RUC')
    trade_name = models.CharField(max_length=200, verbose_name='Nombre comercial')
    legal_name = models.CharField(max_length=300, blank=True, verbose_name='Razón social')
    
    # Contacto
    email = models.EmailField(blank=True, verbose_name='Correo electrónico')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    address = models.TextField(verbose_name='Dirección')
    
    # Configuración comercial
    credit_limit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Límite de crédito'
    )
    payment_terms = models.IntegerField(default=30, verbose_name='Días de pago')
    
    # Configuración de retenciones ecuatorianas
    retention_agent = models.BooleanField(
        default=True,
        verbose_name='Es agente de retención',
        help_text='Si la empresa debe realizar retenciones a este proveedor'
    )
    iva_retention_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Porcentaje retención IVA (%)',
        help_text='Porcentaje de retención de IVA según tipo de proveedor'
    )
    ir_retention_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Porcentaje retención IR (%)',
        help_text='Porcentaje de retención de Impuesto a la Renta'
    )
    
    # Clasificación SRI para retenciones automáticas
    SRI_CLASSIFICATION_CHOICES = [
        ('persona_natural_no_obligada', 'Persona Natural No Obligada'),
        ('persona_natural_obligada', 'Persona Natural Obligada'),
        ('sociedad', 'Sociedad'),
        ('institucion_publica', 'Institución Pública'),
        ('regimen_rimpe', 'Régimen RIMPE'),
    ]
    sri_classification = models.CharField(
        max_length=30,
        choices=SRI_CLASSIFICATION_CHOICES,
        default='sociedad',
        verbose_name='Clasificación SRI',
        help_text='Clasificación del proveedor para cálculo automático de retenciones'
    )
    
    # Cuentas contables por defecto
    payable_account = models.ForeignKey(
        'accounting.ChartOfAccounts',
        on_delete=models.PROTECT,
        related_name='supplier_payable_accounts',
        null=True,
        blank=True,
        verbose_name='Cuenta por pagar'
    )
    expense_account = models.ForeignKey(
        'accounting.ChartOfAccounts',
        on_delete=models.PROTECT,
        related_name='supplier_expense_accounts',
        null=True,
        blank=True,
        verbose_name='Cuenta de gastos'
    )
    
    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        unique_together = ['company', 'identification']
        ordering = ['trade_name']
    
    def __str__(self):
        return f"{self.identification} - {self.trade_name}"
    
    def get_automatic_retention_rates(self):
        """
        Calcula automáticamente las tasas de retención según clasificación SRI
        Basado en normativas ecuatorianas vigentes
        """
        rates = {
            'iva_retention': Decimal('0.00'),
            'ir_retention': Decimal('0.00')
        }
        
        if not self.retention_agent:
            return rates
        
        # Tasas de retención IVA según clasificación SRI
        iva_rates = {
            'persona_natural_no_obligada': Decimal('30.00'),
            'persona_natural_obligada': Decimal('30.00'),
            'sociedad': Decimal('70.00'),
            'institucion_publica': Decimal('100.00'),
            'regimen_rimpe': Decimal('30.00'),
        }
        
        # Tasas de retención IR por defecto (pueden ser ajustadas manualmente)
        ir_rates = {
            'persona_natural_no_obligada': Decimal('2.00'),
            'persona_natural_obligada': Decimal('2.00'),
            'sociedad': Decimal('1.00'),
            'institucion_publica': Decimal('1.00'),
            'regimen_rimpe': Decimal('1.00'),
        }
        
        # Usar tasas personalizadas si están configuradas, sino usar automáticas
        rates['iva_retention'] = (
            self.iva_retention_percentage if self.iva_retention_percentage > 0
            else iva_rates.get(self.sri_classification, Decimal('0.00'))
        )
        
        rates['ir_retention'] = (
            self.ir_retention_percentage if self.ir_retention_percentage > 0
            else ir_rates.get(self.sri_classification, Decimal('0.00'))
        )
        
        return rates
    
    def calculate_retentions(self, subtotal, iva_amount):
        """
        Calcula los montos de retención para una compra específica
        
        Args:
            subtotal (Decimal): Monto base sin IVA
            iva_amount (Decimal): Monto del IVA
            
        Returns:
            dict: Montos calculados de retenciones
        """
        if not self.retention_agent:
            return {
                'iva_retention_amount': Decimal('0.00'),
                'ir_retention_amount': Decimal('0.00'),
                'net_payable': subtotal + iva_amount
            }
        
        rates = self.get_automatic_retention_rates()
        
        # Calcular retenciones
        iva_retention = iva_amount * (rates['iva_retention'] / Decimal('100'))
        ir_retention = subtotal * (rates['ir_retention'] / Decimal('100'))
        
        # Monto neto a pagar (total menos retenciones)
        total_amount = subtotal + iva_amount
        total_retentions = iva_retention + ir_retention
        net_payable = total_amount - total_retentions
        
        return {
            'iva_retention_rate': rates['iva_retention'],
            'ir_retention_rate': rates['ir_retention'],
            'iva_retention_amount': iva_retention.quantize(Decimal('0.01')),
            'ir_retention_amount': ir_retention.quantize(Decimal('0.01')),
            'total_retentions': total_retentions.quantize(Decimal('0.01')),
            'net_payable': net_payable.quantize(Decimal('0.01'))
        }


class PurchaseInvoice(BaseModel):
    """Facturas de compra de proveedores"""
    DRAFT = 'draft'
    RECEIVED = 'received'
    VALIDATED = 'validated'
    PAID = 'paid'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (DRAFT, 'Borrador'),
        (RECEIVED, 'Recibida'),
        (VALIDATED, 'Validada'),
        (PAID, 'Pagada'),
        (CANCELLED, 'Anulada'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name='Proveedor')
    
    # Numeración
    supplier_invoice_number = models.CharField(max_length=20, verbose_name='Número de factura del proveedor')
    internal_number = models.CharField(max_length=20, blank=True, verbose_name='Número interno')
    date = models.DateField(default=timezone.now, verbose_name='Fecha')
    due_date = models.DateField(null=True, blank=True, verbose_name='Fecha de vencimiento')
    
    # Forma de pago
    payment_form = models.ForeignKey(
        'companies.PaymentMethod',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Forma de Pago'
    )
    
    # Cuentas contables
    payable_account = models.ForeignKey(
        'accounting.ChartOfAccounts',
        on_delete=models.PROTECT,
        related_name='purchase_payable_accounts',
        null=True,
        blank=True,
        verbose_name='Cuenta por pagar'
    )
    
    # Montos
    subtotal = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Subtotal'
    )
    tax_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Impuestos'
    )
    total = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Total'
    )
    
    # Estado
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default=DRAFT,
        verbose_name='Estado'
    )
    
    # ========================================
    # RETENCIONES ECUATORIANAS - FASE 1
    # ========================================
    
    # Retención de IVA
    iva_retention_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='% Retención IVA',
        help_text='Porcentaje de retención aplicado al IVA'
    )
    iva_retention_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto Retención IVA'
    )
    
    # Retención de Impuesto a la Renta
    ir_retention_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='% Retención IR',
        help_text='Porcentaje de retención de Impuesto a la Renta'
    )
    ir_retention_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto Retención IR'
    )
    
    # Total retenciones y neto a pagar
    total_retentions = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Retenciones'
    )
    net_payable = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Neto a Pagar',
        help_text='Total de la factura menos las retenciones aplicadas'
    )
    
    # Comprobante de retención
    retention_voucher_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Núm. Comprobante Retención',
        help_text='Número del comprobante de retención generado'
    )
    retention_voucher_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Comprobante Retención'
    )
    
    # Usuario
    received_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        verbose_name='Recibido por'
    )
    
    # Información adicional
    reference = models.CharField(max_length=100, blank=True, verbose_name='Referencia')
    notes = models.TextField(blank=True, verbose_name='Observaciones')
    
    class Meta:
        verbose_name = 'Factura de Compra'
        verbose_name_plural = 'Facturas de Compra'
        unique_together = ['company', 'supplier', 'supplier_invoice_number']
        ordering = ['-date', '-supplier_invoice_number']
    
    def __str__(self):
        return f"{self.supplier_invoice_number} - {self.supplier.trade_name}"
    
    def generate_internal_number(self):
        """
        Genera número interno automático para la factura de compra
        MEJORADO: Sincroniza con facturas existentes para evitar duplicados y saltos
        """
        from apps.companies.models import CompanySettings
        from django.db import transaction
        
        with transaction.atomic():
            # Obtener o crear configuración de la empresa
            settings, created = CompanySettings.objects.get_or_create(
                company=self.company,
                defaults={
                    'invoice_sequential': 1,
                    'purchase_invoice_sequential': 1,
                    'credit_note_sequential': 1,
                    'debit_note_sequential': 1,
                    'withholding_sequential': 1,
                }
            )
            
            # MEJORA: Verificar si existe la última factura real para sincronizar
            last_invoice = PurchaseInvoice.objects.filter(
                company=self.company,
                internal_number__startswith='FC-001-'
            ).exclude(pk=self.pk if self.pk else None).order_by('-internal_number').first()
            
            if last_invoice:
                # Extraer número de la última factura: FC-001-000005 -> 5
                try:
                    last_number_str = last_invoice.internal_number.split('-')[-1]
                    last_number = int(last_number_str)
                    
                    # SINCRONIZACIÓN: Si hay desfase, corregir el secuencial
                    expected_next = last_number + 1
                    if settings.purchase_invoice_sequential != expected_next:
                        settings.purchase_invoice_sequential = expected_next
                        settings.save()
                        
                except (ValueError, IndexError):
                    # Si no se puede parsear, usar el secuencial actual
                    pass
            
            # Generar próximo número
            sequential = str(settings.purchase_invoice_sequential).zfill(6)
            internal_number = f"FC-001-{sequential}"
            
            # VERIFICACIÓN: Asegurar que no existe duplicado
            while PurchaseInvoice.objects.filter(
                company=self.company,
                internal_number=internal_number
            ).exclude(pk=self.pk if self.pk else None).exists():
                settings.purchase_invoice_sequential += 1
                sequential = str(settings.purchase_invoice_sequential).zfill(6)
                internal_number = f"FC-001-{sequential}"
            
            # Incrementar secuencial para la próxima factura
            settings.purchase_invoice_sequential += 1
            settings.save()
            
            return internal_number
    
    def save(self, *args, **kwargs):
        """
        Generar número interno automático si no existe
        MEJORADO: Incluye generación automática de comprobantes de retención
        """
        if not self.internal_number:
            with transaction.atomic():
                self.internal_number = self.generate_internal_number()
        
        # Calcular fecha de vencimiento si no se especifica
        if not self.due_date and self.supplier.payment_terms:
            from datetime import timedelta
            self.due_date = self.date + timedelta(days=self.supplier.payment_terms)
        
        # Establecer cuentas por defecto del proveedor
        if not self.payable_account and self.supplier.payable_account:
            self.payable_account = self.supplier.payable_account
        
        super().save(*args, **kwargs)
        
        # Recalcular totales después de guardar (incluye retenciones)
        self.calculate_totals()
        
        # NUEVO FASE 3: Generar comprobante de retención automáticamente
        if (self.status in ['validated', 'paid'] and 
            self.total_retentions > 0 and 
            not self.retention_voucher_number):
            
            self.generate_retention_voucher()
    
    def calculate_totals(self):
        """
        Calcular subtotal, impuestos, retenciones y total de la factura de compra
        COMPATIBLE: Mantiene funcionalidad original + nuevas retenciones
        """
        lines = self.lines.all()
        
        subtotal = Decimal('0.00')
        tax_amount = Decimal('0.00')
        
        for line in lines:
            line_subtotal = line.quantity * line.unit_cost
            discount_amount = line_subtotal * (line.discount / 100)
            line_net = line_subtotal - discount_amount
            
            subtotal += line_net
            
            # Calcular IVA usando la tasa de la línea
            line_tax = line_net * (line.iva_rate / 100)
            tax_amount += line_tax
        
        # NUEVO: Calcular retenciones automáticamente si aplica
        retentions_data = {'iva_retention_amount': Decimal('0.00'), 'ir_retention_amount': Decimal('0.00')}
        
        if (self.supplier and 
            self.supplier.retention_agent and 
            subtotal > 0):
            
            # Usar porcentajes específicos de la factura o automáticos del proveedor
            if self.iva_retention_percentage > 0 or self.ir_retention_percentage > 0:
                # Cálculo manual con porcentajes específicos
                iva_ret_amount = tax_amount * (self.iva_retention_percentage / Decimal('100'))
                ir_ret_amount = subtotal * (self.ir_retention_percentage / Decimal('100'))
            else:
                # Cálculo automático desde configuración del proveedor
                retentions_data = self.supplier.calculate_retentions(subtotal, tax_amount)
                iva_ret_amount = retentions_data['iva_retention_amount']
                ir_ret_amount = retentions_data['ir_retention_amount']
                
                # Actualizar porcentajes automáticos para referencia
                if 'iva_retention_rate' in retentions_data:
                    self.iva_retention_percentage = retentions_data['iva_retention_rate']
                if 'ir_retention_rate' in retentions_data:
                    self.ir_retention_percentage = retentions_data['ir_retention_rate']
            
            retentions_data['iva_retention_amount'] = iva_ret_amount.quantize(Decimal('0.01'))
            retentions_data['ir_retention_amount'] = ir_ret_amount.quantize(Decimal('0.01'))
        
        # Calcular totales finales
        total_gross = subtotal + tax_amount
        total_retentions = retentions_data['iva_retention_amount'] + retentions_data['ir_retention_amount']
        net_payable = total_gross - total_retentions
        
        # Actualizar solo si hay cambios (COMPATIBLE: preserva lógica original)
        updates_needed = (
            self.subtotal != subtotal or 
            self.tax_amount != tax_amount or 
            self.total != total_gross or
            self.iva_retention_amount != retentions_data['iva_retention_amount'] or
            self.ir_retention_amount != retentions_data['ir_retention_amount'] or
            self.total_retentions != total_retentions or
            self.net_payable != net_payable
        )
        
        if updates_needed:
            self.subtotal = subtotal
            self.tax_amount = tax_amount
            self.total = total_gross
            self.iva_retention_amount = retentions_data['iva_retention_amount']
            self.ir_retention_amount = retentions_data['ir_retention_amount']
            self.total_retentions = total_retentions
            self.net_payable = net_payable
            
            # COMPATIBLE: Usar save() con update_fields para preservar otros campos
            if self.pk:
                super().save(update_fields=[
                    'subtotal', 'tax_amount', 'total',
                    'iva_retention_percentage', 'ir_retention_percentage',
                    'iva_retention_amount', 'ir_retention_amount',
                    'total_retentions', 'net_payable'
                ])
    
    def create_journal_entry(self):
        """
        Crear asiento contable automático para la factura de compra
        MEJORADO: Incluye retenciones ecuatorianas automáticamente
        COMPATIBLE: Mantiene funcionalidad original para facturas sin retenciones
        """
        from apps.accounting.models import JournalEntry, JournalEntryLine, ChartOfAccounts
        
        # No crear asientos para borradores o facturas anuladas
        if self.status in ['draft', 'cancelled']:
            return None
        
        # Verificar si ya existe asiento para esta factura
        existing_entry = JournalEntry.objects.filter(
            reference=f"Factura Compra {self.internal_number}",
            company=self.company
        ).first()
        
        if existing_entry:
            return existing_entry
        
        # Crear asiento contable con relación directa a la factura
        entry = JournalEntry.objects.create(
            company=self.company,
            date=self.date,
            reference=f"Factura Compra {self.internal_number}",
            description=f"Compra a {self.supplier.trade_name} - Fact. {self.supplier_invoice_number}",
            created_by=self.received_by or self.created_by,
            source_purchase_invoice=self  # NUEVA RELACIÓN DIRECTA
        )
        
        # ========================================
        # LÍNEAS DÉBITO (LO QUE COMPRAMOS/GASTAMOS)
        # ========================================
        
        # 1. DÉBITO: Gasto/Inventario (Subtotal)
        if self.supplier.expense_account:
            JournalEntryLine.objects.create(
                journal_entry=entry,
                account=self.supplier.expense_account,
                description=f"Compra según factura {self.supplier_invoice_number}",
                debit=self.subtotal,
                credit=Decimal('0.00'),
                document_type='FACTURA_COMPRA',
                document_number=self.supplier_invoice_number,
                document_date=self.date,
                auxiliary_code=self.supplier.identification,
                auxiliary_name=self.supplier.trade_name
            )
        
        # 2. DÉBITO: IVA por recuperar (Total del IVA)
        if self.tax_amount > 0:
            iva_account = self._get_iva_recoverable_account()
            if iva_account:
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=iva_account,
                    description=f"IVA recuperable factura {self.supplier_invoice_number}",
                    debit=self.tax_amount,
                    credit=Decimal('0.00'),
                    document_type='FACTURA_COMPRA',
                    document_number=self.supplier_invoice_number,
                    document_date=self.date,
                    auxiliary_code=self.supplier.identification,
                    auxiliary_name=self.supplier.trade_name
                )
        
        # ========================================
        # LÍNEAS CRÉDITO (LO QUE DEBEMOS)
        # ========================================
        
        # 3. CRÉDITO: Cuentas por pagar (Neto a pagar - después de retenciones)
        if self.payable_account:
            JournalEntryLine.objects.create(
                journal_entry=entry,
                account=self.payable_account,
                description=f"Por pagar a {self.supplier.trade_name} (neto)",
                debit=Decimal('0.00'),
                credit=self.net_payable,  # NUEVO: Neto después de retenciones
                document_type='FACTURA_COMPRA',
                document_number=self.supplier_invoice_number,
                document_date=self.date,
                auxiliary_code=self.supplier.identification,
                auxiliary_name=self.supplier.trade_name
            )
        
        # 4. CRÉDITO: Retención IVA (NUEVO - FASE 2)
        if self.iva_retention_amount > 0:
            iva_retention_account = self._get_iva_retention_account()
            if iva_retention_account:
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=iva_retention_account,
                    description=f"Retención IVA {self.iva_retention_percentage}% - {self.supplier.trade_name}",
                    debit=Decimal('0.00'),
                    credit=self.iva_retention_amount,
                    document_type='RETENCION',
                    document_number=self.retention_voucher_number or f"RET-{self.internal_number}",
                    document_date=self.retention_voucher_date or self.date,
                    auxiliary_code=self.supplier.identification,
                    auxiliary_name=self.supplier.trade_name
                )
        
        # 5. CRÉDITO: Retención IR (NUEVO - FASE 2)
        if self.ir_retention_amount > 0:
            ir_retention_account = self._get_ir_retention_account()
            if ir_retention_account:
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=ir_retention_account,
                    description=f"Retención IR {self.ir_retention_percentage}% - {self.supplier.trade_name}",
                    debit=Decimal('0.00'),
                    credit=self.ir_retention_amount,
                    document_type='RETENCION',
                    document_number=self.retention_voucher_number or f"RET-{self.internal_number}",
                    document_date=self.retention_voucher_date or self.date,
                    auxiliary_code=self.supplier.identification,
                    auxiliary_name=self.supplier.trade_name
                )
        
        # Recalcular totales del asiento
        entry.calculate_totals()
        
        return entry
    
    def generate_retention_voucher(self):
        """
        Genera comprobante de retención automáticamente
        FASE 3: Comprobantes de retención
        """
        # Solo generar si hay retenciones aplicadas
        if self.total_retentions <= 0:
            return None
        
        # Solo generar si no existe ya
        if self.retention_voucher_number:
            return self.retention_voucher_number
        
        try:
            from apps.companies.models import CompanySettings
            
            # Obtener configuración de secuenciales
            settings, created = CompanySettings.objects.get_or_create(
                company=self.company,
                defaults={'withholding_sequential': 1}
            )
            
            # Generar número de comprobante según normativa ecuatoriana
            # Formato: ESTABLECIMIENTO-PUNTO_EMISION-SECUENCIAL
            establishment = getattr(self.company, 'establishment_code', '001').zfill(3)
            emission_point = getattr(self.company, 'emission_point', '001').zfill(3)
            sequential = str(settings.withholding_sequential).zfill(9)
            
            voucher_number = f"{establishment}-{emission_point}-{sequential}"
            
            # Actualizar factura con datos del comprobante
            self.retention_voucher_number = voucher_number
            self.retention_voucher_date = timezone.now().date()
            
            # Incrementar secuencial
            settings.withholding_sequential += 1
            settings.save()
            
            # Guardar factura con nueva información
            super().save(update_fields=['retention_voucher_number', 'retention_voucher_date'])
            
            return voucher_number
            
        except Exception as e:
            print(f"Error generando comprobante de retención: {e}")
            return None
    
    def get_retention_voucher_data(self):
        """
        Obtiene datos estructurados del comprobante de retención
        Para generar XML, PDF o reportes
        """
        if self.total_retentions <= 0:
            return None
        
        return {
            'voucher_number': self.retention_voucher_number,
            'voucher_date': self.retention_voucher_date,
            'company_data': {
                'ruc': self.company.ruc if hasattr(self.company, 'ruc') else '',
                'legal_name': self.company.legal_name,
                'trade_name': self.company.trade_name,
                'address': getattr(self.company, 'address', ''),
            },
            'supplier_data': {
                'identification': self.supplier.identification,
                'trade_name': self.supplier.trade_name,
                'legal_name': self.supplier.legal_name,
                'address': self.supplier.address,
            },
            'purchase_data': {
                'invoice_number': self.supplier_invoice_number,
                'invoice_date': self.date,
                'subtotal': self.subtotal,
                'iva_amount': self.tax_amount,
                'total_amount': self.total,
            },
            'retentions': [
                {
                    'type': 'IVA',
                    'tax_code': '2',  # Código SRI para IVA
                    'base_amount': self.tax_amount,
                    'percentage': self.iva_retention_percentage,
                    'retention_amount': self.iva_retention_amount,
                } if self.iva_retention_amount > 0 else None,
                {
                    'type': 'RENTA',
                    'tax_code': '1',  # Código SRI para IR
                    'base_amount': self.subtotal,
                    'percentage': self.ir_retention_percentage,
                    'retention_amount': self.ir_retention_amount,
                } if self.ir_retention_amount > 0 else None,
            ],
            'totals': {
                'total_retentions': self.total_retentions,
                'net_payable': self.net_payable,
            }
        }
    
    def _get_iva_recoverable_account(self):
        """Obtiene cuenta de IVA por recuperar de la empresa"""
        from apps.accounting.models import ChartOfAccounts
        
        # Buscar cuenta específica para IVA recuperable
        return ChartOfAccounts.objects.filter(
            company=self.company,
            code__icontains='1.1.05',  # Código típico IVA por recuperar
            accepts_movement=True
        ).first() or ChartOfAccounts.objects.filter(
            company=self.company,
            name__icontains='iva recuperar',
            accepts_movement=True
        ).first()
    
    def _get_iva_retention_account(self):
        """Obtiene cuenta de retenciones IVA por cobrar"""
        from apps.accounting.models import ChartOfAccounts
        
        return ChartOfAccounts.objects.filter(
            company=self.company,
            code__icontains='1.1.07',  # Código típico retenciones IVA por cobrar
            accepts_movement=True
        ).first() or ChartOfAccounts.objects.filter(
            company=self.company,
            name__icontains='retencion iva',
            accepts_movement=True
        ).first()
    
    def _get_ir_retention_account(self):
        """Obtiene cuenta de retenciones IR por cobrar"""
        from apps.accounting.models import ChartOfAccounts
        
        return ChartOfAccounts.objects.filter(
            company=self.company,
            code__icontains='1.1.08',  # Código típico retenciones IR por cobrar
            accepts_movement=True
        ).first() or ChartOfAccounts.objects.filter(
            company=self.company,
            name__icontains='retencion renta',
            accepts_movement=True
        ).first()


class PurchaseInvoiceLine(BaseModel):
    """Líneas de factura de compra"""
    purchase_invoice = models.ForeignKey(
        PurchaseInvoice, 
        on_delete=models.CASCADE, 
        related_name='lines',
        verbose_name='Factura de compra'
    )
    
    # Producto (opcional - puede ser gasto directo)
    product = models.ForeignKey(
        'inventory.Product', 
        on_delete=models.PROTECT, 
        null=True,
        blank=True,
        verbose_name='Producto'
    )
    
    # Descripción (obligatoria)
    description = models.CharField(max_length=200, verbose_name='Descripción')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Cantidad')
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Costo unitario')
    discount = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Descuento (%)'
    )
    
    # Campo IVA
    iva_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('15.00'),
        verbose_name='IVA (%)'
    )
    
    # Cuenta contable (para gastos directos)
    account = models.ForeignKey(
        'accounting.ChartOfAccounts',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Cuenta contable'
    )
    
    # Montos calculados
    line_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name='Total línea'
    )
    
    class Meta:
        verbose_name = 'Línea de Factura de Compra'
        verbose_name_plural = 'Líneas de Factura de Compra'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.purchase_invoice.internal_number} - {self.description}"
    
    def clean(self):
        """Validaciones personalizadas de la línea de compra"""
        super().clean()
        
        # Validar que tenga producto O cuenta contable (no ambos)
        if self.product and self.account:
            from django.core.exceptions import ValidationError
            raise ValidationError({
                'product': 'No puede tener producto y cuenta contable al mismo tiempo'
            })
        
        if not self.product and not self.account:
            from django.core.exceptions import ValidationError
            raise ValidationError({
                'product': 'Debe especificar un producto o una cuenta contable'
            })
    
    def save(self, *args, **kwargs):
        """Guardar línea de compra con cálculos automáticos"""
        # Detectar si es una línea nueva
        is_new = self.pk is None
        
        # Tomar datos del producto si está especificado
        if self.product:
            if not self.unit_cost:
                self.unit_cost = self.product.cost_price
            if not self.description:
                self.description = self.product.name
            if not self.iva_rate or (is_new and self.iva_rate == Decimal('15.00')):
                self.iva_rate = self.product.iva_rate if self.product.has_iva else Decimal('0.00')
        
        # Si es nueva línea y no hay producto o el IVA es el por defecto, usar el IVA de la empresa
        if is_new and self.purchase_invoice and (not self.iva_rate or self.iva_rate == Decimal('15.00')):
            # Obtener la configuración de la empresa desde la factura
            if hasattr(self.purchase_invoice, 'company') and self.purchase_invoice.company:
                from apps.companies.models import CompanySettings
                company_settings, created = CompanySettings.objects.get_or_create(company=self.purchase_invoice.company)
                self.iva_rate = company_settings.default_iva_rate
        
        # Calcular total de línea ANTES de validaciones
        subtotal = self.quantity * self.unit_cost
        discount_amount = subtotal * (self.discount / 100)
        subtotal_after_discount = subtotal - discount_amount
        iva_amount = subtotal_after_discount * (self.iva_rate / 100)
        # Redondear a 2 decimales para evitar problemas de precisión
        self.line_total = round(subtotal_after_discount + iva_amount, 2)
        
        # Ejecutar validaciones
        self.full_clean()
        
        # Guardar la línea
        super().save(*args, **kwargs)
        
        # Recalcular totales de la factura padre
        self.purchase_invoice.calculate_totals()
        
        # Actualizar inventario si es un producto Y la factura está validada (contabilizada)
        if (self.product and 
            self.product.manages_inventory and 
            self.product.product_type == 'product' and 
            self.purchase_invoice.status == 'validated'):
            self.update_inventory()
        
        # Actualizar costo del producto si corresponde (solo cuando validada)
        if self.product and self.purchase_invoice.status == 'validated':
            self.update_product_cost()
    
    def delete(self, *args, **kwargs):
        """Al eliminar línea, recalcular totales de la factura"""
        purchase_invoice = self.purchase_invoice  # Guardar referencia antes de eliminar
        super().delete(*args, **kwargs)
        # Recalcular totales después de eliminar la línea
        purchase_invoice.calculate_totals()
    
    def update_inventory(self):
        """
        Crear movimiento de entrada en inventario al recibir compra
        Solo si es un producto físico que maneja inventario
        """
        from apps.inventory.models import StockMovement, Warehouse
        
        # Obtener bodega principal de la empresa
        main_warehouse = Warehouse.objects.filter(
            company=self.purchase_invoice.company,
            is_active=True
        ).first()
        
        if not main_warehouse:
            # Si no hay bodegas, crear una por defecto
            main_warehouse = Warehouse.objects.create(
                company=self.purchase_invoice.company,
                code='001',
                name='Bodega Principal',
                address='Oficina principal',
                responsible=self.purchase_invoice.received_by,
                is_active=True
            )
        
        # Verificar si ya existe un movimiento para esta línea de compra
        existing_movement = StockMovement.objects.filter(
            product=self.product,
            warehouse=main_warehouse,
            reference=f"Compra {self.purchase_invoice.internal_number}",
            movement_type=StockMovement.IN,
            quantity=self.quantity
        ).first()
        
        if not existing_movement:
            # Crear movimiento de entrada
            movement = StockMovement.objects.create(
                product=self.product,
                warehouse=main_warehouse,
                movement_type=StockMovement.IN,
                quantity=self.quantity,
                unit_cost=self.unit_cost,
                total_cost=self.quantity * self.unit_cost,
                reference=f"Compra {self.purchase_invoice.internal_number}",
                description=f"Compra según factura {self.purchase_invoice.supplier_invoice_number} - Proveedor: {self.purchase_invoice.supplier.trade_name}",
                created_by=self.purchase_invoice.received_by
            )
            
            # Actualizar stock actual
            self.update_stock_quantity(main_warehouse, movement)
    
    def update_stock_quantity(self, warehouse, movement):
        """Actualizar la cantidad en stock después del movimiento"""
        from apps.inventory.models import Stock, StockMovement
        from django.utils import timezone
        
        # Obtener o crear registro de stock
        stock, created = Stock.objects.get_or_create(
            product=self.product,
            warehouse=warehouse,
            defaults={
                'quantity': Decimal('0.00'),
                'average_cost': self.unit_cost,
                'last_movement': timezone.now()
            }
        )
        
        if movement.movement_type == StockMovement.IN:
            # Entrada: aumentar stock y recalcular costo promedio
            total_value_before = stock.quantity * stock.average_cost
            total_value_new = movement.quantity * movement.unit_cost
            total_quantity_after = stock.quantity + movement.quantity
            
            if total_quantity_after > 0:
                stock.average_cost = (total_value_before + total_value_new) / total_quantity_after
            
            stock.quantity += movement.quantity
        elif movement.movement_type == StockMovement.OUT:
            # Salida: reducir stock
            stock.quantity -= movement.quantity
        
        stock.last_movement = timezone.now()
        stock.save()
    
    def update_product_cost(self):
        """Actualizar el costo del producto con el nuevo costo de compra"""
        if self.product and self.unit_cost > 0:
            # Actualizar costo del producto si el nuevo costo es diferente
            if abs(self.product.cost_price - self.unit_cost) > Decimal('0.01'):
                self.product.cost_price = self.unit_cost
                self.product.save(update_fields=['cost_price'])