// Calculadora de totales de línea en tiempo real - VERSIÓN ROBUSTA
(function() {
    'use strict';
    
    console.log('[LINE_CALCULATOR] 🚀 Inicializando calculadora de líneas ROBUSTA...');
    
    function findInputInRow(row, fieldNames) {
        // Estrategia múltiple para encontrar campos
        for (const fieldName of fieldNames) {
            // Estrategia 1: Por atributo name exacto
            let input = row.querySelector(`input[name*="${fieldName}"]`);
            if (input) return input;
            
            // Estrategia 2: Por ID que contenga el fieldName
            input = row.querySelector(`input[id*="${fieldName}"]`);
            if (input) return input;
            
            // Estrategia 3: Por clase CSS
            input = row.querySelector(`input.field-${fieldName}`);
            if (input) return input;
        }
        return null;
    }
    
    function calculateLineTotal(row) {
        try {
            console.log('[LINE_CALCULATOR] 🧮 Calculando línea para fila:', row);
            
            // Buscar campos usando múltiples estrategias
            const quantityInput = findInputInRow(row, ['quantity', 'cantidad']);
            const priceInput = findInputInRow(row, ['unit_price', 'precio_unitario', 'price']);
            const discountInput = findInputInRow(row, ['discount', 'descuento']);
            const ivaInput = findInputInRow(row, ['iva_rate', 'tasa_iva', 'iva']);
            const totalInput = findInputInRow(row, ['line_total', 'total_linea', 'total']);
            
            console.log('[LINE_CALCULATOR] 🔍 Campos encontrados:', {
                quantity: quantityInput?.name || 'NO ENCONTRADO',
                price: priceInput?.name || 'NO ENCONTRADO', 
                discount: discountInput?.name || 'NO ENCONTRADO',
                iva: ivaInput?.name || 'NO ENCONTRADO',
                total: totalInput?.name || 'NO ENCONTRADO'
            });
            
            if (!quantityInput || !priceInput || !totalInput) {
                console.warn('[LINE_CALCULATOR] ⚠️ Campos requeridos no encontrados');
                return;
            }
            
            // Obtener valores numéricos
            const quantity = parseFloat(quantityInput.value) || 0;
            const unitPrice = parseFloat(priceInput.value) || 0;
            const discount = parseFloat(discountInput?.value) || 0;
            const ivaRate = parseFloat(ivaInput?.value) || 15; // IVA por defecto 15%
            
            console.log('[LINE_CALCULATOR] 📊 Valores obtenidos:', {
                quantity, unitPrice, discount, ivaRate
            });
            
            // Calcular subtotal
            const subtotal = quantity * unitPrice;
            
            // Aplicar descuento
            const discountAmount = subtotal * (discount / 100);
            const subtotalAfterDiscount = subtotal - discountAmount;
            
            // Aplicar IVA
            const ivaAmount = subtotalAfterDiscount * (ivaRate / 100);
            const lineTotal = subtotalAfterDiscount + ivaAmount;
            
            // Actualizar campo total (redondeado a 2 decimales)
            const finalTotal = lineTotal.toFixed(2);
            totalInput.value = finalTotal;
            
            // Disparar evento change para que Django lo detecte
            totalInput.dispatchEvent(new Event('change', { bubbles: true }));
            
            console.log(`[LINE_CALCULATOR] ✅ Línea calculada: ${quantity} x ${unitPrice} - ${discount}% + ${ivaRate}% IVA = ${finalTotal}`);
            
        } catch (error) {
            console.error('[LINE_CALCULATOR] ❌ Error calculando línea:', error);
        }
    }
    
    function attachCalculationListeners() {
        console.log('[LINE_CALCULATOR] 🔗 Buscando filas de líneas de factura...');
        
        // Múltiples selectores para encontrar las filas
        const selectors = [
            '.dynamic-invoiceline_set-group .form-row:not(.add-row)',
            '.tabular .form-row:not(.add-row)',
            '.inline-group .form-row:not(.add-row)',
            '[class*="invoiceline"] .form-row:not(.add-row)'
        ];
        
        let inlineRows = [];
        for (const selector of selectors) {
            const rows = document.querySelectorAll(selector);
            if (rows.length > 0) {
                inlineRows = Array.from(rows);
                console.log(`[LINE_CALCULATOR] ✅ Encontradas ${rows.length} filas con selector: ${selector}`);
                break;
            }
        }
        
        if (inlineRows.length === 0) {
            console.warn('[LINE_CALCULATOR] ⚠️ No se encontraron filas de líneas de factura');
            // Mostrar qué elementos SÍ existen
            console.log('[LINE_CALCULATOR] 🔍 Elementos disponibles:', {
                dynamicGroups: document.querySelectorAll('[class*="dynamic"]').length,
                formRows: document.querySelectorAll('.form-row').length,
                inlineGroups: document.querySelectorAll('.inline-group').length,
                tabular: document.querySelectorAll('.tabular').length
            });
            return;
        }
        
        inlineRows.forEach((row, index) => {
            console.log(`[LINE_CALCULATOR] 🔄 Procesando fila ${index + 1}:`, row);
            
            // Buscar TODOS los inputs en la fila
            const allInputs = row.querySelectorAll('input');
            console.log(`[LINE_CALCULATOR] 📝 Inputs encontrados en fila ${index + 1}:`, 
                Array.from(allInputs).map(input => ({ name: input.name, id: input.id, type: input.type }))
            );
            
            // Buscar campos que afectan el cálculo con múltiples selectores
            const calculationFields = row.querySelectorAll(`
                input[name*="quantity"], input[name*="cantidad"],
                input[name*="unit_price"], input[name*="precio"],
                input[name*="discount"], input[name*="descuento"],
                input[name*="iva_rate"], input[name*="iva"]
            `);
            
            calculationFields.forEach(field => {
                console.log(`[LINE_CALCULATOR] 🎯 Añadiendo listeners a campo:`, field.name);
                
                // Añadir listeners para cálculo automático (sin clonar para evitar problemas)
                ['input', 'change', 'keyup', 'blur'].forEach(eventType => {
                    field.addEventListener(eventType, function() {
                        console.log(`[LINE_CALCULATOR] 🔥 Evento ${eventType} disparado en ${field.name}`);
                        calculateLineTotal(row);
                    });
                });
            });
            
            // Calcular total inicial si ya hay datos
            setTimeout(() => calculateLineTotal(row), 100);
        });
        
        console.log(`[LINE_CALCULATOR] ✅ Listeners añadidos a ${inlineRows.length} filas`);
    }
    
    function initialize() {
        console.log('[LINE_CALCULATOR] 🚀 Inicializando calculadora...');
        attachCalculationListeners();
    }
    
    // Ejecutar inmediatamente
    initialize();
    
    // Ejecutar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        // Si ya está listo, ejecutar con delay para asegurar que Django Admin terminó
        setTimeout(initialize, 500);
    }
    
    // Ejecutar cuando la página se cargue completamente
    window.addEventListener('load', function() {
        setTimeout(initialize, 1000);
    });
    
    // Re-ejecutar periódicamente para capturar cambios dinámicos
    setInterval(function() {
        const rows = document.querySelectorAll('.form-row:not(.add-row)');
        if (rows.length > 0) {
            attachCalculationListeners();
        }
    }, 3000);
    
    // Observer para nuevas filas (más agresivo)
    const observer = new MutationObserver(function(mutations) {
        let shouldRecalculate = false;
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) {
                        // Cualquier elemento añadido
                        if (node.classList?.contains('form-row') || 
                            node.querySelector?.('.form-row') ||
                            node.querySelector?.('input')) {
                            shouldRecalculate = true;
                        }
                    }
                });
            }
        });
        
        if (shouldRecalculate) {
            console.log('[LINE_CALCULATOR] 🔄 DOM cambió, re-inicializando...');
            setTimeout(initialize, 200);
        }
    });
    
    // Observar todo el documento
    if (document.body) {
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: false
        });
    }
    
    console.log('[LINE_CALCULATOR] 🎯 Script cargado completamente');
    
})();