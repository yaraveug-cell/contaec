#!/usr/bin/env python3
"""
Script de ayuda para el comando de limpieza de GUEBER

Uso recomendado del comando reset_gueber_transactions
"""

print("""
🧹 COMANDO DE LIMPIEZA TRANSACCIONAL - GUEBER
=============================================

📖 OPCIONES DISPONIBLES:

1️⃣  SIMULACIÓN (Recomendado primero):
    python manage.py reset_gueber_transactions --dry-run
    
    ✅ Muestra qué se eliminará sin hacer cambios reales
    ✅ Seguro para verificar el plan de eliminación
    ✅ No requiere confirmación

2️⃣  CON BACKUP Y CONFIRMACIÓN:
    python manage.py reset_gueber_transactions --backup --confirm
    
    ✅ Crea backup completo antes de eliminar
    ✅ Elimina transacciones reales
    ✅ Requiere --confirm para seguridad

3️⃣  SOLO ELIMINACIÓN (Sin backup):
    python manage.py reset_gueber_transactions --confirm
    
    ⚠️  Elimina transacciones sin crear backup
    ✅ Más rápido pero menos seguro
    ✅ Requiere --confirm para seguridad

4️⃣  EMPRESA ESPECÍFICA:
    python manage.py reset_gueber_transactions --company "OTRA_EMPRESA" --confirm
    
    ✅ Permite especificar otra empresa
    ✅ Por defecto busca "GUEBER"

📊 LO QUE SE ELIMINA:
- ✅ Asientos contables y sus líneas
- ✅ Facturas de venta y sus líneas  
- ✅ Facturas de compra y sus líneas
- ✅ Transacciones bancarias
- ✅ Extractos bancarios
- ✅ Movimientos de inventario (si existen)

🔒 LO QUE SE MANTIENE:
- ✅ Usuarios y permisos
- ✅ Plan de cuentas completo
- ✅ Maestros (clientes, proveedores, productos)
- ✅ Configuraciones de empresa
- ✅ Parámetros contables

⚠️  IMPORTANTE:
- La eliminación NO se puede deshacer
- Use --dry-run primero para verificar
- Use --backup para mayor seguridad
- Requiere --confirm para proceder

🎯 FLUJO RECOMENDADO:
1. python manage.py reset_gueber_transactions --dry-run
2. python manage.py reset_gueber_transactions --backup --confirm

📁 BACKUP LOCATION:
Los backups se guardan en: ./backups/gueber_YYYYMMDD_HHMMSS/
""")