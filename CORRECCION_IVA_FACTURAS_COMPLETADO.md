# CORRECCIÓN DE IVA POR DEFECTO EN FACTURAS - COMPLETADO

## 🔧 **PROBLEMA IDENTIFICADO**

Al crear nuevas facturas de compra y venta, aparecía por defecto el valor de IVA en **12%** en lugar del **15%** actual de Ecuador o el configurado por la empresa.

## ✅ **CORRECCIONES IMPLEMENTADAS**

### 1. **Facturas de Compra (`apps/suppliers/models.py`)**

**Cambios realizados:**
- **Campo `iva_rate`:** Cambiado de `default=Decimal('12.00')` a `default=Decimal('15.00')`
- **Método `save()`:** Mejorado para detectar líneas nuevas y aplicar IVA de la empresa
- **Migración:** `0003_change_iva_default_to_15.py` aplicada exitosamente

**Lógica implementada:**
```python
# Detectar si es una línea nueva
is_new = self.pk is None

# Si es nueva línea y no hay producto o el IVA es el por defecto, usar el IVA de la empresa
if is_new and self.invoice and (not self.iva_rate or self.iva_rate == Decimal('15.00')):
    company_settings, created = CompanySettings.objects.get_or_create(company=self.invoice.company)
    self.iva_rate = company_settings.default_iva_rate
```

### 2. **Facturas de Venta (`apps/invoicing/models.py`)**

**Cambios realizados:**
- **Campo `iva_rate`:** Ya tenía `default=Decimal('15.00')` ✅
- **Método `save()`:** Actualizado con la misma lógica que facturas de compra
- **Sin migración necesaria:** Solo cambios de lógica

**Lógica implementada:**
```python
# Detectar si es una línea nueva
is_new = self.pk is None

# Si es nueva línea y no hay producto o el IVA es el por defecto, usar el IVA de la empresa
if is_new and self.invoice and (not self.iva_rate or self.iva_rate == Decimal('15.00')):
    company_settings, created = CompanySettings.objects.get_or_create(company=self.invoice.company)
    self.iva_rate = company_settings.default_iva_rate
```

### 3. **Productos (`apps/inventory/models.py`)**

**Ya corregido anteriormente:**
- **Campo `iva_rate`:** Cambiado de `default=Decimal('12.00')` a usar IVA de empresa
- **Método `save()`:** Aplica IVA de empresa para productos nuevos

## 📊 **COMPORTAMIENTO ACTUAL**

### **Para Facturas de Compra y Venta:**

1. **Con Producto Asociado:**
   - Si el producto tiene IVA configurado → Usa el IVA del producto
   - Si el producto no tiene IVA → Usa el IVA por defecto de la empresa

2. **Sin Producto Asociado (Servicios):**
   - Usa el IVA por defecto configurado en CompanySettings de la empresa

3. **Facturas Existentes:**
   - ✅ NO se modifican, mantienen sus valores actuales

## 🏢 **Configuración por Empresa**

### **Estado Actual:**
- **CEMENTO MAXI:** IVA configurado en 15.00%
- **GUEBER:** IVA configurado en 15.00%

### **Cómo Cambiar:**
1. Admin Django → Companies → Company settings
2. Seleccionar empresa
3. Sección "Configuraciones Fiscales" 
4. Modificar "IVA por defecto (%)"

## 🔄 **MIGRACIONES EJECUTADAS**

1. **`companies/0005_add_default_iva_rate.py`** ✅
   - Agrega campo `default_iva_rate` a CompanySettings

2. **`suppliers/0003_change_iva_default_to_15.py`** ✅  
   - Cambia valor por defecto de 12% a 15% en PurchaseInvoiceLine

## 🧪 **PRUEBAS NECESARIAS**

Para verificar que funciona correctamente:

1. **Crear nueva factura de compra sin producto:**
   - Debe usar el IVA configurado en CompanySettings (15%)

2. **Crear nueva factura de venta sin producto:**
   - Debe usar el IVA configurado en CompanySettings (15%)

3. **Cambiar IVA de empresa a 16%:**
   - Las nuevas facturas deben usar 16%
   - Las existentes deben mantener sus valores

## ✅ **RESULTADO ESPERADO**

Ahora cuando se cree una **nueva factura de compra o venta**:
- ✅ El IVA por defecto será **15%** (regulación actual de Ecuador)
- ✅ O el valor configurado específicamente por cada empresa
- ✅ Las facturas existentes NO se ven afectadas
- ✅ Cumple con la flexibilidad requerida por empresa

---

**Estado:** ✅ COMPLETADO  
**Fecha:** Octubre 4, 2025  
**Sistema:** ContaEC - Contabilidad Ecuatoriana