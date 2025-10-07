from django.contrib import admin
from django.contrib import messages
from django.utils import timezone
from django.utils.html import format_html
from django import forms
from django.urls import path
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from datetime import date
from .models import (
    AccountType, ChartOfAccounts, JournalEntry, JournalEntryLine, 
    FiscalYear, AccountBalance
)
from apps.core.filters import UserCompanyListFilter, UserCompanyAccountFilter, UserCompanyJournalFilter
from apps.companies.models import CompanyUser


class CompanyFilterMixin:
    """Mixin para filtrar por empresa del usuario"""
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        # Filtrar por empresas del usuario
        user_companies = request.session.get('user_companies', [])
        if user_companies and user_companies != 'all':
            # Buscar el campo de empresa en el modelo
            if hasattr(self.model, 'company'):
                return qs.filter(company_id__in=user_companies)
            elif hasattr(self.model, 'account') and hasattr(self.model.account.field.related_model, 'company'):
                return qs.filter(account__company_id__in=user_companies)
            elif hasattr(self.model, 'journal_entry') and hasattr(self.model.journal_entry.field.related_model, 'company'):
                return qs.filter(journal_entry__company_id__in=user_companies)
        return qs.none()
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Filtrar campo empresa
        if db_field.name == "company":
            if not request.user.is_superuser:
                user_companies = request.session.get('user_companies', [])
                if user_companies and user_companies != 'all':
                    kwargs["queryset"] = db_field.related_model.objects.filter(
                        id__in=user_companies
                    )
        # Filtrar campo Cuenta Padre (parent) solo por empresa asignada
        if db_field.name == "parent":
            if not request.user.is_superuser:
                user_companies = request.session.get('user_companies', [])
                if user_companies and user_companies != 'all':
                    kwargs["queryset"] = db_field.related_model.objects.filter(
                        company_id__in=user_companies
                    )
        # Filtrar campo CUENTA por empresa seleccionada
        if db_field.name == "account":
            company_id = request.GET.get("company")
            if company_id:
                from .models import ChartOfAccounts
                kwargs["queryset"] = ChartOfAccounts.objects.filter(
                    company_id=company_id,
                    is_active=True
                )
            elif not request.user.is_superuser:
                user_companies = request.session.get('user_companies', [])
                if user_companies and user_companies != 'all':
                    from .models import ChartOfAccounts
                    kwargs["queryset"] = ChartOfAccounts.objects.filter(
                        company_id__in=user_companies,
                        is_active=True
                    )
        # Filtrar campo Creado Por solo por usuarios asignados a la empresa seleccionada
        if db_field.name == "created_by":
            company_id = request.GET.get("company")
            if company_id:
                from apps.companies.models import CompanyUser
                user_ids = CompanyUser.objects.filter(company_id=company_id).values_list("user_id", flat=True)
                kwargs["queryset"] = db_field.related_model.objects.filter(id__in=user_ids)
            elif not request.user.is_superuser:
                kwargs["queryset"] = db_field.related_model.objects.filter(id=request.user.id)
        # Filtrar campo Contabilizado Por solo por usuarios asignados a la empresa seleccionada
        if db_field.name == "posted_by":
            company_id = request.GET.get("company")
            if company_id:
                from apps.companies.models import CompanyUser
                user_ids = CompanyUser.objects.filter(company_id=company_id).values_list("user_id", flat=True)
                kwargs["queryset"] = db_field.related_model.objects.filter(id__in=user_ids)
            elif not request.user.is_superuser:
                kwargs["queryset"] = db_field.related_model.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(ChartOfAccounts)
class ChartOfAccountsAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ['hierarchy_display_admin', 'account_type', 'company', 'level', 'is_detail', 'accepts_movement', 'children_count_display']
    list_filter = ['account_type', UserCompanyListFilter, 'level', 'is_detail', 'accepts_movement', 'tax_related']
    search_fields = ['code', 'name', 'sri_code']
    list_select_related = ['account_type', 'company', 'parent']
    readonly_fields = ['level']
    
    def hierarchy_display_admin(self, obj):
        """Muestra la jerarquía con indentación en el admin"""
        return obj.hierarchy_display
    hierarchy_display_admin.short_description = 'Cuenta (Jerarquía)'
    hierarchy_display_admin.admin_order_field = 'code'
    
    def children_count_display(self, obj):
        """Muestra el número de cuentas hijas"""
        count = obj.children_count
        if count > 0:
            return f"{count} subcuentas"
        return "Sin subcuentas"
    children_count_display.short_description = 'Subcuentas'
    
    def get_readonly_fields(self, request, obj=None):
        """Campos de solo lectura dinámicos"""
        readonly = ['level']
        if obj and obj.children_count > 0:
            # Si tiene hijos, no puede ser cuenta de detalle
            readonly.extend(['is_detail'])
        return readonly
    
    def get_search_results(self, request, queryset, search_term):
        """
        Búsqueda mejorada para autocompletado:
        - Búsqueda por código (parcial)
        - Búsqueda por nombre (parcial) 
        - Insensible a mayúsculas
        - Ordenado por código
        """
        from django.db.models import Q
        
        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term
        )
        
        if search_term:
            # Búsqueda mejorada: código O nombre, insensible a mayúsculas
            queryset = queryset.filter(
                Q(code__icontains=search_term) | 
                Q(name__icontains=search_term)
            ).distinct().order_by('code')
            
        return queryset, may_have_duplicates
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('company', 'code', 'name', 'account_type', 'parent')
        }),
        ('Jerarquía (Automática)', {
            'fields': ('level',),
            'description': 'El nivel se calcula automáticamente basado en la cuenta padre.'
        }),
        ('Configuración de Cuenta', {
            'fields': ('is_detail', 'accepts_movement')
        }),
        ('Auxiliares', {
            'fields': ('requires_auxiliary', 'aux_type')
        }),
        ('Configuración Fiscal', {
            'fields': ('sri_code', 'tax_related')
        }),
    )


class JournalEntryLineInline(admin.TabularInline):
    model = JournalEntryLine
    fields = ['account', 'description', 'debit', 'credit', 'auxiliary_code']
    autocomplete_fields = ['account']
    
    class Media:
        css = {
            'all': ('admin/css/journal_entry_lines.css',)
        }
        js = ('admin/js/journal_entry_lines.js',)
    
    def get_formset(self, request, obj=None, **kwargs):
        """
        Personalizar formset para optimizar widgets:
        - Campo description: Input de una sola línea en lugar de textarea
        """
        formset = super().get_formset(request, obj, **kwargs)
        
        # Personalizar widget del campo description
        if 'description' in formset.form.base_fields:
            formset.form.base_fields['description'].widget = forms.TextInput(attrs={
                'style': 'width: 600px; height: 28px;',
                'placeholder': 'Descripción de la línea del asiento...',
                'class': 'vTextField description-single-line'
            })
        
        return formset
    
    def get_extra(self, request, obj=None, **kwargs):
        """
        Líneas automáticas dinámicas según contexto:
        - Creación: 2 líneas automáticas (útil para empezar)
        - Edición: 0 líneas automáticas (interfaz limpia)
        """
        if obj is None:
            # Contexto de creación: útil tener líneas para empezar
            return 2
        else:
            # Contexto de edición: solo mostrar líneas reales
            return 0
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "account":
            # Obtener la empresa del objeto padre (JournalEntry)
            obj_id = request.resolver_match.kwargs.get('object_id')
            if obj_id:
                try:
                    from .models import JournalEntry
                    journal_entry = JournalEntry.objects.get(pk=obj_id)
                    kwargs["queryset"] = ChartOfAccounts.objects.filter(
                        company=journal_entry.company,
                        is_active=True
                    )
                except JournalEntry.DoesNotExist:
                    pass
            else:
                # Para nuevos asientos, usar empresas del usuario
                if not request.user.is_superuser:
                    user_companies = request.session.get('user_companies', [])
                    if user_companies and user_companies != 'all':
                        kwargs["queryset"] = ChartOfAccounts.objects.filter(
                            company_id__in=user_companies,
                            is_active=True
                        )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(JournalEntry)
class JournalEntryAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ['number', 'date', 'company', 'description', 'source_invoice_display', 'total_debit', 'total_credit', 'is_balanced_display', 'get_state_display']
    list_filter = ['state', UserCompanyListFilter, 'date']
    search_fields = ['number', 'description', 'reference']
    list_select_related = ['company', 'created_by', 'source_purchase_invoice']
    inlines = [JournalEntryLineInline]
    actions = ['mark_as_posted', 'mark_as_cancelled', 'mark_as_draft']
    
    def get_fields(self, request, obj=None):
        """Personalizar campos mostrados según si es creación o edición"""
        fields = super().get_fields(request, obj)
        
        # Ocultar número de asiento solo al crear (obj=None)
        if obj is None:
            # Convertir a lista si es tuple
            if isinstance(fields, tuple):
                fields = list(fields)
            
            # Remover el campo 'number' de los campos mostrados
            if 'number' in fields:
                fields = [field for field in fields if field != 'number']
        
        return fields
    
    def get_form(self, request, obj=None, **kwargs):
        """Personalizar formulario con valores por defecto"""
        form = super().get_form(request, obj, **kwargs)
        
        # Solo aplicar valores por defecto para nuevos asientos (obj=None)
        if not obj:
            # Establecer empresa por defecto basada en el usuario
            if not request.user.is_superuser:
                user_companies = CompanyUser.objects.filter(user=request.user)
                if user_companies.exists():
                    # Si el usuario tiene una sola empresa, asignarla por defecto
                    if user_companies.count() == 1:
                        form.base_fields['company'].initial = user_companies.first().company
                    # Si tiene múltiples empresas, usar la primera como sugerencia
                    else:
                        form.base_fields['company'].initial = user_companies.first().company
            
            # Establecer fecha actual por defecto
            form.base_fields['date'].initial = date.today()
            
            # Establecer usuario creador por defecto
            form.base_fields['created_by'].initial = request.user
            
        return form
    
    def get_readonly_fields(self, request, obj=None):
        readonly = ['total_debit', 'total_credit']
        if obj and obj.state == 'posted':
            readonly.extend(['number', 'date', 'company', 'state'])
        return readonly
    
    def is_balanced_display(self, obj):
        """Mostrar si el asiento está balanceado"""
        if obj.is_balanced:
            return "✅ Balanceado"
        else:
            diff = abs(obj.total_debit - obj.total_credit)
            return f"❌ Desbalanceado ({diff:.2f})"
    is_balanced_display.short_description = 'Balance'
    
    def source_invoice_display(self, obj):
        """Mostrar factura de origen si existe"""
        if obj.source_purchase_invoice:
            return f"📄 {obj.source_purchase_invoice.internal_number}"
        return "Manual"
    source_invoice_display.short_description = 'Origen'
    
    def get_state_display(self, obj):
        """Mostrar estado con colores para asientos contables"""
        state_colors = {
            'draft': '#6c757d',        # Gris - borrador (en proceso)
            'posted': '#28a745',       # Verde - contabilizado (éxito/finalizado)
            'cancelled': '#dc3545',    # Rojo - anulado (error/cancelado)
        }
        color = state_colors.get(obj.state, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_state_display()
        )
    get_state_display.short_description = 'Estado'
    
    class Media:
        js = ('admin/js/journal_entry_filters.js',)
    
    def get_fieldsets(self, request, obj=None):
        """Personalizar fieldsets según si es creación o edición"""
        
        if obj is None:
            # Fieldsets para CREACIÓN (sin campo número ni sección totales)
            return (
                ('Información Básica', {
                    'fields': ('company', 'date', 'reference', 'description'),
                    'description': 'La empresa y fecha se establecen automáticamente. El número de asiento se generará automáticamente al guardar.'
                }),
                ('Estado y Control', {
                    'fields': ('state', 'created_by', 'posted_by', 'posted_at'),
                    'description': 'Los totales se calcularán automáticamente y se mostrarán al guardar el asiento.'
                }),
            )
        else:
            # Fieldsets para EDICIÓN (con campo número y sección totales)
            return (
                ('Información Básica', {
                    'fields': ('company', 'number', 'date', 'reference', 'description'),
                    'description': 'La empresa y fecha se establecieron automáticamente al crear el asiento.'
                }),
                ('Estado y Control', {
                    'fields': ('state', 'created_by', 'posted_by', 'posted_at')
                }),
                ('Totales', {
                    'fields': ('total_debit', 'total_credit'),
                    'description': 'Los totales se calculan automáticamente basados en las líneas del asiento.'
                }),
            )
    
    def mark_as_posted(self, request, queryset):
        """Marcar asientos seleccionados como contabilizados"""
        from django.db import transaction
        
        success_count = 0
        error_count = 0
        errors = []
        inventory_lines_updated = 0
        
        for journal_entry in queryset:
            try:
                # Validar que el asiento esté balanceado
                if not journal_entry.is_balanced:
                    raise ValueError(f"Asiento {journal_entry.number} no está balanceado")
                
                # Validar que esté en estado borrador
                if journal_entry.state != 'draft':
                    raise ValueError(f"Asiento {journal_entry.number} no está en estado borrador")
                
                with transaction.atomic():
                    # Cambiar estado y registrar información de contabilización
                    journal_entry.state = 'posted'
                    journal_entry.posted_by = request.user
                    journal_entry.posted_at = timezone.now()
                    journal_entry.save()
                    
                    # NUEVO: Actualizar inventario si es asiento de factura de compra
                    # Usar relación directa (método robusto)
                    if journal_entry.source_purchase_invoice:
                        try:
                            invoice = journal_entry.source_purchase_invoice
                            
                            # Verificar que la factura esté validada
                            if invoice.status == 'validated':
                                # Actualizar inventario de líneas con productos de inventario
                                for line in invoice.lines.filter(
                                    product__manages_inventory=True, 
                                    product__product_type='product'
                                ):
                                    line.save()  # Activará update_inventory() 
                                    inventory_lines_updated += 1
                                    
                        except Exception as inventory_error:
                            # Log error pero continuar - el asiento se contabiliza igual
                            print(f"Error actualizando inventario para asiento {journal_entry.number}: {inventory_error}")
                            errors.append(f"Error inventario en {journal_entry.number}: {inventory_error}")
                    
                    # NUEVO: Crear movimientos bancarios para líneas que afecten cuentas bancarias
                    bank_transactions_created = self._create_bank_transactions_from_journal_entry(
                        journal_entry, request
                    )
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"{journal_entry.number}: {str(e)}")
        
        # Mensajes de resultado mejorados
        if success_count > 0:
            message_parts = [f"{success_count} asiento(s) contabilizado(s) exitosamente"]
            if inventory_lines_updated > 0:
                message_parts.append(f"{inventory_lines_updated} líneas de inventario actualizadas")
            
            self.message_user(request, "✅ " + ". ".join(message_parts) + ".", messages.SUCCESS)
        
        if error_count > 0:
            error_msg = f"❌ {error_count} asiento(s) no pudieron ser contabilizados:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                error_msg += f"\n... y {len(errors) - 5} errores más."
            self.message_user(request, error_msg, messages.ERROR)
    
    mark_as_posted.short_description = "🟢 Contabilizar asientos (incluye actualización de inventario)"
    
    def mark_as_cancelled(self, request, queryset):
        """Marcar asientos seleccionados como anulados"""
        success_count = 0
        error_count = 0
        errors = []
        
        for journal_entry in queryset:
            try:
                # Validar que no esté ya anulado
                if journal_entry.state == 'cancelled':
                    raise ValueError(f"Asiento {journal_entry.number} ya está anulado")
                
                # Cambiar estado
                journal_entry.state = 'cancelled'
                journal_entry.save()
                
                # NUEVO: Anular movimientos bancarios relacionados
                cancelled_transactions = self._cancel_bank_transactions_from_journal_entry(
                    journal_entry, request
                )
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"{journal_entry.number}: {str(e)}")
        
        # Mensajes de resultado
        if success_count > 0:
            self.message_user(request, f"✅ {success_count} asiento(s) anulado(s) exitosamente.", messages.SUCCESS)
        
        if error_count > 0:
            error_msg = f"❌ {error_count} asiento(s) no pudieron ser anulados:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                error_msg += f"\n... y {len(errors) - 5} errores más."
            self.message_user(request, error_msg, messages.ERROR)
    
    mark_as_cancelled.short_description = "🔴 Anular asientos seleccionados"
    
    def mark_as_draft(self, request, queryset):
        """Marcar asientos seleccionados como borradores"""
        success_count = 0
        error_count = 0
        errors = []
        
        for journal_entry in queryset:
            try:
                # Validar que no esté ya en borrador
                if journal_entry.state == 'draft':
                    raise ValueError(f"Asiento {journal_entry.number} ya está en borrador")
                
                # Cambiar estado y limpiar campos de contabilización
                journal_entry.state = 'draft'
                journal_entry.posted_by = None
                journal_entry.posted_at = None
                journal_entry.save()
                
                # NUEVO: Eliminar movimientos bancarios relacionados
                deleted_transactions = self._delete_bank_transactions_from_journal_entry(
                    journal_entry, request
                )
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"{journal_entry.number}: {str(e)}")
        
        # Mensajes de resultado
        if success_count > 0:
            self.message_user(request, f"✅ {success_count} asiento(s) regresado(s) a borrador exitosamente.", messages.SUCCESS)
        
        if error_count > 0:
            error_msg = f"❌ {error_count} asiento(s) no pudieron ser regresados a borrador:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                error_msg += f"\n... y {len(errors) - 5} errores más."
            self.message_user(request, error_msg, messages.ERROR)
    
    mark_as_draft.short_description = "🟡 Regresar asientos a borrador"
    
    def get_urls(self):
        """Agregar URLs personalizadas"""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/print-pdf/',
                self.admin_site.admin_view(self.print_journal_entry_pdf),
                name='accounting_journalentry_print_pdf'
            ),
        ]
        return custom_urls + urls
    
    def print_journal_entry_pdf(self, request, object_id):
        """Generar PDF del asiento contable"""
        from .journal_pdf import generate_journal_entry_pdf
        
        journal_entry = get_object_or_404(JournalEntry, pk=object_id)
        
        # Verificar permisos de empresa si no es superuser
        if not request.user.is_superuser:
            user_companies = CompanyUser.objects.filter(
                user=request.user, is_active=True
            ).values_list('company', flat=True)
            
            if journal_entry.company_id not in user_companies:
                from django.core.exceptions import PermissionDenied
                raise PermissionDenied("No tiene permisos para ver este asiento")
        
        # Generar PDF
        pdf_buffer = generate_journal_entry_pdf(journal_entry)
        
        # Preparar respuesta
        filename = f"Asiento_{journal_entry.number}_{journal_entry.company.trade_name}.pdf"
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    def save_model(self, request, obj, form, change):
        """Personalizar guardado con configuración automática"""
        # Si es un nuevo asiento, configurar valores por defecto
        if not change:  # change=False significa que es un nuevo objeto
            # Si no se especificó usuario creador, usar el usuario actual
            if not obj.created_by:
                obj.created_by = request.user
            
            # Si no se especificó fecha, usar fecha actual
            if not obj.date:
                obj.date = date.today()
            
            # Si no se especificó empresa y el usuario no es superuser
            if not obj.company and not request.user.is_superuser:
                user_companies = CompanyUser.objects.filter(user=request.user)
                if user_companies.exists():
                    obj.company = user_companies.first().company
        
        super().save_model(request, obj, form, change)
    
    def _create_bank_transactions_from_journal_entry(self, journal_entry, request):
        """
        Crear movimientos bancarios para líneas que afecten cuentas bancarias
        Solo se ejecuta cuando el asiento se contabiliza (posted)
        """
        try:
            # Importar servicio bancario (puede fallar si módulo no disponible)
            from apps.banking.services import BankingIntegrationService
            
            # Obtener líneas que afectan cuentas bancarias
            bank_lines = journal_entry.lines.filter(account__aux_type='bank')
            
            if not bank_lines.exists():
                # No hay líneas bancarias - normal
                return []
            
            transactions_created = []
            
            for bank_line in bank_lines:
                try:
                    bank_transaction = BankingIntegrationService.create_bank_transaction_from_journal_line(
                        journal_line=bank_line,
                        journal_entry=journal_entry
                    )
                    
                    if bank_transaction:
                        transactions_created.append(bank_transaction)
                        
                except Exception as line_error:
                    # Log error pero continuar con otras líneas
                    print(f"⚠️ Error creando BankTransaction para línea {bank_line.id}: {line_error}")
            
            # Mensaje informativo si se crearon transacciones
            if transactions_created:
                try:
                    from django.contrib import messages
                    messages.info(
                        request,
                        f"🏦 {len(transactions_created)} movimiento(s) bancario(s) creado(s) automáticamente para asiento {journal_entry.number}"
                    )
                except Exception:
                    # Contexto sin mensajes (ej. pruebas)
                    pass
            
            return transactions_created
            
        except ImportError:
            # Módulo Banking no disponible - continuar normalmente
            print(f"ℹ️ Módulo Banking no disponible para asiento {journal_entry.number}")
            return []
        except Exception as e:
            # Error no crítico - no interrumpir flujo principal
            print(f"⚠️ Error creando BankTransactions para asiento {journal_entry.number}: {e}")
            return []
    
    def _cancel_bank_transactions_from_journal_entry(self, journal_entry, request):
        """
        Anular movimientos bancarios relacionados cuando se anula el asiento
        
        Dado que el modelo BankTransaction actual no tiene campo is_cancelled,
        creamos una transacción de reversión en lugar de modificar la original
        """
        try:
            from apps.banking.models import BankTransaction
            
            # Buscar movimientos bancarios relacionados con este asiento
            related_transactions = BankTransaction.objects.filter(
                reference__startswith=f"AST-{journal_entry.number}",
                bank_account__company=journal_entry.company
            )
            
            if not related_transactions.exists():
                return []
            
            cancelled_transactions = []
            
            for transaction in related_transactions:
                # Verificar si ya existe una reversión
                reverse_reference = f"REV-{transaction.reference}"
                existing_reverse = BankTransaction.objects.filter(
                    reference=reverse_reference
                ).first()
                
                if not existing_reverse:
                    # Crear transacción de reversión
                    reverse_type = 'credit' if transaction.transaction_type == 'debit' else 'debit'
                    
                    reverse_transaction = BankTransaction.objects.create(
                        bank_account=transaction.bank_account,
                        transaction_date=transaction.transaction_date,
                        value_date=transaction.value_date,
                        transaction_type=reverse_type,
                        amount=transaction.amount,
                        description=f"REVERSIÓN - {transaction.description}",
                        reference=reverse_reference,
                        journal_entry=transaction.journal_entry,
                        is_reconciled=False
                    )
                    cancelled_transactions.append(reverse_transaction)
            
            # Mensaje informativo
            if cancelled_transactions:
                try:
                    from django.contrib import messages
                    messages.info(
                        request,
                        f"🏦 {len(cancelled_transactions)} reversión(es) bancaria(s) creada(s) por anulación del asiento {journal_entry.number}"
                    )
                except Exception:
                    # Contexto sin mensajes (ej. pruebas)
                    pass
            
            return cancelled_transactions
            
        except ImportError:
            # Módulo Banking no disponible
            return []
        except Exception as e:
            # Error no crítico
            print(f"⚠️ Error creando reversiones bancarias para asiento {journal_entry.number}: {e}")
            return []
    
    def _delete_bank_transactions_from_journal_entry(self, journal_entry, request):
        """
        Eliminar movimientos bancarios relacionados cuando se regresa asiento a borrador
        ELIMINA físicamente los registros (operación irreversible)
        """
        try:
            from apps.banking.models import BankTransaction
            
            # Buscar movimientos bancarios relacionados con este asiento
            # Usar startswith para capturar todas las líneas del asiento
            related_transactions = BankTransaction.objects.filter(
                reference__startswith=f"AST-{journal_entry.number}",
                bank_account__company=journal_entry.company
            )
            
            if not related_transactions.exists():
                return 0
            
            # Verificar que no estén conciliados
            reconciled_transactions = related_transactions.filter(is_reconciled=True)
            if reconciled_transactions.exists():
                try:
                    from django.contrib import messages
                    messages.warning(
                        request,
                        f"⚠️ No se eliminaron {reconciled_transactions.count()} movimiento(s) bancario(s) porque están conciliados"
                    )
                except Exception:
                    # Contexto sin mensajes (ej. pruebas)
                    pass
                # Solo eliminar los no conciliados
                related_transactions = related_transactions.filter(is_reconciled=False)
            
            transaction_count = related_transactions.count()
            
            # Eliminar físicamente
            if transaction_count > 0:
                # También eliminar reversiones si existen
                reverse_transactions = BankTransaction.objects.filter(
                    reference__startswith=f"REV-AST-{journal_entry.number}",
                    bank_account__company=journal_entry.company,
                    is_reconciled=False
                )
                reverse_count = reverse_transactions.count()
                if reverse_count > 0:
                    reverse_transactions.delete()
                    transaction_count += reverse_count
                
                # Eliminar transacciones originales
                related_transactions.delete()
                
                # Mensaje informativo
                try:
                    from django.contrib import messages
                    messages.info(
                        request,
                        f"🏦 {transaction_count} movimiento(s) bancario(s) eliminado(s) por regreso a borrador del asiento {journal_entry.number}"
                    )
                except Exception:
                    # Contexto sin mensajes (ej. pruebas)
                    pass
            
            return transaction_count
            
        except ImportError:
            # Módulo Banking no disponible
            return 0
        except Exception as e:
            # Error no crítico
            print(f"⚠️ Error eliminando BankTransactions para asiento {journal_entry.number}: {e}")
            return 0
    
    readonly_fields = ['total_debit', 'total_credit', 'posted_at']


@admin.register(JournalEntryLine)
class JournalEntryLineAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ['journal_entry', 'account', 'description', 'debit', 'credit']
    list_filter = [UserCompanyJournalFilter, 'account__account_type']
    search_fields = ['description', 'account__code', 'account__name', 'auxiliary_code']
    list_select_related = ['journal_entry', 'account']


@admin.register(FiscalYear)
class FiscalYearAdmin(admin.ModelAdmin):
    list_display = ['company', 'year', 'start_date', 'end_date', 'is_closed']
    list_filter = ['is_closed', UserCompanyListFilter, 'year']
    search_fields = ['year', 'company__trade_name']
    list_select_related = ['company']


@admin.register(AccountBalance)
class AccountBalanceAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ['account', 'company', 'fiscal_year', 'period', 'final_balance_debit', 'final_balance_credit', 'net_balance']
    list_filter = ['fiscal_year', 'period', 'account__account_type', UserCompanyAccountFilter]
    search_fields = ['account__code', 'account__name']
    list_select_related = ['account', 'fiscal_year']
    
    def company(self, obj):
        return obj.account.company
    company.short_description = 'Empresa'