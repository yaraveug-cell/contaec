from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import json
from .models import Customer, Invoice, InvoiceLine
from apps.inventory.models import Product  # Usar productos de inventario
from apps.core.filters import UserCompanyListFilter
from apps.core.mixins import CompanyFilterMixin

@admin.register(Customer)
class CustomerAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ['identification', 'trade_name', 'customer_type', 'company', 'credit_limit', 'payment_terms']
    list_filter = ['customer_type', UserCompanyListFilter]
    search_fields = ['identification', 'trade_name', 'legal_name', 'email']
    list_select_related = ['company']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('company', 'customer_type', 'identification', 'trade_name', 'legal_name')
        }),
        ('Contacto', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Configuración Comercial', {
            'fields': ('credit_limit', 'payment_terms')
        }),
    )


# PRODUCTOS AHORA SE ADMINISTRAN DESDE apps.inventory.admin
# Los productos están unificados en el módulo de inventario

class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 0  # Por defecto no líneas extras
    min_num = 0  # Sin mínimo de líneas
    max_num = 50  # Máximo 50 líneas
    can_delete = True  # Permitir eliminar líneas
    show_change_link = False  # No mostrar enlace de cambio individual
    fields = ['product', 'description', 'quantity', 'unit_price', 'discount', 'iva_rate', 'line_total']
    readonly_fields = []
    
    def get_extra(self, request, obj=None, **kwargs):
        """Determinar cuántas líneas extra mostrar basado en si es creación o modificación"""
        if obj is None:  # Creando nueva factura
            return 3  # Mostrar 3 líneas vacías para nueva factura
        else:  # Modificando factura existente
            return 0  # No mostrar líneas extras al modificar
    
    class Media:
        css = {
            'all': ('admin/css/invoice_lines.css',)
        }
        js = ('admin/js/invoice_line_autocomplete.js', 'admin/js/invoice_line_calculator.js', 'admin/js/description_autocomplete.js', 'admin/js/tax_breakdown_calculator.js')
    
    def line_total_display(self, obj):
        """Mostrar total de línea formateado sin guión"""
        if obj and obj.pk and hasattr(obj, 'line_total'):
            return f"${obj.line_total:,.2f}"
        return "$0.00"
    line_total_display.short_description = "Total Línea"
    
    def get_formset(self, request, obj=None, **kwargs):
        """Personalizar formset para mejor usabilidad"""
        formset = super().get_formset(request, obj, **kwargs)
        
        # Personalizar widgets con tamaños específicos
        widget_configs = {
            'product': {'class': 'vTextField product-select', 'data-autocomplete': 'true', 'style': 'width: 180px;'},
            'description': {'class': 'vTextField', 'style': 'width: 280px;'},
            'quantity': {'class': 'vTextField', 'style': 'width: 80px; text-align: right;'},
            'unit_price': {'class': 'vTextField', 'style': 'width: 80px; text-align: right;'},
            'discount': {'class': 'vTextField', 'style': 'width: 80px; text-align: right;'},
            'iva_rate': {'class': 'vTextField', 'style': 'width: 80px; text-align: right;'},
            'line_total': {'class': 'vTextField', 'style': 'width: 100px; text-align: right; font-weight: bold; background-color: #f8f9fa;'}
        }
        
        for field_name, attrs in widget_configs.items():
            if field_name in formset.form.base_fields:
                formset.form.base_fields[field_name].widget.attrs.update(attrs)
        
        return formset


@admin.register(Invoice)
class InvoiceAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ['number', 'date', 'customer', 'company', 'status', 'subtotal', 'tax_amount', 'total']
    list_filter = ['status', 'date', UserCompanyListFilter]
    search_fields = ['number', 'customer__trade_name', 'customer__identification']
    list_select_related = ['customer', 'company', 'created_by']
    inlines = [InvoiceLineInline]
    
    def get_urls(self):
        """Agregar URLs personalizadas"""
        urls = super().get_urls()
        custom_urls = [
            path('company-payment-methods/', 
                 self.admin_site.admin_view(self.company_payment_methods_view),
                 name='invoicing_invoice_company_payment_methods'),
            path('payment-method-accounts/', 
                 self.admin_site.admin_view(self.payment_method_accounts_view),
                 name='invoicing_invoice_payment_method_accounts'),
        ]
        return custom_urls + urls
    
    def company_payment_methods_view(self, request):
        """Vista AJAX para obtener configuración de empresa-forma de pago"""
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Solo peticiones AJAX'}, status=400)
        
        try:
            from apps.companies.models import Company
            
            # Obtener todas las empresas con su forma de pago configurada
            companies = Company.objects.select_related('payment_method').filter(
                payment_method__isnull=False,
                payment_method__is_active=True
            )
            
            # Si no es superusuario, filtrar por empresas del usuario
            if not request.user.is_superuser:
                from apps.companies.models import CompanyUser
                user_companies = CompanyUser.objects.filter(
                    user=request.user,
                    is_active=True
                ).values_list('company_id', flat=True)
                companies = companies.filter(id__in=user_companies)
            
            # Crear diccionario con configuración
            company_config = {}
            for company in companies:
                company_config[str(company.id)] = {
                    'id': company.payment_method.id,
                    'name': company.payment_method.name,
                    'company_name': company.trade_name
                }
            
            return JsonResponse(company_config)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def payment_method_accounts_view(self, request):
        """Vista AJAX para obtener configuración de método de pago → cuenta padre"""
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Solo peticiones AJAX'}, status=400)
        
        try:
            from apps.companies.models import PaymentMethod
            
            # Obtener métodos de pago con cuenta padre configurada
            payment_methods = PaymentMethod.objects.select_related('parent_account').filter(
                is_active=True,
                parent_account__isnull=False
            )
            
            # Crear diccionario con configuración método → cuenta padre
            method_config = {}
            for method in payment_methods:
                method_config[str(method.id)] = {
                    'method_name': method.name,
                    'parent_account': {
                        'id': method.parent_account.id,
                        'code': method.parent_account.code,
                        'name': method.parent_account.name,
                        'level': method.parent_account.level
                    }
                }
            
            return JsonResponse(method_config)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    class Media:
        css = {
            'all': ('admin/css/invoice_lines.css',)
        }
        js = ('admin/js/invoice_admin.js', 'admin/js/invoice_line_calculator.js', 'admin/js/description_autocomplete.js', 'admin/js/tax_breakdown_calculator.js', 'admin/js/integrated_payment_account_handler.js')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('company', 'customer', 'date', ('payment_form', 'account'))
        }),
        ('Estado', {
            'fields': ('status', 'created_by')
        }),
    )
    
    readonly_fields = []
    
    def get_form(self, request, obj=None, **kwargs):
        """Personalizar formulario según el tipo de usuario"""
        form = super().get_form(request, obj, **kwargs)
        
        # Para usuarios no superusuarios, limitar opciones de empresa
        if not request.user.is_superuser and 'company' in form.base_fields:
            from apps.companies.models import CompanyUser, PaymentMethod
            user_companies = CompanyUser.objects.filter(
                user=request.user, 
                is_active=True
            ).values_list('company', flat=True)
            
            if user_companies:
                form.base_fields['company'].queryset = form.base_fields['company'].queryset.filter(
                    id__in=user_companies
                )
                
                # Si solo tiene una empresa, hacerla readonly para nuevas facturas
                if len(user_companies) == 1 and obj is None:
                    form.base_fields['company'].widget.attrs['readonly'] = True
                    form.base_fields['company'].widget.attrs['style'] = 'background-color: #f8f9fa;'
                
                # Filtrar cuentas por empresa del usuario
                if 'account' in form.base_fields:
                    from apps.accounting.models import ChartOfAccounts
                    accounts = ChartOfAccounts.objects.filter(
                        company__in=user_companies,
                        accepts_movement=True
                    ).select_related('company', 'account_type').order_by('code')
                    form.base_fields['account'].queryset = accounts
                
                # Filtrar formas de pago (todas las disponibles por ahora, se filtrará con JavaScript)
                if 'payment_form' in form.base_fields:
                    payment_methods = PaymentMethod.objects.filter(
                        is_active=True
                    ).order_by('name')
                    form.base_fields['payment_form'].queryset = payment_methods
        else:
            # Para superusuarios, mostrar todas las cuentas que aceptan movimiento
            if 'account' in form.base_fields:
                from apps.accounting.models import ChartOfAccounts
                accounts = ChartOfAccounts.objects.filter(
                    accepts_movement=True
                ).select_related('company', 'account_type').order_by('code')
                form.base_fields['account'].queryset = accounts
            
            # Para superusuarios, mostrar todas las formas de pago
            if 'payment_form' in form.base_fields:
                from apps.companies.models import PaymentMethod
                payment_methods = PaymentMethod.objects.filter(
                    is_active=True
                ).order_by('name')
                form.base_fields['payment_form'].queryset = payment_methods
        
        return form
    

    

    
    def get_changeform_initial_data(self, request):
        """Establecer valores por defecto para nuevas facturas"""
        initial = super().get_changeform_initial_data(request)
        
        # Establecer empresa por defecto basada en el usuario activo
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            try:
                # Obtener la primera empresa activa del usuario
                company_user = CompanyUser.objects.filter(
                    user=request.user, 
                    is_active=True
                ).select_related('company').first()
                
                if company_user:
                    initial['company'] = company_user.company.id
            except CompanyUser.DoesNotExist:
                pass
        
        return initial
    
    def save_model(self, request, obj, form, change):
        """Asignar usuario creador antes de guardar"""
        if not obj.pk:  # Solo en creación
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        """Agregar datos de productos al contexto para JavaScript"""
        # Obtener productos disponibles para la empresa
        if request.user.is_superuser:
            products = Product.objects.select_related('company').all()
        else:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user, 
                is_active=True
            ).values_list('company_id', flat=True)
            products = Product.objects.select_related('company').filter(company_id__in=user_companies)
        
        # Crear diccionario con datos de productos para JavaScript
        products_data = {}
        for product in products:
            products_data[str(product.id)] = {
                'name': product.name,
                'description': product.description or product.name,
                'sale_price': str(product.sale_price),
                'unit_of_measure': getattr(product, 'unit_of_measure', 'UND'),
                'has_iva': getattr(product, 'has_iva', True),
                'iva_rate': str(getattr(product, 'iva_rate', '12.00'))
            }
        
        # Agregar al contexto para usar en template
        context['products_data_json'] = json.dumps(products_data)
        
        return super().render_change_form(request, context, add, change, form_url, obj)


# InvoiceLineAdmin temporalmente deshabilitado para debugging
# @admin.register(InvoiceLine)
# class InvoiceLineAdmin(admin.ModelAdmin):
#     list_display = ['invoice', 'product', 'description', 'quantity', 'unit_price', 'line_total']
#     search_fields = ['description', 'product__name', 'invoice__number']
#     list_select_related = ['invoice', 'product']