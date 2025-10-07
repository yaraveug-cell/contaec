from django.contrib import admin
from .models import Category, Warehouse, Product, StockMovement, Stock
from apps.core.filters import UserCompanyListFilter, UserCompanyProductFilter, UserCompanyWarehouseFilter


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
            elif hasattr(self.model, 'warehouse') and hasattr(self.model.warehouse.field.related_model, 'company'):
                return qs.filter(warehouse__company_id__in=user_companies)
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


@admin.register(Category)
class CategoryAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ['name', 'company', 'parent', 'has_accounting_config']
    list_filter = [UserCompanyListFilter]
    search_fields = ['name', 'description']
    list_select_related = ['company', 'parent', 'default_sales_account', 'default_cost_account', 'default_inventory_account']
    
    fieldsets = (
        ('Información General', {
            'fields': ('company', 'name', 'description', 'parent')
        }),
        ('Configuración Contable (ESTRATEGIA B - Opcional)', {
            'fields': (
                'default_sales_account', 
                'default_cost_account', 
                'default_inventory_account'
            ),
            'description': (
                'Configure las cuentas contables por defecto para productos de esta categoría. '
                'Si no se configuran, se usarán las cuentas por defecto de la empresa o del sistema. '
                'Esta configuración permite asientos contables más precisos y automatizados.'
            ),
            'classes': ['collapse']
        }),
    )
    
    def has_accounting_config(self, obj):
        """Indica si la categoría tiene configuración contable"""
        return bool(
            obj.default_sales_account or 
            obj.default_cost_account or 
            obj.default_inventory_account
        )
    has_accounting_config.boolean = True
    has_accounting_config.short_description = 'Config. Contable'
    
    def _validate_account_configuration(self, obj, account_field, expected_prefixes):
        """Valida que la cuenta configurada sea del tipo esperado"""
        account = getattr(obj, account_field, None)
        if account and account.code:
            if not any(account.code.startswith(prefix) for prefix in expected_prefixes):
                return False, f"Cuenta {account.code} no es del tipo recomendado para {account_field}"
        return True, None
    
    def save_model(self, request, obj, form, change):
        """Validar configuración antes de guardar y mostrar advertencias"""
        warnings = []
        
        # Validar cuenta de ventas
        valid, msg = self._validate_account_configuration(obj, 'default_sales_account', ['4'])
        if not valid:
            warnings.append(f"⚠️ Ventas: {msg}")
            
        # Validar cuenta de costo
        valid, msg = self._validate_account_configuration(obj, 'default_cost_account', ['4', '5'])
        if not valid:
            warnings.append(f"⚠️ Costo: {msg}")
            
        # Validar cuenta de inventario
        valid, msg = self._validate_account_configuration(obj, 'default_inventory_account', ['1'])
        if not valid:
            warnings.append(f"⚠️ Inventario: {msg}")
        
        # Guardar el objeto
        super().save_model(request, obj, form, change)
        
        # Mostrar advertencias si las hay
        if warnings:
            from django.contrib import messages
            messages.warning(
                request, 
                f"Configuración guardada con advertencias: {' | '.join(warnings)}. "
                "Verifique que las cuentas seleccionadas sean apropiadas para evitar problemas en reportes financieros."
            )
    
    def _should_show_all_accounts(self, request, field_name):
        """Determina si debe mostrar todas las cuentas basado en parámetros y permisos"""
        # Permitir mostrar todas las cuentas si:
        # 1. Es superusuario Y tiene parámetro show_all=1
        # 2. O tiene parámetro show_all_accounts=1 (para expertos contables)
        show_all = request.GET.get('show_all', '0') == '1'
        show_all_accounts = request.GET.get('show_all_accounts', '0') == '1'
        
        return (request.user.is_superuser and show_all) or show_all_accounts
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtrar cuentas contables por empresa del usuario con opción de mostrar todas"""
        if db_field.name in ['default_sales_account', 'default_cost_account', 'default_inventory_account']:
            if not request.user.is_superuser:
                user_companies = request.session.get('user_companies', [])
                if user_companies and user_companies != 'all':
                    kwargs["queryset"] = db_field.related_model.objects.filter(
                        company_id__in=user_companies,
                        accepts_movement=True,  # Solo cuentas que aceptan movimiento
                        is_detail=True  # Solo cuentas de detalle
                    )
            else:
                # Para superusuario, mostrar todas las cuentas válidas
                kwargs["queryset"] = db_field.related_model.objects.filter(
                    accepts_movement=True,
                    is_detail=True
                )
        
        # Aplicar filtro de cuenta específico por tipo (con opción de mostrar todas)
        show_all = self._should_show_all_accounts(request, db_field.name)
        
        if not show_all and 'queryset' in kwargs:
            from django.db import models
            
            if db_field.name == 'default_sales_account':
                # Filtro recomendado: Solo cuentas de ingresos (4.x)
                kwargs["queryset"] = kwargs["queryset"].filter(code__startswith='4')
                
            elif db_field.name == 'default_cost_account':
                # Filtro recomendado: Cuentas de costos de ventas (4.x) y gastos (5.x)
                kwargs["queryset"] = kwargs["queryset"].filter(
                    models.Q(code__startswith='4') | models.Q(code__startswith='5')
                )
                
            elif db_field.name == 'default_inventory_account':
                # Filtro recomendado: Solo cuentas de activos (1.x)
                kwargs["queryset"] = kwargs["queryset"].filter(code__startswith='1')
        
        # Agregar información sobre filtros aplicados
        if 'queryset' in kwargs and db_field.name in ['default_sales_account', 'default_cost_account', 'default_inventory_account']:
            field_descriptions = {
                'default_sales_account': 'Cuentas de Ingresos (4.x) - Recomendado para ventas',
                'default_cost_account': 'Cuentas de Costos (4.x) y Gastos (5.x) - Recomendado para costos',
                'default_inventory_account': 'Cuentas de Activos (1.x) - Recomendado para inventario'
            }
            
            if show_all:
                kwargs['help_text'] = (
                    f'⚠️ MODO EXPERTO: Mostrando todas las cuentas. '
                    f'Recomendación: {field_descriptions.get(db_field.name, "Usar cuentas apropiadas")}. '
                    f'Para volver al filtro estándar, quite el parámetro show_all_accounts de la URL.'
                )
            else:
                kwargs['help_text'] = (
                    f'📋 {field_descriptions.get(db_field.name, "Cuentas filtradas por tipo")}. '
                    f'¿Experto contable? Agregue ?show_all_accounts=1 a la URL para ver todas las cuentas.'
                )
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Warehouse)
class WarehouseAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ['code', 'name', 'company', 'responsible', 'is_active']
    list_filter = [UserCompanyListFilter, 'is_active']
    search_fields = ['code', 'name', 'address']
    list_select_related = ['company', 'responsible']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('company', 'code', 'name', 'address')
        }),
        ('Responsabilidad', {
            'fields': ('responsible', 'is_active')
        }),
    )


@admin.register(Product)
class ProductAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'company', 'product_type', 'sale_price', 'has_iva', 'manages_inventory', 'effective_accounts_summary', 'is_active']
    list_filter = ['product_type', UserCompanyListFilter, 'has_iva', 'manages_inventory', 'is_active', 'category']
    search_fields = ['code', 'name', 'description']
    list_select_related = ['company', 'category', 'category__default_sales_account', 'category__default_cost_account', 'category__default_inventory_account']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('company', 'category', 'code', 'name', 'description', 'product_type')
        }),
        ('Unidades', {
            'fields': ('unit_of_measure',)
        }),
        ('Inventario', {
            'fields': ('manages_inventory', 'minimum_stock', 'maximum_stock')
        }),
        ('Precios', {
            'fields': ('cost_price', 'sale_price')
        }),
        ('Configuración Fiscal', {
            'fields': ('has_iva', 'iva_rate')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Configuración Contable Efectiva (Solo Lectura)', {
            'fields': ('display_effective_sales_account', 'display_effective_cost_account', 'display_effective_inventory_account'),
            'description': 'Cuentas contables que se utilizarán automáticamente para este producto según la ESTRATEGIA B.',
            'classes': ['collapse']
        }),
    )
    
    readonly_fields = ['display_effective_sales_account', 'display_effective_cost_account', 'display_effective_inventory_account']
    
    def effective_accounts_summary(self, obj):
        """Muestra resumen de configuración contable en la lista"""
        config = obj.get_account_configuration_status()
        
        status_icons = []
        if config['sales_configured']:
            status_icons.append('💰')
        if config['cost_configured']:
            status_icons.append('📊')
        if config['inventory_configured']:
            status_icons.append('📦')
        
        if status_icons:
            return ' '.join(status_icons)
        return '⚙️'  # Sin configuración específica
    
    effective_accounts_summary.short_description = 'Cuentas'
    effective_accounts_summary.admin_order_field = 'category'
    
    def display_effective_sales_account(self, obj):
        """Muestra la cuenta de ventas efectiva"""
        account = obj.get_effective_sales_account()
        if account:
            source = "Categoría" if (obj.category and obj.category.default_sales_account) else "Por defecto"
            return f"{account.code} - {account.name} ({source})"
        return "❌ No configurada"
    display_effective_sales_account.short_description = 'Cuenta de Ventas Efectiva'
    
    def display_effective_cost_account(self, obj):
        """Muestra la cuenta de costo efectiva"""
        account = obj.get_effective_cost_account()
        if account:
            source = "Categoría" if (obj.category and obj.category.default_cost_account) else "Por defecto"
            return f"{account.code} - {account.name} ({source})"
        return "❌ No configurada"
    display_effective_cost_account.short_description = 'Cuenta de Costo Efectiva'
    
    def display_effective_inventory_account(self, obj):
        """Muestra la cuenta de inventario efectiva"""
        account = obj.get_effective_inventory_account()
        if account:
            source = "Categoría" if (obj.category and obj.category.default_inventory_account) else "Por defecto"
            return f"{account.code} - {account.name} ({source})"
        return "❌ No configurada"
    display_effective_inventory_account.short_description = 'Cuenta de Inventario Efectiva'
    
    def get_search_results(self, request, queryset, search_term):
        """
        Búsqueda personalizada para autocompletado que:
        1. Filtra por empresas del usuario
        2. Busca por código y nombre de forma inteligente
        3. Mejora la relevancia de resultados
        """
        # Filtrar por empresas del usuario si no es superusuario
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user,
                is_active=True
            ).values_list('company_id', flat=True)
            if user_companies:
                queryset = queryset.filter(company_id__in=user_companies)
        
        # Solo productos activos para autocompletado
        queryset = queryset.filter(is_active=True)
        
        # Si no hay término de búsqueda, devolver queryset filtrado
        if not search_term:
            return queryset, False
        
        # Búsqueda inteligente por código y nombre
        from django.db.models import Q
        
        # Dividir término en palabras para búsqueda más flexible
        terms = search_term.strip().split()
        search_query = Q()
        
        for term in terms:
            # Buscar por código (exacto e inicio)
            term_query = Q(code__iexact=term) | Q(code__istartswith=term)
            # Buscar por nombre (contiene)
            term_query |= Q(name__icontains=term)
            # Buscar por descripción (contiene)
            term_query |= Q(description__icontains=term)
            
            search_query &= term_query
        
        # Aplicar filtros y ordenar por relevancia
        filtered_queryset = queryset.filter(search_query).distinct()
        
        # Ordenar por relevancia: código exacto primero, luego por código y nombre
        if terms:
            term = terms[0]  # Usar primer término para ordenamiento
            try:
                # Ordenar poniendo coincidencias exactas de código primero
                filtered_queryset = filtered_queryset.extra(
                    select={
                        'code_exact_match': "CASE WHEN UPPER(code) = UPPER(%s) THEN 0 ELSE 1 END",
                        'code_starts_with': "CASE WHEN UPPER(code) LIKE UPPER(%s) THEN 0 ELSE 1 END"
                    },
                    select_params=[term, term + '%']
                ).order_by('code_exact_match', 'code_starts_with', 'code', 'name')
            except:
                # Fallback si hay problemas con extra()
                filtered_queryset = filtered_queryset.order_by('code', 'name')
        else:
            filtered_queryset = filtered_queryset.order_by('code', 'name')
        
        return filtered_queryset, False


@admin.register(StockMovement)
class StockMovementAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ['date', 'product', 'warehouse', 'movement_type', 'quantity', 'unit_cost', 'created_by']
    list_filter = ['movement_type', UserCompanyProductFilter, UserCompanyWarehouseFilter, 'date']
    search_fields = ['product__code', 'product__name', 'reference', 'description']
    list_select_related = ['product', 'warehouse', 'created_by']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('product', 'warehouse', 'movement_type', 'reference', 'description')
        }),
        ('Cantidades', {
            'fields': ('quantity', 'unit_cost', 'total_cost')
        }),
        ('Usuario', {
            'fields': ('created_by',)
        }),
    )
    
    readonly_fields = ['total_cost']


@admin.register(Stock)
class StockAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity', 'average_cost', 'last_movement']
    list_filter = [UserCompanyProductFilter, UserCompanyWarehouseFilter]
    search_fields = ['product__code', 'product__name']
    list_select_related = ['product', 'warehouse']
    
    readonly_fields = ['last_movement']