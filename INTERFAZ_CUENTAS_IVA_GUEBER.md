# Interfaz para Configuración de Cuentas IVA - GUEBER

**Fecha de Análisis:** 3 de octubre de 2025  
**Empresa Objetivo:** GUEBER S.A.  
**Patrón Base:** PaymentMethod existente  

## 🎯 Objetivo

Crear una interfaz configurable para asignar cuentas contables específicas a cada tasa de IVA, eliminando el mapeo hardcodeado actual en `AutomaticJournalEntryService` y siguiendo el patrón de `PaymentMethod`.

## 📋 Estado Actual del Sistema

### Mapeo Hardcodeado Actual
```python
# apps/accounting/services.py - AutomaticJournalEntryService
IVA_ACCOUNTS_MAPPING = {
    15.0: '2.1.01.01.03.01',  # IVA Ventas 15%
    5.0: '2.1.01.01.03.02',   # IVA Ventas 5%
    0.0: None                 # Sin IVA
}
```

### Estructura GUEBER Identificada
- **Empresa:** GUEBER S.A. (ID: 2)
- **PaymentMethod Actual:** "Efectivo" 
- **Patrón Existente:** Campo `payment_method` en Company con ForeignKey a PaymentMethod
- **Ubicación Admin:** Sección "Configuración Contable" en CompanyAdmin

## 🏗️ Diseño de la Solución

### 1. Nuevo Modelo - CompanyTaxAccountMapping

```python
# apps/companies/models.py
class CompanyTaxAccountMapping(BaseModel):
    """Configuración de cuentas contables por tipo de IVA para cada empresa"""
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        verbose_name='Empresa'
    )
    tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        verbose_name='Tasa de IVA (%)'
    )
    account = models.ForeignKey(
        'accounting.ChartOfAccounts',
        on_delete=models.PROTECT,
        verbose_name='Cuenta Contable'
    )
    
    class Meta:
        verbose_name = 'Configuración de Cuenta IVA'
        verbose_name_plural = 'Configuraciones de Cuentas IVA'
        unique_together = ['company', 'tax_rate']
        ordering = ['tax_rate']
    
    def __str__(self):
        return f"{self.company.trade_name} - IVA {self.tax_rate}% → {self.account.code}"
```

### 2. Integración en CompanyAdmin

```python
# apps/companies/admin.py
class CompanyTaxAccountMappingInline(admin.TabularInline):
    """Inline para configurar cuentas IVA por empresa"""
    model = CompanyTaxAccountMapping
    extra = 1
    fields = ('tax_rate', 'account')
    verbose_name = 'Configuración Cuenta IVA'
    verbose_name_plural = 'Configuraciones Cuentas IVA'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('account')

@admin.register(Company)
class CompanyAdmin(CompanyFilterMixin, admin.ModelAdmin):
    # ... configuración existente ...
    
    inlines = [CompanyTaxAccountMappingInline]  # ← NUEVA LÍNEA
    
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
```

## 📍 Ubicación de la Interfaz

**Navegación:** `Admin → Empresas → GUEBER S.A. → Modificar empresa`

**Ubicación Visual:**
```
┌─ Configuración Contable ────────────────────────────┐
│ • Moneda base: USD - Dólar estadounidense           │
│ • Forma de Pago: Efectivo                          │
│ • Inicio del ejercicio fiscal: 1                   │
│                                                     │
│ ⬇️ CONFIGURACIÓN DE CUENTAS IVA ⬇️                │
│ ┌─────────────────────────────────────────────────┐ │
│ │ ➕ Agregar Configuración de Cuenta IVA          │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ 📊 Configuraciones actuales:                       │
│ ┌─────────────────────────────────────────────────┐ │
│ │ IVA 15.00% → 2.1.01.01.03.01 - IVA Ventas 15% │ │
│ │ IVA 5.00%  → 2.1.01.01.03.02 - IVA Ventas 5%  │ │
│ │ IVA 0.00%  → (Sin cuenta configurada)          │ │
│ │ [Editar] [Eliminar]   [Editar] [Eliminar]      │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## 🔄 Actualización del Servicio Contable

```python
# apps/accounting/services.py - Método actualizado
def _get_iva_account(self, tax_rate, company):
    """Obtener cuenta IVA desde configuración de empresa"""
    try:
        from apps.companies.models import CompanyTaxAccountMapping
        mapping = CompanyTaxAccountMapping.objects.get(
            company=company, 
            tax_rate=tax_rate
        )
        return mapping.account
    except CompanyTaxAccountMapping.DoesNotExist:
        # Fallback al mapeo hardcodeado actual
        return self.IVA_ACCOUNTS_MAPPING.get(float(tax_rate))
```

## 🎯 Configuración Específica para GUEBER

```
Empresa: GUEBER S.A.
┌─────────────────────────────────────────────────────────┐
│ CONFIGURACIÓN DE CUENTAS IVA                            │
├─────────────────────────────────────────────────────────┤
│ Tasa IVA (%) │ Cuenta Contable                         │
├─────────────────────────────────────────────────────────┤
│ 15.00        │ 2.1.01.01.03.01 - IVA en Ventas 15%   │
│ 5.00         │ 2.1.01.01.03.02 - IVA en Ventas 5%    │
│ 0.00         │ (No requiere cuenta)                    │
└─────────────────────────────────────────────────────────┘
```

## ✨ Ventajas de la Implementación

1. **📍 Ubicación Lógica:** En la sección "Configuración Contable" donde pertenece
2. **🎨 Interfaz Familiar:** Sigue el patrón de PaymentMethod que ya existe
3. **🔧 Flexibilidad:** Cada empresa puede tener sus propias cuentas IVA
4. **🛡️ Seguridad:** Filtrado automático por empresa (CompanyFilterMixin)
5. **📊 Escalabilidad:** Fácil agregar nuevas tasas de IVA
6. **🔄 Compatibilidad:** Mantiene funcionamiento actual como fallback

## 📝 Archivos a Modificar

1. **apps/companies/models.py** - Agregar modelo CompanyTaxAccountMapping
2. **apps/companies/admin.py** - Agregar inline y actualizar CompanyAdmin
3. **apps/accounting/services.py** - Actualizar método _get_iva_account()
4. **Nueva migración** - Crear tabla y relaciones

## 🚀 Pasos de Implementación

1. Crear modelo CompanyTaxAccountMapping
2. Generar y aplicar migración
3. Configurar CompanyTaxAccountMappingInline
4. Actualizar CompanyAdmin con inline
5. Modificar AutomaticJournalEntryService
6. Poblar datos iniciales para GUEBER
7. Verificar funcionamiento con test_factura_iva_mixto.py

## 💡 Notas Técnicas

- **Patrón Base:** PaymentMethod con ForeignKey a ChartOfAccounts
- **Seguridad:** CompanyFilterMixin asegura filtrado por empresa
- **Compatibilidad:** Sistema actual funciona como fallback
- **Escalabilidad:** Soporte para múltiples empresas y tasas IVA
- **UX:** Interface integrada en sección existente "Configuración Contable"

---

**Estado:** Análisis completo - Listo para implementación  
**Próximo Paso:** Crear modelo e inline siguiendo patrón PaymentMethod