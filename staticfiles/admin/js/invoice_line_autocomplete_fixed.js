
/**
 * Autocompletado específico para InvoiceLineInline con widget Django autocomplete
 */
(function() {
    'use strict';
    
    let productsData = {};
    
    // Cargar datos de productos del contexto Django
    function loadProductsData() {
        const dataScript = document.getElementById('products-data');
        if (dataScript) {
            try {
                productsData = JSON.parse(dataScript.textContent);
                console.log('📦 Productos cargados:', Object.keys(productsData).length);
            } catch (e) {
                console.error('❌ Error cargando productos:', e);
            }
        } else if (typeof window.productsData !== 'undefined') {
            productsData = window.productsData;
            console.log('📦 Productos desde window:', Object.keys(productsData).length);
        }
    }
    
    // Manejar selección de producto en widget de autocompletado
    function handleProductSelection(productField) {
        const productId = productField.value;
        
        console.log('🔍 Producto seleccionado:', productId);
        
        if (!productId || !productsData[productId]) {
            console.log('⚠️ Producto no encontrado:', productId);
            return;
        }
        
        const productData = productsData[productId];
        console.log('📦 Datos del producto:', productData);
        
        // Encontrar la fila contenedora
        const row = productField.closest('tr') || productField.closest('.inline-related');
        if (!row) {
            console.log('❌ Fila no encontrada');
            return;
        }
        
        // Buscar campos por nombre exacto del inline
        const prefix = productField.name.replace('-product', '');
        
        const descriptionField = document.querySelector(`[name="${prefix}-description"]`);
        const unitPriceField = document.querySelector(`[name="${prefix}-unit_price"]`); 
        const ivaRateField = document.querySelector(`[name="${prefix}-iva_rate"]`);
        
        console.log('🔍 Campos encontrados:', {
            prefix: prefix,
            description: !!descriptionField,
            unitPrice: !!unitPriceField,
            ivaRate: !!ivaRateField
        });
        
        // Completar campos automáticamente
        if (descriptionField && productData.description) {
            descriptionField.value = productData.description;
            console.log('✅ Descripción actualizada');
        }
        
        if (unitPriceField && productData.sale_price) {
            unitPriceField.value = productData.sale_price;
            unitPriceField.dispatchEvent(new Event('input', { bubbles: true }));
            console.log('✅ Precio actualizado');
        }
        
        if (ivaRateField && productData.iva_rate) {
            ivaRateField.value = productData.iva_rate;
            ivaRateField.dispatchEvent(new Event('input', { bubbles: true }));
            console.log('✅ IVA actualizado');
        }
    }
    
    // Configurar listeners para widgets de autocompletado
    function setupAutocompletedWidgets() {
        // Buscar widgets de autocompletado de producto existentes
        const productWidgets = document.querySelectorAll('input[name*="product"].admin-autocomplete');
        
        console.log(`🔧 Configurando ${productWidgets.length} widgets de producto`);
        
        productWidgets.forEach(function(widget) {
            // Escuchar cambios en el widget
            widget.addEventListener('change', function() {
                setTimeout(() => handleProductSelection(widget), 100);
            });
            
            widget.addEventListener('blur', function() {
                setTimeout(() => handleProductSelection(widget), 150);
            });
            
            console.log('✅ Widget configurado:', widget.name);
        });
    }
    
    // Observer para detectar nuevos widgets
    function setupMutationObserver() {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) {
                        const newWidgets = node.querySelectorAll ? 
                            node.querySelectorAll('input[name*="product"].admin-autocomplete') : [];
                        
                        newWidgets.forEach(function(widget) {
                            widget.addEventListener('change', function() {
                                setTimeout(() => handleProductSelection(widget), 100);
                            });
                        });
                    }
                });
            });
        });
        
        observer.observe(document.body, { childList: true, subtree: true });
    }
    
    // Inicialización
    function init() {
        console.log('🚀 Inicializando autocompletado específico para inline');
        
        loadProductsData();
        
        // Delay para asegurar que los widgets estén completamente cargados
        setTimeout(function() {
            setupAutocompletedWidgets();
            setupMutationObserver();
        }, 1000);
    }
    
    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();
