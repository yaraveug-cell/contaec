/**
 * Calculadora de totales de factura
 * Calcula automáticamente subtotal, impuestos y total general de la factura
 */
(function() {
    'use strict';
    
    let isCalculating = false;
    
    // Función para calcular totales generales de la factura
    function calculateInvoiceTotals() {
        if (isCalculating) return;
        isCalculating = true;
        
        try {
            console.log('🧮 Calculando totales de factura...');
            
            // Obtener todas las filas de líneas de factura
            const lineRows = document.querySelectorAll('[id*="invoiceline_set"] tr.form-row:not(.empty-form)');
            
            let totalSubtotal = 0;
            let totalTaxAmount = 0;
            let totalTotal = 0;
            let validLinesCount = 0;
            
            // Recorrer cada línea para calcular totales
            lineRows.forEach((row, index) => {
                const quantityField = row.querySelector('input[name*="quantity"]');
                const unitPriceField = row.querySelector('input[name*="unit_price"]');
                const discountField = row.querySelector('input[name*="discount"]');
                const ivaRateField = row.querySelector('input[name*="iva_rate"]');
                const deleteCheckbox = row.querySelector('input[name*="DELETE"]');
                
                // Solo procesar si la fila no está marcada para eliminar
                if (deleteCheckbox && deleteCheckbox.checked) {
                    return; // Saltar líneas eliminadas
                }
                
                // Solo procesar si hay datos válidos
                if (!quantityField || !unitPriceField || !quantityField.value || !unitPriceField.value) {
                    return; // Saltar líneas vacías
                }
                
                const quantity = parseFloat(quantityField.value) || 0;
                const unitPrice = parseFloat(unitPriceField.value) || 0;
                const discount = parseFloat(discountField ? discountField.value : 0) || 0;
                const ivaRate = parseFloat(ivaRateField ? ivaRateField.value : 0) || 0;
                
                // Solo procesar si tiene cantidad y precio
                if (quantity <= 0 || unitPrice <= 0) {
                    return;
                }
                
                // Calcular totales de esta línea
                const lineSubtotal = quantity * unitPrice;
                const lineDiscountAmount = lineSubtotal * (discount / 100);
                const lineNetAmount = lineSubtotal - lineDiscountAmount;
                const lineTaxAmount = lineNetAmount * (ivaRate / 100);
                const lineTotal = lineNetAmount + lineTaxAmount;
                
                // Sumar a totales generales
                totalSubtotal += lineNetAmount;
                totalTaxAmount += lineTaxAmount;
                totalTotal += lineTotal;
                validLinesCount++;
                
                console.log(`   Línea ${index + 1}: $${lineNetAmount.toFixed(2)} + $${lineTaxAmount.toFixed(2)} = $${lineTotal.toFixed(2)}`);
            });
            
            console.log(`📊 Totales calculados (${validLinesCount} líneas):`);
            console.log(`   Subtotal: $${totalSubtotal.toFixed(2)}`);
            console.log(`   Impuestos: $${totalTaxAmount.toFixed(2)}`);
            console.log(`   Total: $${totalTotal.toFixed(2)}`);
            
            // Actualizar campos de totales en la interfaz
            updateTotalFields(totalSubtotal, totalTaxAmount, totalTotal);
            
        } catch (error) {
            console.error('❌ Error calculando totales:', error);
        } finally {
            isCalculating = false;
        }
    }
    
    // Función para actualizar campos de totales
    function updateTotalFields(subtotal, taxAmount, total) {
        // Buscar campos de totales (pueden estar ocultos o visibles)
        const subtotalField = document.querySelector('input[name="subtotal"]') || 
                             document.querySelector('#id_subtotal');
        const taxField = document.querySelector('input[name="tax_amount"]') || 
                        document.querySelector('#id_tax_amount');
        const totalField = document.querySelector('input[name="total"]') || 
                          document.querySelector('#id_total');
        
        // Actualizar valores si los campos existen
        if (subtotalField) {
            subtotalField.value = subtotal.toFixed(2);
            console.log(`✅ Subtotal actualizado: $${subtotal.toFixed(2)}`);
        }
        
        if (taxField) {
            taxField.value = taxAmount.toFixed(2);
            console.log(`✅ Impuestos actualizados: $${taxAmount.toFixed(2)}`);
        }
        
        if (totalField) {
            totalField.value = total.toFixed(2);
            console.log(`✅ Total actualizado: $${total.toFixed(2)}`);
        }
        
        // Actualizar displays si existen
        updateTotalDisplays(subtotal, taxAmount, total);
    }
    
    // Función para actualizar displays visuales
    function updateTotalDisplays(subtotal, taxAmount, total) {
        const formatCurrency = (amount) => {
            return '$' + amount.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        };
        
        // Actualizar displays existentes (solo elementos específicos del admin)
        const displays = [
            { selector: '.invoice-subtotal-display', value: subtotal, label: 'Subtotal' },
            { selector: '.invoice-tax-display', value: taxAmount, label: 'Impuestos' },
            { selector: '.invoice-total-display', value: total, label: 'Total' }
        ];
        
        displays.forEach(({ selector, value, label }) => {
            let display = document.querySelector(selector);
            if (display) {
                display.textContent = formatCurrency(value);
            }
        });
        
        // ✅ PANEL FLOTANTE DESHABILITADO - Los totales solo se muestran en los campos del formulario
        // showTotalsSummary(subtotal, taxAmount, total); // <- DESHABILITADO
    }
    
    // Mostrar resumen de totales (DESHABILITADO - solo log en consola)
    function showTotalsSummary(subtotal, taxAmount, total) {
        // ✅ FUNCIONALIDAD OCULTA: No mostrar panel flotante
        // Solo registrar en consola para debugging si es necesario
        console.log('💰 Totales calculados - Panel flotante deshabilitado');
        
        // Eliminar panel existente si existe
        const existingSummary = document.querySelector('#invoice-totals-summary');
        if (existingSummary) {
            existingSummary.remove();
            console.log('🗑️ Panel flotante removido');
        }
        
        // No crear ni mostrar el panel - mantener solo la funcionalidad de cálculo
        return;
    }
    
    // Función para configurar event listeners
    function setupEventListeners() {
        // Event delegation para campos de líneas
        document.addEventListener('input', function(event) {
            const target = event.target;
            if (target.tagName === 'INPUT' && 
                (target.name.includes('quantity') || 
                 target.name.includes('unit_price') || 
                 target.name.includes('discount') || 
                 target.name.includes('iva_rate'))) {
                
                // Recalcular totales después de un breve delay
                setTimeout(calculateInvoiceTotals, 100);
            }
        });
        
        // Event delegation para checkboxes de eliminación
        document.addEventListener('change', function(event) {
            const target = event.target;
            if (target.type === 'checkbox' && target.name.includes('DELETE')) {
                setTimeout(calculateInvoiceTotals, 100);
            }
        });
        
        console.log('✅ Event listeners configurados para cálculo de totales');
    }
    
    // Observer para nuevas filas
    function setupMutationObserver() {
        if (typeof MutationObserver !== 'undefined') {
            const observer = new MutationObserver(function(mutations) {
                let shouldRecalculate = false;
                
                mutations.forEach(function(mutation) {
                    // Verificar si se agregaron o removieron filas
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1 && 
                            (node.classList.contains('form-row') || 
                             node.querySelector && node.querySelector('.form-row'))) {
                            shouldRecalculate = true;
                        }
                    });
                    
                    mutation.removedNodes.forEach(function(node) {
                        if (node.nodeType === 1 && 
                            (node.classList.contains('form-row') || 
                             node.querySelector && node.querySelector('.form-row'))) {
                            shouldRecalculate = true;
                        }
                    });
                });
                
                if (shouldRecalculate) {
                    setTimeout(calculateInvoiceTotals, 200);
                }
            });
            
            // Observar cambios en el contenedor de líneas
            const linesContainer = document.querySelector('[id*="invoiceline_set"]');
            if (linesContainer) {
                observer.observe(linesContainer, {
                    childList: true,
                    subtree: true
                });
                console.log('✅ Observer configurado para nuevas filas');
            }
        }
    }
    
    // Función para detectar si estamos en modo creación o edición
    function isEditMode() {
        // En modo creación, la URL termina con '/add/'
        // En modo edición, la URL contiene '/change/' o un ID numérico
        const url = window.location.pathname;
        const isAdd = url.includes('/add/');
        const isChange = url.includes('/change/') || /\/\d+\//.test(url);
        
        return !isAdd && isChange;
    }
    
    // Función de inicialización
    function init() {
        const editMode = isEditMode();
        console.log(`🚀 Inicializando calculadora de totales - Modo: ${editMode ? 'Edición' : 'Creación'}`);
        
        // Limpiar cualquier panel flotante existente
        cleanupFloatingPanel();
        
        // Solo configurar calculadora completa en modo edición
        if (editMode) {
            console.log('✅ Modo edición: Calculadora completa habilitada');
            setupEventListeners();
            setupMutationObserver();
            // Calcular totales iniciales
            setTimeout(calculateInvoiceTotals, 500);
        } else {
            console.log('ℹ️ Modo creación: Calculadora de líneas solamente');
            // En modo creación, solo configurar event listeners básicos para líneas individuales
            setupBasicLineCalculation();
        }
    }
    
    // Función para limpiar panel flotante
    function cleanupFloatingPanel() {
        const existingPanel = document.querySelector('#invoice-totals-summary');
        if (existingPanel) {
            existingPanel.remove();
            console.log('🗑️ Panel flotante existente removido');
        }
    }
    
    // Función para configuración básica en modo creación (solo cálculo de líneas)
    function setupBasicLineCalculation() {
        console.log('⚡ Configurando cálculo básico para líneas individuales');
        
        // Solo event delegation para campos de líneas (sin actualizar totales generales)
        document.addEventListener('input', function(event) {
            const target = event.target;
            if (target.tagName === 'INPUT' && 
                (target.name.includes('quantity') || 
                 target.name.includes('unit_price') || 
                 target.name.includes('discount') || 
                 target.name.includes('iva_rate'))) {
                
                // Solo calcular total de la línea individual, no totales generales
                const row = target.closest('tr') || target.closest('.form-row') || target.closest('fieldset');
                if (row) {
                    // Dejar que el invoice_line_calculator.js maneje el cálculo individual
                    console.log('📝 Cambio detectado en línea individual');
                }
            }
        });
        
        console.log('✅ Configuración básica completada');
    }
    
    // Inicializar cuando esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Exponer función para uso externo
    window.calculateInvoiceTotals = calculateInvoiceTotals;
    
})();