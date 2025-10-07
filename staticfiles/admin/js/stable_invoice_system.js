/**
 * Sistema optimizado para evitar reajustes visuales en líneas de factura
 * Versión estable que previene "saltos" de campos
 */

(function() {
    'use strict';
    
    let isInitialized = false;
    let layoutStabilized = false;
    
    console.log('🚀 SISTEMA ESTABLE: Iniciando prevención de reajustes...');
    
    // No aplicar estilos de layout - usar Django Admin por defecto
    function stabilizeLayout() {
        if (layoutStabilized) return;
        
        console.log('🔧 ESTABILIZAR: Sin modificaciones de layout');
        layoutStabilized = true;
        console.log('✅ ESTABILIZAR: Usando estilos nativos de Django');
    }
    
    // Inicialización optimizada de calculadora
    function initCalculatorStable() {
        if (isInitialized) return;
        
        console.log('🧮 CALCULADORA ESTABLE: Inicializando...');
        
        function calcularTotalEstable(fila) {
            const inputs = fila.querySelectorAll('input');
            let cantidad = 0, precio = 0, descuento = 0, iva = 15, totalField = null;
            
            inputs.forEach(input => {
                const name = input.name;
                if (name.includes('quantity')) {
                    cantidad = parseFloat(input.value) || 0;
                } else if (name.includes('unit_price')) {
                    precio = parseFloat(input.value) || 0;
                } else if (name.includes('discount')) {
                    descuento = parseFloat(input.value) || 0;
                } else if (name.includes('iva_rate')) {
                    iva = parseFloat(input.value) || 15;
                } else if (name.includes('line_total')) {
                    totalField = input;
                }
            });
            
            if (totalField && (cantidad || precio)) {
                const subtotal = cantidad * precio;
                const conDescuento = subtotal * (1 - descuento / 100);
                const conIva = conDescuento * (1 + iva / 100);
                const total = conIva.toFixed(2);
                
                // Actualizar sin causar reflow
                if (totalField.value !== total) {
                    totalField.removeAttribute('readonly');
                    totalField.value = total;
                    totalField.setAttribute('readonly', 'readonly');
                }
            }
        }
        
        function attachCalculatorEvents() {
            const filas = document.querySelectorAll('.dynamic-invoiceline_set-group .form-row:not(.add-row)');
            
            filas.forEach(fila => {
                const camposCalcular = fila.querySelectorAll('input[name*="quantity"], input[name*="unit_price"], input[name*="discount"], input[name*="iva_rate"]');
                
                camposCalcular.forEach(campo => {
                    // Solo agregar eventos si no los tiene ya
                    if (!campo.hasAttribute('data-calculator-attached')) {
                        campo.setAttribute('data-calculator-attached', 'true');
                        
                        ['input', 'change'].forEach(evento => {
                            campo.addEventListener(evento, () => {
                                // Usar requestAnimationFrame para evitar reflows múltiples
                                requestAnimationFrame(() => {
                                    calcularTotalEstable(fila);
                                });
                            }, { passive: true });
                        });
                    }
                });
                
                // Cálculo inicial
                calcularTotalEstable(fila);
            });
        }
        
        attachCalculatorEvents();
        isInitialized = true;
        console.log('✅ CALCULADORA ESTABLE: Lista');
    }
    
    // Inicialización de autocompletado estable
    function initAutocompleteStable() {
        console.log('🔍 AUTOCOMPLETADO ESTABLE: Verificando...');
        
        // Solo si tenemos datos de productos
        if (typeof window.productsData === 'object' && window.productsData) {
            const productSelects = document.querySelectorAll('select[name*="product"]');
            
            productSelects.forEach(select => {
                if (!select.hasAttribute('data-autocomplete-stable')) {
                    select.setAttribute('data-autocomplete-stable', 'true');
                    
                    // Evento de cambio optimizado
                    select.addEventListener('change', function() {
                        const productId = this.value;
                        const productData = window.productsData[productId];
                        
                        if (productData) {
                            const row = this.closest('.form-row');
                            if (row) {
                                // Llenar campos sin causar layout shifts
                                requestAnimationFrame(() => {
                                    const priceField = row.querySelector('input[name*="unit_price"]');
                                    const ivaField = row.querySelector('input[name*="iva_rate"]');
                                    const stockField = row.querySelector('input[name*="stock"]');
                                    
                                    if (priceField && !priceField.value) {
                                        priceField.value = productData.price;
                                    }
                                    if (ivaField && !ivaField.value) {
                                        ivaField.value = productData.iva_rate;
                                    }
                                    if (stockField) {
                                        stockField.value = productData.current_stock || 0;
                                    }
                                    
                                    // Recalcular
                                    initCalculatorStable();
                                });
                            }
                        }
                    }, { passive: true });
                }
            });
            
            console.log('✅ AUTOCOMPLETADO ESTABLE: Configurado');
        }
    }
    
    // Función principal de inicialización
    function initializeStableSystem() {
        console.log('🎯 SISTEMA ESTABLE: Inicialización completa...');
        
        // 1. Estabilizar layout primero
        stabilizeLayout();
        
        // 2. Esperar a que el DOM esté completamente cargado
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(() => {
                    initCalculatorStable();
                    initAutocompleteStable();
                }, 50); // Mínimo delay necesario
            });
        } else {
            // DOM ya cargado
            setTimeout(() => {
                initCalculatorStable();
                initAutocompleteStable();
            }, 50);
        }
        
        console.log('✅ SISTEMA ESTABLE: Configuración completa');
    }
    
    // Detectar cuando se añaden nuevas filas dinámicamente
    function observeDynamicChanges() {
        const targetNode = document.querySelector('.dynamic-invoiceline_set-group');
        
        if (targetNode) {
            const observer = new MutationObserver(function(mutations) {
                let shouldReinit = false;
                
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                        // Nueva fila añadida
                        shouldReinit = true;
                    }
                });
                
                if (shouldReinit) {
                    // Reinicializar solo los nuevos elementos
                    setTimeout(() => {
                        initCalculatorStable();
                        initAutocompleteStable();
                    }, 100);
                }
            });
            
            observer.observe(targetNode, {
                childList: true,
                subtree: true
            });
            
            console.log('👁️ OBSERVADOR: Vigilando cambios dinámicos');
        }
    }
    
    // Iniciar todo el sistema
    stabilizeLayout(); // Inmediato
    initializeStableSystem(); // Con delays apropiados
    observeDynamicChanges(); // Observador para cambios
    
    console.log('🎉 SISTEMA ESTABLE: Completamente inicializado');
    
})();