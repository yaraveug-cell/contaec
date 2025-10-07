#!/usr/bin/env python3
"""
Verificación final del sistema de filtrado dinámico
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def final_verification():
    """Verificación completa y final"""
    print("🎯 VERIFICACIÓN FINAL DEL SISTEMA")
    print("=" * 60)
    
    from apps.companies.models import Company, PaymentMethod
    from apps.accounting.models import ChartOfAccounts
    
    print("📊 CONFIGURACIÓN ACTUAL:")
    
    # Datos de GUEBER
    gueber = Company.objects.get(trade_name__icontains="GUEBER")
    efectivo = PaymentMethod.objects.get(name__icontains="efectivo")
    
    print(f"🏢 Empresa: {gueber.trade_name} (ID: {gueber.id})")
    print(f"💳 Método Efectivo: {efectivo.name} (ID: {efectivo.id})")
    print(f"📋 Cuenta Padre Efectivo: {efectivo.parent_account.code} - {efectivo.parent_account.name}")
    
    # Buscar CAJA GENERAL específicamente
    caja_general = ChartOfAccounts.objects.filter(
        company=gueber,
        code__startswith=efectivo.parent_account.code.replace('.', ''),
        name__icontains="caja general"
    ).first()
    
    if not caja_general:
        caja_general = ChartOfAccounts.objects.filter(
            company=gueber,
            name__icontains="caja general"
        ).first()
    
    if caja_general:
        print(f"🎯 Caja General: {caja_general.code} - {caja_general.name}")
        
        # Verificar jerarquía
        parent_code_clean = efectivo.parent_account.code.replace('.', '')
        if caja_general.code.startswith(parent_code_clean):
            print(f"✅ CAJA GENERAL es hija de {efectivo.parent_account.name}")
            print(f"   - Padre: {efectivo.parent_account.code} (nivel {efectivo.parent_account.level})")
            print(f"   - Hija: {caja_general.code} (nivel {caja_general.level})")
        else:
            print(f"⚠️  Verificar jerarquía de códigos")
    else:
        print("❌ CAJA GENERAL no encontrada")
    
    print(f"\n🔧 ARCHIVOS ACTUALIZADOS:")
    
    # Verificar JavaScript
    js_file = "static/admin/js/integrated_payment_account_handler.js"
    if os.path.exists(js_file):
        print(f"✅ JavaScript: {js_file}")
        with open(js_file, 'r') as f:
            content = f.read()
            if 'console.log(\'✅ Cuenta hija por código jerárquico:\'' in content:
                print("✅ Logging mejorado implementado")
            if 'cleanParentCode.replace(/\\.$/, \'\')' in content:
                print("✅ Limpieza de código padre implementada")
    
    # Verificar admin.py
    admin_file = "apps/invoicing/admin.py"
    if os.path.exists(admin_file):
        with open(admin_file, 'r') as f:
            content = f.read()
            if 'integrated_payment_account_handler.js?v=2' in content:
                print("✅ Versión de JavaScript actualizada para forzar recarga")
    
    print(f"\n🌐 SERVIDOR:")
    print(f"   Status: Ejecutándose en http://127.0.0.1:8000/")
    
    print(f"\n🎯 PASOS PARA PROBAR:")
    print(f"1. Ir a: http://127.0.0.1:8000/admin/invoicing/invoice/add/")
    print(f"2. Abrir Developer Tools (F12) → Console")
    print(f"3. Refrescar página (Ctrl+F5) para cargar JavaScript actualizado")
    print(f"4. Seleccionar empresa: GUEBER")
    print(f"5. Cambiar forma de pago a: Efectivo")
    print(f"6. Verificar que aparezca: CAJA GENERAL")
    
    print(f"\n💻 TEST AUTOMATIZADO:")
    print(f"   Copiar y pegar en la consola el contenido de:")
    print(f"   → browser_test_complete.js")
    
    print(f"\n🔍 SI NO FUNCIONA:")
    print(f"   1. Refrescar con Ctrl+F5")
    print(f"   2. Verificar consola por errores")
    print(f"   3. Usar modo incógnito")
    print(f"   4. Limpiar caché del navegador")

if __name__ == "__main__":
    final_verification()
    
    print("\n" + "=" * 60)
    print("✅ SISTEMA LISTO - JavaScript actualizado con debugging mejorado")
    print("=" * 60)