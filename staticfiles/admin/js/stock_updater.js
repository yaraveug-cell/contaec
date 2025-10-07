/**
 * Actualizador automático de stock para líneas de factura
 * Compatible con Select2 y eventos nativos
 */
(function() {
    'use strict';
    
    let productsData = {};
    
    // Cargar datos de productos
    function loadProductsData() {
        // Intentar múltiples fuentes
        const dataScript = document.getElementById('products-data');
        if (dataScript) {
            try {
                productsData = JSON.parse(dataScript.textContent);
                return;
            } catch (e) {
                console.error('❌ STOCK UPDATER: Error parseando DOM script:', e);
            }
        }
        
        if (typeof window.productsData !== 'undefined') {
            productsData = window.productsData;
            return;
        }
    }
    
    // Encontrar el campo de stock correspondiente
    function findStockField(productField) {
        
        const prefix = productField.name.replace('-product', '');
        const stockFieldName = prefix + '-stock';
        
        console.log(`   - Prefix: ${prefix}`);
        console.log(`   - Buscando campo: ${stockFieldName}`);
        
        // Buscar por nombre exacto
        let stockField = document.querySelector(`[name="${stockFieldName}"]`);
        
        if (!stockField) {
            // Buscar en la misma fila
            const row = productField.closest('tr') || productField.closest('.inline-related');
            if (row) {
                stockField = row.querySelector('input[name*="stock"]');
            }
        }
        
        if (!stockField) {
            // Buscar por índice de inline
            const match = productField.name.match(/lines-(\d+)-product/);
            if (match) {
                const index = match[1];
                stockField = document.querySelector(`[name="lines-${index}-stock"]`);
            }
        }
        
        if (stockField) {
            console.log(`   ✅ Campo stock encontrado: ${stockField.name}`);
        } else {
            console.log(`   ❌ Campo stock NO encontrado`);
        }
        
        return stockField;
    }
    
    // Actualizar campo de stock
    function updateStockField(productSelect) {
        console.log('🔄 STOCK UPDATER: updateStockField llamado para:', productSelect.name);
        console.log('🔍 STOCK UPDATER: Elemento recibido:', productSelect);
        console.log('🔍 STOCK UPDATER: Tipo de elemento:', typeof productSelect);
        
        const productId = productSelect.value;
        console.log(`   - Product ID: ${productId}`);
        
        if (!productId) {
            console.log('   ⚠️ No hay producto seleccionado');
            return;
        }
        
        const stockField = findStockField(productSelect);
        if (!stockField) {
            console.log('   ❌ Campo stock no encontrado, abortando');
            return;
        }
        
        // Verificar si tenemos datos del producto
        if (!productsData[productId]) {
            console.log('   📡 Producto no en cache, solicitando via AJAX...');
            
            // Hacer petición AJAX para obtener el stock
            fetch(`/admin/inventory/product/${productId}/stock/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('   ✅ Stock recibido via AJAX:', data.stock);
                    stockField.value = data.stock || '0';
                    stockField.dispatchEvent(new Event('input', { bubbles: true }));
                    stockField.dispatchEvent(new Event('change', { bubbles: true }));
                })
                .catch(error => {
                    console.error('   ❌ Error AJAX:', error);
                    console.log('   🔄 Asignando stock = 0 por error');
                    stockField.value = '0';
                });
        } else {
            // Usar datos en cache
            const stock = productsData[productId].current_stock || '0';
            console.log(`   ✅ Stock desde cache: ${stock}`);
            stockField.value = stock;
            stockField.dispatchEvent(new Event('input', { bubbles: true }));
            stockField.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
    
    function initStockUpdater() {
        console.log('🔧 STOCK UPDATER: Iniciando configuración...');
        
        // Esperamos un poco para que Select2 se inicialice completamente
        setTimeout(() => {
            // Encontrar todos los selects de producto
            const productSelects = document.querySelectorAll('select[name*="product"]');
            console.log(`🔍 STOCK UPDATER: Selects de producto encontrados: ${productSelects.length}`);
            
            productSelects.forEach((select, index) => {
                console.log(`🔄 STOCK UPDATER: Procesando select ${index + 1}:`, select);
                console.log(`   - name: "${select.name}"`);
                console.log(`   - value: "${select.value}"`);
                console.log(`   - classes: "${select.className}"`);
                console.log(`   - ya configurado: ${select.hasAttribute('data-stock-updater-attached')}`);
                
                if (!select.hasAttribute('data-stock-updater-attached')) {
                    select.setAttribute('data-stock-updater-attached', 'true');
                    console.log(`   ✅ STOCK UPDATER: Marcado como configurado`);
                    
                    // EVENTOS NATIVOS
                    select.addEventListener('change', function() {
                        console.log(`🔄 STOCK UPDATER: Evento change nativo en: ${this.name} = ${this.value}`);
                        updateStockField(this);
                    });
                    
                    // EVENTOS SELECT2 - Usar jQuery window global y detección mejorada
                    if (typeof window.$ !== 'undefined' || typeof window.jQuery !== 'undefined') {
                        const jq = window.$ || window.jQuery;
                        
                        if (jq && typeof jq.fn.select2 !== 'undefined') {
                            const $select = jq(select);
                            
                            // Verificar si ya es Select2
                            if ($select.hasClass('select2-hidden-accessible') || select.classList.contains('select2-hidden-accessible')) {
                                console.log(`   🎯 STOCK UPDATER: Select2 detectado para: ${select.name}`);
                                
                // Evento principal Select2
                $select.on('select2:select', function(e) {
                    const selectedData = e.params.data;
                    console.log(`🔄 STOCK UPDATER: select2:select disparado en: ${this.name}`);
                    console.log(`   - ID seleccionado: ${selectedData.id}`);
                    console.log(`   - Texto: ${selectedData.text}`);
                    console.log(`   🎯 LLAMANDO updateStockField...`);
                    updateStockField(this);
                });
                
                // Evento de cambio en Select2
                $select.on('change', function() {
                    console.log(`🔄 STOCK UPDATER: Select2 change disparado en: ${this.name} = ${this.value}`);
                    console.log(`   🎯 LLAMANDO updateStockField...`);
                    updateStockField(this);
                });                                // Evento cuando se limpia la selección
                                $select.on('select2:unselecting', function(e) {
                                    console.log(`🔄 STOCK UPDATER: select2:unselecting disparado en: ${this.name}`);
                                    setTimeout(() => {
                                        const stockField = findStockField(this);
                                        if (stockField) {
                                            stockField.value = '0';
                                            console.log(`   📦 Stock establecido a 0 por limpieza`);
                                        }
                                    }, 50);
                                });
                                
                                console.log(`   🔗 STOCK UPDATER: Eventos Select2 (jQuery) configurados para: ${select.name}`);
                            } else {
                                console.log(`   ⚠️ STOCK UPDATER: Select no es Select2 aún, solo eventos nativos`);
                            }
                        } else {
                            console.log(`   ⚠️ STOCK UPDATER: Select2 no disponible, solo eventos nativos`);
                        }
                    } else {
                        console.log(`   ⚠️ STOCK UPDATER: jQuery no disponible, solo eventos nativos`);
                    }
                    
                    // Si ya tiene un valor seleccionado, actualizar stock inmediatamente
                    if (select.value) {
                        console.log(`   🚀 STOCK UPDATER: Actualizando stock inmediatamente para valor: ${select.value}`);
                        updateStockField(select);
                    } else {
                        console.log(`   ⏳ No hay valor seleccionado, esperando...`);
                    }
                } else {
                    console.log(`   ⏭️ Select ya estaba configurado, saltando...`);
                }
            });
            
            console.log(`✅ STOCK UPDATER: Stock updater configurado para ${productSelects.length} selects`);
            
            // Debug adicional: verificar estructura DOM
            const invoiceLineGroup = document.querySelector('.dynamic-invoiceline_set-group');
            console.log('🔍 STOCK UPDATER: Grupo de líneas de factura:', invoiceLineGroup);
            
            if (invoiceLineGroup) {
                const formRows = invoiceLineGroup.querySelectorAll('.form-row');
                console.log(`📋 STOCK UPDATER: Filas de formulario encontradas: ${formRows.length}`);
                
                formRows.forEach((row, i) => {
                    const productSelect = row.querySelector('select[name*="product"]');
                    const stockInput = row.querySelector('input[name*="stock"]');
                    console.log(`   Fila ${i}: producto=${!!productSelect}, stock=${!!stockInput}`);
                });
            }
        }, 2000); // Delay más largo para que Select2 se inicialice completamente
    }
    
    // Observador para elementos dinámicos
    function observeNewRows() {
        console.log('👁️ STOCK UPDATER: Configurando observador...');
        const targetNode = document.querySelector('.dynamic-invoiceline_set-group');
        
        if (targetNode) {
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                        console.log('🆕 STOCK UPDATER: Nuevas filas detectadas, reinicializando...');
                        // Reinicializar cuando se añadan nuevas filas
                        setTimeout(initStockUpdater, 200);
                    }
                });
            });
            
            observer.observe(targetNode, { childList: true, subtree: true });
            console.log('👁️ STOCK UPDATER: Observer configurado para nuevas filas');
        }
    }
    
    // Inicialización
    function init() {
        console.log('🚀 STOCK UPDATER: Comenzando inicialización...');
        console.log('📄 Document ready state:', document.readyState);
        
        loadProductsData();
        
        if (document.readyState === 'loading') {
            console.log('⏳ Documento cargando, esperando DOMContentLoaded...');
            document.addEventListener('DOMContentLoaded', () => {
                console.log('✅ DOMContentLoaded disparado');
                setTimeout(() => {
                    console.log('⏰ Timeout ejecutado, iniciando stock updater...');
                    initStockUpdater();
                    observeNewRows();
                }, 1000); // Delay más largo para asegurar que todo esté cargado
            });
        } else {
            console.log('✅ Documento ya cargado, iniciando inmediatamente...');
            setTimeout(() => {
                console.log('⏰ Timeout ejecutado, iniciando stock updater...');
                initStockUpdater();
                observeNewRows();
            }, 1000);
        }
    }
    
    // ======= INTEGRACIÓN CON AUTOCOMPLETE =======
    
    // Escuchar eventos de selección desde el invoice_line_autocomplete.js
    document.addEventListener('productSelected', function(e) {
        console.log('🎯 STOCK UPDATER: Evento productSelected recibido:', e.detail);
        const { productId, fieldName, fieldElement } = e.detail;
        
        if (fieldElement && fieldElement.value === productId) {
            console.log(`🔄 STOCK UPDATER: Procesando selección desde evento custom: ${fieldName} = ${productId}`);
            updateStockField(fieldElement);
        } else {
            console.log('⚠️ STOCK UPDATER: Field element no válido o ID no coincide');
        }
    });
    
    // Ejecutar inicialización
    init();
    
    // También ejecutar después de que otros scripts se carguen
    setTimeout(init, 2000);
    
    // Función global para prueba manual
    window.manualUpdateStock = function(productSelect) {
        console.log('🔧 MANUAL: Actualizando stock manualmente...');
        if (typeof productSelect === 'string') {
            productSelect = document.querySelector(`select[name="${productSelect}"]`);
        }
        
        if (productSelect) {
            console.log('🔧 MANUAL: Select encontrado:', productSelect.name);
            updateStockField(productSelect);
        } else {
            console.log('❌ MANUAL: Select no encontrado');
        }
    };
    
    // Función para forzar actualización de todos los stocks
    window.updateAllStocks = function() {
        console.log('🔧 MANUAL: Actualizando todos los stocks...');
        const productSelects = document.querySelectorAll('select[name*="product"]');
        productSelects.forEach(select => {
            if (select.value) {
                console.log(`🔧 MANUAL: Actualizando stock para: ${select.name} = ${select.value}`);
                updateStockField(select);
            }
        });
    };
    
    // Función para probar directamente el evento personalizado
    window.testProductSelectedEvent = function(productId = '21', fieldName = 'lines-0-product') {
        console.log('🧪 TEST: Disparando evento productSelected manualmente...');
        const productField = document.querySelector(`[name="${fieldName}"]`);
        if (productField) {
            productField.value = productId;
            
            const event = new CustomEvent('productSelected', {
                bubbles: true,
                detail: {
                    productId: productId,
                    productData: window.productsData ? window.productsData[productId] : null,
                    fieldName: fieldName,
                    fieldElement: productField
                }
            });
            document.dispatchEvent(event);
            console.log('✅ TEST: Evento disparado');
        } else {
            console.log('❌ TEST: Campo no encontrado:', fieldName);
        }
    };
    
})();