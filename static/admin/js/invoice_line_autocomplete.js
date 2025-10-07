/**
 * Autocompletado específico para InvoiceLineInline con widget Django autocomplete
 * Versión optimizada sin logs de debugging
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
                return;
            } catch (e) {
                // Error silencioso
            }
        }
        
        if (typeof window.productsData !== 'undefined') {
            productsData = window.productsData;
            return;
        }
        
        // Intentar buscar en variables globales del template
        if (typeof window.products_data_json !== 'undefined') {
            try {
                productsData = JSON.parse(window.products_data_json);
                return;
            } catch (e) {
                // Error silencioso
            }
        }
    }
    
    // Manejar selección de producto en widget de autocompletado
    function handleProductSelection(productField, retryCount = 0) {
        const productId = productField.value;
        const maxRetries = 3;
        
        if (!productId) {
            return;
        }
        
        if (!productsData[productId]) {
            return;
        }
        
        const productData = productsData[productId];
        
        // Buscar campos por nombre exacto del inline
        const prefix = productField.name.replace('-product', '');
        
        const descriptionField = document.querySelector(`[name="${prefix}-description"]`);
        const unitPriceField = document.querySelector(`[name="${prefix}-unit_price"]`); 
        const ivaRateField = document.querySelector(`[name="${prefix}-iva_rate"]`);
        
        // Si no se encuentran campos y tenemos retries disponibles, intentar de nuevo
        if ((!unitPriceField || !ivaRateField) && retryCount < maxRetries) {
            console.log(`� Campos no encontrados, reintentando en 200ms (retry ${retryCount + 1}/${maxRetries})`);
            setTimeout(() => {
                handleProductSelection(productField, retryCount + 1);
            }, 200);
            return;
        }
        
        // Si después de todos los retries no se encuentran campos
        if (!unitPriceField || !ivaRateField) {
            console.log('❌ AUTOCOMPLETE: No se pudieron encontrar campos después de retries');
            console.log('🔍 AUTOCOMPLETE: Buscando todos los campos con prefix:', prefix);
            // Debug: mostrar todos los campos disponibles
            const allFields = document.querySelectorAll(`[name^="${prefix}-"]`);
            allFields.forEach(field => {
                console.log('  - Campo disponible:', field.name, field.type);
            });
            return;
        }
        
        // Completar campos automáticamente
        if (descriptionField && productData.description) {
            descriptionField.value = productData.description;
        }

        if (unitPriceField && productData.sale_price) {
            unitPriceField.value = productData.sale_price;
            
            // FORZAR ACTUALIZACIÓN VISUAL
            unitPriceField.focus();
            unitPriceField.blur();
            
            unitPriceField.dispatchEvent(new Event('input', { bubbles: true }));
            unitPriceField.dispatchEvent(new Event('change', { bubbles: true }));
        }

        if (ivaRateField && productData.iva_rate !== undefined) {
            ivaRateField.value = productData.iva_rate;
            
            // FORZAR ACTUALIZACIÓN VISUAL
            ivaRateField.focus();
            ivaRateField.blur();
            
            ivaRateField.dispatchEvent(new Event('input', { bubbles: true }));
            ivaRateField.dispatchEvent(new Event('change', { bubbles: true }));
        }

        // DISPARAR EVENTO PERSONALIZADO PARA STOCK UPDATER
        const productSelectedEvent = new CustomEvent('productSelected', {
            bubbles: true,
            detail: {
                productId: productId,
                productData: productData,
                fieldName: productField.name,
                fieldElement: productField
            }
        });
        document.dispatchEvent(productSelectedEvent);
    }
    
    // FUNCIÓN REUTILIZABLE: Configurar un widget individual (inicial o dinámico)
    function setupSingleWidget(widget) {
        // DETECTAR SI ES FILA 4+ PARA FORZAR RECONFIGURACIÓN
        const widgetPrefix = widget.name.replace('-product', '');
        const widgetRowNumber = parseInt(widgetPrefix.split('-')[1]) + 1;
        const isDynamicRow = widgetRowNumber >= 4;
        
        // Para filas 4+, FORZAR reconfiguración incluso si ya está marcado
        if (isDynamicRow) {
            widget.removeAttribute('data-autocomplete-configured');
        }
        
        // Evitar duplicar listeners si ya está configurado (excepto filas 4+)
        if (widget.hasAttribute('data-autocomplete-configured')) {
            return;
        }
        widget.setAttribute('data-autocomplete-configured', 'true');
        
        // Escuchar cambios en el SELECT
        widget.addEventListener('change', function() {
            setTimeout(() => handleProductSelection(widget), 200);
        });
        
        // Para Select2 (Django autocomplete usa Select2)
        if (widget.classList.contains('select2-hidden-accessible')) {
            let retryCount = 0;
            const maxRetries = 10;
            
            const findAndConfigureSelect2 = () => {
                const select2Container = widget.nextElementSibling;
                
                if (select2Container && select2Container.classList.contains('select2-container')) {
                    // Escuchar clics en el resultado de Select2
                    select2Container.addEventListener('click', function() {
                        setTimeout(() => {
                            if (widget.value) {
                                handleProductSelection(widget);
                            }
                        }, 300);
                    });
                    
                    // Backup observer con debounce
                    let observerTimeout = null;
                    const observer = new MutationObserver(function(mutations) {
                        if (observerTimeout) return;
                        
                        mutations.forEach(function(mutation) {
                            if (mutation.type === 'childList' || mutation.type === 'attributes') {
                                if (widget.value && !observerTimeout) {
                                    observerTimeout = setTimeout(() => {
                                        handleProductSelection(widget);
                                        observerTimeout = null;
                                    }, 400);
                                }
                            }
                        });
                    });
                    
                    observer.observe(select2Container, { 
                        childList: true, 
                        subtree: true, 
                        attributes: true 
                    });
                    
                } else if (retryCount < maxRetries) {
                    retryCount++;
                    setTimeout(findAndConfigureSelect2, 100 * retryCount);
                }
            };
            
            setTimeout(findAndConfigureSelect2, 100);
        }
    }
    
    // Configurar listeners para widgets de autocompletado
    function setupAutocompletedWidgets() {
        const productWidgets = document.querySelectorAll('select[name*="product"].admin-autocomplete');
        
        productWidgets.forEach(function(widget, index) {
            setupSingleWidget(widget);
        });
    }
    
    // Observer mejorado para detectar nuevos widgets
    function setupMutationObserver() {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1) {
                            // Find new widgets in added nodes
                            let newWidgets = [];
                            if (node.querySelectorAll) {
                                newWidgets = Array.from(node.querySelectorAll('select[name*="product"]'));
                            }
                            
                            // Check if node is a product select
                            if (node.tagName === 'SELECT' && node.name && node.name.includes('product')) {
                                newWidgets.push(node);
                            }
                            
                            // Fallback: search all unconfigured widgets
                            if (newWidgets.length === 0) {
                                const allWidgets = document.querySelectorAll('select[name*="product"]:not([data-autocomplete-configured])');
                                newWidgets = Array.from(allWidgets);
                            }
                            
                            // Configurar widgets encontrados
                            newWidgets.forEach(function(widget) {
                                setupSingleWidget(widget);
                                
                                // Segundo intento con delay por seguridad
                                setTimeout(() => {
                                    if (!widget.hasAttribute('data-autocomplete-configured')) {
                                        setupSingleWidget(widget);
                                    }
                                }, 500);
                            });
                            
                            // Aplicar estilos si se encontraron widgets
                            if (newWidgets.length > 0) {
                                setTimeout(() => {
                                    forceFieldWidths();
                                }, 300);
                            }
                        }
                    });
                }
            });
        });
        
        observer.observe(document.body, { 
            childList: true, 
            subtree: true,
            attributes: false
        });
    }
    
    // Función adicional de verificación periódica
    function setupPeriodicCheck() {
        setInterval(() => {
            const unconfiguredWidgets = document.querySelectorAll('select[name*="product"]:not([data-autocomplete-configured])');
            
            if (unconfiguredWidgets.length > 0) {
                unconfiguredWidgets.forEach(widget => {
                    setupSingleWidget(widget);
                });
            }
        }, 2000);
    }
    
    // Inicialización
    function init() {
        loadProductsData();
        
        // Delay para asegurar que los widgets estén completamente cargados
        setTimeout(function() {
            setupAutocompletedWidgets();
            setupMutationObserver();
        }, 1000);
    }
    
    // Función de prueba para testing
    window.testAutoComplete = function(productId) {
        const firstProductField = document.querySelector('select[name="lines-0-product"]');
        if (firstProductField) {
            let option = firstProductField.querySelector(`option[value="${productId}"]`);
            if (!option) {
                option = document.createElement('option');
                option.value = productId;
                option.textContent = `Producto ${productId}`;
                option.selected = true;
                firstProductField.appendChild(option);
            }
            
            firstProductField.value = productId;
            firstProductField.dispatchEvent(new Event('change', { bubbles: true }));
            handleProductSelection(firstProductField);
        }
    };
    
    // FUNCIÓN BÁSICA PARA ANCHOS DE CAMPO
    function forceFieldWidths() {
        const productFields = document.querySelectorAll('.field-product');
        productFields.forEach((field) => {
            field.style.width = '35%';
        });
    }
    
    // ==========================================
    // INTERCEPTACIÓN DE FILAS DINÁMICAS
    // ==========================================
    
    // Función simple para interceptar nuevas filas (estado inicial limpio)
    function handleDynamicRowAddition() {
        console.log('� Sistema básico de interceptación configurado');
    }
    
    function detectSelect2Events() {
        console.log('📡 Sistema básico Select2 configurado');
    }
    
    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            init();
            handleDynamicRowAddition();
            detectSelect2Events();
            setupPeriodicCheck();  // Verificación periódica adicional
            // Forzar anchos después de la inicialización
            setTimeout(forceFieldWidths, 2000);
        });
    } else {
        init();
        handleDynamicRowAddition();
        detectSelect2Events();
        setupPeriodicCheck();  // Verificación periódica adicional
        // Forzar anchos inmediatamente si ya está cargado
        setTimeout(forceFieldWidths, 2000);
    }
    
    // Exponer funciones para uso manual y debug
    window.forceFieldWidths = forceFieldWidths;
    
    // Función de debug global
    window.debugAutocomplete = function() {
        console.log('🔍 DEBUG AUTOCOMPLETE STATUS:');
        
        const allProductSelects = document.querySelectorAll('select[name*="product"]');
        console.log(`📊 Total select productos encontrados: ${allProductSelects.length}`);
        
        allProductSelects.forEach((select, index) => {
            const isConfigured = select.hasAttribute('data-autocomplete-configured');
            const hasAdminClass = select.classList.contains('admin-autocomplete');
            const hasSelect2 = select.classList.contains('select2-hidden-accessible');
            
            console.log(`  ${index + 1}. ${select.name || 'sin nombre'}`);
            console.log(`     - Configurado: ${isConfigured ? '✅' : '❌'}`);
            console.log(`     - Admin autocomplete: ${hasAdminClass ? '✅' : '❌'}`);
            console.log(`     - Select2: ${hasSelect2 ? '✅' : '❌'}`);
            console.log(`     - Valor: "${select.value}"`);
            
            if (!isConfigured) {
                console.log(`     🔄 Configurando ahora...`);
                setupSingleWidget(select);
            }
        });
        
        console.log('✅ Debug completado');
    };
    
    // Chequeo periódico reducido
    setInterval(() => {
        const formRows = document.querySelectorAll('.form-row:not(.add-row)');
        if (formRows.length > 0) {
            forceFieldWidths();
        }
    }, 10000); // Cada 10 segundos en lugar de 3
    
})();