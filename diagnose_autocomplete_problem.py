#!/usr/bin/env python3
"""
Script para diagnosticar por qué el autocompletado no funciona
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def diagnose_autocomplete_problem():
    print("🔍 DIAGNÓSTICO DEL PROBLEMA DE AUTOCOMPLETADO")
    print("=" * 60)
    
    print("\n📋 1. VERIFICANDO LOGS DE CONSOLA:")
    print("-" * 50)
    print("❌ PROBLEMA DETECTADO: No aparecen logs de invoice_line_autocomplete.js")
    print("✅ Otros scripts SÍ funcionan: description_autocomplete.js, calculadoras")
    print("🔍 Esto indica que el script NO se está cargando o NO se está ejecutando")
    
    print("\n📁 2. VERIFICANDO ARCHIVOS JAVASCRIPT:")
    print("-" * 50)
    
    js_files_to_check = [
        'static/admin/js/invoice_line_autocomplete.js',
        'static/admin/js/invoice_admin.js'
    ]
    
    for js_file in js_files_to_check:
        if os.path.exists(js_file):
            print(f"✅ {js_file} - EXISTE")
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'console.log' in content:
                    print(f"   📝 Contiene console.log para debugging")
                else:
                    print(f"   ⚠️  Sin console.log")
        else:
            print(f"❌ {js_file} - NO EXISTE")
    
    print("\n🧪 3. POSIBLES CAUSAS DEL PROBLEMA:")
    print("-" * 50)
    print("1. ❌ Error de sintaxis en JavaScript (impide ejecución)")
    print("2. ❌ Conflicto entre scripts (uno bloquea al otro)")
    print("3. ❌ DOM no está listo cuando se ejecuta")
    print("4. ❌ Widget de autocompletado no se detecta correctamente")
    print("5. ❌ Event listeners no se configuran correctamente")
    
    print("\n🛠️ 4. CREANDO VERSIÓN DE DEBUG SIMPLIFICADA:")
    print("-" * 50)
    
    # Crear versión ultra-simplificada para debug
    debug_js = '''
/**
 * DEBUG: Versión ultra-simplificada de autocompletado
 */
(function() {
    'use strict';
    
    console.log('🚀 DEBUG: Script de autocompletado cargado');
    
    function debugLog(message) {
        console.log('[AUTOCOMPLETE DEBUG] ' + message);
    }
    
    // Función simple para probar
    function simpleTest() {
        debugLog('Función de prueba ejecutada');
        
        // Buscar widgets de autocompletado
        const widgets = document.querySelectorAll('input.admin-autocomplete');
        debugLog('Widgets encontrados: ' + widgets.length);
        
        widgets.forEach(function(widget, index) {
            debugLog('Widget ' + (index + 1) + ': ' + widget.name);
        });
        
        // Buscar campos de producto específicamente
        const productFields = document.querySelectorAll('input[name*="product"]');
        debugLog('Campos de producto: ' + productFields.length);
        
        productFields.forEach(function(field, index) {
            debugLog('Campo producto ' + (index + 1) + ': ' + field.name + ' (type: ' + field.type + ')');
        });
    }
    
    // Ejecutar al cargar DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            debugLog('DOM cargado - ejecutando pruebas');
            simpleTest();
        });
    } else {
        debugLog('DOM ya listo - ejecutando pruebas inmediatamente');
        simpleTest();
    }
    
    // También ejecutar después de un delay
    setTimeout(function() {
        debugLog('Ejecutando pruebas después de delay');
        simpleTest();
    }, 2000);
    
})();
'''
    
    # Guardar versión debug
    debug_file = 'static/admin/js/invoice_line_autocomplete_debug.js'
    with open(debug_file, 'w', encoding='utf-8') as f:
        f.write(debug_js)
    
    print(f"✅ Creado: {debug_file}")
    
    print("\n📋 5. PLAN DE CORRECCIÓN:")
    print("-" * 50)
    print("1. 🔄 Reemplazar script actual con versión debug")
    print("2. 🔍 Verificar logs en consola del navegador")
    print("3. 🔧 Identificar causa específica del problema")
    print("4. ✅ Aplicar corrección dirigida")
    
    return debug_file

if __name__ == "__main__":
    debug_file = diagnose_autocomplete_problem()
    
    print(f"\n🔧 PRÓXIMOS PASOS:")
    print(f"1. Reemplazar invoice_line_autocomplete.js con versión debug")
    print(f"2. Refrescar página del admin")
    print(f"3. Abrir consola (F12) y verificar logs de DEBUG")
    print(f"4. Reportar qué mensajes aparecen")