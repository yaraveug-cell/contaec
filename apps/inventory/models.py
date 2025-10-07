from django.db import models
from decimal import Decimal
from apps.core.models import BaseModel
from apps.companies.models import Company
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(BaseModel):
    """Categorías de productos"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa')
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name='Categoría padre'
    )
    
    # Configuración contable opcional (ESTRATEGIA B - Híbrida)
    default_sales_account = models.ForeignKey(
        'accounting.ChartOfAccounts',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='sales_categories',
        verbose_name='Cuenta de ventas por defecto',
        help_text='Cuenta contable que se usará automáticamente para ventas de productos de esta categoría'
    )
    default_cost_account = models.ForeignKey(
        'accounting.ChartOfAccounts',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='cost_categories',
        verbose_name='Cuenta de costo por defecto',
        help_text='Cuenta contable para el costo de ventas de productos de esta categoría'
    )
    default_inventory_account = models.ForeignKey(
        'accounting.ChartOfAccounts',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='inventory_categories',
        verbose_name='Cuenta de inventario por defecto',
        help_text='Cuenta contable para el inventario de productos de esta categoría'
    )
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        unique_together = ['company', 'name']
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Warehouse(BaseModel):
    """Bodegas/Almacenes"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa')
    code = models.CharField(max_length=10, verbose_name='Código')
    name = models.CharField(max_length=100, verbose_name='Nombre')
    address = models.TextField(verbose_name='Dirección')
    responsible = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        verbose_name='Responsable'
    )
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    class Meta:
        verbose_name = 'Bodega'
        verbose_name_plural = 'Bodegas'
        unique_together = ['company', 'code']
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Product(BaseModel):
    """Productos para inventario"""
    PRODUCT = 'product'
    SERVICE = 'service'
    KIT = 'kit'
    
    TYPE_CHOICES = [
        (PRODUCT, 'Producto'),
        (SERVICE, 'Servicio'),
        (KIT, 'Kit/Paquete'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='inventory_products', verbose_name='Empresa')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Categoría')
    
    code = models.CharField(max_length=50, verbose_name='Código')
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    product_type = models.CharField(
        max_length=10, 
        choices=TYPE_CHOICES, 
        default=PRODUCT,
        verbose_name='Tipo'
    )
    
    # Unidades de medida
    unit_of_measure = models.CharField(max_length=20, verbose_name='Unidad de medida')
    
    # Control de inventario
    manages_inventory = models.BooleanField(default=True, verbose_name='Maneja inventario')
    minimum_stock = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Stock mínimo'
    )
    maximum_stock = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Stock máximo'
    )
    
    # Precios
    cost_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Precio de costo'
    )
    sale_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Precio de venta'
    )
    
    # Configuración fiscal (para facturación)
    has_iva = models.BooleanField(default=True, verbose_name='Aplica IVA')
    iva_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('12.00'),
        verbose_name='Tarifa IVA (%)'
    )
    
    # Estado
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        unique_together = ['company', 'code']
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def save(self, *args, **kwargs):
        """Guardar producto con configuraciones por defecto de la empresa"""
        # Si es un nuevo producto y no tiene configurado el IVA rate, usar el por defecto de la empresa
        if not self.pk and self.has_iva and self.iva_rate == Decimal('12.00'):
            from apps.companies.models import CompanySettings
            company_settings, created = CompanySettings.objects.get_or_create(company=self.company)
            self.iva_rate = company_settings.default_iva_rate
        
        super().save(*args, **kwargs)
    
    def get_price_with_tax(self):
        """Calcula el precio de venta con IVA incluido"""
        if self.has_iva:
            return self.sale_price * (1 + self.iva_rate / 100)
        return self.sale_price
    
    def get_current_stock(self, warehouse=None):
        """Obtiene el stock actual del producto"""
        if not self.manages_inventory:
            return None
            
        if warehouse:
            stock_obj = Stock.objects.filter(product=self, warehouse=warehouse).first()
            return stock_obj.quantity if stock_obj else Decimal('0.00')
        else:
            # Total en todas las bodegas
            return Stock.objects.filter(product=self).aggregate(
                total=models.Sum('quantity')
            )['total'] or Decimal('0.00')
    
    def has_sufficient_stock(self, quantity, warehouse=None):
        """Verifica si hay stock suficiente para la cantidad solicitada"""
        if not self.manages_inventory:
            return True  # Los servicios no manejan stock
            
        current_stock = self.get_current_stock(warehouse)
        return current_stock >= quantity if current_stock is not None else False
    
    # ========================
    # ESTRATEGIA B - MÉTODOS DE CUENTAS CONTABLES INTELIGENTES
    # ========================
    
    def get_effective_sales_account(self):
        """
        Obtiene la cuenta de ventas efectiva con lógica de fallback:
        1. Cuenta específica de la categoría del producto
        2. Cuenta por defecto de la empresa
        3. Primera cuenta de ventas disponible (código 4)
        """
        # Prioridad 1: Cuenta específica de la categoría
        if (self.category and 
            self.category.default_sales_account and 
            self.category.default_sales_account.accepts_movement):
            return self.category.default_sales_account
        
        # Prioridad 2: Cuenta por defecto de la empresa (si existe configuración)
        try:
            from apps.companies.models import CompanyAccountDefaults
            defaults = CompanyAccountDefaults.objects.get(company=self.company)
            if (defaults.default_sales_account and 
                defaults.default_sales_account.accepts_movement):
                return defaults.default_sales_account
        except:
            pass  # Si no existe el modelo o configuración, continuar al fallback
        
        # Prioridad 3: Primera cuenta de ventas disponible (fallback actual)
        from apps.accounting.models import ChartOfAccounts
        return ChartOfAccounts.objects.filter(
            company=self.company,
            code__startswith='4',
            accepts_movement=True,
            is_detail=True
        ).first()
    
    def get_effective_cost_account(self):
        """
        Obtiene la cuenta de costo de ventas efectiva con lógica de fallback:
        1. Cuenta específica de la categoría del producto  
        2. Cuenta por defecto de la empresa
        3. Primera cuenta de costos disponible (código 5.1)
        """
        # Prioridad 1: Cuenta específica de la categoría
        if (self.category and 
            self.category.default_cost_account and 
            self.category.default_cost_account.accepts_movement):
            return self.category.default_cost_account
        
        # Prioridad 2: Cuenta por defecto de la empresa (si existe configuración)
        try:
            from apps.companies.models import CompanyAccountDefaults
            defaults = CompanyAccountDefaults.objects.get(company=self.company)
            if (defaults.default_cost_account and 
                defaults.default_cost_account.accepts_movement):
                return defaults.default_cost_account
        except:
            pass
        
        # Prioridad 3: Primera cuenta de costos disponible (fallback)
        from apps.accounting.models import ChartOfAccounts
        return ChartOfAccounts.objects.filter(
            company=self.company,
            code__startswith='5.1',
            accepts_movement=True,
            is_detail=True
        ).first()
    
    def get_effective_inventory_account(self):
        """
        Obtiene la cuenta de inventario efectiva con lógica de fallback:
        1. Cuenta específica de la categoría del producto
        2. Cuenta por defecto de la empresa  
        3. Primera cuenta de inventario disponible (código 1.1)
        """
        # Prioridad 1: Cuenta específica de la categoría
        if (self.category and 
            self.category.default_inventory_account and 
            self.category.default_inventory_account.accepts_movement):
            return self.category.default_inventory_account
        
        # Prioridad 2: Cuenta por defecto de la empresa (si existe configuración)
        try:
            from apps.companies.models import CompanyAccountDefaults
            defaults = CompanyAccountDefaults.objects.get(company=self.company)
            if (defaults.default_inventory_account and 
                defaults.default_inventory_account.accepts_movement):
                return defaults.default_inventory_account
        except:
            pass
        
        # Prioridad 3: Primera cuenta de inventario disponible (fallback)
        from apps.accounting.models import ChartOfAccounts
        return ChartOfAccounts.objects.filter(
            company=self.company,
            code__startswith='1.1',
            accepts_movement=True,
            is_detail=True
        ).first()
    
    def get_account_configuration_status(self):
        """
        Retorna el estado de configuración de cuentas contables para este producto.
        Útil para dashboards y validaciones.
        """
        return {
            'sales_configured': bool(self.category and self.category.default_sales_account),
            'cost_configured': bool(self.category and self.category.default_cost_account),
            'inventory_configured': bool(self.category and self.category.default_inventory_account),
            'category_name': self.category.name if self.category else 'Sin categoría',
            'effective_sales_account': self.get_effective_sales_account(),
            'effective_cost_account': self.get_effective_cost_account(),
            'effective_inventory_account': self.get_effective_inventory_account()
        }


class StockMovement(BaseModel):
    """Movimientos de inventario"""
    IN = 'in'
    OUT = 'out'
    TRANSFER = 'transfer'
    ADJUSTMENT = 'adjustment'
    
    TYPE_CHOICES = [
        (IN, 'Entrada'),
        (OUT, 'Salida'),
        (TRANSFER, 'Transferencia'),
        (ADJUSTMENT, 'Ajuste'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Producto')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name='Bodega')
    
    movement_type = models.CharField(
        max_length=10, 
        choices=TYPE_CHOICES, 
        verbose_name='Tipo de movimiento'
    )
    
    date = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    reference = models.CharField(max_length=100, blank=True, verbose_name='Referencia')
    description = models.TextField(verbose_name='Descripción')
    
    # Cantidades
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Cantidad')
    unit_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Costo unitario'
    )
    total_cost = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Costo total'
    )
    
    # Usuario responsable
    created_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        verbose_name='Creado por'
    )
    
    class Meta:
        verbose_name = 'Movimiento de Stock'
        verbose_name_plural = 'Movimientos de Stock'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.product.code} - {self.get_movement_type_display()}"


class Stock(BaseModel):
    """Stock actual por bodega"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Producto')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name='Bodega')
    
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Cantidad'
    )
    average_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Costo promedio'
    )
    
    last_movement = models.DateTimeField(null=True, blank=True, verbose_name='Último movimiento')
    
    class Meta:
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'
        unique_together = ['product', 'warehouse']
        ordering = ['product__code']
    
    def __str__(self):
        return f"{self.product.code} - {self.warehouse.code}: {self.quantity}"