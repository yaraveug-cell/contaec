/**
 * FORZAR ANCHOS DE COLUMNAS DINÁMICAMENTE
 * Para garantizar que el campo producto tenga 60% del ancho
 */
(function() {
    'use strict';
    
    function forceProductColumnWidth() {
        console.log('🎯 FORZANDO anchos de columnas para líneas de factura...');
        
        // Buscar la tabla de líneas de factura
        const tables = [
            document.querySelector('#invoiceline_set-group table'),
            document.querySelector('#invoiceline_set-group .tabular table'),
            document.querySelector('table[id*="invoiceline"]'),
            document.querySelector('.inline-group .tabular table')
        ].filter(t => t !== null);
        
        if (tables.length === 0) {
            console.log('❌ No se encontró tabla de líneas de factura');
            return;
        }
        
        tables.forEach((table, tableIndex) => {
            console.log(`📋 Procesando tabla ${tableIndex + 1}:`, table.id || table.className);
            
            // Configurar la tabla
            table.style.setProperty('width', '100%', 'important');
            table.style.setProperty('table-layout', 'fixed', 'important');
            
            // Procesar todas las filas (headers y data)
            const rows = table.querySelectorAll('tr');
            console.log(`  📊 Filas encontradas: ${rows.length}`);
            
            rows.forEach((row, rowIndex) => {
                const cells = row.querySelectorAll('th, td');
                
                if (cells.length >= 6) { // Verificar que tenga al menos las columnas esperadas
                    console.log(`    🔧 Fila ${rowIndex}: ${cells.length} celdas`);
                    
                    // CONFIGURACIÓN PARA 8 COLUMNAS (estructura real de Django)
                    // [0: order/drag, 1: product, 2: quantity, 3: unit_price, 4: discount, 5: iva_rate, 6: line_total, 7: delete]
                    const widths = ['3%', '55%', '8%', '12%', '6%', '6%', '8%', '2%'];  // 8 columnas
                    const colors = ['rgba(128,128,128,0.1)', 'rgba(255,0,0,0.2)', 'rgba(0,255,0,0.1)', 
                                  'rgba(0,0,255,0.1)', 'rgba(255,255,0,0.1)', 'rgba(255,0,255,0.1)', 
                                  'rgba(0,255,255,0.1)', 'rgba(128,128,128,0.1)'];
                    const labels = ['ORDER', 'PRODUCTO', 'CANTIDAD', 'PRECIO', 'DESCUENTO', 'IVA', 'TOTAL', 'DELETE'];
                    
                    cells.forEach((cell, cellIndex) => {
                        const width = widths[cellIndex] || '1%'; // Fallback para celdas extra
                        const color = colors[cellIndex] || 'rgba(200,200,200,0.1)';
                        const label = labels[cellIndex] || 'EXTRA';
                        
                        cell.style.setProperty('width', width, 'important');
                        cell.style.setProperty('min-width', width, 'important');
                        cell.style.setProperty('max-width', width, 'important');
                        cell.style.setProperty('box-sizing', 'border-box', 'important');
                        
                        // Colores de debug para identificar columnas
                        cell.style.setProperty('background', color, 'important');
                        
                        // Agregar texto de debug en headers
                        if (cell.tagName === 'TH' && cellIndex === 1) {
                            cell.style.setProperty('border', '3px solid red', 'important');
                        }
                        
                        console.log(`      ✅ Celda ${cellIndex} (${label}): ${width} aplicado`);
                    });
                }
            });
            
            // Ajustar inputs/selects dentro de las celdas
            const inputs = table.querySelectorAll('input, select');
            inputs.forEach(input => {
                // Para campos normales - 100% del contenedor
                if (!input.name || !input.name.includes('product')) {
                    input.style.setProperty('width', '100%', 'important');
                    input.style.setProperty('box-sizing', 'border-box', 'important');
                }
            });
            
            // TRATAMIENTO ESPECIAL PARA CAMPOS PRODUCTO - MÉTODO SIMPLE
            const productSelects = table.querySelectorAll('select[name*="product"]');
            productSelects.forEach((select, index) => {
                // Remover estilos conflictivos primero
                select.style.removeProperty('width');
                select.style.removeProperty('min-width');
                select.style.removeProperty('max-width');
                
                // Aplicar ancho simple y efectivo
                select.style.setProperty('width', '100%', 'important');
                select.style.setProperty('box-sizing', 'border-box', 'important');
                select.style.setProperty('border', '2px solid #ff0000', 'important');
                
                // Asegurar que el contenedor padre no limite el ancho
                const parentTd = select.closest('td');
                if (parentTd) {
                    parentTd.style.setProperty('padding', '2px', 'important');
                }
                
                console.log(`      🎯 Campo producto ${index + 1} simplificado: 100% del contenedor (${select.name})`);
            });
            
            // TRATAMIENTO SIMPLE PARA SELECT2 (autocompletado)
            const select2Containers = table.querySelectorAll('.select2-container');
            select2Containers.forEach((container, index) => {
                const parentTd = container.closest('td');
                if (parentTd && parentTd.cellIndex === 1) { // Columna 2 (index 1) es producto
                    container.style.setProperty('width', '100%', 'important');
                    container.style.setProperty('display', 'block', 'important');
                    
                    const selection = container.querySelector('.select2-selection--single');
                    if (selection) {
                        selection.style.setProperty('width', '100%', 'important');
                    }
                    
                    console.log(`      🎯 Select2 container producto ${index + 1} simplificado`);
                }
            });
            
            console.log(`  ✅ Tabla ${tableIndex + 1} procesada completamente`);
        });
        
        console.log('🏁 FORZADO DE ANCHOS COMPLETADO');
    }
    
    function observeForNewRows() {
        const observer = new MutationObserver(function(mutations) {
            let shouldReapply = false;
            
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1 && (
                            node.matches && (
                                node.matches('tr') ||
                                node.querySelector && node.querySelector('tr')
                            )
                        )) {
                            shouldReapply = true;
                        }
                    });
                }
            });
            
            if (shouldReapply) {
                console.log('🔄 Nueva fila detectada, reaplicando anchos...');
                setTimeout(forceProductColumnWidth, 100);
            }
        });
        
        const container = document.querySelector('#invoiceline_set-group') || document.body;
        observer.observe(container, { childList: true, subtree: true });
        console.log('👁️ Observer configurado para detectar nuevas filas');
    }
    
    function init() {
        console.log('🚀 INICIANDO forzado de anchos de producto...');
        
        // Aplicar inmediatamente
        setTimeout(forceProductColumnWidth, 500);
        
        // Aplicar después de delays para asegurar carga completa
        setTimeout(forceProductColumnWidth, 1500);
        setTimeout(forceProductColumnWidth, 3000);
        
        // Configurar observer
        observeForNewRows();
        
        console.log('✅ Configuración de forzado de anchos completada');
    }
    
    // Exponer funciones globalmente
    window.forceProductColumnWidth = forceProductColumnWidth;
    
    // Inicializar
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // También al cargar completamente la ventana
    window.addEventListener('load', function() {
        setTimeout(forceProductColumnWidth, 1000);
    });
    
})();