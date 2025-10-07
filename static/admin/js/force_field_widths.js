/**
 * Script de emergencia para forzar anchos de campos en líneas de factura
 * Ejecuta después de la carga completa de la página
 */
(function() {
    'use strict';
    
    function forceInvoiceLineWidths() {
        console.log('🛠️ EMERGENCY: Forzando anchos de campos de líneas de factura');
        
        // Crear estilos dinámicos con máxima especificidad
        const style = document.createElement('style');
        style.id = 'emergency-invoice-line-widths';
        style.textContent = `
            /* ESTILOS DE EMERGENCIA - MÁXIMA PRIORIDAD */
            .field-product, 
            td.field-product, 
            .inline-group .field-product,
            .tabular .field-product {
                width: 35% !important;
                min-width: 35% !important;
                max-width: 35% !important;
                flex: 0 0 35% !important;
            }
            
            .field-quantity, 
            td.field-quantity {
                width: 10% !important;
                min-width: 10% !important;
                max-width: 10% !important;
            }
            
            .field-unit_price, 
            td.field-unit_price {
                width: 12% !important;
                min-width: 12% !important;
                max-width: 12% !important;
            }
            
            .field-discount, 
            td.field-discount {
                width: 8% !important;
                min-width: 8% !important;
                max-width: 8% !important;
            }
            
            .field-iva_rate, 
            td.field-iva_rate {
                width: 8% !important;
                min-width: 8% !important;
                max-width: 8% !important;
            }
            
            .field-line_total, 
            td.field-line_total {
                width: 15% !important;
                min-width: 15% !important;
                max-width: 15% !important;
            }
            
            /* Ocultar descripción */
            .field-description,
            td.field-description {
                display: none !important;
            }
            
            /* Asegurar que los select usen todo el ancho del contenedor */
            select[name*="product"] {
                width: 100% !important;
                min-width: unset !important;
            }
        `;
        
        // Remover estilo anterior si existe
        const existing = document.getElementById('emergency-invoice-line-widths');
        if (existing) {
            existing.remove();
        }
        
        // Agregar al head para máxima prioridad
        document.head.appendChild(style);
        console.log('✅ EMERGENCY: Estilos dinámicos aplicados');
        
        // También aplicar estilos inline como backup
        applyInlineStyles();
    }
    
    function applyInlineStyles() {
        console.log('🎨 EMERGENCY: Aplicando estilos inline como backup');
        
        const fieldMappings = [
            { selector: '.field-product, td.field-product', width: '35%' },
            { selector: '.field-quantity, td.field-quantity', width: '10%' },
            { selector: '.field-unit_price, td.field-unit_price', width: '12%' },
            { selector: '.field-discount, td.field-discount', width: '8%' },
            { selector: '.field-iva_rate, td.field-iva_rate', width: '8%' },
            { selector: '.field-line_total, td.field-line_total', width: '15%' }
        ];
        
        fieldMappings.forEach(mapping => {
            const elements = document.querySelectorAll(mapping.selector);
            elements.forEach((element, index) => {
                element.style.setProperty('width', mapping.width, 'important');
                element.style.setProperty('min-width', mapping.width, 'important');
                element.style.setProperty('max-width', mapping.width, 'important');
                element.style.setProperty('flex', `0 0 ${mapping.width}`, 'important');
                element.style.setProperty('box-sizing', 'border-box', 'important');
            });
            console.log(`✅ EMERGENCY: ${elements.length} elementos ${mapping.selector} ajustados a ${mapping.width}`);
        });
        
        // Ocultar descripción
        const descriptionFields = document.querySelectorAll('.field-description, td.field-description');
        descriptionFields.forEach(field => {
            field.style.setProperty('display', 'none', 'important');
        });
        console.log(`✅ EMERGENCY: ${descriptionFields.length} campos descripción ocultados`);
        
        // Ajustar select de productos
        const productSelects = document.querySelectorAll('select[name*="product"]');
        productSelects.forEach(select => {
            select.style.setProperty('width', '100%', 'important');
            select.style.setProperty('min-width', 'unset', 'important');
        });
        console.log(`✅ EMERGENCY: ${productSelects.length} select productos ajustados`);
    }
    
    function observeNewRows() {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1 && (
                        node.classList.contains('dynamic-form') ||
                        node.querySelector && node.querySelector('.dynamic-form')
                    )) {
                        console.log('🆕 EMERGENCY: Nueva fila detectada, aplicando estilos...');
                        setTimeout(applyInlineStyles, 100);
                    }
                });
            });
        });
        
        observer.observe(document.body, { childList: true, subtree: true });
        console.log('👁️ EMERGENCY: Observer configurado para nuevas filas');
    }
    
    function init() {
        console.log('🚀 EMERGENCY: Inicializando forzado de anchos...');
        
        // Aplicar inmediatamente
        forceInvoiceLineWidths();
        
        // Aplicar después de un delay para asegurar carga completa
        setTimeout(forceInvoiceLineWidths, 1000);
        setTimeout(forceInvoiceLineWidths, 3000);
        
        // Configurar observer para nuevas filas
        observeNewRows();
        
        console.log('✅ EMERGENCY: Inicialización completada');
    }
    
    // Exponer función globalmente para uso manual
    window.forceInvoiceLineWidths = forceInvoiceLineWidths;
    window.applyInlineStyles = applyInlineStyles;
    
    // Inicializar
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // También ejecutar cuando la ventana termine de cargar completamente
    window.addEventListener('load', function() {
        setTimeout(forceInvoiceLineWidths, 500);
    });
    
})();