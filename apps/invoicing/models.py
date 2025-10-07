from django.db import models, transaction
from decimal import Decimal
from django.utils import timezone
from apps.core.models import BaseModel
from apps.companies.models import Company
from django.contrib.auth import get_user_model

User = get_user_model()

# Las constantes de forma de pago ahora se manejan dinámicamente
# a través del modelo PaymentMethod en apps.companies.models


class Customer(BaseModel):
    """Clientes del sistema"""
    NATURAL = 'natural'
    JURIDICAL = 'juridical'
    
    CUSTOMER_TYPE_CHOICES = [
        (NATURAL, 'Persona Natural'),
        (JURIDICAL, 'Persona Jurídica'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa')
    customer_type = models.CharField(
        max_length=10, 
        choices=CUSTOMER_TYPE_CHOICES, 
        verbose_name='Tipo de cliente'
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
    payment_terms = models.IntegerField(default=0, verbose_name='Días de crédito')
    
    # Configuración de retenciones ecuatorianas
    retention_agent = models.BooleanField(
        default=False,
        verbose_name='Es agente de retención',
        help_text='Si el cliente debe realizar retenciones en sus compras'
    )
    iva_retention_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Porcentaje retención IVA (%)',
        help_text='Porcentaje de retención de IVA según tipo de cliente'
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
        help_text='Clasificación del cliente para cálculo automático de retenciones'
    )
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        unique_together = ['company', 'identification']
        ordering = ['trade_name']
    
    def __str__(self):
        return f"{self.identification} - {self.trade_name}"
    
    def get_retention_rates(self):
        """
        Calcula las tasas de retención aplicables según clasificación SRI
        Similar al método en Supplier pero para clientes como agentes de retención
        """
        rates = {
            'iva_retention': Decimal('0.00'),
            'ir_retention': Decimal('0.00')
        }
        
        if not self.retention_agent:
            return rates
        
        # Tasas de retención IVA según clasificación SRI (normativa ecuatoriana)
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
    
    def calculate_retention_amounts(self, subtotal, tax_amount):
        """
        Calcula los montos de retención para una factura
        
        Args:
            subtotal: Subtotal de la factura
            tax_amount: Monto del IVA de la factura
            
        Returns:
            dict: {'iva_retention': amount, 'ir_retention': amount}
        """
        if not self.retention_agent:
            return {'iva_retention': Decimal('0.00'), 'ir_retention': Decimal('0.00')}
        
        rates = self.get_retention_rates()
        
        # Cálculo de retención IVA (se aplica sobre el IVA de la factura)
        iva_retention_amount = (tax_amount * rates['iva_retention'] / Decimal('100.00')).quantize(Decimal('0.01'))
        
        # Cálculo de retención IR (se aplica sobre el subtotal)
        ir_retention_amount = (subtotal * rates['ir_retention'] / Decimal('100.00')).quantize(Decimal('0.01'))
        
        return {
            'iva_retention': iva_retention_amount,
            'ir_retention': ir_retention_amount
        }


# MODELO ELIMINADO - AHORA SE USA inventory.Product
# Los productos ahora están unificados en apps/inventory/models.py


class Invoice(BaseModel):
    """Facturas"""
    DRAFT = 'draft'
    SENT = 'sent'
    PAID = 'paid'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (DRAFT, 'Borrador'),
        (SENT, 'Enviada'),
        (PAID, 'Pagada'),
        (CANCELLED, 'Anulada'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name='Cliente')
    
    # Numeración
    number = models.CharField(max_length=20, verbose_name='Número')
    date = models.DateField(default=timezone.now, verbose_name='Fecha')
    due_date = models.DateField(null=True, blank=True, verbose_name='Fecha de vencimiento')
    payment_form = models.ForeignKey(
        'companies.PaymentMethod',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Forma de Pago'
    )
    account = models.ForeignKey('accounting.ChartOfAccounts', on_delete=models.PROTECT, null=True, blank=True, verbose_name='Cuenta')
    transfer_detail = models.TextField(blank=True, verbose_name='Detalle Transferencia')  # DEPRECATED - usar bank_observations
    bank_observations = models.TextField(blank=True, verbose_name='Observaciones Bancarias', help_text='Observaciones adicionales para transferencias bancarias')
    
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
    
    # Usuario
    created_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        verbose_name='Creado por'
    )
    
    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        unique_together = ['company', 'number']
        ordering = ['-date', '-number']
        
        # Permisos personalizados para control granular de estados
        permissions = [
            ('change_invoice_status', 'Puede cambiar estado de facturas'),
            ('mark_invoice_sent', 'Puede marcar facturas como enviadas'),
            ('mark_invoice_paid', 'Puede marcar facturas como pagadas'),
            ('mark_invoice_cancelled', 'Puede anular facturas'),
            ('approve_invoices', 'Puede aprobar facturas'),
            ('reverse_invoice_entries', 'Puede revertir asientos de facturas'),
        ]
    
    def __str__(self):
        return f"{self.number} - {self.customer.trade_name}"
    
    def generate_invoice_number(self):
        """Genera número automático de factura según normativa ecuatoriana"""
        from apps.companies.models import CompanySettings
        
        # Obtener o crear configuración de la empresa
        settings, created = CompanySettings.objects.get_or_create(
            company=self.company,
            defaults={
                'invoice_sequential': 1,
                'credit_note_sequential': 1,
                'debit_note_sequential': 1,
                'withholding_sequential': 1,
            }
        )
        
        # Formato ecuatoriano: ESTABLECIMIENTO-PUNTO_EMISION-SECUENCIAL
        # Ejemplo: 001-001-000000001
        establishment = self.company.establishment_code.zfill(3)
        emission_point = self.company.emission_point.zfill(3)
        sequential = str(settings.invoice_sequential).zfill(9)
        
        invoice_number = f"{establishment}-{emission_point}-{sequential}"
        
        # Incrementar secuencial para la próxima factura
        settings.invoice_sequential += 1
        settings.save()
        
        return invoice_number
    
    def save(self, *args, **kwargs):
        """Generar número automático si no existe"""
        if not self.number:
            with transaction.atomic():
                self.number = self.generate_invoice_number()
        
        super().save(*args, **kwargs)
        
        # Recalcular totales después de guardar
        self.calculate_totals()
    
    def get_tax_breakdown(self):
        """Obtener desglose de impuestos por tasa de IVA"""
        lines = self.lines.all()
        tax_breakdown = {}
        
        for line in lines:
            line_subtotal = line.quantity * line.unit_price
            discount_amount = line_subtotal * (line.discount / 100)
            line_net = line_subtotal - discount_amount
            
            # Usar la tasa de IVA de la línea (no del producto)
            iva_rate = line.iva_rate
            line_tax = line_net * (iva_rate / 100)
            
            if iva_rate in tax_breakdown:
                tax_breakdown[iva_rate]['base'] += line_net
                tax_breakdown[iva_rate]['tax'] += line_tax
            else:
                tax_breakdown[iva_rate] = {
                    'rate': iva_rate,
                    'base': line_net,
                    'tax': line_tax
                }
        
        return tax_breakdown
    
    def calculate_totals(self):
        """Calcular subtotal, impuestos y total de la factura"""
        lines = self.lines.all()
        
        subtotal = Decimal('0.00')
        tax_amount = Decimal('0.00')
        
        for line in lines:
            line_subtotal = line.quantity * line.unit_price
            discount_amount = line_subtotal * (line.discount / 100)
            line_net = line_subtotal - discount_amount
            
            subtotal += line_net
            
            # Calcular IVA usando la tasa de la línea
            line_tax = line_net * (line.iva_rate / 100)
            tax_amount += line_tax
        
        # Actualizar solo si hay cambios
        if (self.subtotal != subtotal or 
            self.tax_amount != tax_amount or 
            self.total != subtotal + tax_amount):
            
            self.subtotal = subtotal
            self.tax_amount = tax_amount
            self.total = subtotal + tax_amount
            
            # CORRECCIÓN: Usar save() con update_fields para preservar otros campos
            if self.pk:
                # Usar save() con update_fields para no sobrescribir payment_form, account, transfer_detail
                super().save(update_fields=['subtotal', 'tax_amount', 'total'])
            # Si es nueva factura, los valores se guardan en el siguiente save()


class InvoiceLine(BaseModel):
    """Líneas de factura usando productos unificados de inventario"""
    invoice = models.ForeignKey(
        Invoice, 
        on_delete=models.CASCADE, 
        related_name='lines',
        verbose_name='Factura'
    )
    # Usar producto de inventario (unificado)
    product = models.ForeignKey(
        'inventory.Product', 
        on_delete=models.PROTECT, 
        verbose_name='Producto'
    )
    
    description = models.CharField(max_length=200, verbose_name='Descripción')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Cantidad')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio unitario')
    discount = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Descuento (%)'
    )
    
    # Campo Stock (solo informativo)
    stock = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Stock',
        help_text='Stock disponible del producto al momento de la venta'
    )
    
    # Campo IVA
    iva_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('15.00'),
        verbose_name='IVA (%)'
    )
    
    # Montos calculados
    line_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Total línea'
    )
    
    class Meta:
        verbose_name = 'Línea de Factura'
        verbose_name_plural = 'Líneas de Factura'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.invoice.number} - {self.product.name}"
    
    def calculate_line_total(self):
        """Calcular total de línea incluyendo descuentos e IVA"""
        if not all([self.quantity, self.unit_price]):
            return Decimal('0.00')
        
        # Subtotal base
        subtotal = Decimal(str(self.quantity)) * Decimal(str(self.unit_price))
        
        # Aplicar descuento
        discount_amount = subtotal * (Decimal(str(self.discount or 0)) / 100)
        subtotal_after_discount = subtotal - discount_amount
        
        # Aplicar IVA
        iva_amount = subtotal_after_discount * (Decimal(str(self.iva_rate or 0)) / 100)
        
        # Total final redondeado
        total = subtotal_after_discount + iva_amount
        return total.quantize(Decimal('0.01'))
    
    @property
    def calculated_line_total(self):
        """Property para obtener el total calculado"""
        return self.calculate_line_total()
    
    def check_stock_availability(self):
        """
        Verificar disponibilidad de stock con niveles inteligentes de alerta.
        
        Returns:
            dict: {
                'has_sufficient_stock': bool,
                'available_stock': Decimal,
                'requested_quantity': Decimal,
                'shortage': Decimal,
                'level': str ('error', 'warning', 'info', 'success'),
                'message': str (mensaje para mostrar al usuario),
                'icon': str (emoji para el mensaje)
            }
        """
        if not self.product or not self.quantity:
            return None
            
        try:
            # Obtener stock actual del producto
            available_stock = Decimal(str(self.product.get_current_stock() or 0))
            requested_quantity = Decimal(str(self.quantity or 0))
            
            # Calcular diferencia
            shortage = max(Decimal('0'), requested_quantity - available_stock)
            has_sufficient_stock = available_stock >= requested_quantity
            
            # Determinar nivel y mensaje según las condiciones
            if not has_sufficient_stock:
                # STOCK INSUFICIENTE - Error crítico
                return {
                    'has_sufficient_stock': False,
                    'available_stock': available_stock,
                    'requested_quantity': requested_quantity,
                    'shortage': shortage,
                    'level': 'error',
                    'icon': '🚨',
                    'message': (
                        f"{self.product.name} "
                        f"(Código: {getattr(self.product, 'code', 'N/A')}) - "
                        f"Solicitado: {requested_quantity}, "
                        f"Disponible: {available_stock}, "
                        f"Faltante: {shortage}"
                    )
                }
            
            elif available_stock <= 5:
                # STOCK CRÍTICO - Advertencia alta
                return {
                    'has_sufficient_stock': True,
                    'available_stock': available_stock,
                    'requested_quantity': requested_quantity,
                    'shortage': Decimal('0'),
                    'level': 'warning',
                    'icon': '⚠️',
                    'message': (
                        f"{self.product.name} "
                        f"(Código: {getattr(self.product, 'code', 'N/A')}) - "
                        f"Solo quedan {available_stock} unidades disponibles. "
                        f"Considere reabastecer urgentemente."
                    )
                }
            
            elif available_stock <= 10:
                # STOCK BAJO - Advertencia media
                return {
                    'has_sufficient_stock': True,
                    'available_stock': available_stock,
                    'requested_quantity': requested_quantity,
                    'shortage': Decimal('0'),
                    'level': 'warning',
                    'icon': '📦',
                    'message': (
                        f"{self.product.name} "
                        f"(Código: {getattr(self.product, 'code', 'N/A')}) - "
                        f"Quedan {available_stock} unidades. Planifique reabastecimiento."
                    )
                }
            
            elif requested_quantity > (available_stock * Decimal('0.8')):
                # USANDO GRAN PARTE DEL STOCK - Información
                percentage = int((requested_quantity / available_stock) * 100)
                return {
                    'has_sufficient_stock': True,
                    'available_stock': available_stock,
                    'requested_quantity': requested_quantity,
                    'shortage': Decimal('0'),
                    'level': 'info',
                    'icon': '📊',
                    'message': (
                        f"{self.product.name} - "
                        f"Utilizando {percentage}% del stock disponible "
                        f"({requested_quantity} de {available_stock} unidades)."
                    )
                }
            
            else:
                # STOCK SUFICIENTE - Todo OK
                return {
                    'has_sufficient_stock': True,
                    'available_stock': available_stock,
                    'requested_quantity': requested_quantity,
                    'shortage': Decimal('0'),
                    'level': 'success',
                    'icon': '✅',
                    'message': (
                        f"{self.product.name} - "
                        f"Disponible: {available_stock} unidades."
                    )
                }
                
        except Exception as e:
            # Error al verificar stock - No crítico
            return {
                'has_sufficient_stock': True,  # Permitir continuar en caso de error
                'available_stock': Decimal('0'),
                'requested_quantity': requested_quantity,
                'shortage': Decimal('0'),
                'level': 'warning',
                'icon': '⚠️',
                'message': f"⚠️ Error verificando stock de {self.product.name}: {str(e)}"
            }
    
    def clean(self):
        """
        Validación del modelo con verificación inteligente de stock.
        IMPORTANTE: Solo bloquea el guardado si hay stock INSUFICIENTE.
        """
        from django.core.exceptions import ValidationError
        
        super().clean()
        
        # Validación básica de cantidad
        if self.quantity and self.quantity <= 0:
            raise ValidationError({
                'quantity': 'La cantidad debe ser mayor a cero.'
            })
        
        # VALIDACIÓN CRÍTICA DE STOCK
        if self.product and self.quantity:
            stock_info = self.check_stock_availability()
            
            if stock_info and not stock_info.get('has_sufficient_stock', True):
                # Bloqueo silencioso en backend - Sin mensaje invasivo
                # El frontend debe impedir llegar a este punto
                raise ValidationError({
                    'quantity': "Stock insuficiente."
                })
    
    def save(self, *args, **kwargs):
        """Guardar línea con cálculo automático del total"""
        # Auto-completar descripción desde el producto si está vacía
        if self.product and not self.description:
            self.description = str(self.product.name)
        
        # Auto-actualizar stock informativo
        if self.product:
            try:
                self.stock = Decimal(str(self.product.get_current_stock() or 0))
            except:
                self.stock = Decimal('0')
        
        # Calcular total de línea
        self.line_total = self.calculate_line_total()
        
        # Ejecutar validaciones antes de guardar
        self.full_clean()
        
        super().save(*args, **kwargs)
    

    
    def save(self, *args, **kwargs):
        """
        Al guardar la línea de factura:
        1. Tomar precio del producto si no se especifica
        2. Calcular total de línea
        3. Actualizar inventario si corresponde
        """
        # Tomar precio del producto si no se especifica
        if not self.unit_price:
            self.unit_price = self.product.sale_price
        
        # Tomar descripción del producto si no se especifica
        if not self.description:
            self.description = self.product.name
            
        # Tomar stock actual del producto
        if not self.stock:
            self.stock = self.product.get_current_stock() or 0
            
        # Tomar IVA del producto si no se especifica
        if not self.iva_rate:
            self.iva_rate = self.product.iva_rate
    

        
    def save(self, *args, **kwargs):
        """Guardar línea de factura con cálculos automáticos"""
        # Detectar si es una línea nueva
        is_new = self.pk is None
        
        # Establecer valores por defecto del producto si es necesario
        if self.product:
            if not self.unit_price:
                self.unit_price = self.product.sale_price or 0
            if not self.description:
                self.description = self.product.name
            if not self.iva_rate or (is_new and self.iva_rate == Decimal('15.00')):
                self.iva_rate = self.product.iva_rate if hasattr(self.product, 'iva_rate') else Decimal('15.00')
        
        # Si es nueva línea y no hay producto o el IVA es el por defecto, usar el IVA de la empresa
        if is_new and self.invoice and (not self.iva_rate or self.iva_rate == Decimal('15.00')):
            # Obtener la configuración de la empresa desde la factura
            if hasattr(self.invoice, 'company') and self.invoice.company:
                from apps.companies.models import CompanySettings
                company_settings, created = CompanySettings.objects.get_or_create(company=self.invoice.company)
                self.iva_rate = company_settings.default_iva_rate
        
        # Calcular total de línea usando el método especializado
        self.line_total = self.calculate_line_total()
        
        # Ejecutar validaciones
        self.full_clean()
        
        # Guardar la línea
        super().save(*args, **kwargs)
        
        # Recalcular totales de la factura padre
        self.invoice.calculate_totals()
        
        # Actualizar inventario si es necesario
        if (self.product.manages_inventory and 
            self.product.product_type == 'product' and 
            self.invoice.status != 'cancelled'):
            self.update_inventory()
    
    def delete(self, *args, **kwargs):
        """Al eliminar línea, recalcular totales de la factura"""
        invoice = self.invoice  # Guardar referencia antes de eliminar
        super().delete(*args, **kwargs)
        # Recalcular totales después de eliminar la línea
        invoice.calculate_totals()
    
    def update_inventory(self):
        """
        Crear movimiento de salida en inventario al facturar
        Solo si es un producto físico que maneja inventario
        """
        from apps.inventory.models import StockMovement, Warehouse
        
        # Obtener bodega principal de la empresa
        main_warehouse = Warehouse.objects.filter(
            company=self.invoice.company,
            is_active=True
        ).first()
        
        if not main_warehouse:
            # Si no hay bodegas, crear una por defecto
            main_warehouse = Warehouse.objects.create(
                company=self.invoice.company,
                code='001',
                name='Bodega Principal',
                address='Oficina principal',
                responsible=self.invoice.created_by,
                is_active=True
            )
        
        # Verificar si ya existe un movimiento para esta línea de factura
        existing_movement = StockMovement.objects.filter(
            product=self.product,
            warehouse=main_warehouse,
            reference=f"Factura {self.invoice.number}",
            movement_type=StockMovement.OUT,
            quantity=self.quantity
        ).first()
        
        if not existing_movement:
            # Crear movimiento de salida
            movement = StockMovement.objects.create(
                product=self.product,
                warehouse=main_warehouse,
                movement_type=StockMovement.OUT,
                quantity=self.quantity,
                unit_cost=self.product.cost_price,
                total_cost=self.quantity * self.product.cost_price,
                reference=f"Factura {self.invoice.number}",
                description=f"Venta según factura {self.invoice.number} - Cliente: {self.invoice.customer.trade_name}",
                created_by=self.invoice.created_by
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
                'average_cost': self.product.cost_price,
                'last_movement': timezone.now()
            }
        )
        
        if movement.movement_type == StockMovement.OUT:
            # Salida: reducir stock
            stock.quantity -= movement.quantity
        elif movement.movement_type == StockMovement.IN:
            # Entrada: aumentar stock y recalcular costo promedio
            total_value_before = stock.quantity * stock.average_cost
            total_value_new = movement.quantity * movement.unit_cost
            total_quantity_after = stock.quantity + movement.quantity
            
            if total_quantity_after > 0:
                stock.average_cost = (total_value_before + total_value_new) / total_quantity_after
            
            stock.quantity += movement.quantity
        
        stock.last_movement = timezone.now()
        stock.save()