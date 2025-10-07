"""
Filtros personalizados para el admin que respetan las empresas asignadas al usuario
"""
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from apps.companies.models import Company, CompanyUser


class UserCompanyListFilter(SimpleListFilter):
    """
    Filtro personalizado que muestra solo las empresas asignadas al usuario
    """
    title = _('Empresa')
    parameter_name = 'company'

    def lookups(self, request, model_admin):
        """
        Retorna solo las empresas asignadas al usuario actual
        """
        if not request.user.is_authenticated:
            return []
        
        if request.user.is_superuser:
            # Superuser ve todas las empresas
            companies = Company.objects.filter(is_active=True)
        else:
            # Usuario normal solo ve sus empresas asignadas
            user_company_ids = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            companies = Company.objects.filter(
                id__in=user_company_ids,
                is_active=True
            )
        
        return [(company.id, company.trade_name) for company in companies]

    def queryset(self, request, queryset):
        """
        Filtra el queryset según la empresa seleccionada
        """
        if self.value():
            return queryset.filter(company_id=self.value())
        return queryset


class UserCompanyAccountFilter(SimpleListFilter):
    """
    Filtro para cuentas contables que respeta las empresas del usuario
    """
    title = _('Empresa de la Cuenta')
    parameter_name = 'account__company'

    def lookups(self, request, model_admin):
        if not request.user.is_authenticated:
            return []
        
        if request.user.is_superuser:
            companies = Company.objects.filter(is_active=True)
        else:
            user_company_ids = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            companies = Company.objects.filter(
                id__in=user_company_ids,
                is_active=True
            )
        
        return [(company.id, company.trade_name) for company in companies]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(account__company_id=self.value())
        return queryset


class UserCompanyJournalFilter(SimpleListFilter):
    """
    Filtro para asientos contables que respeta las empresas del usuario
    """
    title = _('Empresa del Asiento')
    parameter_name = 'journal_entry__company'

    def lookups(self, request, model_admin):
        if not request.user.is_authenticated:
            return []
        
        if request.user.is_superuser:
            companies = Company.objects.filter(is_active=True)
        else:
            user_company_ids = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            companies = Company.objects.filter(
                id__in=user_company_ids,
                is_active=True
            )
        
        return [(company.id, company.trade_name) for company in companies]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(journal_entry__company_id=self.value())
        return queryset


class UserCompanyProductFilter(SimpleListFilter):
    """
    Filtro para productos que respeta las empresas del usuario
    """
    title = _('Empresa del Producto')
    parameter_name = 'product__company'

    def lookups(self, request, model_admin):
        if not request.user.is_authenticated:
            return []
        
        if request.user.is_superuser:
            companies = Company.objects.filter(is_active=True)
        else:
            user_company_ids = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            companies = Company.objects.filter(
                id__in=user_company_ids,
                is_active=True
            )
        
        return [(company.id, company.trade_name) for company in companies]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product__company_id=self.value())
        return queryset


class UserCompanyAssetFilter(SimpleListFilter):
    """
    Filtro para activos fijos que respeta las empresas del usuario
    """
    title = _('Empresa del Activo')
    parameter_name = 'asset__company'

    def lookups(self, request, model_admin):
        if not request.user.is_authenticated:
            return []
        
        if request.user.is_superuser:
            companies = Company.objects.filter(is_active=True)
        else:
            user_company_ids = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            companies = Company.objects.filter(
                id__in=user_company_ids,
                is_active=True
            )
        
        return [(company.id, company.trade_name) for company in companies]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(asset__company_id=self.value())
        return queryset


class UserCompanyPeriodFilter(SimpleListFilter):
    """
    Filtro para períodos de nómina que respeta las empresas del usuario
    """
    title = _('Empresa del Período')
    parameter_name = 'period__company'

    def lookups(self, request, model_admin):
        if not request.user.is_authenticated:
            return []
        
        if request.user.is_superuser:
            companies = Company.objects.filter(is_active=True)
        else:
            user_company_ids = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            companies = Company.objects.filter(
                id__in=user_company_ids,
                is_active=True
            )
        
        return [(company.id, company.trade_name) for company in companies]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(period__company_id=self.value())
        return queryset


class UserCompanyConceptFilter(SimpleListFilter):
    """
    Filtro para conceptos de nómina que respeta las empresas del usuario
    """
    title = _('Empresa del Concepto')
    parameter_name = 'concept__company'

    def lookups(self, request, model_admin):
        if not request.user.is_authenticated:
            return []
        
        if request.user.is_superuser:
            companies = Company.objects.filter(is_active=True)
        else:
            user_company_ids = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            companies = Company.objects.filter(
                id__in=user_company_ids,
                is_active=True
            )
        
        return [(company.id, company.trade_name) for company in companies]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(concept__company_id=self.value())
        return queryset


class UserCompanyWarehouseFilter(SimpleListFilter):
    """
    Filtro para bodegas que respeta las empresas del usuario
    """
    title = _('Bodega')
    parameter_name = 'warehouse'

    def lookups(self, request, model_admin):
        if not request.user.is_authenticated:
            return []
        
        from apps.inventory.models import Warehouse
        
        if request.user.is_superuser:
            warehouses = Warehouse.objects.filter(is_active=True).select_related('company')
        else:
            user_company_ids = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            warehouses = Warehouse.objects.filter(
                company_id__in=user_company_ids,
                is_active=True
            ).select_related('company')
        
        return [(warehouse.id, f"{warehouse.name} ({warehouse.company.trade_name})") for warehouse in warehouses]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(warehouse_id=self.value())
        return queryset