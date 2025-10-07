"""
Configuración del admin para el módulo Banking
Integración cuidadosa sin afectar funcionalidades existentes
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.utils import timezone
from apps.core.filters import UserCompanyListFilter
from .models import Bank, BankAccount, BankTransaction, ExtractoBancario, ExtractoBancarioDetalle
from .processors import ExtractoBancarioProcessor


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    """Administración del catálogo de bancos"""
    
    list_display = [
        'name', 
        'short_name', 
        'sbs_code', 
        'swift_code', 
        'phone',
        'accounts_count',
        'is_active'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'short_name', 'sbs_code', 'swift_code']
    ordering = ['name']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'short_name', 'sbs_code')
        }),
        ('Códigos Internacionales', {
            'fields': ('swift_code',),
            'classes': ('collapse',)
        }),
        ('Información de Contacto', {
            'fields': ('website', 'phone'),
            'classes': ('collapse',)
        }),
    )
    
    def accounts_count(self, obj):
        """Mostrar número de cuentas bancarias asociadas"""
        count = obj.bankaccount_set.count()
        if count > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{} cuentas</span>',
                count
            )
        return format_html('<span style="color: gray;">Sin cuentas</span>')
    accounts_count.short_description = 'Cuentas'


class BankAccountInline(admin.TabularInline):
    """Inline para cuentas bancarias en el admin de empresas"""
    model = BankAccount
    extra = 0
    fields = [
        'bank', 
        'account_number', 
        'account_type', 
        'currency',
        'chart_account',
        'is_active'
    ]
    autocomplete_fields = ['bank']
    
    def get_queryset(self, request):
        """Filtrar por empresas del usuario"""
        qs = super().get_queryset(request)
        
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            if user_companies:
                qs = qs.filter(company_id__in=user_companies)
            else:
                qs = qs.none()
        
        return qs


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    """Administración de cuentas bancarias"""
    
    list_display = [
        'company',
        'bank', 
        'masked_account_display',
        'account_type', 
        'currency',
        'chart_account_display',
        'initial_balance',
        'is_active'
    ]
    list_filter = [
        'account_type', 
        'currency',
        'bank',
        UserCompanyListFilter, 
        'is_active'
    ]
    search_fields = [
        'bank__name', 
        'account_number', 
        'company__trade_name',
        'contact_person'
    ]
    autocomplete_fields = ['bank', 'company']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('company', 'bank', 'account_number', 'account_type', 'currency')
        }),
        ('Integración Contable', {
            'fields': ('chart_account',),
            'description': 'Vincular con cuenta contable existente (opcional)'
        }),
        ('Configuración Inicial', {
            'fields': ('initial_balance', 'opening_date'),
            'classes': ('collapse',)
        }),
        ('Información Adicional', {
            'fields': ('contact_person', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    def masked_account_display(self, obj):
        """Mostrar número de cuenta enmascarado"""
        return obj.masked_account_number
    masked_account_display.short_description = 'Número de Cuenta'
    
    def chart_account_display(self, obj):
        """Mostrar cuenta contable vinculada"""
        if obj.chart_account:
            return format_html(
                '<span style="color: green;">✓ {}</span>',
                obj.chart_account
            )
        return format_html('<span style="color: orange;">Sin vincular</span>')
    chart_account_display.short_description = 'Cuenta Contable'
    
    def get_queryset(self, request):
        """Filtrar por empresas del usuario"""
        qs = super().get_queryset(request)
        qs = qs.select_related('company', 'bank', 'chart_account')
        
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            if user_companies:
                qs = qs.filter(company_id__in=user_companies)
            else:
                qs = qs.none()
        
        return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtrar opciones según permisos del usuario"""
        if db_field.name == "company" and not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            if user_companies:
                kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                    id__in=user_companies
                )
        
        elif db_field.name == "chart_account":
            # Filtrar solo cuentas con aux_type='bank'
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                aux_type='bank',
                is_active=True
            )
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(BankTransaction)
class BankTransactionAdmin(admin.ModelAdmin):
    """Administración de movimientos bancarios (preparado para futuro)"""
    
    list_display = [
        'bank_account',
        'transaction_date',
        'transaction_type',
        'signed_amount_display',
        'description',
        'reference',
        'is_reconciled'
    ]
    list_filter = [
        'transaction_type',
        'is_reconciled',
        'transaction_date',
        'bank_account__bank'
    ]
    search_fields = [
        'description',
        'reference',
        'bank_account__account_number'
    ]
    date_hierarchy = 'transaction_date'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('bank_account', 'transaction_date', 'value_date')
        }),
        ('Transacción', {
            'fields': ('transaction_type', 'amount', 'description', 'reference')
        }),
        ('Contabilidad', {
            'fields': ('journal_entry', 'is_reconciled'),
            'classes': ('collapse',)
        }),
    )
    
    def signed_amount_display(self, obj):
        """Mostrar monto con signo y color"""
        signed = obj.signed_amount
        if signed < 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">-${}</span>',
                abs(float(signed))
            )
        else:
            return format_html(
                '<span style="color: green; font-weight: bold;">+${}</span>',
                float(signed)
            )
    signed_amount_display.short_description = 'Monto'
    
    def get_queryset(self, request):
        """Filtrar por empresas del usuario"""
        qs = super().get_queryset(request)
        qs = qs.select_related('bank_account', 'bank_account__company', 'bank_account__bank')
        
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            if user_companies:
                qs = qs.filter(bank_account__company_id__in=user_companies)
            else:
                qs = qs.none()
        
        return qs


class ExtractoBancarioDetalleInline(admin.TabularInline):
    """Inline para detalles del extracto"""
    model = ExtractoBancarioDetalle
    extra = 0
    fields = [
        'fecha', 'descripcion', 'referencia', 'debito', 'credito', 
        'saldo', 'is_reconciled', 'matched_transaction'
    ]
    readonly_fields = ['is_reconciled', 'matched_transaction']


@admin.register(ExtractoBancario)
class ExtractoBancarioAdmin(admin.ModelAdmin):
    """Administración de extractos bancarios"""
    
    list_display = [
        'bank_account',
        'period_start',
        'period_end', 
        'initial_balance',
        'final_balance',
        'status_display',
        'uploaded_by',
        'detalles_count'
    ]
    list_filter = [
        'status',
        'period_start',
        'bank_account__bank'
    ]
    search_fields = [
        'bank_account__account_number',
        'bank_account__bank__name',
        'notes'
    ]
    date_hierarchy = 'period_start'
    inlines = [ExtractoBancarioDetalleInline]
    actions = ['procesar_extractos', 'marcar_como_error', 'reprocesar_extractos']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('bank_account', 'file', 'period_start', 'period_end')
        }),
        ('Saldos', {
            'fields': ('initial_balance', 'final_balance')
        }),
        ('Estado y Observaciones', {
            'fields': ('status', 'notes')
        }),
        ('Información de Sistema', {
            'fields': ('uploaded_by',),
            'classes': ('collapse',)
        }),
    )
    
    def status_display(self, obj):
        """Mostrar status con color"""
        status_colors = {
            'uploaded': 'orange',
            'processing': 'blue',
            'processed': 'green',
            'reconciled': 'darkgreen',
            'error': 'red',
        }
        color = status_colors.get(obj.status, 'gray')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Estado'

    def detalles_count(self, obj):
        """Mostrar número de detalles del extracto"""
        count = obj.detalles.count()
        reconciled_count = obj.detalles.filter(is_reconciled=True).count()
        
        if count > 0:
            return format_html(
                '<span style="font-weight: bold;">{} total</span><br>'
                '<span style="color: green;">{} conciliados</span>',
                count, reconciled_count
            )
        return format_html('<span style="color: gray;">Sin detalles</span>')
    detalles_count.short_description = 'Detalles'
    
    def save_model(self, request, obj, form, change):
        """Asignar usuario al subir"""
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Filtrar por empresas del usuario"""
        qs = super().get_queryset(request)
        qs = qs.select_related('bank_account', 'bank_account__company', 'uploaded_by')
        
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            if user_companies:
                qs = qs.filter(bank_account__company_id__in=user_companies)
            else:
                qs = qs.none()
        
        return qs

    # ========== ACCIONES DE ADMIN ==========
    
    def procesar_extractos(self, request, queryset):
        """Acción para procesar extractos uploaded"""
        procesados = 0
        errores = 0
        
        for extracto in queryset.filter(status='uploaded'):
            try:
                extracto.status = 'processing'
                extracto.save()
                
                success, message = ExtractoBancarioProcessor.process_extracto(extracto)
                
                if success:
                    procesados += 1
                    self.message_user(
                        request,
                        f"✅ {extracto.bank_account}: {message}",
                        messages.SUCCESS
                    )
                else:
                    extracto.status = 'error'
                    extracto.notes = f"Error: {message}"
                    extracto.save()
                    errores += 1
                    self.message_user(
                        request,
                        f"❌ {extracto.bank_account}: {message}",
                        messages.ERROR
                    )
            
            except Exception as e:
                extracto.status = 'error'
                extracto.notes = f"Error inesperado: {str(e)}"
                extracto.save()
                errores += 1
                self.message_user(
                    request,
                    f"❌ {extracto.bank_account}: Error inesperado - {str(e)}",
                    messages.ERROR
                )
        
        # Mensaje resumen
        if procesados > 0:
            self.message_user(
                request,
                f"🎉 Procesados exitosamente: {procesados} extractos",
                messages.SUCCESS
            )
        
        if errores > 0:
            self.message_user(
                request,
                f"⚠️ Errores encontrados: {errores} extractos",
                messages.WARNING
            )
    
    procesar_extractos.short_description = "🔄 Procesar extractos seleccionados"

    def marcar_como_error(self, request, queryset):
        """Marcar extractos como error"""
        count = queryset.update(status='error', notes='Marcado manualmente como error')
        self.message_user(
            request,
            f"Marcados como error: {count} extractos",
            messages.WARNING
        )
    
    marcar_como_error.short_description = "❌ Marcar como error"

    def reprocesar_extractos(self, request, queryset):
        """Reprocesar extractos (error -> uploaded)"""
        count = 0
        for extracto in queryset.filter(status__in=['error', 'processed']):
            # Limpiar detalles existentes
            extracto.detalles.all().delete()
            extracto.status = 'uploaded'
            extracto.notes = 'Preparado para reprocesamiento'
            extracto.save()
            count += 1
        
        self.message_user(
            request,
            f"Preparados para reprocesamiento: {count} extractos",
            messages.INFO
        )
    
    reprocesar_extractos.short_description = "🔄 Preparar para reprocesar"


@admin.register(ExtractoBancarioDetalle)
class ExtractoBancarioDetalleAdmin(admin.ModelAdmin):
    """Administración de detalles de extractos"""
    
    list_display = [
        'extracto_info',
        'fecha',
        'descripcion_short',
        'monto_display', 
        'is_reconciled',
        'matched_transaction'
    ]
    list_filter = [
        'is_reconciled',
        'fecha',
        'extracto__bank_account__bank'
    ]
    search_fields = [
        'descripcion',
        'referencia',
        'extracto__bank_account__account_number'
    ]
    date_hierarchy = 'fecha'
    
    def extracto_info(self, obj):
        """Información del extracto"""
        return f"{obj.extracto.bank_account} ({obj.extracto.period_start} - {obj.extracto.period_end})"
    extracto_info.short_description = 'Extracto'
    
    def descripcion_short(self, obj):
        """Descripción truncada"""
        return obj.descripcion[:50] + "..." if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_short.short_description = 'Descripción'
    
    def monto_display(self, obj):
        """Mostrar monto con color"""
        monto = obj.monto
        if obj.tipo_movimiento == 'credito':
            return format_html(
                '<span style="color: green; font-weight: bold;">+${}</span>',
                float(monto)
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">-${}</span>',
                float(monto)
            )
    monto_display.short_description = 'Monto'
    
    def get_queryset(self, request):
        """Filtrar por empresas del usuario"""
        qs = super().get_queryset(request)
        qs = qs.select_related('extracto', 'extracto__bank_account', 'matched_transaction')
        
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            if user_companies:
                qs = qs.filter(extracto__bank_account__company_id__in=user_companies)
            else:
                qs = qs.none()
        
        return qs