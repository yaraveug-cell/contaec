"""
Modelos para el módulo de nómina
Sistema de contabilidad para pequeñas empresas ecuatorianas
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from apps.companies.models import Company
from apps.users.models import User


class EmployeeCategory(models.Model):
    """Categorías de empleados"""
    name = models.CharField('Nombre', max_length=100)
    description = models.TextField('Descripción', blank=True)
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Categoría de Empleado'
        verbose_name_plural = 'Categorías de Empleados'
    
    def __str__(self):
        return self.name


class Employee(models.Model):
    """Empleados de la empresa"""
    CIVIL_STATUS_CHOICES = [
        ('soltero', 'Soltero/a'),
        ('casado', 'Casado/a'),
        ('divorciado', 'Divorciado/a'),
        ('viudo', 'Viudo/a'),
        ('union_libre', 'Unión Libre'),
    ]
    
    EMPLOYMENT_STATUS_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('vacaciones', 'En Vacaciones'),
        ('licencia', 'En Licencia'),
        ('terminado', 'Terminado'),
    ]
    
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        verbose_name='Empresa',
        related_name='payroll_employees'
    )
    
    # Información personal
    cedula = models.CharField('Cédula', max_length=10, unique=True)
    first_name = models.CharField('Nombres', max_length=100)
    last_name = models.CharField('Apellidos', max_length=100)
    email = models.EmailField('Email', blank=True)
    phone = models.CharField('Teléfono', max_length=20, blank=True)
    address = models.TextField('Dirección', blank=True)
    birth_date = models.DateField('Fecha de Nacimiento', null=True, blank=True)
    civil_status = models.CharField('Estado Civil', max_length=20, choices=CIVIL_STATUS_CHOICES, default='soltero')
    
    # Información laboral
    employee_code = models.CharField('Código de Empleado', max_length=20, unique=True)
    hire_date = models.DateField('Fecha de Ingreso')
    position = models.CharField('Cargo', max_length=100)
    department = models.CharField('Departamento', max_length=100, blank=True)
    category = models.ForeignKey(
        EmployeeCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Categoría',
        related_name='payroll_category_employees'
    )
    
    # Información salarial
    base_salary = models.DecimalField(
        'Salario Base', 
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Estado
    status = models.CharField('Estado', max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, default='activo')
    termination_date = models.DateField('Fecha de Terminación', null=True, blank=True)
    
    # Auditoría
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)
    
    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        unique_together = ['company', 'employee_code']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.employee_code}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class PayrollPeriod(models.Model):
    """Períodos de nómina"""
    PERIOD_TYPE_CHOICES = [
        ('mensual', 'Mensual'),
        ('quincenal', 'Quincenal'),
        ('semanal', 'Semanal'),
    ]
    
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        verbose_name='Empresa',
        related_name='payroll_periods'
    )
    name = models.CharField('Nombre del Período', max_length=100)
    period_type = models.CharField('Tipo de Período', max_length=20, choices=PERIOD_TYPE_CHOICES, default='mensual')
    start_date = models.DateField('Fecha de Inicio')
    end_date = models.DateField('Fecha de Fin')
    payment_date = models.DateField('Fecha de Pago')
    is_closed = models.BooleanField('Cerrado', default=False)
    
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)
    
    class Meta:
        verbose_name = 'Período de Nómina'
        verbose_name_plural = 'Períodos de Nómina'
        unique_together = ['company', 'start_date', 'end_date']
    
    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"


class PayrollConcept(models.Model):
    """Conceptos de nómina (ingresos, deducciones, aportes)"""
    CONCEPT_TYPE_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('deduccion', 'Deducción'),
        ('aporte_empleador', 'Aporte Empleador'),
    ]
    
    CALCULATION_TYPE_CHOICES = [
        ('fijo', 'Valor Fijo'),
        ('porcentaje', 'Porcentaje'),
        ('formula', 'Fórmula'),
    ]
    
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        verbose_name='Empresa',
        related_name='payroll_concepts'
    )
    code = models.CharField('Código', max_length=20)
    name = models.CharField('Nombre', max_length=100)
    description = models.TextField('Descripción', blank=True)
    concept_type = models.CharField('Tipo de Concepto', max_length=20, choices=CONCEPT_TYPE_CHOICES)
    calculation_type = models.CharField('Tipo de Cálculo', max_length=20, choices=CALCULATION_TYPE_CHOICES, default='fijo')
    
    # Para cálculos porcentuales
    percentage = models.DecimalField(
        'Porcentaje', 
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))]
    )
    
    # Para valores fijos
    fixed_amount = models.DecimalField(
        'Valor Fijo', 
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    # Configuración
    is_active = models.BooleanField('Activo', default=True)
    affects_iess = models.BooleanField('Afecta IESS', default=False)
    affects_income_tax = models.BooleanField('Afecta Impuesto a la Renta', default=False)
    
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Concepto de Nómina'
        verbose_name_plural = 'Conceptos de Nómina'
        unique_together = ['company', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Payroll(models.Model):
    """Nómina principal"""
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        verbose_name='Empresa',
        related_name='payrolls'
    )
    period = models.ForeignKey(
        PayrollPeriod, 
        on_delete=models.CASCADE, 
        verbose_name='Período',
        related_name='payrolls'
    )
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        verbose_name='Empleado',
        related_name='payrolls'
    )
    
    # Totales calculados
    total_income = models.DecimalField('Total Ingresos', max_digits=10, decimal_places=2, default=0)
    total_deductions = models.DecimalField('Total Deducciones', max_digits=10, decimal_places=2, default=0)
    total_employer_contributions = models.DecimalField('Total Aportes Empleador', max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField('Salario Neto', max_digits=10, decimal_places=2, default=0)
    
    # Estado
    is_processed = models.BooleanField('Procesado', default=False)
    is_paid = models.BooleanField('Pagado', default=False)
    payment_date = models.DateField('Fecha de Pago', null=True, blank=True)
    
    # Auditoría
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)
    processed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Procesado por',
        related_name='processed_payrolls'
    )
    
    class Meta:
        verbose_name = 'Nómina'
        verbose_name_plural = 'Nóminas'
        unique_together = ['period', 'employee']
    
    def __str__(self):
        return f"Nómina {self.employee.full_name} - {self.period.name}"


class PayrollDetail(models.Model):
    """Detalles de nómina por concepto"""
    payroll = models.ForeignKey(
        Payroll, 
        on_delete=models.CASCADE, 
        verbose_name='Nómina',
        related_name='details'
    )
    concept = models.ForeignKey(
        PayrollConcept, 
        on_delete=models.CASCADE, 
        verbose_name='Concepto',
        related_name='payroll_concept_details'
    )
    
    quantity = models.DecimalField('Cantidad', max_digits=10, decimal_places=2, default=1)
    unit_value = models.DecimalField('Valor Unitario', max_digits=10, decimal_places=2, default=0)
    total_value = models.DecimalField('Valor Total', max_digits=10, decimal_places=2, default=0)
    
    # Observaciones
    notes = models.TextField('Observaciones', blank=True)
    
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Detalle de Nómina'
        verbose_name_plural = 'Detalles de Nómina'
        unique_together = ['payroll', 'concept']
    
    def __str__(self):
        return f"{self.payroll.employee.full_name} - {self.concept.name}: ${self.total_value}"
    
    def save(self, *args, **kwargs):
        self.total_value = self.quantity * self.unit_value
        super().save(*args, **kwargs)