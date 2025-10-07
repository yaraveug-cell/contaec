/**
 * Sistema Inteligente de Validación de Stock para Facturas
 * 
 * Funcionalidades:
 * 1. Validación en tiempo real mientras se edita
 * 2. Niveles de advertencia (Error, Warning, Info, Success)
 * 3. Mensajes nativos de Django Admin
 * 4. Bloqueo inteligente del botón de guardar
 * 5. Integración con el sistema de autocompletado
 */

(function() {
    'use strict';
    
    // Sistema Inteligente de Validación de Stock inicializado
    
    // ======= CONFIGURACIÓN =======
    const CONFIG = {
        CHECK_INTERVAL: 1000, // ms
        DEBOUNCE_DELAY: 500, // ms
        WARNING_LEVELS: {
            CRITICAL_STOCK: 5,
            LOW_STOCK: 10,
            HIGH_USAGE_PERCENT: 80
        },
        MESSAGES: {
            INSUFFICIENT: 'STOCK INSUFICIENTE',
            CRITICAL: 'STOCK CRÍTICO', 
            LOW: 'STOCK BAJO',
            HIGH_USAGE: 'ALTO CONSUMO',
            SUFFICIENT: 'Stock suficiente',
            ERROR: 'Error verificando stock'
        }
    };
    
    // ======= VARIABLES GLOBALES =======
    let validationTimer = null;
    let productsData = {};
    let formElement = null;
    let saveButtons = [];
    let validationMessages = new Map(); // Almacenar mensajes por línea
    let lastValidationResults = new Map(); // Cache de últimas validaciones
    let shownMessages = new Set(); // Prevenir spam de mensajes idénticos
    let messageThrottle = new Map(); // Throttle por tipo de mensaje
    
    // ======= FUNCIONES DE UTILIDAD =======
    
    /**
     * Verificar si estamos en modo edición de factura
     * Las validaciones de stock NO deben funcionar en modo edición
     */
    function isEditMode() {
        const currentPath = window.location.pathname;
        const isEdit = currentPath.includes('/change/');
        
        console.log('🔍 STOCK VALIDATOR: Verificando modo edición...');
        console.log(`   📄 URL actual: ${currentPath}`);
        console.log(`   ✏️ Modo edición: ${isEdit ? 'SÍ' : 'NO'}`);
        
        return isEdit;
    }
    
    /**
     * Verificar si estamos en formulario de nueva factura
     */
    function isNewInvoiceForm() {
        const currentPath = window.location.pathname;
        const isNewInvoice = currentPath.includes('/invoice/add/');
        
        console.log('🆕 STOCK VALIDATOR: Verificando nueva factura...');
        console.log(`   📄 URL actual: ${currentPath}`);
        console.log(`   ➕ Nueva factura: ${isNewInvoice ? 'SÍ' : 'NO'}`);
        
        return isNewInvoice;
    }
    
    /**
     * Obtener datos de productos disponibles
     */
    function loadProductsData() {
        console.log('📦 STOCK VALIDATOR: Cargando datos de productos...');
        
        // Intentar obtener desde window.productsData
        if (window.productsData) {
            productsData = window.productsData;
            console.log(`✅ STOCK VALIDATOR: ${Object.keys(productsData).length} productos cargados desde window`);
            return true;
        }
        
        // Intentar obtener desde script en DOM
        const scriptElement = document.querySelector('script[data-products-data]');
        if (scriptElement) {
            try {
                const rawData = scriptElement.textContent;
                productsData = JSON.parse(rawData);
                console.log(`✅ STOCK VALIDATOR: ${Object.keys(productsData).length} productos cargados desde DOM`);
                return true;
            } catch (e) {
                console.log('❌ STOCK VALIDATOR: Error parseando datos de productos:', e);
            }
        }
        
        console.log('⚠️ STOCK VALIDATOR: No se encontraron datos de productos');
        return false;
    }
    
    /**
     * Verificar stock de un producto específico
     */
    function checkProductStock(productId, quantity) {
        if (!productsData[productId] || !quantity || quantity <= 0) {
            return null;
        }
        
        const product = productsData[productId];
        const availableStock = parseFloat(product.current_stock || 0);
        const requestedQuantity = parseFloat(quantity);
        const shortage = Math.max(0, requestedQuantity - availableStock);
        const hasSufficientStock = availableStock >= requestedQuantity;
        
        // Determinar nivel y mensaje
        if (!hasSufficientStock) {
            return {
                hasSufficientStock: false,
                level: 'error',
                icon: CONFIG.MESSAGES.INSUFFICIENT,
                message: `${product.name} - Solicitado: ${requestedQuantity}, Disponible: ${availableStock}, Faltante: ${shortage}`,
                availableStock,
                requestedQuantity,
                shortage,
                productName: product.name
            };
        } else if (availableStock <= CONFIG.WARNING_LEVELS.CRITICAL_STOCK) {
            return {
                hasSufficientStock: true,
                level: 'warning',
                icon: CONFIG.MESSAGES.CRITICAL,
                message: `${product.name} - Solo quedan ${availableStock} unidades. Considere reabastecer urgentemente.`,
                availableStock,
                requestedQuantity,
                shortage: 0,
                productName: product.name
            };
        } else if (availableStock <= CONFIG.WARNING_LEVELS.LOW_STOCK) {
            return {
                hasSufficientStock: true,
                level: 'warning',
                icon: CONFIG.MESSAGES.LOW,
                message: `${product.name} - Quedan ${availableStock} unidades. Planifique reabastecimiento.`,
                availableStock,
                requestedQuantity,
                shortage: 0,
                productName: product.name
            };
        } else if (requestedQuantity > (availableStock * (CONFIG.WARNING_LEVELS.HIGH_USAGE_PERCENT / 100))) {
            const percentage = Math.round((requestedQuantity / availableStock) * 100);
            return {
                hasSufficientStock: true,
                level: 'info',
                icon: CONFIG.MESSAGES.HIGH_USAGE,
                message: `${product.name} - Utilizando ${percentage}% del stock disponible (${requestedQuantity} de ${availableStock} unidades).`,
                availableStock,
                requestedQuantity,
                shortage: 0,
                productName: product.name
            };
        } else {
            return {
                hasSufficientStock: true,
                level: 'success',
                icon: CONFIG.MESSAGES.SUFFICIENT,
                message: `${product.name} - Disponible: ${availableStock} unidades.`,
                availableStock,
                requestedQuantity,
                shortage: 0,
                productName: product.name
            };
        }
    }
    
    /**
     * Obtener todas las líneas de factura del formulario
     */
    function getInvoiceLines() {
        const lines = [];
        const formRows = document.querySelectorAll('.tabular .form-row:not(.add-row)');
        
        formRows.forEach((row, index) => {
            const productField = row.querySelector('select[name*="-product"]');
            const quantityField = row.querySelector('input[name*="-quantity"]');
            
            if (productField && quantityField) {
                const productId = productField.value;
                const quantity = parseFloat(quantityField.value) || 0;
                
                lines.push({
                    index,
                    row,
                    productField,
                    quantityField,
                    productId,
                    quantity,
                    prefix: productField.name.match(/lines-(\d+)-product/)?.[1] || index
                });
            }
        });
        
        return lines;
    }
    
    /**
     * Mostrar mensaje flotante estilo Django Admin (con throttling)
     */
    function showDjangoStyleMessage(message, level = 'info', duration = 6000) {
        // Crear hash único del mensaje para evitar duplicados
        const messageHash = `${level}:${message}`;
        
        // Verificar throttling - no mostrar mensajes idénticos muy seguidos
        const now = Date.now();
        const lastShown = messageThrottle.get(messageHash);
        if (lastShown && (now - lastShown) < 3000) { // 3 segundos de throttle
            return null;
        }
        messageThrottle.set(messageHash, now);
        // Crear contenedor flotante específico si no existe
        let messagesContainer = document.querySelector('.messagelist.stock-messages');
        if (!messagesContainer) {
            messagesContainer = document.createElement('ul');
            messagesContainer.className = 'messagelist stock-messages';
            messagesContainer.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
                pointer-events: none;
                list-style: none;
                padding: 0;
                margin: 0;
            `;
            
            // Agregar al body para que sea verdaderamente flotante
            document.body.appendChild(messagesContainer);
        }
        
        // Crear elemento de mensaje
        const messageElement = document.createElement('li');
        messageElement.className = `${level} stock-validation-message`;
        messageElement.style.cssText = `
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
            margin-bottom: 10px;
            padding: 12px 15px;
            border-radius: 6px;
            position: relative;
            pointer-events: auto;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            font-size: 14px;
            font-weight: 500;
            max-width: 100%;
            word-wrap: break-word;
        `;
        
        // Aplicar estilos según el nivel con gradientes
        switch(level) {
            case 'error':
                messageElement.style.background = 'linear-gradient(135deg, #f8d7da 0%, #f1aeb5 100%)';
                messageElement.style.color = '#721c24';
                messageElement.style.borderLeft = '4px solid #dc3545';
                break;
            case 'warning':
                messageElement.style.background = 'linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%)';
                messageElement.style.color = '#856404';
                messageElement.style.borderLeft = '4px solid #ffc107';
                break;
            case 'success':
                messageElement.style.background = 'linear-gradient(135deg, #d1e7dd 0%, #a3cfbb 100%)';
                messageElement.style.color = '#0f5132';
                messageElement.style.borderLeft = '4px solid #28a745';
                break;
            default: // info
                messageElement.style.background = 'linear-gradient(135deg, #d1ecf1 0%, #abdde5 100%)';
                messageElement.style.color = '#0c5460';
                messageElement.style.borderLeft = '4px solid #17a2b8';
        }
        
        messageElement.innerHTML = `
            <span class="message-icon" style="display: inline-block; margin-right: 8px; font-size: 16px; vertical-align: middle;">${getIconForLevel(level)}</span>
            <span class="message-text" style="display: inline-block; vertical-align: middle; line-height: 1.4; padding-right: 25px;">${message}</span>
            <button type="button" class="close-message" style="
                position: absolute;
                top: 8px;
                right: 10px;
                background: none;
                border: none;
                font-size: 18px;
                cursor: pointer;
                padding: 0;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0.6;
                transition: opacity 0.2s ease;
            " onclick="this.parentElement.style.transform='translateX(100%)'; this.parentElement.style.opacity='0'; setTimeout(() => this.parentElement.remove(), 300);">×</button>
            <div class="message-progress" style="
                position: absolute;
                bottom: 0;
                left: 0;
                height: 2px;
                width: 100%;
                background: ${getProgressColorForLevel(level)};
                transition: width ${duration}ms linear;
            "></div>
        `;
        
        // Agregar al contenedor
        messagesContainer.appendChild(messageElement);
        
        // Animar entrada deslizando desde la derecha
        requestAnimationFrame(() => {
            messageElement.style.opacity = '1';
            messageElement.style.transform = 'translateX(0)';
        });
        
        // Iniciar animación de la barra de progreso
        const progressBar = messageElement.querySelector('.message-progress');
        if (progressBar) {
            requestAnimationFrame(() => {
                progressBar.style.width = '0%';
            });
        }
        
        // Auto-eliminar después de la duración especificada
        setTimeout(() => {
            messageElement.style.transform = 'translateX(100%)';
            messageElement.style.opacity = '0';
            setTimeout(() => {
                if (messageElement.parentNode) {
                    messageElement.parentNode.removeChild(messageElement);
                }
            }, 300);
        }, duration);
        
        return messageElement;
    }
    
    /**
     * Obtener icono según el nivel del mensaje
     */
    function getIconForLevel(level) {
        const icons = {
            'error': '🚨',
            'warning': '⚠️',
            'info': 'ℹ️',
            'success': '✅'
        };
        return icons[level] || 'ℹ️';
    }
    
    /**
     * Obtener color de la barra de progreso según el nivel
     */
    function getProgressColorForLevel(level) {
        const colors = {
            'error': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'success': '#28a745'
        };
        return colors[level] || '#17a2b8';
    }
    
    /**
     * Limpiar alertas en línea (ahora solo se usan las flotantes)
     */
    function clearInlineAlerts() {
        document.querySelectorAll('.stock-validation-alert').forEach(alert => {
            alert.remove();
        });
    }
    
    /**
     * Mostrar mensaje de validación como notificación flotante
     */
    function showLineValidationMessage(line, validationResult) {
        if (!validationResult) return;
        
        // Limpiar mensajes previos en línea
        const existingAlert = line.row.querySelector('.stock-validation-alert');
        if (existingAlert) {
            existingAlert.remove();
        }
        
        // Mostrar notificaciones flotantes para todos los problemas (ERROR, WARNING, INFO)
        if (['error', 'warning', 'info'].includes(validationResult.level)) {
            showDjangoStyleMessage(
                validationResult.message,
                validationResult.level,
                validationResult.level === 'error' ? 8000 : 6000 // ERROR dura más (8 segundos)
            );
        }
        // SUCCESS = stock suficiente, silencioso (no necesita notificación)
        
        // Guardar referencia en el mapa (sin elemento DOM en línea)
        validationMessages.set(line.prefix, {
            element: null, // No hay elemento en línea ahora
            result: validationResult
        });
    }
    
    /**
     * Actualizar estado de los botones de guardar
     */
    function updateSaveButtonsState() {
        // Verificar si hay errores críticos (stock insuficiente) DINÁMICAMENTE
        const hasErrors = Array.from(validationMessages.values()).some(
            msg => msg.result && msg.result.level === 'error'
        );
        
        const currentState = hasErrors ? 'disabled' : 'enabled';
        
        saveButtons.forEach(button => {
            const wasDisabled = button.disabled;
            
            if (hasErrors) {
                // Deshabilitar cuando no hay stock suficiente
                button.disabled = true;
                button.style.opacity = '0.6';
                button.style.cursor = 'not-allowed';
                button.title = 'No se puede guardar: stock insuficiente';
                
                if (!wasDisabled) {
                    console.log('🔒 STOCK VALIDATOR: Botones deshabilitados (stock insuficiente)');
                }
            } else {
                // Habilitar cuando el stock es suficiente
                button.disabled = false;
                button.style.opacity = '1';
                button.style.cursor = 'pointer';
                button.title = '';
                
                if (wasDisabled) {
                    console.log('🔓 STOCK VALIDATOR: Botones habilitados (stock corregido)');
                }
            }
        });
        
        return currentState;
    }
    
    /**
     * Validar todas las líneas de factura
     */
    function validateAllLines() {
        console.log('🔍 VALIDANDO LÍNEAS (SOLO NOTIFICACIONES FLOTANTES)...');
        
        const lines = getInvoiceLines();
        let currentMessages = [];
        
        lines.forEach(line => {
            if (line.productId && line.quantity > 0) {
                const validationResult = checkProductStock(line.productId, line.quantity);
                
                if (validationResult) {
                    // Solo mostrar notificaciones flotantes, sin bloqueos
                    const lastResult = lastValidationResults.get(line.prefix);
                    const isNewOrChanged = !lastResult || 
                                         lastResult.level !== validationResult.level ||
                                         lastResult.requestedQuantity !== validationResult.requestedQuantity;
                    
                    if (isNewOrChanged) {
                        showLineValidationMessage(line, validationResult);
                        currentMessages.push(validationResult);
                    }
                    
                    lastValidationResults.set(line.prefix, validationResult);
                }
            }
        });
        
        // Actualizar estado de botones (deshabilitar solo si hay ERROR crítico)
        updateSaveButtonsState();
        
        console.log(`📊 VALIDACIÓN COMPLETA: ${currentMessages.length} notificaciones mostradas`);
        
        return {
            totalLines: lines.length,
            messagesShown: currentMessages.length
        };
    }
    
    /**
     * Validar una línea específica inmediatamente (sin debounce)
     */
    function validateLineImmediately(lineElement) {
        const productField = lineElement.querySelector('select[name*="-product"]');
        const quantityField = lineElement.querySelector('input[name*="-quantity"]');
        
        if (!productField || !quantityField) return;
        
        const productId = productField.value;
        const quantity = parseFloat(quantityField.value) || 0;
        const linePrefix = productField.name.replace('-product', '');
        
        if (productId && quantity > 0) {
            const validationResult = checkProductStock(productId, quantity);
            
            if (validationResult) {
                // Actualizar el mapa de validaciones
                validationMessages.set(linePrefix, {
                    element: null,
                    result: validationResult
                });
                
                console.log(`⚡ Validación inmediata línea ${linePrefix}: ${validationResult.level}`);
            } else {
                // Limpiar validación si no hay resultado
                validationMessages.delete(linePrefix);
            }
        } else {
            // Limpiar validación si no hay datos válidos
            validationMessages.delete(linePrefix);
        }
        
        // Actualizar botones inmediatamente
        updateSaveButtonsState();
    }
    
    /**
     * Configurar observadores de eventos para validación en tiempo real
     */
    function setupEventListeners() {
        console.log('🔧 STOCK VALIDATOR: Configurando event listeners...');
        
        // Debounce para evitar validaciones excesivas
        let debounceTimer = null;
        
        function debouncedValidation() {
            if (debounceTimer) {
                clearTimeout(debounceTimer);
            }
            debounceTimer = setTimeout(validateAllLines, CONFIG.DEBOUNCE_DELAY);
        }
        
        // Escuchar cambios en productos y cantidades
        document.addEventListener('change', function(e) {
            if (e.target.matches('select[name*="-product"]')) {
                console.log('📝 STOCK VALIDATOR: Producto cambiado, revalidando...');
                // Limpiar validaciones anteriores del producto que cambió
                const linePrefix = e.target.name.replace('-product', '');
                validationMessages.delete(linePrefix);
                lastValidationResults.delete(linePrefix);
                
                // Validación inmediata de la línea
                const lineElement = e.target.closest('.inline-related, tr');
                if (lineElement) {
                    validateLineImmediately(lineElement);
                }
                
                debouncedValidation();
            } else if (e.target.matches('input[name*="-quantity"]')) {
                console.log('📝 STOCK VALIDATOR: Cantidad cambiada, validación completa...');
                
                // Validación inmediata de la línea
                const lineElement = e.target.closest('.inline-related, tr');
                if (lineElement) {
                    validateLineImmediately(lineElement);
                }
                
                debouncedValidation();
            }
        });
        
        // Escuchar eventos de input para validación MÁS rápida en cantidad
        document.addEventListener('input', function(e) {
            if (e.target.matches('input[name*="-quantity"]')) {
                // Validación inmediata de la línea específica
                const lineElement = e.target.closest('.inline-related, tr');
                if (lineElement) {
                    validateLineImmediately(lineElement);
                }
                
                // Validación completa con debounce (para notificaciones)
                debouncedValidation();
            }
        });
        
        // Escuchar eventos personalizados del autocompletado
        document.addEventListener('productSelected', function(e) {
            console.log('🎯 STOCK VALIDATOR: Producto seleccionado via evento custom');
            setTimeout(debouncedValidation, 100);
        });
        
        // Evento submit eliminado - Solo notificaciones flotantes, sin bloqueos invasivos
        // El backend ya maneja la validación crítica (ERROR)
        // WARNING/INFO/SUCCESS permiten guardado normal con notificaciones flotantes
    }
    
    /**
     * Encontrar botones de guardar en la página
     */
    function findSaveButtons() {
        const selectors = [
            'input[name="_save"]',
            'input[name="_continue"]',
            'input[name="_addanother"]',
            '.submit-row input[type="submit"]',
            'button[type="submit"]'
        ];
        
        saveButtons = [];
        selectors.forEach(selector => {
            const buttons = document.querySelectorAll(selector);
            buttons.forEach(button => {
                if (!saveButtons.includes(button)) {
                    saveButtons.push(button);
                }
            });
        });
        
        console.log(`🎯 STOCK VALIDATOR: ${saveButtons.length} botones de guardar encontrados`);
    }
    
    /**
     * Configurar observador para nuevas filas dinámicas
     */
    function setupMutationObserver() {
        const observer = new MutationObserver(function(mutations) {
            let shouldRevalidate = false;
            
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1 && 
                            (node.matches('.form-row') || node.querySelector('.form-row'))) {
                            shouldRevalidate = true;
                        }
                    });
                }
            });
            
            if (shouldRevalidate) {
                console.log('👁️ STOCK VALIDATOR: Nuevas filas detectadas, revalidando...');
                setTimeout(validateAllLines, 500);
            }
        });
        
        const formContainer = document.querySelector('.js-inline-admin-formset') || document.body;
        observer.observe(formContainer, { childList: true, subtree: true });
        
        console.log('👁️ STOCK VALIDATOR: Observer de mutaciones configurado');
    }
    
    /**
     * Inicializar el sistema
     */
    function init() {
        console.log('🚀 STOCK VALIDATOR: Iniciando sistema inteligente...');
        
        // Verificar si estamos en una página de factura
        const isInvoiceForm = window.location.pathname.includes('/invoicing/invoice/');
        if (!isInvoiceForm) {
            console.log('⏭️ STOCK VALIDATOR: No es página de factura, saltando...');
            return;
        }
        
        // IMPORTANTE: No validar stock en modo edición
        if (isEditMode()) {
            console.log('✏️ STOCK VALIDATOR: Modo edición detectado - Las validaciones de stock están DESHABILITADAS');
            console.log('💡 Razón: No tiene sentido validar stock en facturas ya existentes');
            return;
        }
        
        // Solo activar en modo creación de nueva factura
        if (!isNewInvoiceForm()) {
            console.log('⏭️ STOCK VALIDATOR: No es formulario de nueva factura, saltando...');
            return;
        }
        
        console.log('✅ STOCK VALIDATOR: Modo NUEVA FACTURA confirmado - Activando validaciones');
        
        // Cargar datos de productos
        if (!loadProductsData()) {
            console.log('❌ STOCK VALIDATOR: Sin datos de productos, no se puede inicializar');
            return;
        }
        
        // Encontrar elementos del formulario
        formElement = document.querySelector('#invoice_form') || document.querySelector('form');
        if (!formElement) {
            console.log('❌ STOCK VALIDATOR: Formulario no encontrado');
            return;
        }
        
        // Configurar componentes
        findSaveButtons();
        setupEventListeners();
        setupMutationObserver();
        
        // Validación inicial
        setTimeout(() => {
            validateAllLines();
            console.log('✅ STOCK VALIDATOR: Sistema inicializado correctamente');
        }, 1000);
    }
    
    // ======= FUNCIONES GLOBALES PARA DEBUG =======
    
    window.stockValidator = {
        validateNow: validateAllLines,
        checkProduct: checkProductStock,
        getValidationResults: () => lastValidationResults,
        getMessages: () => validationMessages,
        config: CONFIG,
        showMessage: showDjangoStyleMessage,
        
        // Función de demostración
        demo: function() {
            console.log('🎭 Ejecutando demo de notificaciones...');
            
            showDjangoStyleMessage(
                'DEMO: Producto Test - Disponible: 2, Solicitado: 5, Faltante: 3 unidades.',
                'error',
                8000
            );
            
            setTimeout(() => {
                showDjangoStyleMessage(
                    'DEMO: Producto XYZ - Solo quedan 3 unidades disponibles. Considere reabastecer urgentemente.',
                    'warning',
                    6000
                );
            }, 1000);
            
            setTimeout(() => {
                showDjangoStyleMessage(
                    'DEMO: Producto ABC - Utilizando 85% del stock disponible (17 de 20 unidades).',
                    'info',
                    5000
                );
            }, 2000);
            
            setTimeout(() => {
                showDjangoStyleMessage(
                    'DEMO: Producto OK - Disponible: 50 unidades.',
                    'success',
                    4000
                );
            }, 3000);
        }
    };
    
    // ======= INICIALIZACIÓN =======
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        setTimeout(init, 500);
    }
    
    // También inicializar después de otros scripts
    setTimeout(init, 2000);
    
    console.log('✅ STOCK VALIDATOR: Módulo cargado');
    
})();