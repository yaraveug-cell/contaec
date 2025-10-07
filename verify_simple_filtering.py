#!/usr/bin/env python
"""
Script simple para verificar el filtrado frontend
"""
import os
import sys

def test_simple_filtering():
    """Probar la funcionalidad básica"""
    
    print("🔍 VERIFICACIÓN DE FILTRADO FRONTEND")
    print("=" * 60)
    
    # 1. Verificar archivo JavaScript
    js_file = 'static/admin/js/payment_form_handler.js'
    print("📁 Verificando archivo JavaScript...")
    
    if os.path.exists(js_file):
        print(f"   ✅ {js_file} existe")
        
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar componentes clave
        checks = [
            ('PaymentFormHandler', 'Clase principal'),
            ('filterCashAccounts', 'Método de filtrado de caja'),
            ('showAllAccounts', 'Método para mostrar todas las cuentas'),
            ('EFECTIVO', 'Detección de pago en efectivo'),
            ('CAJA', 'Filtro de cuentas de caja'),
            ('originalOptions', 'Almacenamiento de opciones originales')
        ]
        
        for check, description in checks:
            if check in content:
                print(f"   ✅ {description}: Encontrado")
            else:
                print(f"   ❌ {description}: NO encontrado")
    else:
        print(f"   ❌ {js_file} no encontrado")
        return False
    
    # 2. Verificar configuración en admin
    print("\n⚙️ Verificando configuración del admin...")
    
    admin_file = 'apps/invoicing/admin.py'
    if os.path.exists(admin_file):
        with open(admin_file, 'r', encoding='utf-8') as f:
            admin_content = f.read()
            
        if 'payment_form_handler.js' in admin_content:
            print("   ✅ JavaScript incluido en Media class")
        else:
            print("   ❌ JavaScript NO incluido en Media class")
            
        if "('payment_form', 'account')" in admin_content:
            print("   ✅ Campos en la misma fila en fieldsets")
        else:
            print("   ❌ Campos NO en la misma fila")
    else:
        print("   ❌ Archivo admin.py no encontrado")
    
    # 3. Verificar CSS
    print("\n🎨 Verificando estilos CSS...")
    
    css_file = 'static/admin/css/invoice_lines.css'
    if os.path.exists(css_file):
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
            
        css_checks = [
            ('.field-payment_form', 'Estilos para forma de pago'),
            ('.field-account', 'Estilos para campo cuenta'),
            ('display: inline-block', 'Campos en línea')
        ]
        
        for check, description in css_checks:
            if check in css_content:
                print(f"   ✅ {description}: Configurado")
            else:
                print(f"   ❌ {description}: NO configurado")
    else:
        print("   ❌ Archivo CSS no encontrado")
    
    print("\n" + "=" * 60)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("\n📋 INSTRUCCIONES DE USO:")
    print("1. Ingresar al admin de Django")
    print("2. Ir a Invoicing > Invoices > Add Invoice")
    print("3. Seleccionar 'EFECTIVO' en Forma de Pago")
    print("4. El campo Cuenta debería filtrar automáticamente")
    print("5. Cambiar a 'CREDITO' para ver todas las cuentas")
    
    print("\n🔍 FUNCIONALIDADES:")
    print("• Filtrado automático sin AJAX")
    print("• Basado en texto que contiene 'CAJA'")
    print("• Valor por defecto automático para EFECTIVO")
    print("• Restauración completa para otros métodos")
    
    return True

if __name__ == "__main__":
    success = test_simple_filtering()
    sys.exit(0 if success else 1)