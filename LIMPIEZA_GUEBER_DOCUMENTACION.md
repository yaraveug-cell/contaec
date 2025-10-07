# 🧹 LIMPIEZA TRANSACCIONAL GUEBER - DOCUMENTACIÓN COMPLETA

## 📋 Resumen

Se ha implementado un sistema completo y seguro para eliminar las transacciones de la empresa GUEBER manteniendo toda la estructura base del sistema contable.

## 🎯 Objetivo

Permitir que GUEBER comience operaciones "en limpio" eliminando todas las transacciones de prueba/demostración mientras conserva:
- ✅ Plan de cuentas completo
- ✅ Maestros (clientes, proveedores, productos)  
- ✅ Usuarios y permisos
- ✅ Configuraciones de empresa
- ✅ Parámetros contables

## 🛠️ Implementación

### Comando Django Management
**Archivo**: `apps/core/management/commands/reset_gueber_transactions.py`

### Características Principales

1. **🔍 Análisis Inteligente**: Detecta automáticamente todos los tipos de transacciones
2. **🛡️ Múltiples Capas de Seguridad**: Confirmaciones, dry-run, backups
3. **📊 Reportes Detallados**: Muestra exactamente qué se eliminará
4. **🔄 Orden de Dependencias**: Elimina en secuencia correcta para evitar errores
5. **💾 Sistema de Backup**: Backup completo en JSON antes de eliminar

## 📊 Datos Identificados en GUEBER

```
Empresa: GUEBER (Yolanda Bermeo)
RUC: 1600279945001
ID: 2

Transacciones encontradas:
- 📄 Asientos Contables: 15 registros
- 📄 Líneas de Asiento: 73 registros  
- 📄 Facturas de Venta: 19 registros
- 📄 Líneas Factura Venta: 23 registros
- 📄 Facturas de Compra: 5 registros
- 📄 Líneas Factura Compra: 13 registros
- 📄 Transacciones Bancarias: 7 registros
- 📄 Extractos Bancarios: 1 registros

TOTAL: 156 registros transaccionales
```

## 🚀 Uso del Comando

### 1️⃣ SIMULACIÓN (Recomendado primero)
```bash
python manage.py reset_gueber_transactions --dry-run
```
- ✅ Muestra plan de eliminación sin hacer cambios
- ✅ Seguro para verificar funcionamiento
- ✅ No requiere confirmación

### 2️⃣ ELIMINACIÓN CON BACKUP (Recomendado)
```bash
python manage.py reset_gueber_transactions --backup --confirm
```
- ✅ Crea backup completo antes de eliminar
- ✅ Máxima seguridad
- ✅ Permite recuperación si es necesario

### 3️⃣ ELIMINACIÓN DIRECTA
```bash
python manage.py reset_gueber_transactions --confirm
```
- ⚠️ Sin backup (más rápido)
- ✅ Requiere confirmación explícita

### 4️⃣ EMPRESA ESPECÍFICA
```bash
python manage.py reset_gueber_transactions --company "OTRA_EMPRESA" --confirm
```
- ✅ Permite trabajar con otra empresa
- ✅ Por defecto usa "GUEBER"

## 🔒 Medidas de Seguridad

### Validaciones Implementadas
1. **Identificación de Empresa**: Verifica que existe la empresa objetivo
2. **Confirmación Explícita**: Requiere parámetro `--confirm` para proceder
3. **Análisis Previo**: Muestra exactamente qué se eliminará
4. **Orden de Dependencias**: Elimina relaciones dependientes primero
5. **Transacción Atómica**: Todo se ejecuta en una sola transacción DB
6. **Verificación Final**: Confirma que la eliminación fue completa

### Sistema de Backup
- **Ubicación**: `./backups/gueber_YYYYMMDD_HHMMSS/`
- **Formato**: JSON por modelo
- **Contenido**: Todos los registros que se van a eliminar
- **Recuperación**: Datos listos para re-importar si necesario

## 📈 Orden de Eliminación

El comando elimina en el siguiente orden para respetar dependencias:

1. 🗑️ **Extractos Bancarios**
2. 🗑️ **Transacciones Bancarias** 
3. 🗑️ **Líneas Factura Compra**
4. 🗑️ **Facturas de Compra**
5. 🗑️ **Líneas Factura Venta**
6. 🗑️ **Facturas de Venta**
7. 🗑️ **Líneas de Asiento**
8. 🗑️ **Asientos Contables**

## 🎯 Flujo Recomendado

```bash
# 1. Verificar qué se eliminará
python manage.py reset_gueber_transactions --dry-run

# 2. Si todo está correcto, proceder con backup
python manage.py reset_gueber_transactions --backup --confirm

# 3. Verificar resultado (debe mostrar 0 transacciones)
python manage.py reset_gueber_transactions --dry-run
```

## ✅ Estado Actual

- **✅ Comando Implementado**: Django management command funcional
- **✅ Empresa Identificada**: GUEBER (ID: 2) con 156 transacciones
- **✅ Análisis Completo**: Todos los modelos transaccionales mapeados
- **✅ Pruebas Realizadas**: Dry-run ejecutado exitosamente
- **✅ Documentación**: Completa con ejemplos de uso

## 🚨 Advertencias Importantes

1. **IRREVERSIBLE**: Una vez ejecutado (sin --dry-run), NO se puede deshacer
2. **BACKUP RECOMENDADO**: Siempre use --backup en producción
3. **VERIFICAR PRIMERO**: Ejecute --dry-run antes del comando real
4. **CONFIRMACIÓN REQUERIDA**: Debe usar --confirm para proceder

## 🎉 Resultado Esperado

Después de ejecutar el comando, GUEBER tendrá:
- ✅ **0 transacciones** (asientos, facturas, movimientos bancarios)
- ✅ **Plan de cuentas intacto**
- ✅ **Maestros conservados** (clientes, proveedores, productos)
- ✅ **Configuraciones preservadas**
- ✅ **Sistema listo** para operaciones nuevas

## 💡 Próximos Pasos Sugeridos

1. **Ejecutar dry-run** para confirmar datos
2. **Ejecutar con backup** para proceder seguro
3. **Verificar resultado** con nuevo dry-run
4. **Comenzar operaciones** con GUEBER limpio

---

**Fecha Implementación**: 2024-10-07  
**Comandos Disponibles**: 
- `reset_gueber_transactions` (principal)
- `help_gueber_cleanup.py` (ayuda)

**Archivos Creados**:
- `apps/core/management/commands/reset_gueber_transactions.py`
- `help_gueber_cleanup.py`