from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from apps.core.filters import UserCompanyListFilter
from .models import Supplier, PurchaseInvoice, PurchaseInvoiceLine


class PurchaseInvoiceLineInline(admin.TabularInline):
    """Inline para líneas de factura de compra"""
    model = PurchaseInvoiceLine
    extra = 1
    fields = ('product', 'description', 'quantity', 'unit_cost', 'discount', 'iva_rate', 'account', 'line_total')
    readonly_fields = ('line_total',)
    
    def get_queryset(self, request):
        """Optimizar queryset con select_related y filtrar por empresa"""
        qs = super().get_queryset(request)
        qs = qs.select_related('product', 'account')
        
        # Filtrar por empresas del usuario
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            if user_companies:
                qs = qs.filter(purchase_invoice__company_id__in=user_companies)
            else:
                qs = qs.none()
        
        return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtrar foreign keys por empresa del usuario"""
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            if db_field.name == 'product':
                # Solo productos de empresas del usuario
                kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                    company_id__in=user_companies
                )
            elif db_field.name == 'account':
                # Solo cuentas de empresas del usuario
                kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                    company_id__in=user_companies
                )
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Administración de proveedores"""
    list_display = ('identification', 'trade_name', 'supplier_type', 'email', 'phone', 'payment_terms', 'retention_status', 'is_active')
    list_filter = ('supplier_type', UserCompanyListFilter, 'retention_agent', 'sri_classification', 'is_active', 'created_at')
    search_fields = ('identification', 'trade_name', 'legal_name', 'email')
    ordering = ('trade_name',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('company', 'supplier_type', 'identification', 'trade_name', 'legal_name')
        }),
        ('Contacto', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Configuración Comercial', {
            'fields': ('credit_limit', 'payment_terms')
        }),
        ('Configuración Contable', {
            'fields': ('payable_account', 'expense_account'),
            'classes': ('collapse',)
        }),
        ('Retenciones Ecuatorianas - IMPLEMENTADO', {
            'fields': (
                'retention_agent',
                'sri_classification', 
                'iva_retention_percentage',
                'ir_retention_percentage'
            ),
            'description': (
                'Configure las retenciones automáticas según normativas ecuatorianas. '
                'El sistema calculará automáticamente los porcentajes según la clasificación SRI, '
                'pero puede personalizar los valores específicos para este proveedor.'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def retention_status(self, obj):
        """Indica el estado de configuración de retenciones"""
        if not obj.retention_agent:
            return "❌ No aplica"
        
        rates = obj.get_automatic_retention_rates()
        iva_rate = rates.get('iva_retention', 0)
        ir_rate = rates.get('ir_retention', 0)
        
        if iva_rate > 0 or ir_rate > 0:
            return f"✅ IVA:{iva_rate}% IR:{ir_rate}%"
        return "⚠️ Sin configurar"
        
    retention_status.short_description = 'Estado Retenciones'
    
    def get_queryset(self, request):
        """Filtrar estrictamente por empresas asignadas al usuario"""
        qs = super().get_queryset(request)
        
        # Solo superuser ve todo
        if request.user.is_superuser:
            return qs
            
        # Usuarios normales solo ven sus empresas asignadas
        from apps.companies.models import CompanyUser
        user_companies = CompanyUser.objects.filter(
            user=request.user
        ).values_list('company_id', flat=True)
        
        if user_companies:
            return qs.filter(company_id__in=user_companies)
        else:
            # Si no tiene empresas asignadas, no ve nada
            return qs.none()
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtrar foreign keys estrictamente por empresa del usuario"""
        from apps.companies.models import CompanyUser
        
        # Solo superuser ve todo
        if not request.user.is_superuser:
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            if db_field.name == "company":
                # Solo empresas asignadas al usuario
                kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                    id__in=user_companies
                )
            
            elif db_field.name in ["payable_account", "expense_account"]:
                # Solo cuentas de empresas del usuario
                kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                    company_id__in=user_companies
                )
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    """Administración de facturas de compra"""
    list_display = (
        'internal_number', 
        'supplier_invoice_number', 
        'supplier', 
        'date', 
        'due_date',
        'get_status_display',
        'total_amount',
        'retentions_summary',
        'net_payable_amount',
        'payment_form',
        'print_retention_voucher_button',
        'purchase_invoice_buttons'
    )
    list_filter = ('status', UserCompanyListFilter, 'date', 'payment_form', 'created_at')
    search_fields = ('internal_number', 'supplier_invoice_number', 'supplier__trade_name', 'supplier__identification')
    ordering = ('-date', '-internal_number')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('company', 'supplier', 'supplier_invoice_number', 'internal_number')
        }),
        ('Fechas', {
            'fields': ('date', 'due_date')
        }),
        ('Configuración', {
            'fields': ('payment_form', 'payable_account', 'status')
        }),
        ('Montos Básicos', {
            'fields': ('subtotal', 'tax_amount', 'total'),
            'classes': ('collapse',)
        }),
        ('Retenciones Ecuatorianas - IMPLEMENTADO', {
            'fields': (
                ('iva_retention_percentage', 'iva_retention_amount'),
                ('ir_retention_percentage', 'ir_retention_amount'),
                'total_retentions',
                'net_payable'
            ),
            'description': 'Retenciones aplicadas según normativas ecuatorianas. Los cálculos son automáticos según la configuración del proveedor.',
            'classes': ('collapse',)
        }),
        ('Comprobante de Retención', {
            'fields': ('retention_voucher_number', 'retention_voucher_date'),
            'classes': ('collapse',)
        }),
        ('Información Adicional', {
            'fields': ('reference', 'notes', 'received_by'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = (
        'internal_number', 'subtotal', 'tax_amount', 'total',
        'iva_retention_amount', 'ir_retention_amount', 'total_retentions', 'net_payable',
        'retention_voucher_number', 'retention_voucher_date'
    )
    inlines = [PurchaseInvoiceLineInline]
    
    # Acciones en lote
    actions = [
        'mark_as_received', 
        'mark_as_validated', 
        'mark_as_paid', 
        'mark_as_cancelled', 
        'create_journal_entries',
        'print_multiple_retention_vouchers',
        'print_selected_purchase_invoices_pdf'
    ]
    
    def retentions_summary(self, obj):
        """Muestra resumen de retenciones aplicadas"""
        if obj.total_retentions <= 0:
            return "❌ Sin retenciones"
        
        summary_parts = []
        if obj.iva_retention_amount > 0:
            summary_parts.append(f"IVA: ${obj.iva_retention_amount}")
        if obj.ir_retention_amount > 0:
            summary_parts.append(f"IR: ${obj.ir_retention_amount}")
        
        return " | ".join(summary_parts) if summary_parts else "❌"
    
    retentions_summary.short_description = 'Retenciones'
    
    def net_payable_amount(self, obj):
        """Muestra el monto neto a pagar"""
        if obj.total_retentions > 0:
            return f"${obj.net_payable} (neto)"
        return f"${obj.total}"
    
    net_payable_amount.short_description = 'Neto a Pagar'
    
    def total_amount(self, obj):
        """Muestra total con indicador de retenciones"""
        if obj.total_retentions > 0:
            return f"${obj.total} (🧮 con ret.)"
        return f"${obj.total}"
    
    total_amount.short_description = 'Total Factura'

    def print_retention_voucher_button(self, obj):
        """Botón para imprimir comprobante de retención"""
        if obj.total_retentions <= 0:
            return "❌ Sin retenciones"
        
        # Generar URL para impresión
        print_url = reverse('suppliers:print_retention_voucher', args=[obj.pk])
        
        return format_html(
            '<a href="{}" target="_blank" class="button" style="'
            'background-color: #28a745; color: white; padding: 5px 10px; '
            'text-decoration: none; border-radius: 3px; font-size: 12px;">'
            '🖨️ PDF</a>',
            print_url
        )
    
    print_retention_voucher_button.short_description = 'Retención'
    print_retention_voucher_button.allow_tags = True

    def get_status_display(self, obj):
        """Mostrar estado con colores"""
        status_colors = {
            'draft': 'gray',
            'received': 'blue',
            'validated': 'green',
            'paid': 'purple',
            'cancelled': 'red',
        }
        color = status_colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_display.short_description = 'Estado'
    
    def total_amount(self, obj):
        """Mostrar total formateado"""
        return f"${obj.total:,.2f}"
    total_amount.short_description = 'Total'
    
    def get_queryset(self, request):
        """Filtrar estrictamente por empresas del usuario y optimizar consultas"""
        qs = super().get_queryset(request)
        qs = qs.select_related('company', 'supplier', 'payment_form', 'payable_account', 'received_by')
        
        # Solo superuser ve todo
        if request.user.is_superuser:
            return qs
            
        # Usuarios normales solo ven sus empresas asignadas
        from apps.companies.models import CompanyUser
        user_companies = CompanyUser.objects.filter(
            user=request.user
        ).values_list('company_id', flat=True)
        
        if user_companies:
            return qs.filter(company_id__in=user_companies)
        else:
            # Si no tiene empresas asignadas, no ve nada
            return qs.none()
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtrar foreign keys estrictamente por empresa del usuario"""
        from apps.companies.models import CompanyUser
        
        # Solo superuser ve todo
        if not request.user.is_superuser:
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            if db_field.name == "company":
                # Solo empresas asignadas al usuario
                kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                    id__in=user_companies
                )
            
            elif db_field.name == "supplier":
                # Solo proveedores de empresas del usuario
                kwargs["queryset"] = Supplier.objects.filter(
                    company_id__in=user_companies
                )
            
            elif db_field.name in ["payable_account"]:
                # Solo cuentas de empresas del usuario
                kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                    company_id__in=user_companies
                )
            
            elif db_field.name == "received_by":
                # Solo usuarios de las mismas empresas
                company_user_ids = CompanyUser.objects.filter(
                    company_id__in=user_companies
                ).values_list('user_id', flat=True)
                kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                    id__in=company_user_ids
                )
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        """Configurar usuario y empresa por defecto, generar asientos"""
        if not obj.received_by_id:
            obj.received_by = request.user
        
        # Asegurar que se usa una empresa del usuario si no es superuser
        if not request.user.is_superuser and not change:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            
            if user_companies and not obj.company_id:
                # Asignar primera empresa del usuario por defecto
                obj.company_id = user_companies[0]
        
        super().save_model(request, obj, form, change)
        
        # Crear asiento contable automáticamente si está validada
        if obj.status in ['validated', 'paid']:
            obj.create_journal_entry()
    
    # Acciones en lote
    @admin.action(description='📥 Marcar como recibidas (sin actualizar inventario)')
    def mark_as_received(self, request, queryset):
        # Filtrar por empresas del usuario para seguridad
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            queryset = queryset.filter(company_id__in=user_companies)
        
        updated = 0
        with transaction.atomic():
            for invoice in queryset.filter(status='draft'):
                invoice.status = 'received'
                invoice.save()
                updated += 1
        
        # Mensaje simple - solo cambio de estado, sin inventario
        self.message_user(request, f'{updated} facturas marcadas como recibidas. El inventario se actualizará al validar la factura.')
    
    @admin.action(description='✅ Marcar como validadas (crea asiento en borrador)')
    def mark_as_validated(self, request, queryset):
        # Filtrar por empresas del usuario para seguridad
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            queryset = queryset.filter(company_id__in=user_companies)
        
        updated = 0
        created_entries = 0
        with transaction.atomic():
            for invoice in queryset.filter(status__in=['draft', 'received']):
                old_status = invoice.status
                invoice.status = 'validated'
                invoice.save()
                
                # Crear asiento contable
                entry = invoice.create_journal_entry()
                if entry:
                    created_entries += 1
                
                # FLUJO CORREGIDO: NO actualizar inventario aquí
                # El inventario se actualizará cuando el asiento se contabilice
                # Esto mantiene la consistencia: asiento posted = inventario actualizado
                
                updated += 1
        
        # Mensaje actualizado sin inventario
        message_parts = [f'{updated} facturas validadas', f'{created_entries} asientos contables creados (en borrador)']
        message_parts.append('El inventario se actualizará al contabilizar los asientos')
        
        self.message_user(request, '. '.join(message_parts) + '.')
    

    
    @admin.action(description='💳 Marcar como pagadas')
    def mark_as_paid(self, request, queryset):
        # Filtrar por empresas del usuario para seguridad
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            queryset = queryset.filter(company_id__in=user_companies)
        
        updated = 0
        with transaction.atomic():
            for invoice in queryset.filter(status__in=['received', 'validated']):
                invoice.status = 'paid'
                invoice.save()
                updated += 1
        
        self.message_user(request, f'{updated} facturas marcadas como pagadas.')
    
    @admin.action(description='❌ Marcar como anuladas')
    def mark_as_cancelled(self, request, queryset):
        # Filtrar por empresas del usuario para seguridad
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            queryset = queryset.filter(company_id__in=user_companies)
        
        updated = 0
        with transaction.atomic():
            for invoice in queryset.exclude(status='cancelled'):
                invoice.status = 'cancelled'
                invoice.save()
                updated += 1
        
        self.message_user(request, f'{updated} facturas anuladas.')
    
    @admin.action(description='📊 Crear asientos contables')
    def create_journal_entries(self, request, queryset):
        # Filtrar por empresas del usuario para seguridad
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            queryset = queryset.filter(company_id__in=user_companies)
        
        created = 0
        skipped = 0
        with transaction.atomic():
            for invoice in queryset.filter(status__in=['validated', 'paid']):
                entry = invoice.create_journal_entry()
                if entry:
                    created += 1
                else:
                    skipped += 1
        
        message = f'{created} asientos contables creados.'
        if skipped > 0:
            message += f' {skipped} facturas omitidas (ya tenían asiento).'
        
        self.message_user(request, message)
    
    @admin.action(description='🧾 Imprimir comprobantes de retención (PDF)')
    def print_multiple_retention_vouchers(self, request, queryset):
        """Acción para imprimir múltiples comprobantes de retención"""
        # Filtrar por empresas del usuario para seguridad
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            queryset = queryset.filter(company_id__in=user_companies)
        
        # Filtrar solo facturas con retenciones
        invoices_with_retentions = queryset.filter(total_retentions__gt=0)
        
        if not invoices_with_retentions.exists():
            self.message_user(
                request, 
                "No se encontraron facturas con retenciones en la selección.",
                level='warning'
            )
            return
        
        # Generar URL para múltiples comprobantes
        invoice_ids = list(invoices_with_retentions.values_list('id', flat=True))
        print_url = reverse('suppliers:print_multiple_retention_vouchers')
        print_url += f"?invoice_ids={','.join(map(str, invoice_ids))}"
        
        # Redirigir para abrir PDF en nueva ventana
        from django.shortcuts import redirect
        return redirect(print_url)

    # ===============================
    # FUNCIONALIDAD PDF FACTURAS DE COMPRA
    # ===============================
    
    def get_urls(self):
        """Agregar URLs personalizadas para PDF de facturas (sin afectar sistemas existentes)"""
        from django.urls import path as url_path
        urls = super().get_urls()
        custom_urls = [
            url_path(
                '<int:object_id>/print-pdf/',
                self.admin_site.admin_view(self.print_purchase_invoice_pdf),
                name='suppliers_purchaseinvoice_print_pdf',
            ),
        ]
        return custom_urls + urls
    
    def print_purchase_invoice_pdf(self, request, object_id):
        """Generar PDF individual de factura de compra (sin afectar sistemas existentes)"""
        try:
            # Obtener factura con validación de empresa
            invoice = get_object_or_404(PurchaseInvoice, pk=object_id)
            
            # Validación de seguridad por empresa
            if not request.user.is_superuser:
                from apps.companies.models import CompanyUser
                user_companies = CompanyUser.objects.filter(
                    user=request.user
                ).values_list('company_id', flat=True)
                
                if invoice.company_id not in user_companies:
                    messages.error(request, "No tiene permisos para acceder a esta factura.")
                    return HttpResponse("Acceso denegado", status=403)
            
            # Generar PDF usando el nuevo generador
            from .purchase_invoice_pdf_enhanced import generate_purchase_invoice_pdf_enhanced
            
            pdf_buffer = generate_purchase_invoice_pdf_enhanced(invoice)
            
            # Crear respuesta HTTP con PDF para descarga
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="factura_compra_{invoice.internal_number}.pdf"'
            response.write(pdf_buffer.read())
            
            return response
            
        except Exception as e:
            messages.error(request, f"Error al generar PDF: {str(e)}")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    def purchase_invoice_buttons(self, obj):
        """Botones adicionales para facturas (sin afectar funcionalidad existente)"""
        buttons = []
        
        # Botón PDF de factura (nuevo)
        if obj.pk:
            pdf_url = reverse('admin:suppliers_purchaseinvoice_print_pdf', args=[obj.pk])
            buttons.append(
                f'<a href="{pdf_url}" class="button" target="_blank" '
                f'style="margin: 2px; padding: 8px 12px; background-color: #417690; '
                f'color: white; text-decoration: none; border-radius: 4px; display: inline-flex; align-items: center;">'
                f'<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="margin-right: 6px;"><path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zM16 19H8v-5h8v5zM19 12c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-3-7H8v2h8V5z"/></svg>PDF</a>'
            )
        
        return mark_safe(' '.join(buttons))
    purchase_invoice_buttons.short_description = 'Factura Compra'
    
    @admin.action(description='🖨️ Imprimir facturas seleccionadas (PDF)')
    def print_selected_purchase_invoices_pdf(self, request, queryset):
        """Imprimir múltiples facturas de compra en PDF (sin afectar sistemas existentes)"""
        # Aplicar filtros de empresa
        if not request.user.is_superuser:
            from apps.companies.models import CompanyUser
            user_companies = CompanyUser.objects.filter(
                user=request.user
            ).values_list('company_id', flat=True)
            queryset = queryset.filter(company_id__in=user_companies)
        
        if not queryset.exists():
            self.message_user(
                request, 
                "No se encontraron facturas válidas para imprimir.",
                level='warning'
            )
            return
        
        # Generar URL para múltiples facturas
        invoice_ids = list(queryset.values_list('id', flat=True))
        print_url = reverse('suppliers:print_multiple_purchase_invoices_pdf')
        print_url += f"?invoice_ids={','.join(map(str, invoice_ids))}"
        
        # Redirigir para abrir PDF en nueva ventana
        from django.shortcuts import redirect
        return redirect(print_url)


@admin.register(PurchaseInvoiceLine)
class PurchaseInvoiceLineAdmin(admin.ModelAdmin):
    """Administración de líneas de factura de compra (vista independiente)"""
    list_display = (
        'purchase_invoice', 
        'description', 
        'product', 
        'quantity', 
        'unit_cost', 
        'discount',
        'iva_rate',
        'line_total'
    )
    list_filter = (UserCompanyListFilter, 'product', 'iva_rate', 'created_at')
    search_fields = (
        'description', 
        'product__name', 
        'product__code',
        'purchase_invoice__internal_number',
        'purchase_invoice__supplier__trade_name'
    )
    ordering = ('-purchase_invoice__date', 'id')
    
    def get_queryset(self, request):
        """Filtrar estrictamente por empresas del usuario"""
        qs = super().get_queryset(request)
        qs = qs.select_related('purchase_invoice', 'product', 'account')
        
        # Solo superuser ve todo
        if request.user.is_superuser:
            return qs
            
        # Usuarios normales solo ven líneas de sus empresas
        from apps.companies.models import CompanyUser
        user_companies = CompanyUser.objects.filter(
            user=request.user
        ).values_list('company_id', flat=True)
        
        if user_companies:
            return qs.filter(purchase_invoice__company_id__in=user_companies)
        else:
            # Si no tiene empresas asignadas, no ve nada
            return qs.none()