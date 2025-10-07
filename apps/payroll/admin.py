from django.contrib import admin
from .models import (
    EmployeeCategory, Employee, PayrollPeriod, 
    PayrollConcept, Payroll, PayrollDetail
)
from apps.core.filters import UserCompanyListFilter, UserCompanyPeriodFilter, UserCompanyConceptFilter


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
            elif hasattr(self.model, 'employee') and hasattr(self.model.employee.field.related_model, 'company'):
                return qs.filter(employee__company_id__in=user_companies)
            elif hasattr(self.model, 'payroll') and hasattr(self.model.payroll.field.related_model, 'employee'):
                return qs.filter(payroll__employee__company_id__in=user_companies)
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


class PayrollDetailInline(admin.TabularInline):
    model = PayrollDetail
    extra = 1
    fields = ('concept', 'quantity', 'unit_value', 'total_value', 'notes')
    readonly_fields = ('total_value',)


@admin.register(EmployeeCategory)
class EmployeeCategoryAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)


@admin.register(Employee)
class EmployeeAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ('employee_code', 'full_name', 'position', 'company', 'status', 'hire_date')
    list_filter = (UserCompanyListFilter, 'status', 'category', 'hire_date')
    search_fields = ('first_name', 'last_name', 'cedula', 'employee_code', 'email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('cedula', 'first_name', 'last_name', 'email', 'phone', 'address', 'birth_date', 'civil_status')
        }),
        ('Información Laboral', {
            'fields': ('company', 'employee_code', 'hire_date', 'position', 'department', 'category')
        }),
        ('Información Salarial', {
            'fields': ('base_salary',)
        }),
        ('Estado', {
            'fields': ('status', 'termination_date')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ('name', 'company', 'period_type', 'start_date', 'end_date', 'payment_date', 'is_closed')
    list_filter = (UserCompanyListFilter, 'period_type', 'is_closed', 'start_date')
    search_fields = ('name',)
    date_hierarchy = 'start_date'


@admin.register(PayrollConcept)
class PayrollConceptAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ('code', 'name', 'company', 'concept_type', 'calculation_type', 'is_active')
    list_filter = (UserCompanyListFilter, 'concept_type', 'calculation_type', 'is_active', 'affects_iess')
    search_fields = ('code', 'name')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('company', 'code', 'name', 'description', 'concept_type', 'calculation_type')
        }),
        ('Configuración de Cálculo', {
            'fields': ('percentage', 'fixed_amount'),
            'description': 'Configure según el tipo de cálculo seleccionado'
        }),
        ('Configuración Tributaria', {
            'fields': ('affects_iess', 'affects_income_tax', 'is_active')
        })
    )


@admin.register(Payroll)
class PayrollAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ('employee', 'period', 'total_income', 'total_deductions', 'net_salary', 'is_processed', 'is_paid')
    list_filter = (UserCompanyPeriodFilter, 'is_processed', 'is_paid', 'period')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__employee_code')
    readonly_fields = ('total_income', 'total_deductions', 'total_employer_contributions', 'net_salary', 'created_at', 'updated_at')
    inlines = [PayrollDetailInline]
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('period', 'employee')
        }),
        ('Totales Calculados', {
            'fields': ('total_income', 'total_deductions', 'total_employer_contributions', 'net_salary'),
            'classes': ('collapse',)
        }),
        ('Estado de Procesamiento', {
            'fields': ('is_processed', 'is_paid', 'payment_date', 'processed_by')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(PayrollDetail)
class PayrollDetailAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ('payroll', 'concept', 'quantity', 'unit_value', 'total_value')
    list_filter = (UserCompanyConceptFilter, 'concept__concept_type', 'payroll__period')
    search_fields = ('payroll__employee__first_name', 'payroll__employee__last_name', 'concept__name')
    readonly_fields = ('total_value',)