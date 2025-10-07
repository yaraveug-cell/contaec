from django.contrib import admin
from .models import (
    AssetCategory, AssetLocation, FixedAsset, 
    DepreciationSchedule, DepreciationEntry, AssetMaintenance
)
from apps.core.filters import UserCompanyListFilter, UserCompanyAssetFilter


class CompanyFilterMixin:
    """Mixin para filtrar por empresa del usuario"""
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        # Filtrar por empresas del usuario
        user_companies = request.session.get('user_companies', [])
        if user_companies and user_companies != 'all':
            if hasattr(self.model, 'company'):
                return qs.filter(company_id__in=user_companies)
            elif hasattr(self.model, 'asset') and hasattr(self.model.asset.field.related_model, 'company'):
                return qs.filter(asset__company_id__in=user_companies)
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


class DepreciationScheduleInline(admin.StackedInline):
    model = DepreciationSchedule
    extra = 0
    fields = ('method', 'useful_life_years', 'useful_life_months', 'salvage_value', 'start_date')
    readonly_fields = ('annual_depreciation', 'monthly_depreciation', 'end_date')


class DepreciationEntryInline(admin.TabularInline):
    model = DepreciationEntry
    extra = 0
    fields = ('period_year', 'period_month', 'depreciation_amount', 'is_posted', 'posting_date')
    readonly_fields = ('accumulated_before', 'accumulated_after')


class AssetMaintenanceInline(admin.TabularInline):
    model = AssetMaintenance
    extra = 1
    fields = ('maintenance_date', 'maintenance_type', 'description', 'total_cost', 'next_maintenance_date')
    readonly_fields = ('total_cost',)


@admin.register(AssetCategory)
class AssetCategoryAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ('name', 'useful_life_years', 'depreciation_rate', 'created_at')
    search_fields = ('name',)
    list_filter = ('useful_life_years', 'created_at')


@admin.register(AssetLocation)
class AssetLocationAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ('name', 'company', 'responsible_person', 'created_at')
    list_filter = (UserCompanyListFilter, 'created_at')
    search_fields = ('name', 'responsible_person', 'company__trade_name')


@admin.register(FixedAsset)
class FixedAssetAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ('asset_code', 'name', 'company', 'category', 'status', 'acquisition_cost', 'book_value', 'acquisition_date')
    list_filter = (UserCompanyListFilter, 'category', 'status', 'acquisition_method', 'acquisition_date')
    search_fields = ('asset_code', 'name', 'serial_number', 'brand', 'model')
    readonly_fields = ('book_value', 'get_depreciation_percentage', 'created_at', 'updated_at')
    inlines = [DepreciationScheduleInline, DepreciationEntryInline, AssetMaintenanceInline]
    
    def get_depreciation_percentage(self, obj):
        """Mostrar porcentaje de depreciación"""
        if obj and obj.pk:
            return f"{obj.depreciation_percentage:.2f}%"
        return "0.00%"
    get_depreciation_percentage.short_description = 'Porcentaje de Depreciación'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('company', 'asset_code', 'name', 'description', 'category', 'location')
        }),
        ('Adquisición', {
            'fields': ('acquisition_date', 'acquisition_method', 'supplier', 'invoice_number', 'acquisition_cost')
        }),
        ('Valores Contables', {
            'fields': ('accumulated_depreciation', 'book_value', 'get_depreciation_percentage'),
            'classes': ('collapse',)
        }),
        ('Información Técnica', {
            'fields': ('brand', 'model', 'serial_number', 'color'),
            'classes': ('collapse',)
        }),
        ('Estado y Condición', {
            'fields': ('status', 'condition_notes')
        }),
        ('Información de Baja', {
            'fields': ('disposal_date', 'disposal_reason', 'disposal_value'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        })
    )


@admin.register(DepreciationSchedule)
class DepreciationScheduleAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ('asset', 'method', 'useful_life_years', 'annual_depreciation', 'monthly_depreciation', 'start_date', 'end_date')
    list_filter = ('method', 'useful_life_years', 'start_date')
    search_fields = ('asset__name', 'asset__asset_code')
    readonly_fields = ('annual_depreciation', 'monthly_depreciation', 'end_date', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Activo', {
            'fields': ('asset',)
        }),
        ('Configuración de Depreciación', {
            'fields': ('method', 'useful_life_years', 'useful_life_months', 'salvage_value')
        }),
        ('Cálculos', {
            'fields': ('annual_depreciation', 'monthly_depreciation'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('start_date', 'end_date')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(DepreciationEntry)
class DepreciationEntryAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ('asset', 'period_year', 'period_month', 'depreciation_amount', 'accumulated_after', 'is_posted', 'posting_date')
    list_filter = (UserCompanyAssetFilter, 'period_year', 'is_posted', 'posting_date')
    search_fields = ('asset__name', 'asset__asset_code', 'journal_entry_reference')
    readonly_fields = ('accumulated_after', 'created_at')
    
    fieldsets = (
        ('Activo y Período', {
            'fields': ('asset', 'period_year', 'period_month')
        }),
        ('Depreciación', {
            'fields': ('depreciation_amount', 'accumulated_before', 'accumulated_after')
        }),
        ('Contabilización', {
            'fields': ('is_posted', 'posting_date', 'journal_entry_reference')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        })
    )


@admin.register(AssetMaintenance)
class AssetMaintenanceAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ('asset', 'maintenance_date', 'maintenance_type', 'total_cost', 'provider', 'next_maintenance_date')
    list_filter = (UserCompanyAssetFilter, 'maintenance_type', 'maintenance_date')
    search_fields = ('asset__name', 'asset__asset_code', 'provider', 'description')
    readonly_fields = ('total_cost', 'created_at')
    date_hierarchy = 'maintenance_date'
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('asset', 'maintenance_date', 'maintenance_type', 'description')
        }),
        ('Costos', {
            'fields': ('labor_cost', 'parts_cost', 'external_cost', 'total_cost')
        }),
        ('Proveedor', {
            'fields': ('provider', 'invoice_number')
        }),
        ('Seguimiento', {
            'fields': ('next_maintenance_date', 'warranty_until')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        })
    )