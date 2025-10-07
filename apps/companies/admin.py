from django.contrib import admin
from .models import CompanyType, EconomicActivity, Company, CompanyUser, CompanySettings, PaymentMethod, CompanyTaxAccountMapping, CompanyAccountDefaults
from apps.core.filters import UserCompanyListFilter

# Importación opcional del módulo banking para integración gradual
try:
    from apps.banking.admin import BankAccountInline
    BANKING_MODULE_AVAILABLE = True
except ImportError:
    BANKING_MODULE_AVAILABLE = False
    BankAccountInline = None

# CompanyAccountDefaults y CompanyTaxAccountMapping se configuran
# solo como inlines dentro de Company para evitar duplicación


class CompanyFilterMixin:
    """Mixin para filtrar por empresa del usuario"""
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        # Filtrar por empresas del usuario
        user_companies = request.session.get('user_companies', [])
        if user_companies and user_companies != 'all':
            # Para el modelo Company, filtrar directamente por ID
            if self.model == Company:
                return qs.filter(id__in=user_companies)
            # Para otros modelos, buscar el campo de empresa
            elif hasattr(self.model, 'company'):
                return qs.filter(company_id__in=user_companies)
            elif hasattr(self.model, 'user') and hasattr(self.model, 'company'):
                # Para CompanyUser, filtrar por empresa del usuario
                return qs.filter(company_id__in=user_companies)
        return qs.none()
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "company":
            if not request.user.is_superuser:
                user_companies = request.session.get('user_companies', [])
                if user_companies and user_companies != 'all':
                    kwargs["queryset"] = db_field.related_model.objects.filter(
                        id__in=user_companies
                    )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(CompanyType)
class CompanyTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent_account', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_select_related = ['parent_account']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'parent_account', 'is_active')
        }),
    )


@admin.register(EconomicActivity)
class EconomicActivityAdmin(admin.ModelAdmin):
    list_display = ['code', 'description', 'parent', 'is_active']
    list_filter = ['parent', 'is_active']
    search_fields = ['code', 'description']
    list_select_related = ['parent']


class CompanyAccountDefaultsInline(admin.StackedInline):
    """Inline para configurar cuentas contables por defecto"""
    model = CompanyAccountDefaults
    max_num = 1
    extra = 0
    fields = (
        ('default_sales_account',),
        ('iva_retention_receivable_account', 'ir_retention_receivable_account'),
    )
    verbose_name = 'Configuración Contable por Defecto'
    verbose_name_plural = 'Configuración Contable por Defecto'


class CompanyTaxAccountMappingInline(admin.TabularInline):
    """Inline para configurar cuentas IVA por empresa"""
    model = CompanyTaxAccountMapping
    extra = 1
    fields = ('tax_rate', 'account', 'retention_account')
    verbose_name = 'Configuración Cuenta IVA'
    verbose_name_plural = 'Configuraciones Cuentas IVA'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('account', 'retention_account')


@admin.register(Company)
class CompanyAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ['trade_name', 'legal_name', 'ruc', 'company_type', 'city', 'is_active']
    list_filter = ['company_type', 'city__province', 'is_active', 'sri_environment']
    search_fields = ['trade_name', 'legal_name', 'ruc', 'email']
    list_select_related = ['company_type', 'city', 'base_currency', 'primary_activity']
    
    def get_queryset(self, request):
        """
        🔧 OVERRIDE: Usar CompanyUser directo en lugar de sesión para autocomplete
        
        El CompanyFilterMixin original usa request.session.get('user_companies', [])
        que no funciona para autocomplete. Esta versión usa CompanyUser directo.
        """
        qs = super(CompanyFilterMixin, self).get_queryset(request)  # Saltar CompanyFilterMixin
        
        if request.user.is_superuser:
            return qs
        
        # Usar CompanyUser directo (como BankingAdmin y otros módulos)
        from apps.companies.models import CompanyUser
        user_companies = CompanyUser.objects.filter(
            user=request.user, 
            is_active=True
        ).values_list('company_id', flat=True)
        
        if user_companies:
            return qs.filter(id__in=user_companies)
        else:
            return qs.none()
    
    # Configurar inlines dinámicamente
    def get_inlines(self, request, obj):
        """Configurar inlines dinámicamente según módulos disponibles"""
        inlines = [CompanyAccountDefaultsInline, CompanyTaxAccountMappingInline]
        
        # Agregar inline de cuentas bancarias si el módulo está disponible
        if BANKING_MODULE_AVAILABLE and BankAccountInline:
            inlines.append(BankAccountInline)
        
        return inlines
    
    @property
    def inlines(self):
        """Inlines por defecto (para compatibilidad)"""
        return [CompanyAccountDefaultsInline, CompanyTaxAccountMappingInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('trade_name', 'legal_name', 'company_type')
        }),
        ('Identificación Fiscal', {
            'fields': ('ruc', 'establishment_code', 'emission_point')
        }),
        ('Actividad Económica', {
            'fields': ('primary_activity', 'secondary_activities')
        }),
        ('Ubicación y Contacto', {
            'fields': ('city', 'address', 'phone', 'email', 'website')
        }),
        ('Configuración Contable', {
            'fields': ('base_currency', 'payment_method', 'fiscal_year_start'),
            'description': 'Configuración contable y cuentas por defecto. Las cuentas IVA se configuran en la sección inferior.'
        }),
        ('Configuración SRI', {
            'fields': ('sri_environment', 'certificate_file', 'certificate_password')
        }),
        ('Branding', {
            'fields': ('logo',)
        }),
    )
    
    filter_horizontal = ['secondary_activities']


@admin.register(CompanyUser)
class CompanyUserAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ['user', 'company', 'role', 'is_active']
    list_filter = ['role', 'is_active', UserCompanyListFilter]
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'company__trade_name']
    list_select_related = ['user', 'company']


@admin.register(CompanySettings)
class CompanySettingsAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ['company', 'invoice_sequential', 'default_iva_rate', 'auto_create_entries', 'default_report_format']
    list_filter = ['auto_create_entries', 'default_report_format', 'default_iva_rate']
    search_fields = ['company__trade_name']
    
    fieldsets = (
        ('Configuraciones de Facturación', {
            'fields': (
                'invoice_sequential',
                'purchase_invoice_sequential', 
                'credit_note_sequential',
                'debit_note_sequential',
                'withholding_sequential'
            )
        }),
        ('Configuraciones Fiscales', {
            'fields': ('default_iva_rate',),
            'description': 'Configuración de IVA por defecto para nuevos productos y facturas. No afecta documentos existentes.'
        }),
        ('Configuraciones Contables', {
            'fields': ('decimal_places', 'auto_create_entries')
        }),
        ('Configuraciones de Reportes', {
            'fields': ('default_report_format',)
        }),
    )


# CompanyAccountDefaults y CompanyTaxAccountMapping se configuran
# solo como inlines dentro de Company para evitar duplicación


# @admin.register(CompanyTaxAccountMapping)  # ELIMINADO - Solo inline
class CompanyTaxAccountMappingAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ['company', 'tax_rate', 'account', 'retention_account', 'is_active']
    list_filter = ['tax_rate', 'is_active']
    search_fields = ['company__trade_name', 'account__code', 'account__name']
    list_select_related = ['company', 'account', 'retention_account']
    
    fieldsets = (
        ('Configuración Básica', {
            'fields': ('company', 'tax_rate')
        }),
        ('Cuentas Contables', {
            'fields': ('account', 'retention_account'),
            'description': 'Cuenta para IVA en ventas y cuenta para retención de IVA por cobrar'
        }),
    )