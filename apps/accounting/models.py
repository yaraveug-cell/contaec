from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from apps.core.models import BaseModel
from apps.companies.models import Company
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountType(BaseModel):
    """Tipos de cuenta contable según plan contable ecuatoriano"""
    ASSET = 'ASSET'
    LIABILITY = 'LIABILITY'
    EQUITY = 'EQUITY'
    INCOME = 'INCOME'
    EXPENSE = 'EXPENSE'
    
    TYPE_CHOICES = [
        (ASSET, 'Activo'),
        (LIABILITY, 'Pasivo'),
        (EQUITY, 'Patrimonio'),
        (INCOME, 'Ingresos'),
        (EXPENSE, 'Gastos'),
    ]
    
    code = models.CharField(max_length=10, choices=TYPE_CHOICES, unique=True, verbose_name='Código')
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    
    class Meta:
        verbose_name = 'Tipo de Cuenta'
        verbose_name_plural = 'Tipos de Cuenta'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ChartOfAccounts(BaseModel):
    """Plan de cuentas contables"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa')
    code = models.CharField(max_length=20, verbose_name='Código de cuenta')
    name = models.CharField(max_length=200, verbose_name='Nombre de cuenta')
    account_type = models.ForeignKey(
        AccountType, 
        on_delete=models.PROTECT, 
        verbose_name='Tipo de cuenta'
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name='Cuenta padre'
    )
    level = models.PositiveIntegerField(verbose_name='Nivel')
    is_detail = models.BooleanField(default=False, verbose_name='Cuenta de detalle')
    accepts_movement = models.BooleanField(default=True, verbose_name='Acepta movimiento')
    
    # Control de saldos
    requires_auxiliary = models.BooleanField(default=False, verbose_name='Requiere auxiliar')
    aux_type = models.CharField(
        max_length=20,
        choices=[
            ('client', 'Cliente'),
            ('supplier', 'Proveedor'),
            ('employee', 'Empleado'),
            ('bank', 'Banco'),
            ('product', 'Producto'),
            ('other', 'Otro'),
        ],
        blank=True,
        verbose_name='Tipo de auxiliar'
    )
    
    # Configuración fiscal
    sri_code = models.CharField(max_length=10, blank=True, verbose_name='Código SRI')
    tax_related = models.BooleanField(default=False, verbose_name='Relacionada con impuestos')
    
    class Meta:
        verbose_name = 'Cuenta Contable'
        verbose_name_plural = 'Plan de Cuentas'
        unique_together = ['company', 'code']
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def save(self, *args, **kwargs):
        """Guardar cuenta con cálculo automático del nivel"""
        # Calcular nivel automáticamente basado en la cuenta padre
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 1
        
        # Determinar automáticamente si es cuenta de detalle
        # Una cuenta es de detalle si no tiene cuentas hijas
        super().save(*args, **kwargs)
        
        # Actualizar el estado de cuenta de detalle del padre si existe
        if self.parent:
            self.parent._update_detail_status()
    
    def _update_detail_status(self):
        """Actualiza el estado de cuenta de detalle basado en si tiene hijos"""
        has_children = ChartOfAccounts.objects.filter(parent=self).exists()
        if has_children and self.is_detail:
            self.is_detail = False
            self.accepts_movement = False
            super().save(update_fields=['is_detail', 'accepts_movement'])
        elif not has_children and not self.is_detail:
            self.is_detail = True
            self.accepts_movement = True
            super().save(update_fields=['is_detail', 'accepts_movement'])
    
    @property
    def full_code(self):
        """Código completo incluyendo jerarquía"""
        if self.parent:
            return f"{self.parent.full_code}.{self.code}"
        return self.code
    
    @property 
    def children_count(self):
        """Número de cuentas hijas"""
        return ChartOfAccounts.objects.filter(parent=self).count()
    
    @property
    def hierarchy_display(self):
        """Muestra la cuenta con indentación según el nivel"""
        indent = "    " * (self.level - 1)
        return f"{indent}{self.code} - {self.name}"


class JournalEntry(BaseModel):
    """Asientos contables"""
    DRAFT = 'draft'
    POSTED = 'posted'
    CANCELLED = 'cancelled'
    
    STATE_CHOICES = [
        (DRAFT, 'Borrador'),
        (POSTED, 'Contabilizado'),
        (CANCELLED, 'Anulado'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa')
    number = models.CharField(max_length=20, verbose_name='Número de asiento')
    date = models.DateField(verbose_name='Fecha')
    reference = models.CharField(max_length=100, blank=True, verbose_name='Referencia')
    description = models.TextField(verbose_name='Descripción')
    state = models.CharField(
        max_length=10, 
        choices=STATE_CHOICES, 
        default=DRAFT,
        verbose_name='Estado'
    )
    
    # Usuario que crea y contabiliza
    created_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='journal_entries_created',
        verbose_name='Creado por'
    )
    posted_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        related_name='journal_entries_posted',
        verbose_name='Contabilizado por'
    )
    posted_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de contabilización')
    
    # Relación con factura de compra (para actualización de inventario)
    source_purchase_invoice = models.ForeignKey(
        'suppliers.PurchaseInvoice',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='journal_entries',
        verbose_name='Factura de compra origen'
    )
    
    # Totales
    total_debit = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Total débito'
    )
    total_credit = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Total crédito'
    )
    
    class Meta:
        verbose_name = 'Asiento Contable'
        verbose_name_plural = 'Asientos Contables'
        unique_together = ['company', 'number']
        ordering = ['-date', '-number']
    
    def __str__(self):
        return f"{self.number} - {self.date} - {self.description[:50]}"
    
    def calculate_totals(self):
        """Calcula los totales de débito y crédito"""
        from django.db.models import Sum
        
        lines = self.lines.all()
        
        self.total_debit = lines.aggregate(
            total=Sum('debit')
        )['total'] or Decimal('0.00')
        
        self.total_credit = lines.aggregate(
            total=Sum('credit')
        )['total'] or Decimal('0.00')
    
    def save(self, *args, **kwargs):
        """Guardar y calcular totales automáticamente"""
        # Si es un nuevo asiento, generar número
        if not self.pk and not self.number:
            last_entry = JournalEntry.objects.filter(
                company=self.company
            ).order_by('-id').first()
            
            if last_entry and last_entry.number.isdigit():
                last_number = int(last_entry.number)
                self.number = str(last_number + 1).zfill(6)
            else:
                self.number = '000001'
        
        # Guardar primero
        super().save(*args, **kwargs)
        
        # Calcular totales después de que existan las líneas
        if self.pk:
            self.calculate_totals()
            # Solo actualizar si hay cambios
            super().save(update_fields=['total_debit', 'total_credit'])
    
    @property
    def is_balanced(self):
        """Verifica si el asiento está balanceado"""
        return abs(self.total_debit - self.total_credit) < Decimal('0.01')


class JournalEntryLine(BaseModel):
    """Líneas de asientos contables"""
    journal_entry = models.ForeignKey(
        JournalEntry, 
        on_delete=models.CASCADE, 
        related_name='lines',
        verbose_name='Asiento contable'
    )
    account = models.ForeignKey(
        ChartOfAccounts, 
        on_delete=models.PROTECT,
        verbose_name='Cuenta'
    )
    description = models.CharField(max_length=200, verbose_name='Descripción')
    
    # Montos
    debit = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Débito'
    )
    credit = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Crédito'
    )
    
    # Auxiliares
    auxiliary_code = models.CharField(max_length=50, blank=True, verbose_name='Código auxiliar')
    auxiliary_name = models.CharField(max_length=200, blank=True, verbose_name='Nombre auxiliar')
    
    # Referencias
    document_type = models.CharField(max_length=20, blank=True, verbose_name='Tipo de documento')
    document_number = models.CharField(max_length=50, blank=True, verbose_name='Número de documento')
    document_date = models.DateField(null=True, blank=True, verbose_name='Fecha del documento')
    
    class Meta:
        verbose_name = 'Línea de Asiento'
        verbose_name_plural = 'Líneas de Asiento'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.account.code} - {self.description}"
    
    def clean(self):
        """Validaciones personalizadas"""
        from django.core.exceptions import ValidationError
        
        # No puede tener débito y crédito al mismo tiempo
        if self.debit > 0 and self.credit > 0:
            raise ValidationError('No puede tener débito y crédito al mismo tiempo')
        
        # Debe tener débito o crédito
        if self.debit == 0 and self.credit == 0:
            raise ValidationError('Debe tener un valor en débito o crédito')


class FiscalYear(BaseModel):
    """Ejercicios fiscales"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa')
    year = models.IntegerField(verbose_name='Año')
    start_date = models.DateField(verbose_name='Fecha de inicio')
    end_date = models.DateField(verbose_name='Fecha de fin')
    is_closed = models.BooleanField(default=False, verbose_name='Cerrado')
    closed_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        verbose_name='Cerrado por'
    )
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de cierre')
    
    class Meta:
        verbose_name = 'Ejercicio Fiscal'
        verbose_name_plural = 'Ejercicios Fiscales'
        unique_together = ['company', 'year']
        ordering = ['-year']
    
    def __str__(self):
        return f"{self.company.trade_name} - {self.year}"


class AccountBalance(BaseModel):
    """Saldos de cuentas contables"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa')
    account = models.ForeignKey(ChartOfAccounts, on_delete=models.CASCADE, verbose_name='Cuenta')
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, verbose_name='Ejercicio fiscal')
    period = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name='Período (mes)'
    )
    
    # Saldos
    initial_balance_debit = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Saldo inicial débito'
    )
    initial_balance_credit = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Saldo inicial crédito'
    )
    
    period_debit = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Débito del período'
    )
    period_credit = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Crédito del período'
    )
    
    final_balance_debit = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Saldo final débito'
    )
    final_balance_credit = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Saldo final crédito'
    )
    
    class Meta:
        verbose_name = 'Saldo de Cuenta'
        verbose_name_plural = 'Saldos de Cuentas'
        unique_together = ['company', 'account', 'fiscal_year', 'period']
        ordering = ['account__code', 'period']
    
    def __str__(self):
        return f"{self.account.code} - {self.fiscal_year.year}/{self.period:02d}"
    
    @property
    def net_balance(self):
        """Balance neto de la cuenta"""
        return (self.final_balance_debit - self.final_balance_credit)