/**
 * Calculadora de total de línea para facturas
 * Calcula automáticamente el total basado en cantidad, precio, descuento e IVA
 */
(function() {
    'use strict';
    
    // Función para calcular el total de línea
    function calculateLineTotal(row) {
        // Obtener valores de los campos
        const quantityField = row.querySelector('input[name*="quantity"]');
        const unitPriceField = row.querySelector('input[name*="unit_price"]');
        const discountField = row.querySelector('input[name*="discount"]');
        const ivaRateField = row.querySelector('input[name*="iva_rate"]');
        const totalField = row.querySelector('input[name*="line_total"]');
        
        if (!quantityField || !unitPriceField || !totalField) {
            return;
        }
        
        // Obtener valores (usar 0 como default)
        const quantity = parseFloat(quantityField.value) || 0;
        const unitPrice = parseFloat(unitPriceField.value) || 0;
        const discount = parseFloat(discountField ? discountField.value : 0) || 0;
        const ivaRate = parseFloat(ivaRateField ? ivaRateField.value : 0) || 0;
        
        // Calcular total de línea
        const subtotal = quantity * unitPrice;
        const discountAmount = subtotal * (discount / 100);
        const subtotalAfterDiscount = subtotal - discountAmount;
        const ivaAmount = subtotalAfterDiscount * (ivaRate / 100);
        const lineTotal = subtotalAfterDiscount + ivaAmount;
        
        // Actualizar campo total con formato
        totalField.value = lineTotal.toFixed(2);
        
        // Actualizar display si existe
        const totalDisplay = row.querySelector('.line-total-display');
        if (totalDisplay) {
            totalDisplay.textContent = '$' + lineTotal.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
        
        console.log(`Calculado: ${quantity} × $${unitPrice} - ${discount}% + ${ivaRate}% IVA = $${lineTotal.toFixed(2)}`);
    }
    
    // Función para configurar calculadora en una fila
    function setupRowCalculator(row) {
        const fields = [
            'input[name*="quantity"]',
            'input[name*="unit_price"]',
            'input[name*="discount"]',
            'input[name*="iva_rate"]'
        ];
        
        fields.forEach(selector => {
            const field = row.querySelector(selector);
            if (field && !field.hasAttribute('data-calculator-setup')) {
                field.setAttribute('data-calculator-setup', 'true');
                
                // Eventos para recalcular
                ['input', 'change', 'blur', 'keyup'].forEach(eventType => {
                    field.addEventListener(eventType, function() {
                        setTimeout(() => calculateLineTotal(row), 50);
                    });
                });
            }
        });
    }
    
    // Configurar todas las filas existentes
    function setupAllRows() {
        const rows = document.querySelectorAll('tr.form-row, .form-row, fieldset.module');
        rows.forEach(setupRowCalculator);
    }
    
    // Función para configurar calculadora usando event delegation
    function setupCalculator() {
        // Usar event delegation para capturar cambios en cualquier campo
        document.addEventListener('input', function(event) {
            const target = event.target;
            if (target.tagName === 'INPUT' && 
                (target.name.includes('quantity') || 
                 target.name.includes('unit_price') || 
                 target.name.includes('discount') || 
                 target.name.includes('iva_rate'))) {
                
                const row = target.closest('tr') || target.closest('.form-row') || target.closest('fieldset');
                if (row) {
                    setTimeout(() => calculateLineTotal(row), 50);
                }
            }
        });
        
        // También capturar eventos change
        document.addEventListener('change', function(event) {
            const target = event.target;
            if (target.tagName === 'INPUT' && 
                (target.name.includes('quantity') || 
                 target.name.includes('unit_price') || 
                 target.name.includes('discount') || 
                 target.name.includes('iva_rate'))) {
                
                const row = target.closest('tr') || target.closest('.form-row') || target.closest('fieldset');
                if (row) {
                    setTimeout(() => calculateLineTotal(row), 50);
                }
            }
        });
        
        console.log('Calculadora de total de línea configurada');
    }
    
    // Inicializar
    function init() {
        setupCalculator();
        setupAllRows();
        
        // Observer para nuevas filas
        if (typeof MutationObserver !== 'undefined') {
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1) { // Element node
                            const newRows = node.querySelectorAll ? 
                                node.querySelectorAll('tr.form-row, .form-row, fieldset.module') : [];
                            newRows.forEach(setupRowCalculator);
                            
                            // Si el nodo mismo es una fila
                            if (node.matches && node.matches('tr.form-row, .form-row, fieldset.module')) {
                                setupRowCalculator(node);
                            }
                        }
                    });
                });
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        }
    }
    
    // Inicializar cuando esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();