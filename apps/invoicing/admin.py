from django.contrib import admin
from django.contrib import messages
from django.http import JsonResponse
from django.urls import path
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
import json
from .models import Customer, Invoice, InvoiceLine
from apps.inventory.models import Product  # Usar productos de inventario
from apps.core.filters import UserCompanyListFilter
from apps.core.mixins import CompanyFilterMixin


class IntelligentInvoiceLineForm(forms.ModelForm):
    """
    Formulario inteligente para líneas de factura con validación de stock avanzada.
    
    Características:
    1. Validación en tiempo real de stock
    2. Mensajes de error específicos por nivel
    3. Bloqueo inteligente según disponibilidad
    4. Integración con el sistema de productos
    """
    
    class Meta:
        model = InvoiceLine
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar widgets para mejor UX
        if 'quantity' in self.fields:
            self.fields['quantity'].widget.attrs.update({
                'class': 'intelligent-quantity-field',
                'step': '0.01',
                'min': '0.01',
                'data-validation': 'stock-check'
            })
            
        if 'stock' in self.fields:
            self.fields['stock'].widget.attrs.update({
                'readonly': True,
                'class': 'stock-display-field',
                'style': 'background-color: #e9ecef; text-align: center;'
            })
    
    def clean(self):
        """
        Validación inteligente con múltiples niveles de advertencia.
        Solo bloquea el guardado en casos CRÍTICOS.
        """
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        
        if not product or not quantity:
            return cleaned_data
            
        try:
            # Obtener stock actual
            available_stock = Decimal(str(product.get_current_stock() or 0))
            requested_quantity = Decimal(str(quantity))
            
            # VALIDACIÓN CRÍTICA: Stock insuficiente - Solo JavaScript maneja el bloqueo
            if available_stock < requested_quantity:
                # No mostrar mensaje invasivo, solo marcar como inválido silenciosamente
                # El JavaScript detectará esto y deshabilitará botones de guardar
                pass
            
            # Stock crítico - Solo notificaciones flotantes, NO mensajes invasivos
            elif available_stock <= 5:
                # Solo log para debug - Las notificaciones flotantes se encargan del UX
                pass  # Sin mensajes invasivos, solo JavaScript maneja la notificación
            
            # INFORMACIÓN: Stock bajo (≤10 unidades) 
            elif available_stock <= 10:
                # Solo mensaje informativo, no error
                pass  # Se manejará en JavaScript para mejor UX
            
            # Validar cantidad mínima
            if requested_quantity <= 0:
                raise ValidationError({
                    'quantity': 'La cantidad debe ser mayor a cero.'
                })
                
        except Exception as e:
            # Error en validación - permitir continuar pero advertir
            if 'STOCK INSUFICIENTE' in str(e):
                raise  # Re-lanzar errores críticos
            else:
                # Otros errores no críticos
                self.add_error(
                    'quantity',
                    f"⚠️ Error verificando stock: {str(e)}. Verifique manualmente."
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        """Guardar con actualización automática de información de stock"""
        instance = super().save(commit=False)
        
        # Auto-actualizar stock informativo
        if instance.product:
            try:
                instance.stock = Decimal(str(instance.product.get_current_stock() or 0))
            except:
                instance.stock = Decimal('0')
        
        if commit:
            instance.save()
            
        return instance


@admin.register(Customer)
class CustomerAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ['identification', 'trade_name', 'customer_type', 'retention_agent', 'company', 'credit_limit', 'payment_terms']
    list_filter = ['customer_type', 'retention_agent', 'sri_classification', UserCompanyListFilter]
    search_fields = ['identification', 'trade_name', 'legal_name', 'email', 'phone']  # Campos para autocompletado
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
        ('Configuración de Retenciones', {
            'fields': ('retention_agent', 'sri_classification', 'iva_retention_percentage', 'ir_retention_percentage'),
            'description': 'Configuración para clientes que actúan como agentes de retención según normativa ecuatoriana SRI'
        }),
    )


# PRODUCTOS AHORA SE ADMINISTRAN DESDE apps.inventory.admin
# Los productos están unificados en el módulo de inventario

class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    form = IntelligentInvoiceLineForm  # Usar formulario inteligente
    extra = 0  # Por defecto no líneas extras
    min_num = 0  # Sin mínimo de líneas
    max_num = 50  # Máximo 50 líneas
    can_delete = True  # Permitir eliminar líneas
    show_change_link = False  # No mostrar enlace de cambio individual
    
    # SOLUCIÓN ELEGANTE: Usar exclude para ocultar descripción, se auto-completa en el modelo
    fields = ['product', 'stock', 'quantity', 'unit_price', 'discount', 'iva_rate', 'line_total']
    exclude = ['description']  # Se auto-completa desde el producto en el modelo
    autocomplete_fields = ['product']  # Habilitar autocompletado para productos
    readonly_fields = []  # Permitir edición del total para JavaScript
    
    # Personalizar clases CSS para el inline
    classes = ['collapse-open']
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Personalizar widgets para campos específicos"""
        if db_field.name == 'line_total':
            # Campo total editable por JavaScript pero con apariencia readonly
            kwargs['widget'] = admin.widgets.AdminTextInputWidget(attrs={
                'readonly': 'readonly',
                'style': 'background-color: #f8f9fa; cursor: not-allowed;',
                'class': 'line-total-calculated'
            })
        elif db_field.name == 'stock':
            # Campo stock solo lectura (informativo)
            kwargs['widget'] = admin.widgets.AdminTextInputWidget(attrs={
                'readonly': 'readonly',
                'style': 'background-color: #e9ecef; cursor: not-allowed; text-align: center;',
                'class': 'stock-info'
            })
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
    def save_formset(self, request, form, formset, change):
        """
        Guardar formset con validación inteligente de stock y mensajes nativos de Django.
        
        Proceso:
        1. Validar stock ANTES de guardar (crítico)
        2. Guardar solo si pasa validaciones críticas
        3. Mostrar mensajes informativos post-guardado
        """
        
        # PASO 1: Validaciones PREVIAS críticas
        instances = formset.save(commit=False)
        critical_errors = []
        warning_messages = []
        info_messages = []
        
        for instance in instances:
            try:
                if hasattr(instance, 'check_stock_availability') and instance.product and instance.quantity:
                    stock_info = instance.check_stock_availability()
                    
                    if stock_info:
                        level = stock_info.get('level', 'info')
                        message = stock_info['message']
                        
                        if level == 'error' and not stock_info.get('has_sufficient_stock', True):
                            # ERROR CRÍTICO: Stock insuficiente - BLOQUEAR guardado
                            critical_errors.append(message)
                        elif level == 'warning':
                            # Advertencia: Stock bajo - permitir pero advertir
                            warning_messages.append(message)
                        elif level == 'info':
                            # Información: Consumo alto - solo informar
                            info_messages.append(message)
                            
            except Exception as validation_error:
                print(f"⚠️ Error en validación previa: {validation_error}")
                continue
        
        # PASO 2: Verificar errores críticos
        if critical_errors:
            # HAY ERRORES CRÍTICOS - NO GUARDAR
            for error_msg in critical_errors:
                messages.error(request, error_msg)
            
            messages.error(
                request, 
                "❌ GUARDADO BLOQUEADO: Corrija los problemas de stock insuficiente antes de continuar."
            )
            
            # Lanzar excepción para evitar guardado
            from django.core.exceptions import ValidationError
            raise ValidationError("Stock insuficiente detectado")
        
        # PASO 3: Guardar si no hay errores críticos
        for instance in instances:
            instance.save()
        
        formset.save_m2m()
        
        # Eliminar objetos marcados para eliminación
        for obj in formset.deleted_objects:
            obj.delete()
        
        # PASO 4: Solo mensaje básico de éxito - Sin mensajes invasivos adicionales
        # Las notificaciones flotantes JavaScript manejan toda la información de stock
        
        messages.success(
            request,
            f"✅ Factura guardada exitosamente con {len(instances)} líneas procesadas."
        )
        
        # Sin mensajes adicionales de stock - Solo notificaciones flotantes discretas
    
    def get_extra(self, request, obj=None, **kwargs):
        """
        SOLUCIÓN ÓPTIMA: 3 filas iniciales + interceptación de filas dinámicas.
        
        Ventajas:
        1. Rendimiento optimizado (solo 3 filas iniciales)
        2. UX inteligente (usuario agrega según necesidad)
        3. Timing correcto post-Select2 para filas dinámicas
        4. Recursos eficientes
        """
        if obj is None:  # Creando nueva factura
            return 3   # Óptimo para inicio - filas dinámicas manejadas por JavaScript
        else:  # Modificando factura existente
            return 3   # Consistente para edición

@admin.register(Invoice)
class InvoiceAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ['number', 'date', 'customer', 'company', 'get_status_display', 'subtotal', 'tax_amount', 'total']
    list_filter = ['status', 'date', UserCompanyListFilter]
    search_fields = ['number', 'customer__trade_name', 'customer__identification']
    list_select_related = ['customer', 'company', 'created_by']
    autocomplete_fields = ['customer']  # Habilitar autocompletado para el campo cliente
    inlines = [InvoiceLineInline]
    
    # Acciones grupales para cambio de estado
    actions = ['mark_as_sent', 'mark_as_paid', 'mark_as_cancelled', 'mark_as_draft', 'print_selected_invoices_pdf']
    
    def get_status_display(self, obj):
        """Mostrar estado con colores para facturas de venta"""
        status_colors = {
            'draft': '#6c757d',        # Gris - borrador
            'sent': '#17a2b8',         # Azul - enviada
            'paid': '#28a745',         # Verde - pagada
            'cancelled': '#dc3545',    # Rojo - anulada
        }
        color = status_colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_display.short_description = 'Estado'
    
    def get_actions(self, request):
        """Filtrar acciones disponibles según permisos del usuario"""
        actions = super().get_actions(request)
        
        # Si es superusuario, permitir todas las acciones
        if request and request.user and request.user.is_superuser:
            return actions
        
        # Filtrar acciones según permisos específicos
        filtered_actions = {}
        
        # Verificar permiso para marcar como enviada
        if request.user.has_perm('invoicing.mark_invoice_sent'):
            filtered_actions['mark_as_sent'] = actions.get('mark_as_sent')
        
        # Verificar permiso para marcar como pagada
        if request.user.has_perm('invoicing.mark_invoice_paid'):
            filtered_actions['mark_as_paid'] = actions.get('mark_as_paid')
        
        # Verificar permiso para anular
        if request.user.has_perm('invoicing.mark_invoice_cancelled'):
            filtered_actions['mark_as_cancelled'] = actions.get('mark_as_cancelled')
            # Solo si puede anular, puede marcar como borrador
            filtered_actions['mark_as_draft'] = actions.get('mark_as_draft')
        
        # Imprimir siempre disponible para usuarios con acceso a facturas
        if request.user.has_perm('invoicing.view_invoice'):
            filtered_actions['print_selected_invoices_pdf'] = actions.get('print_selected_invoices_pdf')
        
        return filtered_actions
    
    class Media:
        css = {
            'all': ('admin/css/invoice_lines_clean.css', 'admin/css/intelligent_stock_notifications.css', 'admin/css/bank_observations_field.css')
        }
        js = ('admin/js/simple_calculator.js', 'admin/js/invoice_admin.js', 'admin/js/invoice_line_autocomplete.js', 'admin/js/invoice_totals_calculator.js', 'admin/js/description_autocomplete.js', 'admin/js/tax_breakdown_calculator.js', 'admin/js/simple_payment_handler.js', 'admin/js/bank_observations_handler.js', 'admin/js/stock_validator_soft.js', 'admin/js/stock_updater.js', 'admin/js/intelligent_stock_validator.js')
    
    # Fieldsets base - será personalizado dinámicamente (SIN sección Estado)
    base_fieldsets_no_status = (
        ('Información Básica', {
            'fields': ('company', 'customer', 'date', 'payment_form', 'account', 'bank_observations')
        }),
    )
    
    # Fieldsets originales (mantenidos para referencia si se necesitan)
    base_fieldsets = (
        ('Información Básica', {
            'fields': ('company', 'customer', 'date', 'payment_form', 'account', 'bank_observations')
        }),
        ('Estado', {
            'fields': (('status', 'created_by'),)
        }),
    )
    
    # Fieldsets con totales para edición (SIN sección Estado)
    edit_fieldsets_no_status = (
        ('Información Básica', {
            'fields': ('company', 'customer', 'date', 'payment_form', 'account', 'bank_observations')
        }),
        ('Totales', {
            'fields': (('subtotal', 'tax_amount', 'total'),),
            'classes': ('collapse',)
        }),
    )
    
    # Fieldsets originales (mantenidos para referencia si se necesitan)
    edit_fieldsets = (
        ('Información Básica', {
            'fields': ('company', 'customer', 'date', 'payment_form', 'account', 'bank_observations')
        }),
        ('Totales', {
            'fields': (('subtotal', 'tax_amount', 'total'),),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': (('status', 'created_by'),)
        }),
    )
    
    readonly_fields = []
    
    # ========================================
    # OPCIÓN B: FIELDSETS SIN SECCIÓN ESTADO
    # ========================================
    # Los campos 'status' y 'created_by' se manejan automáticamente:
    # - status: Siempre 'draft' inicial, cambios via acciones grupales
    # - created_by: Asignado automáticamente en save_model()
    # - UX más limpia: Sin sección Estado visible para usuario
    # - Funcionalidad preservada: Lógica de estados sigue funcionando
    
    def get_fieldsets(self, request, obj=None):
        """
        Personalizar fieldsets según si es creación o edición:
        - Añadir factura (obj=None): Sin sección Totales ni Estado
        - Modificar factura (obj exists): Con sección Totales pero sin Estado
        
        OPCIÓN B: Ocultar sección Estado completamente en ambos modos
        """
        if obj is None:  # Creando nueva factura
            return self.base_fieldsets_no_status
        else:  # Editando factura existente
            return self.edit_fieldsets_no_status
    
    # AJAX URLs y vistas
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
            path('filter-accounts-by-payment/', 
                 self.admin_site.admin_view(self.filter_accounts_by_payment_view),
                 name='invoicing_invoice_filter_accounts_by_payment'),
            path('check-product-stock/<int:product_id>/', 
                 self.admin_site.admin_view(self.check_product_stock_view),
                 name='invoicing_invoice_check_product_stock'),
            path('search-products/',
                 self.admin_site.admin_view(self.search_products_ajax_view),
                 name='invoicing_invoice_search_products'),
            path('<path:object_id>/print-pdf/',
                 self.admin_site.admin_view(self.print_invoice_pdf),
                 name='invoicing_invoice_print_pdf'),
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
    
    def filter_accounts_by_payment_view(self, request):
        """Vista AJAX para filtrar cuentas contables por forma de pago"""
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Solo peticiones AJAX'}, status=400)
        
        try:
            from apps.companies.models import PaymentMethod
            from apps.accounting.models import ChartOfAccounts
            
            # Obtener parámetros
            payment_method_id = request.GET.get('payment_method_id')
            company_id = request.GET.get('company_id')
            
            if not payment_method_id:
                return JsonResponse({
                    'accounts': [],
                    'message': 'No se especificó forma de pago'
                })
            
            # Obtener forma de pago y su cuenta padre
            try:
                payment_method = PaymentMethod.objects.get(id=payment_method_id)
                if not payment_method.parent_account:
                    return JsonResponse({
                        'accounts': [],
                        'message': f'Forma de pago "{payment_method.name}" sin cuenta padre configurada'
                    })
            except PaymentMethod.DoesNotExist:
                return JsonResponse({'error': 'Forma de pago no encontrada'}, status=404)
            
            # Filtrar cuentas por empresa del usuario si no es superuser
            accounts_qs = ChartOfAccounts.objects.filter(
                accepts_movement=True
            ).select_related('company')
            
            if company_id:
                accounts_qs = accounts_qs.filter(company_id=company_id)
            elif not request.user.is_superuser:
                from apps.companies.models import CompanyUser
                user_companies = CompanyUser.objects.filter(
                    user=request.user,
                    is_active=True
                ).values_list('company_id', flat=True)
                accounts_qs = accounts_qs.filter(company_id__in=user_companies)
            
            # Filtrar por jerarquía de cuenta padre
            parent_code = payment_method.parent_account.code
            filtered_accounts = accounts_qs.filter(
                code__startswith=parent_code
            ).exclude(
                code=parent_code  # Excluir la cuenta padre
            ).order_by('code')
            
            # Preparar respuesta
            accounts_data = []
            for account in filtered_accounts:
                accounts_data.append({
                    'id': account.id,
                    'code': account.code,
                    'name': account.name,
                    'display': f"{account.code} - {account.name}",
                    'company_name': account.company.trade_name
                })
            
            return JsonResponse({
                'accounts': accounts_data,
                'count': len(accounts_data),
                'payment_method': payment_method.name,
                'parent_account': f"{parent_code} - {payment_method.parent_account.name}"
            })
            
        except Exception as e:
            print(f"❌ Error en filter_accounts_by_payment_view: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

    def get_form(self, request, obj=None, **kwargs):
        """Personalizar formulario según el tipo de usuario"""
        form = super().get_form(request, obj, **kwargs)
        
        # Para usuarios no superusuarios, limitar opciones de empresa
        if request and request.user and not request.user.is_superuser and 'company' in form.base_fields:
            from apps.companies.models import CompanyUser, PaymentMethod
            user_companies_qs = CompanyUser.objects.filter(
                user=request.user, 
                is_active=True
            )
            user_companies = user_companies_qs.values_list('company', flat=True)
            
            if user_companies:
                form.base_fields['company'].queryset = form.base_fields['company'].queryset.filter(
                    id__in=user_companies
                )
                
                # Establecer empresa por defecto para nuevas facturas
                if obj is None:  # Solo para nuevas facturas
                    # Si solo tiene una empresa, establecerla como valor por defecto
                    if len(user_companies) == 1:
                        form.base_fields['company'].initial = user_companies[0]
                        form.base_fields['company'].widget.attrs['readonly'] = True
                        form.base_fields['company'].widget.attrs['style'] = 'background-color: #f8f9fa;'
                    # Si tiene múltiples empresas, establecer la primera como por defecto
                    elif len(user_companies) > 1:
                        form.base_fields['company'].initial = user_companies[0]
                
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
                    
                    # Establecer "Efectivo" como valor por defecto para nuevas facturas
                    if obj is None:  # Solo para nuevas facturas
                        try:
                            efectivo_method = PaymentMethod.objects.filter(
                                is_active=True,
                                name__icontains='efectivo'
                            ).first()
                            if efectivo_method:
                                form.base_fields['payment_form'].initial = efectivo_method.id
                        except PaymentMethod.DoesNotExist:
                            pass
        else:
            # Para superusuarios, configurar valores por defecto
            if obj is None:  # Solo para nuevas facturas
                # Establecer primera empresa disponible como por defecto
                if 'company' in form.base_fields:
                    first_company = form.base_fields['company'].queryset.first()
                    if first_company:
                        form.base_fields['company'].initial = first_company.id
            
            # Para superusuarios, mostrar todas las cuentas que aceptan movimiento
            if 'account' in form.base_fields:
                from apps.accounting.models import ChartOfAccounts
                accounts = ChartOfAccounts.objects.filter(
                    accepts_movement=True
                ).select_related('company', 'account_type').order_by('code')
                form.base_fields['account'].queryset = accounts
            
            # Filtrar formas de pago para superusuario también
            if 'payment_form' in form.base_fields:
                from apps.companies.models import PaymentMethod
                payment_methods = PaymentMethod.objects.filter(
                    is_active=True
                ).order_by('name')
                form.base_fields['payment_form'].queryset = payment_methods
        
        # Establecer "Efectivo" como valor por defecto para TODAS las empresas y usuarios
        if obj is None and 'payment_form' in form.base_fields:  # Solo para nuevas facturas
            from apps.companies.models import PaymentMethod
            try:
                efectivo_method = PaymentMethod.objects.filter(
                    is_active=True,
                    name__icontains='efectivo'
                ).first()
                if efectivo_method:
                    form.base_fields['payment_form'].initial = efectivo_method.id
            except PaymentMethod.DoesNotExist:
                pass
        
        return form
    
    def _check_and_notify_bank_transaction(self, request, invoice):
        """
        Verifica si se creó movimiento bancario y notifica al usuario
        """
        try:
            # Verificar si el módulo banking está disponible
            from apps.banking.models import BankTransaction
            
            # Buscar movimiento bancario para esta factura
            reference = f"FAC-{invoice.id}"
            bank_transaction = BankTransaction.objects.filter(
                reference=reference
            ).first()
            
            if bank_transaction:
                from django.contrib import messages
                messages.success(
                    request,
                    f"🏦 Movimiento bancario creado en {bank_transaction.bank_account.bank.short_name} - {bank_transaction.bank_account.masked_account_number} por ${bank_transaction.amount}"
                )
            else:
                # Verificar si era una transferencia que debería haber creado movimiento
                if (invoice.payment_form and 
                    'transferencia' in invoice.payment_form.name.lower() and 
                    invoice.account):
                    
                    from django.contrib import messages
                    messages.info(
                        request,
                        f"ℹ️ Transferencia a {invoice.account.code} registrada en contabilidad. Movimiento bancario no disponible (cuenta no vinculada con módulo Banking)."
                    )
                    
        except ImportError:
            # Módulo Banking no disponible - normal
            pass
        except Exception as e:
            # Error no crítico - no interrumpir flujo
            print(f"⚠️ Error verificando BankTransaction para factura {invoice.id}: {e}")
    
    def get_readonly_fields(self, request, obj=None):
        """Campos de solo lectura dependiendo de permisos"""
        base_readonly = ['created_by', 'subtotal', 'tax_amount', 'total']
        
        # OPCIÓN B: Ocultar campo status siempre (no aparece en fieldsets)
        # Al no estar en fieldsets, estos campos se manejan automáticamente
        base_readonly.append('status')
        
        # Control de permisos para campo status (mantenido para compatibilidad con acciones)
        if request and request.user and not request.user.is_superuser:
            # Control para CREACIÓN de nueva factura
            if obj is None:
                # Al crear nueva factura, solo usuarios con permisos pueden cambiar status
                if not request.user.has_perm('invoicing.change_invoice_status'):
                    pass  # Ya está en readonly
            else:
                # Al EDITAR factura existente
                if not request.user.has_perm('invoicing.change_invoice_status') and obj.status != 'draft':
                    pass  # Ya está en readonly
        
        if obj and obj.status == 'APPROVED':  # Factura aprobada
            return base_readonly + ['number', 'company', 'customer']
        return base_readonly
    
    def has_change_permission(self, request, obj=None):
        """Controlar acceso a cambios según permisos específicos"""
        # Permiso base de Django
        if not super().has_change_permission(request, obj):
            return False
        
        # Si es superusuario, permitir todo
        if request and request.user and request.user.is_superuser:
            return True
        
        # Si es solo para ver (GET), permitir
        if request.method == 'GET':
            return True
        
        # Validación mejorada para cambios de estado
        if hasattr(request, 'POST') and 'status' in request.POST:
            # Para CREACIÓN (obj=None) con status diferente a draft
            if obj is None:
                requested_status = request.POST.get('status')
                if requested_status and requested_status != 'draft':
                    return request.user.has_perm('invoicing.change_invoice_status')
            # Para EDICIÓN de factura existente
            else:
                return request.user.has_perm('invoicing.change_invoice_status')
        
        # Para otros cambios, permitir con permiso base
        return True
    
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        """Agregar datos optimizados de productos al contexto para JavaScript mejorado"""
        # Obtener productos disponibles para la empresa con datos optimizados
        if request and request.user and request.user.is_superuser:
            products = Product.objects.select_related('company').all()
        elif request and request.user:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user, 
                is_active=True
            ).values_list('company_id', flat=True)
            products = Product.objects.select_related('company').filter(company_id__in=user_companies)
        else:
            products = Product.objects.none()
        
        # Crear diccionario optimizado con más datos para JavaScript
        products_data = {}
        for product in products:
            # Obtener categoría de forma segura para JSON
            category = getattr(product, 'category', None)
            category_name = str(category) if category else 'General'
            
            # Asegurar que todos los valores sean serializables a JSON
            products_data[str(product.id)] = {
                'id': product.id,
                'code': getattr(product, 'code', '') or f'P{product.id:06d}',
                'name': str(product.name),
                'description': str(product.description or product.name),
                'sale_price': float(product.sale_price or 0),
                'unit_of_measure': str(getattr(product, 'unit_of_measure', 'UND')),
                'has_iva': bool(getattr(product, 'has_iva', True)),
                'iva_rate': float(getattr(product, 'iva_rate', 15.00)),
                'current_stock': float(product.get_current_stock() or 0),
                'min_stock': float(getattr(product, 'min_stock', 0)),
                'category': category_name,
                'is_active': bool(getattr(product, 'is_active', True)),
                'company_id': int(product.company_id) if product.company_id else None,
                'company_name': str(product.company.trade_name) if product.company else '',
                # Campos de búsqueda combinados
                'search_text': f"{getattr(product, 'code', '')} {product.name} {product.description or ''}".lower()
            }
        
        # Agregar al contexto para usar en template
        context['products_data_json'] = json.dumps(products_data, ensure_ascii=False)
        
        return super().render_change_form(request, context, add, change, form_url, obj)
    
    def save_model(self, request, obj, form, change):
        """Personalizar el guardado y crear asientos contables automáticos"""
        # Obtener estado anterior si es edición
        old_status = None
        if change and obj.pk:
            try:
                old_status = Invoice.objects.get(pk=obj.pk).status
            except Invoice.DoesNotExist:
                old_status = None
        
        if not change:  # Nueva factura
            if request and request.user:
                obj.created_by = request.user
            
            # OPCIÓN 2: Validación de permisos para estado inicial
            if request and request.user and not request.user.is_superuser:
                # Forzar estado 'draft' si no tiene permisos para cambiar estados
                if not request.user.has_perm('invoicing.change_invoice_status'):
                    if obj.status != 'draft':
                        from django.contrib import messages
                        messages.warning(
                            request,
                            f"⚠️ Estado cambiado a 'Borrador'. No tiene permisos para crear facturas en estado '{obj.get_status_display()}'"
                        )
                        obj.status = 'draft'
            
            # Si es un usuario con empresas limitadas, asignar automáticamente
            if not request.user.is_superuser:
                from apps.companies.models import CompanyUser
                user_companies = CompanyUser.objects.filter(
                    user=request.user, 
                    is_active=True
                )
                if user_companies.count() == 1:
                    obj.company = user_companies.first().company
        

        
        # Guardar la factura
        super().save_model(request, obj, form, change)
        
        # CRÍTICO: Manejar creación de asientos contables INMEDIATAMENTE después del guardado
        # Esto no debe ser afectado por verificaciones de stock
        self._handle_journal_entry_creation(obj, old_status, request)
        
        # OPCIONAL: Verificar stock y mostrar mensajes informativos (no crítico)
        # Se ejecuta al final para no interferir con operaciones críticas
        self._check_stock_and_notify(request, obj)
    
    def _check_stock_and_notify(self, request, invoice):
        """
        Verificar stock de líneas y mostrar mensajes informativos de Django Admin.
        
        CRÍTICO: Esta función NO debe interferir con:
        1. El guardado de la factura
        2. La creación de asientos contables
        3. El cambio de estado de la factura
        
        Solo proporciona información adicional al usuario.
        """
        try:
            # Solo validar stock sin mostrar mensajes invasivos
            # Las notificaciones flotantes JavaScript se encargan del UX
            for line in invoice.lines.all():
                try:
                    stock_info = line.check_stock_availability()
                    # Solo log para debug, NO mensajes invasivos a usuario
                except Exception as line_error:
                    # Error en línea específica no debe afectar el flujo principal
                    print(f"⚠️ Error verificando stock en línea {line.id}: {line_error}")
                    continue
                    
        except Exception as e:
            # Error general en verificación de stock no debe afectar el guardado
            print(f"⚠️ Error general en verificación de stock: {e}")
            pass  # Continuar sin mostrar mensajes de stock
    
    def _handle_journal_entry_creation(self, invoice, old_status, request):
        """Maneja la creación de asientos contables según cambios de estado"""
        from apps.accounting.services import AutomaticJournalEntryService
        from django.contrib import messages
        
        current_status = invoice.status
        
        # Crear asiento cuando cambia a "Enviada" (sent)
        if current_status == 'sent' and old_status != 'sent':
            try:
                journal_entry, created = AutomaticJournalEntryService.create_journal_entry_from_invoice(invoice)
                
                if created and journal_entry:
                    messages.success(
                        request,
                        f"✅ Asiento contable #{journal_entry.number} creado automáticamente para factura #{invoice.number}"
                    )
                    
                    # Verificar si se creó también movimiento bancario
                    self._check_and_notify_bank_transaction(request, invoice)
                elif journal_entry and not created:
                    messages.warning(
                        request,
                        f"⚠️ Ya existe asiento contable #{journal_entry.number} para esta factura"
                    )
                else:
                    messages.error(
                        request,
                        "❌ Error al crear asiento contable. Verifique datos de la factura y configuración de cuentas"
                    )
            except Exception as e:
                messages.error(
                    request,
                    f"❌ Error al crear asiento contable: {str(e)}"
                )
        
        # Crear reversión cuando se anula factura
        elif current_status == 'cancelled' and old_status != 'cancelled':
            try:
                reverse_entry, created = AutomaticJournalEntryService.reverse_journal_entry(invoice)
                
                if created and reverse_entry:
                    messages.success(
                        request,
                        f"🔄 Asiento de reversión #{reverse_entry.number} creado para factura anulada"
                    )
                elif reverse_entry and not created:
                    messages.warning(
                        request,
                        f"⚠️ Ya existe asiento de reversión #{reverse_entry.number} para esta factura"
                    )
                else:
                    messages.warning(
                        request,
                        "⚠️ No se encontró asiento original para crear la reversión"
                    )
            except Exception as e:
                messages.error(
                    request,
                    f"❌ Error al crear asiento de reversión: {str(e)}"
                )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Personalizar campos de clave externa"""
        if db_field.name == "customer":
            # Filtrar solo clientes de las empresas del usuario
            if not request.user.is_superuser:
                from apps.companies.models import CompanyUser
                user_companies = CompanyUser.objects.filter(
                    user=request.user,
                    is_active=True
                ).values_list('company', flat=True)
                if user_companies:
                    kwargs["queryset"] = Customer.objects.filter(company__in=user_companies)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_queryset(self, request):
        """Filtrar facturas según permisos de usuario"""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user,
                is_active=True
            ).values_list('company', flat=True)
            if user_companies:
                qs = qs.filter(company__in=user_companies)
        return qs
    
    def check_product_stock_view(self, request, product_id):
        """Vista para verificar stock de producto via AJAX"""
        try:
            from django.http import JsonResponse
            from apps.inventory.models import Product
            
            product = Product.objects.get(id=product_id)
            quantity = float(request.GET.get('quantity', 0))
            current_stock = product.get_current_stock()
            
            response_data = {
                'product_name': product.name,
                'available_stock': current_stock,
                'requested_quantity': quantity,
                'has_sufficient_stock': current_stock >= quantity,
                'shortage': max(0, quantity - current_stock) if quantity > current_stock else 0
            }
            
            return JsonResponse(response_data)
            
        except Product.DoesNotExist:
            return JsonResponse({
                'error': True,
                'message': 'Producto no encontrado'
            }, status=404)
        except ValueError:
            return JsonResponse({
                'error': True,
                'message': 'Cantidad inválida'
            }, status=400)
    
    def search_products_ajax_view(self, request):
        """Vista AJAX para búsqueda inteligente de productos"""
        from django.http import JsonResponse
        from django.db.models import Q
        from apps.inventory.models import Product
        
        # Verificar que sea petición AJAX
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Solo peticiones AJAX'}, status=400)
            
        # Solo permitir GET
        if request.method != 'GET':
            return JsonResponse({'error': 'Método no permitido'}, status=405)
        
        try:
            query = request.GET.get('q', '').strip()
            company_id = request.GET.get('company_id')
            limit = int(request.GET.get('limit', 20))
            
            if len(query) < 2:
                return JsonResponse({
                    'results': [],
                    'message': 'Ingrese al menos 2 caracteres para buscar'
                })
            
            # Filtros base
            filters = Q(is_active=True)
            
            # Filtrar por empresa si se especifica
            if company_id:
                filters &= Q(company_id=company_id)
            elif not request.user.is_superuser:
                # Para usuarios no admin, filtrar por empresas permitidas
                from apps.companies.models import CompanyUser
                user_companies = CompanyUser.objects.filter(
                    user=request.user, 
                    is_active=True
                ).values_list('company_id', flat=True)
                if user_companies:
                    filters &= Q(company_id__in=user_companies)
            
            # Búsqueda inteligente por código, nombre y descripción
            search_filters = (
                Q(code__icontains=query) |
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )
            
            products = Product.objects.filter(filters & search_filters).select_related(
                'company'
            ).order_by('code', 'name')[:limit]
            
            results = []
            for product in products:
                # Obtener stock actual de forma segura
                try:
                    current_stock = float(getattr(product, 'current_stock', 0))
                except (ValueError, TypeError):
                    current_stock = 0
                
                # Determinar estado del stock
                if current_stock > 10:
                    stock_status = 'ok'
                elif current_stock > 0:
                    stock_status = 'low'
                else:
                    stock_status = 'out'
                
                results.append({
                    'id': product.id,
                    'code': getattr(product, 'code', '') or f'P{product.id:06d}',
                    'name': product.name,
                    'description': product.description or product.name,
                    'sale_price': float(product.sale_price or 0),
                    'iva_rate': float(getattr(product, 'iva_rate', 15.00)),
                    'current_stock': current_stock,
                    'stock_status': stock_status,
                    'category': str(getattr(product, 'category', 'General')),
                    'company_name': product.company.trade_name if product.company else '',
                    'display_text': f"{getattr(product, 'code', '')} - {product.name}",
                    'full_info': f"{getattr(product, 'code', '')} - {product.name} (Stock: {current_stock}) - ${product.sale_price}"
                })
            
            return JsonResponse({
                'results': results,
                'total_found': len(results),
                'query': query
            })
            
        except Exception as e:
            return JsonResponse({
                'error': f'Error en búsqueda: {str(e)}',
                'results': []
            }, status=500)
            
        except Exception as e:
            return JsonResponse({
                'error': True,
                'message': f'Error en búsqueda: {str(e)}'
            }, status=500)
        except Exception as e:
            return JsonResponse({
                'error': True,
                'message': f'Error interno: {str(e)}'
            }, status=500)
    
    def print_invoice_pdf(self, request, object_id):
        """Generar PDF de la factura"""
        from django.shortcuts import get_object_or_404
        from django.http import HttpResponse
        from .invoice_pdf import generate_invoice_pdf
        
        invoice = get_object_or_404(Invoice, pk=object_id)
        
        # Verificar permisos de empresa si no es superuser
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user, is_active=True
            ).values_list('company', flat=True)
            
            if invoice.company_id not in user_companies:
                from django.core.exceptions import PermissionDenied
                raise PermissionDenied("No tiene permisos para ver esta factura")
        
        # Generar PDF
        pdf_buffer = generate_invoice_pdf(invoice)
        
        # Preparar respuesta
        filename = f"Factura_{invoice.number}_{invoice.customer.trade_name.replace(' ', '_')}.pdf"
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response

    def response_add(self, request, obj, post_url_continue=None):
        """Respuesta personalizada después de agregar"""
        if "_addanother" in request.POST:
            return super().response_add(request, obj, post_url_continue)
        elif "_continue" in request.POST:
            return super().response_add(request, obj, post_url_continue)
        else:
            # Redirigir a la lista de facturas
            return self.response_post_save_add(request, obj)
    
    # ==========================================
    # ACCIONES GRUPALES PARA CAMBIO DE ESTADO
    # ==========================================
    
    def mark_as_sent(self, request, queryset):
        """Marcar facturas seleccionadas como 'Enviadas'"""
        # Validar permiso específico
        if not request.user.has_perm('invoicing.mark_invoice_sent'):
            self.message_user(
                request,
                "❌ No tiene permisos para marcar facturas como enviadas",
                level=messages.ERROR
            )
            return
        
        updated = 0
        errors = []
        
        for invoice in queryset:
            try:
                if invoice.status != 'sent':
                    old_status = invoice.status
                    invoice.status = 'sent'
                    invoice.save()
                    
                    # Crear asiento contable automáticamente
                    self._handle_journal_entry_creation(invoice, old_status, request)
                    updated += 1
                    
            except Exception as e:
                errors.append(f"Error en factura {invoice.number}: {str(e)}")
        
        if updated:
            self.message_user(
                request, 
                f"✅ {updated} factura(s) marcada(s) como 'Enviadas' exitosamente."
            )
        if errors:
            self.message_user(
                request,
                f"❌ Errores: {'; '.join(errors)}",
                level=messages.ERROR
            )
    
    mark_as_sent.short_description = "📤 Marcar como Enviadas"
    
    def mark_as_paid(self, request, queryset):
        """Marcar facturas seleccionadas como 'Pagadas'"""
        # Validar permiso específico
        if not request.user.has_perm('invoicing.mark_invoice_paid'):
            self.message_user(
                request,
                "❌ No tiene permisos para marcar facturas como pagadas",
                level=messages.ERROR
            )
            return
        
        updated = 0
        errors = []
        
        for invoice in queryset:
            try:
                if invoice.status != 'paid':
                    old_status = invoice.status
                    invoice.status = 'paid'
                    invoice.save()
                    
                    # Crear asiento contable si es necesario
                    if old_status != 'sent':  # Si no venía de 'sent', crear asiento
                        self._handle_journal_entry_creation(invoice, old_status, request)
                    updated += 1
                    
            except Exception as e:
                errors.append(f"Error en factura {invoice.number}: {str(e)}")
        
        if updated:
            self.message_user(
                request, 
                f"✅ {updated} factura(s) marcada(s) como 'Pagadas' exitosamente."
            )
        if errors:
            self.message_user(
                request,
                f"❌ Errores: {'; '.join(errors)}",
                level=messages.ERROR
            )
    
    mark_as_paid.short_description = "💰 Marcar como Pagadas"
    
    def mark_as_cancelled(self, request, queryset):
        """Marcar facturas seleccionadas como 'Anuladas'"""
        # Validar permiso específico
        if not request.user.has_perm('invoicing.mark_invoice_cancelled'):
            self.message_user(
                request,
                "❌ No tiene permisos para anular facturas",
                level=messages.ERROR
            )
            return
        
        updated = 0
        errors = []
        
        for invoice in queryset:
            try:
                if invoice.status != 'cancelled':
                    old_status = invoice.status
                    invoice.status = 'cancelled'
                    invoice.save()
                    
                    # Crear asiento de reversión si tenía asiento contable
                    if old_status in ['sent', 'paid']:
                        from apps.accounting.services import AutomaticJournalEntryService
                        AutomaticJournalEntryService.reverse_journal_entry(invoice)
                    
                    updated += 1
                    
            except Exception as e:
                errors.append(f"Error en factura {invoice.number}: {str(e)}")
        
        if updated:
            self.message_user(
                request, 
                f"✅ {updated} factura(s) marcada(s) como 'Anuladas' exitosamente."
            )
        if errors:
            self.message_user(
                request,
                f"❌ Errores: {'; '.join(errors)}",
                level=messages.ERROR
            )
    
    mark_as_cancelled.short_description = "❌ Marcar como Anuladas"
    
    def mark_as_draft(self, request, queryset):
        """Marcar facturas seleccionadas como 'Borrador'"""
        # Validar permiso específico (mismo que anular)
        if not request.user.has_perm('invoicing.mark_invoice_cancelled'):
            self.message_user(
                request,
                "❌ No tiene permisos para cambiar facturas a borrador",
                level=messages.ERROR
            )
            return
        
        updated = 0
        errors = []
        
        for invoice in queryset:
            try:
                if invoice.status != 'draft':
                    old_status = invoice.status
                    invoice.status = 'draft'
                    invoice.save()
                    
                    # Crear asiento de reversión si tenía asiento contable
                    if old_status in ['sent', 'paid']:
                        from apps.accounting.services import AutomaticJournalEntryService
                        AutomaticJournalEntryService.reverse_journal_entry(invoice)
                    
                    updated += 1
                    
            except Exception as e:
                errors.append(f"Error en factura {invoice.number}: {str(e)}")
        
        if updated:
            self.message_user(
                request, 
                f"✅ {updated} factura(s) marcada(s) como 'Borrador' exitosamente."
            )
        if errors:
            self.message_user(
                request,
                f"❌ Errores: {'; '.join(errors)}",
                level=messages.ERROR
            )
    
    mark_as_draft.short_description = "📝 Marcar como Borrador"
    
    def print_selected_invoices_pdf(self, request, queryset):
        """Acción masiva para imprimir facturas seleccionadas"""
        from django.http import HttpResponse
        from .invoice_pdf import generate_invoice_pdf
        from io import BytesIO
        import zipfile
        
        # Filtrar facturas según permisos del usuario
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user, is_active=True
            ).values_list('company', flat=True)
            queryset = queryset.filter(company__in=user_companies)
        
        if queryset.count() == 0:
            from django.contrib import messages
            messages.error(request, "No se encontraron facturas para imprimir")
            return
        
        elif queryset.count() == 1:
            # Si es solo una factura, generar PDF individual
            invoice = queryset.first()
            pdf_buffer = generate_invoice_pdf(invoice)
            filename = f"Factura_{invoice.number}_{invoice.customer.trade_name.replace(' ', '_')}.pdf"
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        
        else:
            # Múltiples facturas: crear ZIP con PDFs individuales
            zip_buffer = BytesIO()
            processed_count = 0
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for invoice in queryset:
                    try:
                        pdf_buffer = generate_invoice_pdf(invoice)
                        safe_customer_name = invoice.customer.trade_name.replace(' ', '_').replace('/', '_')[:50]
                        filename = f"Factura_{invoice.number}_{safe_customer_name}.pdf"
                        zip_file.writestr(filename, pdf_buffer.getvalue())
                        processed_count += 1
                        
                    except Exception as e:
                        # Si hay error con una factura, continuar con las demás
                        print(f"Error generando PDF para factura {invoice.number}: {e}")
                        continue
            
            if processed_count == 0:
                from django.contrib import messages
                messages.error(request, "No se pudieron generar PDFs de las facturas seleccionadas")
                return
            
            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="Facturas_{processed_count}_documentos.zip"'
            
            from django.contrib import messages
            messages.success(request, f"✅ Se generaron {processed_count} facturas en PDF")
            return response
    
    print_selected_invoices_pdf.short_description = "🖨️ Imprimir facturas seleccionadas"
    
    def print_selected_invoices_pdf(self, request, queryset):
        """Acción masiva para imprimir facturas seleccionadas"""
        from django.http import HttpResponse
        from .invoice_pdf import generate_invoice_pdf
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate
        from io import BytesIO
        import zipfile
        
        if queryset.count() == 1:
            # Si es solo una factura, generar PDF individual
            invoice = queryset.first()
            pdf_buffer = generate_invoice_pdf(invoice)
            filename = f"Factura_{invoice.number}_{invoice.customer.trade_name.replace(' ', '_')}.pdf"
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        
        elif queryset.count() > 1:
            # Múltiples facturas: crear ZIP con PDFs individuales
            zip_buffer = BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for invoice in queryset:
                    try:
                        # Verificar permisos por factura
                        if not request.user.is_superuser:
                            from apps.companies.models import CompanyUser
                            user_companies = CompanyUser.objects.filter(
                                user=request.user, is_active=True
                            ).values_list('company', flat=True)
                            
                            if invoice.company_id not in user_companies:
                                continue  # Saltar facturas sin permisos
                        
                        pdf_buffer = generate_invoice_pdf(invoice)
                        filename = f"Factura_{invoice.number}_{invoice.customer.trade_name.replace(' ', '_')}.pdf"
                        zip_file.writestr(filename, pdf_buffer.getvalue())
                        
                    except Exception as e:
                        # Si hay error con una factura, continuar con las demás
                        continue
            
            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="Facturas_Seleccionadas.zip"'
            return response
        
        else:
            from django.contrib import messages
            messages.error(request, "No se seleccionaron facturas para imprimir")
    
    print_selected_invoices_pdf.short_description = "🖨️ Imprimir facturas seleccionadas"