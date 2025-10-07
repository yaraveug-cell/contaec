
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
