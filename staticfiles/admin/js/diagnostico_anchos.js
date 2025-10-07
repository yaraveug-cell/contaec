/**
 * HERRAMIENTA DE DIAGNÓSTICO - Inspeccionar estructura HTML y CSS
 * Ejecutar en consola del navegador para diagnosticar el problema
 */
(function() {
    'use strict';
    
    function diagnosticarEstructuraHTML() {
        console.log('🔍 DIAGNÓSTICO: Analizando estructura HTML de líneas de factura...');
        
        // Buscar todas las posibles estructuras
        const posiblesStructuras = [
            '.inline-group',
            '.tabular',
            '.dynamic-form',
            '[class*="inline"]',
            'table',
            '.form-row'
        ];
        
        posiblesStructuras.forEach(selector => {
            const elementos = document.querySelectorAll(selector);
            if (elementos.length > 0) {
                console.log(`✅ ENCONTRADO: ${selector} (${elementos.length} elementos)`);
                elementos.forEach((el, i) => {
                    console.log(`  📋 ${selector}[${i}]:`, el.className, el.tagName);
                });
            }
        });
        
        // Buscar campos específicos
        console.log('\n🎯 DIAGNÓSTICO: Buscando campos de producto...');
        const camposProducto = [
            'select[name*="product"]',
            'input[name*="product"]',
            '.field-product',
            '[class*="product"]',
            'td.field-product',
            'th.column-product'
        ];
        
        camposProducto.forEach(selector => {
            const elementos = document.querySelectorAll(selector);
            if (elementos.length > 0) {
                console.log(`✅ CAMPOS PRODUCTO: ${selector} (${elementos.length} elementos)`);
                elementos.forEach((el, i) => {
                    const styles = window.getComputedStyle(el);
                    console.log(`  📊 ${selector}[${i}]:`, {
                        tagName: el.tagName,
                        className: el.className,
                        width: styles.width,
                        minWidth: styles.minWidth,
                        maxWidth: styles.maxWidth,
                        display: styles.display,
                        flex: styles.flex
                    });
                });
            }
        });
        
        // Analizar estructura de tabla/inline específica
        console.log('\n📋 DIAGNÓSTICO: Analizando estructura de tabla inline...');
        const tabla = document.querySelector('table.inline-tabular, .tabular table, table[id*="inline"], table');
        if (tabla) {
            console.log('✅ TABLA ENCONTRADA:', tabla.className, tabla.id);
            
            // Analizar headers
            const headers = tabla.querySelectorAll('thead th, tr th');
            console.log(`  📌 HEADERS (${headers.length}):`)
            headers.forEach((th, i) => {
                console.log(`    ${i}: "${th.textContent.trim()}" - clase: "${th.className}" - ancho: ${window.getComputedStyle(th).width}`);
            });
            
            // Analizar primera fila de datos
            const primeraFila = tabla.querySelector('tbody tr, tr');
            if (primeraFila) {
                const celdas = primeraFila.querySelectorAll('td');
                console.log(`  📊 CELDAS PRIMERA FILA (${celdas.length}):`);
                celdas.forEach((td, i) => {
                    const styles = window.getComputedStyle(td);
                    console.log(`    ${i}: clase="${td.className}" ancho=${styles.width} contenido="${td.textContent.trim().substring(0, 20)}..."`);
                });
            }
        }
        
        return {
            tabla: tabla,
            campos: document.querySelectorAll('select[name*="product"], .field-product'),
            headers: document.querySelectorAll('th')
        };
    }
    
    function aplicarEstilosDirectos() {
        console.log('🛠️ DIAGNÓSTICO: Aplicando estilos directos para testing...');
        
        // Buscar TODOS los elementos posibles y aplicar estilos
        const selectoresYAnchos = [
            { selector: 'td.field-product, .field-product, th.column-product', ancho: '35%', nombre: 'PRODUCTO' },
            { selector: 'td.field-quantity, .field-quantity, th.column-quantity', ancho: '10%', nombre: 'CANTIDAD' },
            { selector: 'td.field-unit_price, .field-unit_price, th.column-unit_price', ancho: '12%', nombre: 'PRECIO' },
            { selector: 'td.field-discount, .field-discount, th.column-discount', ancho: '8%', nombre: 'DESCUENTO' },
            { selector: 'td.field-iva_rate, .field-iva_rate, th.column-iva_rate', ancho: '8%', nombre: 'IVA' },
            { selector: 'td.field-line_total, .field-line_total, th.column-line_total', ancho: '15%', nombre: 'TOTAL' },
            { selector: 'td.field-description, .field-description, th.column-description', ancho: '0%', nombre: 'DESCRIPCION (OCULTAR)' }
        ];
        
        selectoresYAnchos.forEach(config => {
            const elementos = document.querySelectorAll(config.selector);
            console.log(`🎨 ${config.nombre}: ${elementos.length} elementos encontrados`);
            
            elementos.forEach((el, i) => {
                // Aplicar múltiples métodos para forzar el ancho
                el.style.setProperty('width', config.ancho, 'important');
                el.style.setProperty('min-width', config.ancho, 'important');
                el.style.setProperty('max-width', config.ancho, 'important');
                el.style.setProperty('flex', `0 0 ${config.ancho}`, 'important');
                el.style.setProperty('box-sizing', 'border-box', 'important');
                
                if (config.nombre === 'DESCRIPCION (OCULTAR)') {
                    el.style.setProperty('display', 'none', 'important');
                }
                
                // Agregar borde de color para identificación visual
                const colores = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink'];
                el.style.setProperty('border', `2px solid ${colores[i % colores.length]}`, 'important');
                
                console.log(`  ✅ ${config.nombre}[${i}] aplicado: ${config.ancho}`);
            });
        });
        
        // Forzar selects de producto específicamente
        const selectsProducto = document.querySelectorAll('select[name*="product"], input[name*="product"]');
        console.log(`🎯 SELECTS PRODUCTO: ${selectsProducto.length} encontrados`);
        selectsProducto.forEach((select, i) => {
            select.style.setProperty('width', '100%', 'important');
            select.style.setProperty('min-width', '100%', 'important');
            select.style.border = '3px solid red';
            console.log(`  ✅ SELECT PRODUCTO[${i}] forzado a 100%`);
        });
    }
    
    function identificarReglasCSSConflictivas() {
        console.log('🔍 DIAGNÓSTICO: Identificando reglas CSS que pueden estar interfiriendo...');
        
        const campo = document.querySelector('.field-product, td.field-product');
        if (!campo) {
            console.log('❌ No se encontró campo producto para analizar');
            return;
        }
        
        const estilos = window.getComputedStyle(campo);
        console.log('📊 ESTILOS COMPUTADOS DEL CAMPO PRODUCTO:', {
            width: estilos.width,
            minWidth: estilos.minWidth,
            maxWidth: estilos.maxWidth,
            display: estilos.display,
            position: estilos.position,
            flex: estilos.flex,
            boxSizing: estilos.boxSizing
        });
        
        // Intentar identificar hojas de estilo cargadas
        console.log('📋 HOJAS DE ESTILO CARGADAS:');
        Array.from(document.styleSheets).forEach((sheet, i) => {
            try {
                console.log(`  ${i}: ${sheet.href || 'Inline'} (${sheet.cssRules?.length || 0} reglas)`);
            } catch (e) {
                console.log(`  ${i}: ${sheet.href || 'Inline'} (No accesible - CORS)`);
            }
        });
    }
    
    // Función principal de diagnóstico
    function ejecutarDiagnosticoCompleto() {
        console.clear();
        console.log('🚀 INICIANDO DIAGNÓSTICO COMPLETO DE LÍNEAS DE FACTURA...');
        console.log('================================================\n');
        
        const estructura = diagnosticarEstructuraHTML();
        console.log('\n================================================');
        identificarReglasCSSConflictivas();
        console.log('\n================================================');
        aplicarEstilosDirectos();
        
        console.log('\n🎯 RESUMEN DEL DIAGNÓSTICO:');
        console.log('- Revisa los elementos encontrados arriba');
        console.log('- Los campos ahora tienen bordes de colores para identificación');
        console.log('- Si los anchos no cambiaron, hay reglas CSS más específicas interfiriendo');
        console.log('\n💡 PRÓXIMOS PASOS:');
        console.log('- Inspecciona visualmente los campos con bordes de colores');
        console.log('- Usa las herramientas de desarrollador para ver qué CSS se aplica');
        console.log('- Ejecuta: window.forzarAnchosPorInspeccion() para más pruebas');
        
        return estructura;
    }
    
    // Exponer funciones globalmente
    window.diagnosticarLineasFactura = ejecutarDiagnosticoCompleto;
    window.aplicarEstilosDirectos = aplicarEstilosDirectos;
    window.diagnosticarEstructura = diagnosticarEstructuraHTML;
    
    // Ejecutar automáticamente
    console.log('🔧 Herramientas de diagnóstico cargadas. Ejecutando automáticamente...');
    setTimeout(ejecutarDiagnosticoCompleto, 1000);
    
})();

// Función adicional para inspeccionar elemento específico
window.inspeccionarElemento = function(selector) {
    const elemento = document.querySelector(selector);
    if (!elemento) {
        console.log(`❌ No encontrado: ${selector}`);
        return;
    }
    
    const estilos = window.getComputedStyle(elemento);
    console.log(`🔍 INSPECCIÓN: ${selector}`);
    console.log('📊 Estilos computados:', {
        tagName: elemento.tagName,
        className: elemento.className,
        id: elemento.id,
        width: estilos.width,
        minWidth: estilos.minWidth,
        maxWidth: estilos.maxWidth,
        display: estilos.display,
        position: estilos.position,
        flex: estilos.flex,
        flexBasis: estilos.flexBasis,
        boxSizing: estilos.boxSizing,
        borderWidth: estilos.borderWidth,
        padding: estilos.padding,
        margin: estilos.margin
    });
    
    return elemento;
};