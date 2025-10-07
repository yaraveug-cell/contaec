"""
Modelos para el módulo de activos fijos
Sistema de contabilidad para pequeñas empresas ecuatorianas
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import date
from apps.companies.models import Company
from apps.users.models import User


class AssetCategory(models.Model):
    """Categorías de activos fijos"""
    name = models.CharField('Nombre', max_length=100)
    description = models.TextField('Descripción', blank=True)
    useful_life_years = models.IntegerField(
        'Vida Útil (años)', 
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    depreciation_rate = models.DecimalField(
        'Tasa de Depreciación (%)', 
        max_digits=5, 
        decimal_places=2,
        default=10.00,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('100.00'))]
    )
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Categoría de Activo'
        verbose_name_plural = 'Categorías de Activos'
    
    def __str__(self):
        return self.name


class AssetLocation(models.Model):
    """Ubicaciones de activos fijos"""
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        verbose_name='Empresa',
        related_name='asset_locations'
    )
    name = models.CharField('Nombre', max_length=100)
    description = models.TextField('Descripción', blank=True)
    address = models.TextField('Dirección', blank=True)
    responsible_person = models.CharField('Persona Responsable', max_length=100, blank=True)
    
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Ubicación de Activo'
        verbose_name_plural = 'Ubicaciones de Activos'
        unique_together = ['company', 'name']
    
    def __str__(self):
        return f"{self.company.trade_name} - {self.name}"


class FixedAsset(models.Model):
    """Activos fijos de la empresa"""
    STATUS_CHOICES = [
        ('activo', 'Activo'),
        ('en_mantenimiento', 'En Mantenimiento'),
        ('fuera_servicio', 'Fuera de Servicio'),
        ('vendido', 'Vendido'),
        ('dado_baja', 'Dado de Baja'),
    ]
    
    ACQUISITION_METHOD_CHOICES = [
        ('compra', 'Compra'),
        ('donacion', 'Donación'),
        ('construccion', 'Construcción Propia'),
        ('arrendamiento', 'Arrendamiento Financiero'),
        ('aporte', 'Aporte de Socios'),
    ]
    
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        verbose_name='Empresa',
        related_name='fixed_assets'
    )
    
    # Información básica
    asset_code = models.CharField('Código de Activo', max_length=50, unique=True)
    name = models.CharField('Nombre del Activo', max_length=200)
    description = models.TextField('Descripción Detallada', blank=True)
    category = models.ForeignKey(
        AssetCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name='Categoría',
        related_name='fixed_assets'
    )
    location = models.ForeignKey(
        AssetLocation, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Ubicación',
        related_name='located_assets'
    )
    
    # Información de adquisición
    acquisition_date = models.DateField('Fecha de Adquisición')
    acquisition_method = models.CharField(
        'Método de Adquisición', 
        max_length=20, 
        choices=ACQUISITION_METHOD_CHOICES, 
        default='compra'
    )
    supplier = models.CharField('Proveedor', max_length=200, blank=True)
    invoice_number = models.CharField('Número de Factura', max_length=50, blank=True)
    
    # Valores financieros
    acquisition_cost = models.DecimalField(
        'Costo de Adquisición', 
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    accumulated_depreciation = models.DecimalField(
        'Depreciación Acumulada', 
        max_digits=12, 
        decimal_places=2, 
        default=0
    )
    book_value = models.DecimalField(
        'Valor en Libros', 
        max_digits=12, 
        decimal_places=2, 
        default=0
    )
    
    # Información técnica
    brand = models.CharField('Marca', max_length=100, blank=True)
    model = models.CharField('Modelo', max_length=100, blank=True)
    serial_number = models.CharField('Número de Serie', max_length=100, blank=True)
    color = models.CharField('Color', max_length=50, blank=True)
    
    # Estado y condición
    status = models.CharField('Estado', max_length=20, choices=STATUS_CHOICES, default='activo')
    condition_notes = models.TextField('Notas de Condición', blank=True)
    
    # Información de baja (si aplica)
    disposal_date = models.DateField('Fecha de Baja', null=True, blank=True)
    disposal_reason = models.TextField('Motivo de Baja', blank=True)
    disposal_value = models.DecimalField(
        'Valor de Disposición', 
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Auditoría
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Creado por',
        related_name='created_assets'
    )
    
    class Meta:
        verbose_name = 'Activo Fijo'
        verbose_name_plural = 'Activos Fijos'
        unique_together = ['company', 'asset_code']
    
    def __str__(self):
        return f"{self.asset_code} - {self.name}"
    
    def save(self, *args, **kwargs):
        """Calcular valor en libros automáticamente"""
        self.book_value = self.acquisition_cost - self.accumulated_depreciation
        super().save(*args, **kwargs)
    
    @property
    def depreciation_percentage(self):
        """Calcular porcentaje de depreciación actual"""
        if self.acquisition_cost and self.acquisition_cost > 0:
            return (self.accumulated_depreciation / self.acquisition_cost) * 100
        return 0


class DepreciationSchedule(models.Model):
    """Cronograma de depreciación de activos"""
    DEPRECIATION_METHOD_CHOICES = [
        ('lineal', 'Línea Recta'),
        ('acelerada', 'Acelerada'),
        ('unidades_produccion', 'Unidades de Producción'),
    ]
    
    asset = models.OneToOneField(
        FixedAsset, 
        on_delete=models.CASCADE, 
        verbose_name='Activo',
        related_name='depreciation_schedule'
    )
    
    method = models.CharField(
        'Método de Depreciación', 
        max_length=20, 
        choices=DEPRECIATION_METHOD_CHOICES, 
        default='lineal'
    )
    useful_life_years = models.IntegerField(
        'Vida Útil (años)',
        validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    useful_life_months = models.IntegerField(
        'Vida Útil (meses)',
        validators=[MinValueValidator(1), MaxValueValidator(600)]
    )
    salvage_value = models.DecimalField(
        'Valor de Salvamento', 
        max_digits=12, 
        decimal_places=2, 
        default=0
    )
    annual_depreciation = models.DecimalField(
        'Depreciación Anual', 
        max_digits=12, 
        decimal_places=2, 
        default=0
    )
    monthly_depreciation = models.DecimalField(
        'Depreciación Mensual', 
        max_digits=12, 
        decimal_places=2, 
        default=0
    )
    
    start_date = models.DateField('Fecha de Inicio Depreciación')
    end_date = models.DateField('Fecha de Fin Depreciación', null=True, blank=True)
    
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)
    
    class Meta:
        verbose_name = 'Cronograma de Depreciación'
        verbose_name_plural = 'Cronogramas de Depreciación'
    
    def __str__(self):
        return f"Depreciación {self.asset.name}"
    
    def save(self, *args, **kwargs):
        """Calcular depreciaciones automáticamente"""
        if self.method == 'lineal':
            depreciable_value = self.asset.acquisition_cost - self.salvage_value
            self.annual_depreciation = depreciable_value / self.useful_life_years
            self.monthly_depreciation = self.annual_depreciation / 12
        
        # Calcular fecha de fin
        if self.start_date:
            from datetime import timedelta
            from dateutil.relativedelta import relativedelta
            self.end_date = self.start_date + relativedelta(months=self.useful_life_months)
        
        super().save(*args, **kwargs)


class DepreciationEntry(models.Model):
    """Asientos de depreciación registrados"""
    asset = models.ForeignKey(
        FixedAsset, 
        on_delete=models.CASCADE, 
        verbose_name='Activo',
        related_name='depreciation_entries'
    )
    
    period_year = models.IntegerField('Año del Período')
    period_month = models.IntegerField(
        'Mes del Período',
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    
    depreciation_amount = models.DecimalField(
        'Monto de Depreciación', 
        max_digits=12, 
        decimal_places=2
    )
    accumulated_before = models.DecimalField(
        'Depreciación Acumulada Anterior', 
        max_digits=12, 
        decimal_places=2, 
        default=0
    )
    accumulated_after = models.DecimalField(
        'Depreciación Acumulada Posterior', 
        max_digits=12, 
        decimal_places=2, 
        default=0
    )
    
    # Referencia contable
    journal_entry_reference = models.CharField(
        'Referencia Asiento Contable', 
        max_length=50, 
        blank=True
    )
    
    # Estado
    is_posted = models.BooleanField('Contabilizado', default=False)
    posting_date = models.DateField('Fecha de Contabilización', null=True, blank=True)
    
    # Auditoría
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name='Creado por',
        related_name='created_depreciation_entries'
    )
    
    class Meta:
        verbose_name = 'Asiento de Depreciación'
        verbose_name_plural = 'Asientos de Depreciación'
        unique_together = ['asset', 'period_year', 'period_month']
    
    def __str__(self):
        return f"Depreciación {self.asset.name} - {self.period_month}/{self.period_year}"
    
    def save(self, *args, **kwargs):
        """Actualizar acumulados automáticamente"""
        self.accumulated_after = self.accumulated_before + self.depreciation_amount
        super().save(*args, **kwargs)


class AssetMaintenance(models.Model):
    """Registros de mantenimiento de activos"""
    MAINTENANCE_TYPE_CHOICES = [
        ('preventivo', 'Preventivo'),
        ('correctivo', 'Correctivo'),
        ('predictivo', 'Predictivo'),
        ('emergencia', 'Emergencia'),
    ]
    
    asset = models.ForeignKey(
        FixedAsset, 
        on_delete=models.CASCADE, 
        verbose_name='Activo',
        related_name='maintenances'
    )
    
    maintenance_date = models.DateField('Fecha de Mantenimiento')
    maintenance_type = models.CharField(
        'Tipo de Mantenimiento', 
        max_length=20, 
        choices=MAINTENANCE_TYPE_CHOICES
    )
    description = models.TextField('Descripción del Mantenimiento')
    
    # Costos
    labor_cost = models.DecimalField(
        'Costo de Mano de Obra', 
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    parts_cost = models.DecimalField(
        'Costo de Repuestos', 
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    external_cost = models.DecimalField(
        'Costo Externo', 
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    total_cost = models.DecimalField(
        'Costo Total', 
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    
    # Proveedor/Técnico
    provider = models.CharField('Proveedor/Técnico', max_length=200, blank=True)
    invoice_number = models.CharField('Número de Factura', max_length=50, blank=True)
    
    # Seguimiento
    next_maintenance_date = models.DateField('Próximo Mantenimiento', null=True, blank=True)
    warranty_until = models.DateField('Garantía Hasta', null=True, blank=True)
    
    # Auditoría
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name='Registrado por',
        related_name='registered_maintenances'
    )
    
    class Meta:
        verbose_name = 'Mantenimiento de Activo'
        verbose_name_plural = 'Mantenimientos de Activos'
    
    def __str__(self):
        return f"{self.asset.name} - {self.maintenance_type} ({self.maintenance_date})"
    
    def save(self, *args, **kwargs):
        """Calcular costo total automáticamente"""
        self.total_cost = self.labor_cost + self.parts_cost + self.external_cost
        super().save(*args, **kwargs)