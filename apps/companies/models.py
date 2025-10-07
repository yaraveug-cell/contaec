from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from apps.core.models import BaseModel, City, Currency, DocumentType

User = get_user_model()


class CompanyType(BaseModel):
    """Tipos de empresa según legislación ecuatoriana"""
    PERSONA_NATURAL = 'PN'
    SOCIEDAD_ANONIMA = 'SA'
    COMPANIA_LIMITADA = 'CL'
    SOCIEDAD_CIVIL = 'SC'
    
    TYPE_CHOICES = [
        (PERSONA_NATURAL, 'Persona Natural'),
        (SOCIEDAD_ANONIMA, 'Sociedad Anónima'),
        (COMPANIA_LIMITADA, 'Compañía de Responsabilidad Limitada'),
        (SOCIEDAD_CIVIL, 'Sociedad Civil'),
    ]
    
    code = models.CharField(max_length=2, choices=TYPE_CHOICES, unique=True, verbose_name='Código')
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    
    class Meta:
        verbose_name = 'Tipo de Empresa'
        verbose_name_plural = 'Tipos de Empresa'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PaymentMethod(BaseModel):
    """Métodos de pago para empresas"""
    name = models.CharField(max_length=50, unique=True, verbose_name='Forma de Pago')
    description = models.TextField(blank=True, verbose_name='Descripción')
    parent_account = models.ForeignKey(
        'accounting.ChartOfAccounts',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Cuenta Padre'
    )
    
    class Meta:
        verbose_name = 'Forma de Pago'
        verbose_name_plural = 'Formas de Pago'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class EconomicActivity(BaseModel):
    """Actividades económicas según CIIU Ecuador"""
    code = models.CharField(max_length=6, unique=True, verbose_name='Código CIIU')
    description = models.TextField(verbose_name='Descripción')
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name='Actividad padre'
    )
    
    class Meta:
        verbose_name = 'Actividad Económica'
        verbose_name_plural = 'Actividades Económicas'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.description[:50]}"


class Company(BaseModel):
    """Empresas del sistema"""
    # Información básica
    trade_name = models.CharField(max_length=200, verbose_name='Nombre comercial')
    legal_name = models.CharField(max_length=300, verbose_name='Razón social')
    company_type = models.ForeignKey(
        CompanyType, 
        on_delete=models.PROTECT, 
        verbose_name='Tipo de empresa'
    )
    
    # Identificación fiscal
    ruc = models.CharField(max_length=13, unique=True, verbose_name='RUC')
    establishment_code = models.CharField(
        max_length=3, 
        default='001', 
        verbose_name='Código de establecimiento'
    )
    emission_point = models.CharField(
        max_length=3, 
        default='001', 
        verbose_name='Punto de emisión'
    )
    
    # Actividad económica
    primary_activity = models.ForeignKey(
        EconomicActivity, 
        on_delete=models.PROTECT, 
        related_name='companies_primary',
        verbose_name='Actividad económica principal'
    )
    secondary_activities = models.ManyToManyField(
        EconomicActivity, 
        blank=True,
        related_name='companies_secondary',
        verbose_name='Actividades económicas secundarias'
    )
    
    # Ubicación
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name='Ciudad')
    address = models.TextField(verbose_name='Dirección')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    email = models.EmailField(blank=True, verbose_name='Correo electrónico')
    website = models.URLField(blank=True, verbose_name='Sitio web')
    
    # Configuración contable
    base_currency = models.ForeignKey(
        Currency, 
        on_delete=models.PROTECT, 
        verbose_name='Moneda base'
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Forma de Pago'
    )
    fiscal_year_start = models.IntegerField(
        choices=[(i, f"{i:02d}") for i in range(1, 13)],
        default=1,
        verbose_name='Mes de inicio del ejercicio fiscal'
    )
    
    # SRI Configuration
    sri_environment = models.CharField(
        max_length=1, 
        choices=[('1', 'Pruebas'), ('2', 'Producción')],
        default='1',
        verbose_name='Ambiente SRI'
    )
    certificate_file = models.FileField(
        upload_to='certificates/', 
        null=True, 
        blank=True,
        verbose_name='Certificado digital (.p12)'
    )
    certificate_password = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name='Contraseña del certificado'
    )
    
    # Logo y branding
    logo = models.ImageField(
        upload_to='company_logos/', 
        null=True, 
        blank=True,
        verbose_name='Logo'
    )
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['trade_name']
    
    def __str__(self):
        return self.trade_name


class CompanyUser(BaseModel):
    """Relación usuario-empresa con roles"""
    OWNER = 'owner'
    ADMIN = 'admin'
    ACCOUNTANT = 'accountant'
    EMPLOYEE = 'employee'
    VIEWER = 'viewer'
    
    ROLE_CHOICES = [
        (OWNER, 'Propietario'),
        (ADMIN, 'Administrador'),
        (ACCOUNTANT, 'Contador'),
        (EMPLOYEE, 'Empleado'),
        (VIEWER, 'Solo lectura'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa')
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        verbose_name='Rol'
    )
    permissions = models.JSONField(
        default=dict, 
        blank=True,
        verbose_name='Permisos específicos'
    )
    
    class Meta:
        verbose_name = 'Usuario de Empresa'
        verbose_name_plural = 'Usuarios de Empresa'
        unique_together = ['user', 'company']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.company.trade_name} ({self.get_role_display()})"


class CompanyAccountDefaults(BaseModel):
    """Configuración por defecto de cuentas contables para cada empresa"""
    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        verbose_name='Empresa',
        related_name='account_defaults'
    )
    
    # Cuentas base para ventas
    default_sales_account = models.ForeignKey(
        'accounting.ChartOfAccounts',
        on_delete=models.PROTECT,
        related_name='company_sales_defaults',
        null=True,
        blank=True,
        verbose_name='Cuenta de Ventas por Defecto',
        help_text='Cuenta contable por defecto para registrar ventas'
    )
    
    # Cuentas para retenciones por cobrar
    iva_retention_receivable_account = models.ForeignKey(
        'accounting.ChartOfAccounts',
        on_delete=models.PROTECT,
        related_name='company_iva_retention_defaults',
        null=True,
        blank=True,
        verbose_name='Cuenta Retención IVA por Cobrar',
        help_text='Cuenta para registrar retenciones de IVA realizadas por clientes'
    )
    
    ir_retention_receivable_account = models.ForeignKey(
        'accounting.ChartOfAccounts',
        on_delete=models.PROTECT,
        related_name='company_ir_retention_defaults',
        null=True,
        blank=True,
        verbose_name='Cuenta Retención IR por Cobrar',
        help_text='Cuenta para registrar retenciones de Impuesto a la Renta realizadas por clientes'
    )
    
    class Meta:
        verbose_name = 'Configuración Contable por Defecto'
        verbose_name_plural = 'Configuraciones Contables por Defecto'
    
    def __str__(self):
        return f"Configuración contable - {self.company.trade_name}"


class CompanyTaxAccountMapping(BaseModel):
    """Configuración de cuentas contables por tipo de IVA para cada empresa"""
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        verbose_name='Empresa'
    )
    tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        verbose_name='Tasa de IVA (%)'
    )
    
    # Cuenta para IVA en ventas
    account = models.ForeignKey(
        'accounting.ChartOfAccounts',
        on_delete=models.PROTECT,
        verbose_name='Cuenta IVA en Ventas',
        help_text='Cuenta contable para registrar IVA cobrado en ventas'
    )
    
    # NUEVA: Cuenta para retención de IVA por cobrar específica para esta tarifa
    retention_account = models.ForeignKey(
        'accounting.ChartOfAccounts',
        on_delete=models.PROTECT,
        related_name='tax_retention_mappings',
        null=True,
        blank=True,
        verbose_name='Cuenta Retención IVA por Cobrar',
        help_text='Cuenta específica para retenciones de IVA de esta tarifa'
    )
    
    class Meta:
        verbose_name = 'Configuración de Cuenta IVA'
        verbose_name_plural = 'Configuraciones de Cuentas IVA'
        unique_together = ['company', 'tax_rate']
        ordering = ['tax_rate']
    
    def __str__(self):
        return f"{self.company.trade_name} - IVA {self.tax_rate}% → {self.account.code}"


class CompanySettings(BaseModel):
    """Configuraciones específicas de la empresa"""
    company = models.OneToOneField(
        Company, 
        on_delete=models.CASCADE, 
        verbose_name='Empresa'
    )
    
    # Configuraciones de facturación
    invoice_sequential = models.PositiveIntegerField(
        default=1, 
        verbose_name='Secuencial de facturas'
    )
    purchase_invoice_sequential = models.PositiveIntegerField(
        default=1, 
        verbose_name='Secuencial de facturas de compra'
    )
    credit_note_sequential = models.PositiveIntegerField(
        default=1, 
        verbose_name='Secuencial de notas de crédito'
    )
    debit_note_sequential = models.PositiveIntegerField(
        default=1, 
        verbose_name='Secuencial de notas de débito'
    )
    withholding_sequential = models.PositiveIntegerField(
        default=1, 
        verbose_name='Secuencial de retenciones'
    )
    
    # Configuraciones contables
    decimal_places = models.IntegerField(
        default=2, 
        verbose_name='Decimales en montos'
    )
    auto_create_entries = models.BooleanField(
        default=True, 
        verbose_name='Crear asientos automáticamente'
    )
    
    # Configuraciones de reportes
    default_report_format = models.CharField(
        max_length=10,
        choices=[('PDF', 'PDF'), ('XLSX', 'Excel')],
        default='PDF',
        verbose_name='Formato de reportes por defecto'
    )
    
    # Configuraciones fiscales
    default_iva_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('15.00'),
        verbose_name='IVA por defecto (%)',
        help_text='Tasa de IVA que se aplicará por defecto en nuevos productos y facturas. No afecta facturas existentes.'
    )
    
    class Meta:
        verbose_name = 'Configuración de Empresa'
        verbose_name_plural = 'Configuraciones de Empresa'
    
    def __str__(self):
        return f"Configuración de {self.company.trade_name}"