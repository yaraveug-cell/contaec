"""
Modelos del módulo Banking
Implementación gradual sin afectar funcionalidades existentes del sistema contable
"""

from django.db import models
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.conf import settings
from apps.core.models import BaseModel


class Bank(BaseModel):
    """
    Catálogo de instituciones bancarias ecuatorianas
    Independiente del sistema contable existente
    """
    sbs_code = models.CharField(
        max_length=4, 
        unique=True, 
        verbose_name='Código SBS',
        help_text='Código de la Superintendencia de Bancos del Ecuador'
    )
    name = models.CharField(
        max_length=100, 
        verbose_name='Nombre del Banco'
    )
    short_name = models.CharField(
        max_length=20, 
        verbose_name='Nombre Corto',
        help_text='Nombre abreviado para mostrar en interfaces'
    )
    swift_code = models.CharField(
        max_length=11, 
        blank=True, 
        verbose_name='Código SWIFT',
        help_text='Código SWIFT para transferencias internacionales'
    )
    website = models.URLField(
        blank=True, 
        verbose_name='Sitio Web'
    )
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name='Teléfono'
    )
    
    class Meta:
        verbose_name = 'Banco'
        verbose_name_plural = 'Bancos'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BankAccount(BaseModel):
    """
    Cuentas bancarias por empresa
    Integración OPCIONAL con sistema contable existente
    """
    
    ACCOUNT_TYPES = [
        ('checking', 'Cuenta Corriente'),
        ('savings', 'Cuenta de Ahorros'),
        ('credit', 'Tarjeta de Crédito'),
        ('other', 'Otra'),
    ]
    
    CURRENCIES = [
        ('USD', 'Dólares Americanos'),
        ('EUR', 'Euros'),
        ('COL', 'Pesos Colombianos'),
    ]
    
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        verbose_name='Empresa'
    )
    bank = models.ForeignKey(
        Bank,
        on_delete=models.PROTECT,
        verbose_name='Banco'
    )
    account_number = models.CharField(
        max_length=50,
        verbose_name='Número de Cuenta'
    )
    account_type = models.CharField(
        max_length=10,
        choices=ACCOUNT_TYPES,
        default='checking',
        verbose_name='Tipo de Cuenta'
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCIES,
        default='USD',
        verbose_name='Moneda'
    )
    
    # Integración OPCIONAL con sistema contable existente
    # NO obligatorio para mantener compatibilidad
    chart_account = models.ForeignKey(
        'accounting.ChartOfAccounts',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={'aux_type': 'bank'},
        verbose_name='Cuenta Contable',
        help_text='Vincular con cuenta contable existente (opcional)'
    )
    
    # Información adicional
    initial_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Saldo Inicial'
    )
    opening_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Apertura'
    )
    contact_person = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Persona de Contacto'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    class Meta:
        verbose_name = 'Cuenta Bancaria'
        verbose_name_plural = 'Cuentas Bancarias'
        ordering = ['bank__name', 'account_number']
        unique_together = ['company', 'bank', 'account_number']
    
    def __str__(self):
        return f"{self.bank.short_name} - {self.account_number}"
    
    @property
    def masked_account_number(self):
        """Número de cuenta enmascarado para seguridad"""
        if len(self.account_number) > 4:
            return f"****{self.account_number[-4:]}"
        return self.account_number
    
    def get_account_display(self):
        """Representación completa para mostrar en selectors"""
        return f"{self.bank.name} - {self.get_account_type_display()} - {self.masked_account_number}"


class BankTransaction(BaseModel):
    """
    Movimientos bancarios (para futuras implementaciones)
    Preparado para conciliación bancaria
    """
    
    TRANSACTION_TYPES = [
        ('debit', 'Débito'),
        ('credit', 'Crédito'),
        ('transfer_in', 'Transferencia Recibida'),
        ('transfer_out', 'Transferencia Enviada'),
        ('fee', 'Comisión Bancaria'),
        ('interest', 'Interés'),
        ('other', 'Otro'),
    ]
    
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        verbose_name='Cuenta Bancaria'
    )
    transaction_date = models.DateField(
        verbose_name='Fecha de Transacción'
    )
    value_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Valor'
    )
    transaction_type = models.CharField(
        max_length=15,
        choices=TRANSACTION_TYPES,
        verbose_name='Tipo de Transacción'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Monto'
    )
    description = models.TextField(
        verbose_name='Descripción'
    )
    reference = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Referencia'
    )
    
    # Integración OPCIONAL con contabilidad
    journal_entry = models.ForeignKey(
        'accounting.JournalEntry',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Asiento Contable'
    )
    
    is_reconciled = models.BooleanField(
        default=False,
        verbose_name='Conciliado'
    )
    reconciliation_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Conciliación'
    )
    reconciled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Conciliado por'
    )
    
    class Meta:
        verbose_name = 'Movimiento Bancario'
        verbose_name_plural = 'Movimientos Bancarios'
        ordering = ['-transaction_date', '-created_at']
    
    def __str__(self):
        return f"{self.bank_account} - {self.transaction_date} - {self.amount}"
    
    @property
    def is_debit(self):
        """True si es un débito (disminuye el saldo)"""
        return self.transaction_type in ['debit', 'transfer_out', 'fee']
    
    @property
    def signed_amount(self):
        """Monto con signo según tipo de transacción"""
        return -self.amount if self.is_debit else self.amount


class ExtractoBancario(BaseModel):
    """
    Extractos bancarios importados para conciliación
    """
    
    STATUS_CHOICES = [
        ('uploaded', 'Cargado'),
        ('processing', 'Procesando'),
        ('processed', 'Procesado'),
        ('reconciled', 'Conciliado'),
        ('error', 'Error'),
    ]
    
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        verbose_name='Cuenta Bancaria'
    )
    file = models.FileField(
        upload_to='extractos_bancarios/%Y/%m/',
        verbose_name='Archivo del Extracto'
    )
    period_start = models.DateField(
        verbose_name='Fecha Inicio del Período'
    )
    period_end = models.DateField(
        verbose_name='Fecha Fin del Período'
    )
    initial_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Saldo Inicial'
    )
    final_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Saldo Final'
    )
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default='uploaded',
        verbose_name='Estado'
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Subido por'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Procesado el'
    )
    
    class Meta:
        verbose_name = 'Extracto Bancario'
        verbose_name_plural = 'Extractos Bancarios'
        ordering = ['-period_end', '-created_at']
    
    def __str__(self):
        return f"{self.bank_account} - {self.period_start} a {self.period_end}"
    
    def clean(self):
        if self.period_start and self.period_end and self.period_start > self.period_end:
            raise ValidationError('La fecha de inicio no puede ser mayor que la fecha de fin')


class ExtractoBancarioDetalle(BaseModel):
    """
    Líneas individuales del extracto bancario
    """
    
    extracto = models.ForeignKey(
        ExtractoBancario,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Extracto'
    )
    fecha = models.DateField(
        verbose_name='Fecha'
    )
    descripcion = models.TextField(
        verbose_name='Descripción'
    )
    referencia = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Referencia'
    )
    debito = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Débito'
    )
    credito = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Crédito'
    )
    saldo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Saldo'
    )
    is_reconciled = models.BooleanField(
        default=False,
        verbose_name='Conciliado'
    )
    matched_transaction = models.ForeignKey(
        BankTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Transacción Coincidente'
    )
    
    class Meta:
        verbose_name = 'Detalle de Extracto'
        verbose_name_plural = 'Detalles de Extracto'
        ordering = ['fecha', 'id']
    
    def __str__(self):
        return f"{self.fecha} - {self.descripcion[:50]}"
    
    @property
    def monto(self):
        """Retorna el monto de la transacción (débito o crédito)"""
        return self.credito if self.credito else self.debito
    
    @property
    def tipo_movimiento(self):
        """Retorna si es débito o crédito"""
        return 'credito' if self.credito else 'debito'