/**
 * Calculadora de desglose dinámico de IVA - v2.0 
 * Compatible con Django Admin TabularInline
 */
(function() {
    'use strict';
    
    // Calculadora de desglose de IVA v2.0 inicializada
    
    let isCalculating = false;
    let updateTimeout = null;
    
    // OPCIÓN B MEJORADA: Configuración responsive para modal enganchada
    const RESPONSIVE_CONFIG = {
        DESKTOP_MIN: 1200,
        TABLET_MIN: 768,
        MODAL_WIDTH: 280,
        MODAL_MIN_WIDTH: 260,
        MODAL_MAX_WIDTH: 320,
        SCROLL_THROTTLE: 16 // ~60fps
    };

    // Variables globales para tracking
    let modalAttachmentState = {
        isAttached: false,
        targetFieldset: null,
        scrollListener: null,
        resizeListener: null,
        animationFrame: null
    };

    // Función para detectar el fieldset "Información Básica" - MEJORADA
    function findInfoBasicaFieldset() {
        console.log('🔍 Iniciando detección mejorada del fieldset "Información Básica"...');
        
        // ESTRATEGIA 1: Buscar por headers con texto específico
        console.log('📋 Estrategia 1: Buscando por headers...');
        const headers = document.querySelectorAll('h1, h2, h3, legend, .module h2');
        for (const header of headers) {
            const text = header.textContent.toLowerCase();
            if (text.includes('información básica') || text.includes('informacion basica') || 
                text.includes('basic') || text.includes('general')) {
                const container = header.closest('fieldset, .module, .form-group, .section');
                if (container) {
                    console.log('✅ Fieldset encontrado via header:', header.textContent, container);
                    return container;
                }
            }
        }
        
        // ESTRATEGIA 2: Buscar fieldset.module.aligned (estructura típica Django)
        console.log('📋 Estrategia 2: Buscando fieldset.module.aligned...');
        const moduleFieldset = document.querySelector('fieldset.module.aligned, fieldset.module');
        if (moduleFieldset) {
            console.log('✅ Fieldset module encontrado:', moduleFieldset);
            return moduleFieldset;
        }
        
        // ESTRATEGIA 3: Buscar por contenedor de campos conocidos
        console.log('📋 Estrategia 3: Buscando por campos conocidos...');
        const knownFields = [
            '.field-company',
            '.field-customer', 
            '.field-payment_form',
            '.field-date',
            '.field-account'
        ];
        
        for (const fieldSelector of knownFields) {
            const field = document.querySelector(fieldSelector);
            if (field) {
                // Buscar contenedor padre común
                const containers = [
                    field.closest('fieldset'),
                    field.closest('.module'),
                    field.closest('.form-group'),
                    field.closest('.section')
                ].filter(Boolean);
                
                if (containers.length > 0) {
                    const container = containers[0];
                    console.log(`✅ Fieldset detectado via ${fieldSelector}:`, container);
                    return container;
                }
            }
        }
        
        // ESTRATEGIA 4: Buscar contenedor padre común de múltiples campos
        console.log('📋 Estrategia 4: Buscando contenedor padre común...');
        const companyField = document.querySelector('.field-company, #id_company');
        const customerField = document.querySelector('.field-customer, #id_customer');
        
        if (companyField && customerField) {
            // Buscar ancestro común más cercano
            let parent = companyField.parentElement;
            while (parent && parent !== document.body) {
                if (parent.contains(customerField)) {
                    console.log('✅ Contenedor padre común encontrado:', parent);
                    return parent;
                }
                parent = parent.parentElement;
            }
        }
        
        // ESTRATEGIA 5: Fallback al formulario principal
        console.log('📋 Estrategia 5: Fallback al formulario principal...');
        const mainForm = document.querySelector('form[method="post"]');
        if (mainForm) {
            // Buscar el primer contenedor dentro del form
            const firstContainer = mainForm.querySelector('fieldset, .module, .form-group, .section');
            if (firstContainer) {
                console.log('✅ Contenedor fallback encontrado en form:', firstContainer);
                return firstContainer;
            }
        }
        
        // ESTRATEGIA 6: Último recurso - crear referencia virtual
        console.log('📋 Estrategia 6: Creando referencia virtual...');
        const firstField = document.querySelector('.form-row, .field-company, [class*="field-"]');
        if (firstField) {
            console.log('⚠️ Usando referencia virtual basada en primer campo:', firstField);
            return firstField.parentElement || firstField;
        }
        
        console.log('❌ No se pudo detectar el fieldset "Información Básica"');
        console.log('🔍 Elementos disponibles en la página:');
        console.log('   - Fieldsets:', document.querySelectorAll('fieldset').length);
        console.log('   - Modules:', document.querySelectorAll('.module').length);
        console.log('   - Form-rows:', document.querySelectorAll('.form-row').length);
        console.log('   - Fields:', document.querySelectorAll('[class*="field-"]').length);
        
        return null;
    }

    // Función para calcular posición enganchada - MEJORADA
    function calculateAttachedPosition(fieldset, modal) {
        if (!fieldset || !modal) {
            console.log('⚠️ calculateAttachedPosition: fieldset o modal faltante');
            return null;
        }
        
        try {
            const fieldsetRect = fieldset.getBoundingClientRect();
            const modalWidth = RESPONSIVE_CONFIG.MODAL_WIDTH;
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;
            const scrollY = window.scrollY;
            
            // Validar que el fieldset tenga dimensiones válidas
            if (fieldsetRect.width === 0 || fieldsetRect.height === 0) {
                console.log('⚠️ Fieldset tiene dimensiones inválidas:', fieldsetRect);
                return null;
            }
            
            // Calcular posición derecha del fieldset
            const rightEdge = fieldsetRect.right;
            const leftEdge = fieldsetRect.left;
            const availableSpace = viewportWidth - rightEdge;
            const fieldsetTop = fieldsetRect.top + scrollY;
            
            // Determinar mejor posición horizontal
            let targetLeft;
            if (availableSpace >= modalWidth + 20) {
                // Espacio suficiente a la derecha
                targetLeft = rightEdge + 10;
            } else if (leftEdge >= modalWidth + 20) {
                // Espacio suficiente a la izquierda
                targetLeft = leftEdge - modalWidth - 10;
            } else {
                // Fallback: posición fija derecha
                targetLeft = viewportWidth - modalWidth - 15;
            }
            
            // Asegurar que no salga de los límites
            targetLeft = Math.max(10, Math.min(targetLeft, viewportWidth - modalWidth - 10));
            
            const result = {
                left: targetLeft,
                top: Math.max(fieldsetTop, scrollY + 10), // Evitar que se salga por arriba
                canAttach: availableSpace >= modalWidth + 20 || leftEdge >= modalWidth + 20,
                attachSide: availableSpace >= modalWidth + 20 ? 'right' : 'left',
                fieldsetRect: fieldsetRect,
                availableSpace: availableSpace
            };
            
            console.log('📐 Posición calculada:', {
                fieldsetDimensions: `${fieldsetRect.width}x${fieldsetRect.height}`,
                fieldsetPosition: `${fieldsetRect.left},${fieldsetRect.top}`,
                rightEdge: rightEdge,
                availableSpace: availableSpace,
                modalWidth: modalWidth,
                targetPosition: `${result.left},${result.top}`,
                canAttach: result.canAttach,
                attachSide: result.attachSide
            });
            
            return result;
            
        } catch (error) {
            console.error('❌ Error calculando posición:', error);
            return null;
        }
    }

    // Función para detectar tipo de dispositivo
    function getDeviceType() {
        const width = window.innerWidth;
        if (width >= RESPONSIVE_CONFIG.DESKTOP_MIN) return 'desktop';
        if (width >= RESPONSIVE_CONFIG.TABLET_MIN) return 'tablet';
        return 'mobile';
    }

    // Función optimizada para tracking de scroll - MEJORADA
    function createScrollTracker(modal, fieldset) {
        let ticking = false;
        let lastScrollY = window.scrollY;
        
        return function() {
            const currentScrollY = window.scrollY;
            
            // Solo procesar si hay cambio significativo o es la primera vez
            if (Math.abs(currentScrollY - lastScrollY) < 5 && lastScrollY !== 0) {
                return;
            }
            
            if (!ticking) {
                modalAttachmentState.animationFrame = requestAnimationFrame(() => {
                    // Verificar que la modal y fieldset sigan siendo válidos
                    if (modalAttachmentState.isAttached && modal && modal.isConnected) {
                        const currentFieldset = modalAttachmentState.targetFieldset;
                        
                        // Re-detectar fieldset si es necesario
                        if (!currentFieldset || !currentFieldset.isConnected) {
                            console.log('🔄 Re-detectando fieldset durante scroll...');
                            const newFieldset = findInfoBasicaFieldset();
                            if (newFieldset) {
                                modalAttachmentState.targetFieldset = newFieldset;
                                positionModalCorrectly(modal, newFieldset);
                            } else {
                                console.log('⚠️ Fieldset perdido durante scroll, usando posición fija');
                                fallbackToFixedPosition(modal);
                            }
                        } else {
                            // Fieldset válido - actualizar posición
                            positionModalCorrectly(modal, currentFieldset);
                        }
                    }
                    
                    lastScrollY = currentScrollY;
                    ticking = false;
                });
                ticking = true;
            }
        };
    }

    // Función para crear la ventana flotante del resumen - OPCIÓN B MEJORADA
    function createFloatingWindow() {
        console.log('🏗️ OPCIÓN B MEJORADA: Creando ventana modal enganchada...');
        
        // Buscar si ya existe
        if (document.querySelector('#floating-invoice-summary')) {
            console.log('✅ Ventana flotante ya existe');
            return;
        }
        
        // Detectar fieldset target
        const targetFieldset = findInfoBasicaFieldset();
        const deviceType = getDeviceType();
        
        console.log(`📱 Dispositivo detectado: ${deviceType}`);
        console.log(`🎯 Fieldset target: ${targetFieldset ? 'ENCONTRADO' : 'NO ENCONTRADO'}`);
        
        // Crear la ventana flotante con configuración responsive
        const floatingWindow = document.createElement('div');
        floatingWindow.id = 'floating-invoice-summary';
        
        // Configurar estilo inicial según dispositivo
        let initialStyles = {};
        let shouldAttach = false;
        
        if (deviceType === 'desktop' && targetFieldset) {
            // Desktop: Modal enganchado - calcular después de que el DOM esté listo
            console.log('🎯 Configurando modo ENGANCHADO para desktop');
            modalAttachmentState.isAttached = true;
            modalAttachmentState.targetFieldset = targetFieldset;
            shouldAttach = true;
            
            // Posición inicial temporal - se ajustará después
            initialStyles = {
                position: 'absolute',
                left: '0px',
                top: '0px',
                width: RESPONSIVE_CONFIG.MODAL_WIDTH + 'px',
                visibility: 'hidden' // Ocultar hasta posicionar correctamente
            };
        }
        
        if (!shouldAttach) {
            // Fallback: Modal tradicional centrado/flotante
            console.log(`📌 Activando modo TRADICIONAL para ${deviceType}`);
            modalAttachmentState.isAttached = false;
            
            if (deviceType === 'mobile') {
                initialStyles = {
                    position: 'fixed',
                    top: '10px',
                    left: '10px',
                    right: '10px',
                    width: 'auto',
                    maxWidth: 'calc(100% - 20px)'
                };
            } else {
                initialStyles = {
                    position: 'fixed',
                    top: '80px',
                    right: '15px',
                    width: RESPONSIVE_CONFIG.MODAL_WIDTH + 'px'
                };
            }
        }
        
        // Aplicar estilos base + responsivos
        const baseStyles = `
            min-width: ${RESPONSIVE_CONFIG.MODAL_MIN_WIDTH}px;
            max-width: ${RESPONSIVE_CONFIG.MODAL_MAX_WIDTH}px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            z-index: 9999;
            font-family: 'Roboto', 'Lucida Grande', Verdana, Arial, sans-serif;
            font-size: 13px;
            transition: all 0.2s ease;
        `;
        
        const styleString = baseStyles + Object.entries(initialStyles)
            .map(([key, value]) => `${key.replace(/([A-Z])/g, '-$1').toLowerCase()}: ${value};`)
            .join(' ');
            
        floatingWindow.style.cssText = styleString;
        
        // Crear barra de título estilo Django admin
        const titleBar = document.createElement('div');
        titleBar.id = 'floating-title-bar';
        titleBar.style.cssText = `
            background: #79aec8;
            color: white;
            padding: 8px 12px;
            cursor: move;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
            border-radius: 4px 4px 0 0;
            border-bottom: 1px solid #417690;
        `;
        
        const titleText = document.createElement('span');
        // Indicador visual si está enganchada
        const attachedIndicator = modalAttachmentState.isAttached ? ' 📎' : '';
        titleText.textContent = `Resumen de Factura${attachedIndicator}`;
        titleText.style.cssText = `
            font-weight: normal;
            font-size: 12px;
        `;
        
        // Botones de control
        const controls = document.createElement('div');
        controls.style.cssText = `
            display: flex;
            gap: 8px;
            align-items: center;
        `;
        
        // Botón minimizar estilo Django admin
        const minimizeBtn = document.createElement('button');
        minimizeBtn.type = 'button'; // Evita submit del formulario
        minimizeBtn.innerHTML = '▲';
        minimizeBtn.title = 'Minimizar';
        minimizeBtn.style.cssText = `
            background: none;
            border: none;
            color: white;
            font-size: 10px;
            cursor: pointer;
            padding: 2px 4px;
            border-radius: 2px;
            line-height: 1;
            transition: background-color 0.1s;
        `;
        minimizeBtn.onmouseover = () => minimizeBtn.style.backgroundColor = 'rgba(255,255,255,0.2)';
        minimizeBtn.onmouseout = () => minimizeBtn.style.backgroundColor = 'transparent';
        
        // Botón cerrar estilo Django admin
        const closeBtn = document.createElement('button');
        closeBtn.type = 'button'; // Evita submit del formulario
        closeBtn.innerHTML = '×';
        closeBtn.title = 'Cerrar';
        closeBtn.style.cssText = `
            background: none;
            border: none;
            color: white;
            font-size: 12px;
            cursor: pointer;
            padding: 2px 4px;
            border-radius: 2px;
            line-height: 1;
            transition: background-color 0.1s;
        `;
        closeBtn.onmouseover = () => closeBtn.style.backgroundColor = 'rgba(255,255,255,0.3)';
        closeBtn.onmouseout = () => closeBtn.style.backgroundColor = 'transparent';
        
        controls.appendChild(minimizeBtn);
        controls.appendChild(closeBtn);
        titleBar.appendChild(titleText);
        titleBar.appendChild(controls);
        
        // Contenedor del contenido estilo Django admin
        const contentContainer = document.createElement('div');
        contentContainer.id = 'floating-content';
        contentContainer.style.cssText = `
            padding: 10px;
            max-height: 300px;
            overflow-y: auto;
            display: none;
            background: white;
            font-size: 12px;
        `;
        
        floatingWindow.appendChild(titleBar);
        floatingWindow.appendChild(contentContainer);
        
        // Agregar al body
        document.body.appendChild(floatingWindow);
        
        // Hacer la ventana arrastrable
        makeDraggable(floatingWindow, titleBar);
        
        // Funcionalidad de botones - INICIA DESPLEGADA
        let isMinimized = false;
        
        // Configurar estado inicial desplegado
        contentContainer.style.display = 'block';
        floatingWindow.style.height = 'auto';
        minimizeBtn.innerHTML = '▲';
        minimizeBtn.title = 'Minimizar';
        titleText.textContent = 'Resumen de Factura';
        
        // Agregar indicador visual minimalista
        const minimizedIndicator = document.createElement('div');
        minimizedIndicator.id = 'minimized-indicator';
        minimizedIndicator.style.cssText = `
            position: absolute;
            top: -3px;
            right: -3px;
            width: 8px;
            height: 8px;
            background: #79aec8;
            border-radius: 50%;
            border: 1px solid white;
            box-shadow: 0 1px 2px rgba(0,0,0,0.2);
            animation: pulse 2s infinite;
            display: none;
        `;
        floatingWindow.appendChild(minimizedIndicator);
        
        minimizeBtn.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            isMinimized = !isMinimized;
            if (isMinimized) {
                contentContainer.style.display = 'none';
                floatingWindow.style.height = 'auto';
                minimizeBtn.innerHTML = '▼';
                minimizeBtn.title = 'Expandir';
                titleText.textContent = 'Resumen (minimizado)';
                // Mostrar indicador si hay contenido
                const hasContent = contentContainer.innerHTML.trim() !== '';
                if (hasContent) {
                    minimizedIndicator.style.display = 'block';
                }
            } else {
                contentContainer.style.display = 'block';
                minimizeBtn.innerHTML = '▲';
                minimizeBtn.title = 'Minimizar';
                titleText.textContent = 'Resumen de Factura';
                minimizedIndicator.style.display = 'none';
            }
        };
        
        closeBtn.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            // Limpiar event listeners antes de cerrar
            cleanupModalEventListeners();
            
            floatingWindow.style.opacity = '0';
            floatingWindow.style.transform = 'scale(0.8)';
            setTimeout(() => {
                floatingWindow.remove();
            }, 300);
        };
        
        // OPCIÓN B MEJORADA: Configurar scroll tracking si está enganchada
        if (modalAttachmentState.isAttached && targetFieldset) {
            console.log('🔄 Configurando scroll tracking para modal enganchada...');
            
            // Crear scroll tracker optimizado
            const scrollTracker = createScrollTracker(floatingWindow, targetFieldset);
            modalAttachmentState.scrollListener = scrollTracker;
            
            // Agregar event listener con throttling
            window.addEventListener('scroll', scrollTracker, { passive: true });
            
            // Crear resize listener para recalcular posición
            const resizeHandler = () => {
                const newDeviceType = getDeviceType();
                
                if (newDeviceType === 'desktop') {
                    // Mantener enganche en desktop usando función mejorada
                    modalAttachmentState.isAttached = true;
                    positionModalCorrectly(floatingWindow, targetFieldset);
                } else {
                    // Cambiar a modo tradicional en tablet/mobile
                    console.log(`📱 Cambiando a modo tradicional: ${newDeviceType}`);
                    floatingWindow.style.position = 'fixed';
                    floatingWindow.style.top = '80px';
                    floatingWindow.style.right = '15px';
                    floatingWindow.style.left = 'auto';
                    floatingWindow.style.visibility = 'visible';
                    modalAttachmentState.isAttached = false;
                    
                    // Quitar indicador de enganche
                    const titleText = floatingWindow.querySelector('#floating-title-bar span');
                    if (titleText && titleText.textContent.includes('📎')) {
                        titleText.textContent = 'Resumen de Factura';
                    }
                }
            };
            
            modalAttachmentState.resizeListener = resizeHandler;
            window.addEventListener('resize', resizeHandler, { passive: true });
            
            console.log('✅ Scroll tracking configurado exitosamente');
            
            // Posicionar correctamente la modal después de que esté en el DOM
            setTimeout(() => {
                positionModalCorrectly(floatingWindow, targetFieldset);
            }, 100);
        }
        
        console.log('🎉 OPCIÓN B MEJORADA: Ventana modal enganchada creada exitosamente');
        return contentContainer;
    }
    
    // Función para posicionar la modal correctamente SOBRE el fieldset al extremo derecho
    function positionModalCorrectly(modal, fieldset) {
        if (!modal || !fieldset) {
            console.log('⚠️ Modal o fieldset faltante para posicionamiento');
            return;
        }
        
        console.log('📐 Posicionando modal SOBRE fieldset al extremo derecho...');
        
        try {
            // Re-detectar fieldset si es necesario
            const currentFieldset = fieldset && fieldset.isConnected ? fieldset : findInfoBasicaFieldset();
            
            if (!currentFieldset) {
                console.log('❌ No se pudo re-detectar fieldset, usando posición fija');
                fallbackToFixedPosition(modal);
                return;
            }
            
            const fieldsetRect = currentFieldset.getBoundingClientRect();
            const modalWidth = RESPONSIVE_CONFIG.MODAL_WIDTH;
            const viewportWidth = window.innerWidth;
            
            // Validar que el fieldset tenga dimensiones válidas
            if (fieldsetRect.width === 0 || fieldsetRect.height === 0) {
                console.log('⚠️ Fieldset con dimensiones inválidas, reintentando...');
                setTimeout(() => positionModalCorrectly(modal, currentFieldset), 100);
                return;
            }
            
            console.log('📊 Fieldset detectado:', {
                width: fieldsetRect.width,
                height: fieldsetRect.height,
                left: fieldsetRect.left,
                top: fieldsetRect.top,
                right: fieldsetRect.right
            });
            
            // Calcular si hay espacio suficiente a la derecha
            const availableSpace = viewportWidth - fieldsetRect.right;
            const minSpaceNeeded = modalWidth + 10; // Reducido de 20 a 10px
            
            console.log('📏 Cálculo de espacio:', {
                viewportWidth: viewportWidth,
                fieldsetRight: fieldsetRect.right,
                availableSpace: availableSpace,
                modalWidth: modalWidth,
                minSpaceNeeded: minSpaceNeeded,
                hasSpace: availableSpace >= minSpaceNeeded
            });
            
            // Intentar posición a la derecha primero
            const canAttachRight = availableSpace >= minSpaceNeeded;
            
            if (canAttachRight) {
                // POSICIONAMIENTO SOBRE EL FIELDSET AL EXTREMO DERECHO
                attachModalToFieldset(modal, currentFieldset, fieldsetRect, modalWidth, 'right');
                console.log('✅ Modal enganchada SOBRE fieldset al extremo derecho');
            } else if (viewportWidth >= 768) {
                // Para pantallas medianas/grandes: posicionar sobre fieldset alineada a la derecha
                attachModalToFieldset(modal, currentFieldset, fieldsetRect, modalWidth, 'center');
                console.log('✅ Modal enganchada SOBRE fieldset (alineada derecha - espacio limitado)');
            } else {
                // Pantallas pequeñas: usar overlay completo
                attachModalToFieldset(modal, currentFieldset, fieldsetRect, modalWidth, 'overlay');
                console.log('✅ Modal enganchada SOBRE fieldset (overlay móvil)');
            }
            
            // Actualizar estado para cualquier attachment exitoso
            modalAttachmentState.isAttached = true;
            modalAttachmentState.targetFieldset = currentFieldset;
            
            // Indicador visual
            updateModalTitle(modal, true);
            
        } catch (error) {
            console.error('❌ Error posicionando modal:', error);
            fallbackToFixedPosition(modal);
        }
    }
    
    // Función para enganchar la modal al fieldset usando posición relativa
    function attachModalToFieldset(modal, fieldset, fieldsetRect, modalWidth, position = 'right') {
        // Crear contenedor de posicionamiento si no existe
        let positionWrapper = fieldset.querySelector('.modal-position-wrapper');
        
        if (!positionWrapper) {
            positionWrapper = document.createElement('div');
            positionWrapper.className = 'modal-position-wrapper';
            positionWrapper.style.cssText = `
                position: relative;
                display: block;
                width: 100%;
            `;
            
            // Envolver el contenido del fieldset
            const fieldsetContent = Array.from(fieldset.children);
            fieldsetContent.forEach(child => {
                if (child !== positionWrapper) {
                    positionWrapper.appendChild(child);
                }
            });
            fieldset.appendChild(positionWrapper);
        }
        
        // Configurar estilo base de la modal
        modal.style.position = 'absolute';
        modal.style.zIndex = '9999';
        modal.style.visibility = 'visible';
        
        // Aplicar posición específica según el modo
        switch (position) {
            case 'right':
                // Posición original: a la derecha del fieldset
                modal.style.left = (fieldsetRect.width + 10) + 'px';
                modal.style.top = '0px';
                modal.style.right = 'auto';
                break;
                
            case 'center':
                // Alineada a la derecha sobre el fieldset
                modal.style.left = 'auto';
                modal.style.top = '10px';
                modal.style.right = '10px';
                modal.style.transform = 'none';
                break;
                
            case 'overlay':
                // Overlay completo sobre el fieldset
                modal.style.left = '10px';
                modal.style.top = '10px';
                modal.style.right = '10px';
                modal.style.width = 'calc(100% - 20px)';
                modal.style.maxWidth = 'none';
                break;
                
            default:
                // Fallback a derecha
                modal.style.left = (fieldsetRect.width + 10) + 'px';
                modal.style.top = '0px';
                modal.style.right = 'auto';
        }
        
        // Agregar modal al wrapper si no está ya ahí
        if (modal.parentNode !== positionWrapper) {
            positionWrapper.appendChild(modal);
        }
        
        const modeDescription = {
            'right': 'extremo derecho',
            'center': 'alineada derecha sobre fieldset', 
            'overlay': 'overlay completo'
        };
        console.log(`📌 Modal enganchada usando posición relativa al fieldset (modo: ${modeDescription[position] || position})`);
    }
    
    // Función para fallback a posición fija
    function fallbackToFixedPosition(modal) {
        modal.style.position = 'fixed';
        modal.style.top = '80px';
        modal.style.right = '15px';
        modal.style.left = 'auto';
        modal.style.visibility = 'visible';
        modal.style.zIndex = '9999';
        
        // Mover al body si no está ahí
        if (modal.parentNode !== document.body) {
            document.body.appendChild(modal);
        }
        
        modalAttachmentState.isAttached = false;
        updateModalTitle(modal, false);
        
        console.log('📌 Modal usando posición fija tradicional');
    }
    
    // Función para actualizar el título de la modal
    function updateModalTitle(modal, isAttached) {
        const titleText = modal.querySelector('#floating-title-bar span');
        if (titleText) {
            if (isAttached && !titleText.textContent.includes('📎')) {
                titleText.textContent = 'Resumen de Factura 📎';
            } else if (!isAttached && titleText.textContent.includes('📎')) {
                titleText.textContent = 'Resumen de Factura';
            }
        }
    }
    
    // Función para limpiar event listeners de la modal
    function cleanupModalEventListeners() {
        console.log('🧹 Limpiando event listeners de la modal...');
        
        if (modalAttachmentState.scrollListener) {
            window.removeEventListener('scroll', modalAttachmentState.scrollListener);
            modalAttachmentState.scrollListener = null;
        }
        
        if (modalAttachmentState.resizeListener) {
            window.removeEventListener('resize', modalAttachmentState.resizeListener);
            modalAttachmentState.resizeListener = null;
        }
        
        if (modalAttachmentState.animationFrame) {
            cancelAnimationFrame(modalAttachmentState.animationFrame);
            modalAttachmentState.animationFrame = null;
        }
        
        // Reset state
        modalAttachmentState.isAttached = false;
        modalAttachmentState.targetFieldset = null;
        
        console.log('✅ Event listeners limpiados correctamente');
    }
    
    // Función para hacer una ventana arrastrable
    function makeDraggable(element, handle) {
        let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
        
        handle.onmousedown = dragMouseDown;
        
        function dragMouseDown(e) {
            e = e || window.event;
            e.preventDefault();
            pos3 = e.clientX;
            pos4 = e.clientY;
            document.onmouseup = closeDragElement;
            document.onmousemove = elementDrag;
            element.style.cursor = 'grabbing';
        }
        
        function elementDrag(e) {
            e = e || window.event;
            e.preventDefault();
            pos1 = pos3 - e.clientX;
            pos2 = pos4 - e.clientY;
            pos3 = e.clientX;
            pos4 = e.clientY;
            
            const newTop = element.offsetTop - pos2;
            const newLeft = element.offsetLeft - pos1;
            
            // Mantener dentro de los límites de la ventana
            const maxTop = window.innerHeight - element.offsetHeight;
            const maxLeft = window.innerWidth - element.offsetWidth;
            
            element.style.top = Math.max(0, Math.min(newTop, maxTop)) + "px";
            element.style.left = Math.max(0, Math.min(newLeft, maxLeft)) + "px";
            element.style.right = 'auto';
        }
        
        function closeDragElement() {
            document.onmouseup = null;
            document.onmousemove = null;
            element.style.cursor = 'default';
        }
    }
    
    // Función para encontrar el contenedor donde insertar el desglose
    function findTaxBreakdownContainer() {
        console.log('🔍 Buscando contenedor para desglose...');
        
        // Prioridad 1: Verificar si ya existe la ventana flotante
        let floatingContent = document.querySelector('#floating-content');
        if (floatingContent) {
            console.log('✅ Ventana flotante encontrada');
            return floatingContent;
        }
        
        // Prioridad 2: Crear la ventana flotante
        floatingContent = createFloatingWindow();
        if (floatingContent) {
            console.log('✅ Ventana flotante creada y encontrada');
            return floatingContent;
        }
        
        // Fallback: Buscar en la sección de líneas directamente (solo si falla la ventana flotante)
        const linesContainer = document.querySelector('#invoiceline_set-group, .inline-group');
        if (linesContainer) {
            console.log('⚠️ Usando contenedor de líneas como fallback de emergencia');
            return linesContainer;
        }
        
        console.log('❌ No se encontró contenedor apropiado');
        return null;
    }
    
    // Función para encontrar campos de totales por ID o contenedor
    function findTotalFields() {
        console.log('🔍 Buscando campos de totales...');
        
        // Buscar por contenedores conocidos
        const subtotalField = document.querySelector('.field-subtotal input, #id_subtotal, input[name*="subtotal"]');
        const taxField = document.querySelector('.field-tax_amount input, #id_tax_amount, input[name*="tax_amount"]');
        const totalField = document.querySelector('.field-total input, #id_total, input[name*="total"]:not([name*="line_total"])');
        
        console.log('📊 Campos encontrados:');
        console.log('  Subtotal:', subtotalField);
        console.log('  Impuesto:', taxField);
        console.log('  Total:', totalField);
        
        return { subtotalField, taxField, totalField };
    }
    
    // Función para obtener todas las filas de líneas de factura
    function getInvoiceLineRows() {
        const selectors = [
            '#invoiceline_set-group .form-row:not(.add-row)',
            '.tabular .form-row:not(.add-row)',
            '.dynamic-invoiceline_set:not(.add-row)',
            'tr.form-row:not(.add-row)'
        ];
        
        for (const selector of selectors) {
            const rows = document.querySelectorAll(selector);
            if (rows.length > 0) {
                console.log(`✅ Encontradas ${rows.length} filas con selector: ${selector}`);
                return rows;
            }
        }
        
        console.log('⚠️ No se encontraron filas de líneas');
        return [];
    }
    
    // Función para obtener valores de una fila
    function getRowValues(row) {
        const getValue = (suffix) => {
            const selectors = [
                `input[name$="${suffix}"]`,
                `input[id*="${suffix}"]`,
                `input[name*="${suffix.replace('-', '_')}"]`
            ];
            
            for (const selector of selectors) {
                const input = row.querySelector(selector);
                if (input && input.value !== '') {
                    return parseFloat(input.value) || 0;
                }
            }
            return 0;
        };
        
        return {
            quantity: getValue('-quantity'),
            unit_price: getValue('-unit_price'),
            discount: getValue('-discount'),
            iva_rate: getValue('-iva_rate')
        };
    }
    
    // Función principal de cálculo
    function calculateTotals() {
        if (isCalculating) return;
        isCalculating = true;
        
        console.log('🔄 Calculando totales y desglose...');
        console.log('⏰ Timestamp:', new Date().toLocaleTimeString());
        
        const rows = getInvoiceLineRows();
        console.log('📊 Filas para procesar:', rows.length);
        const breakdown = {};
        let totalSubtotal = 0;
        let totalTax = 0;
        
        rows.forEach((row, index) => {
            const values = getRowValues(row);
            console.log(`Fila ${index + 1}:`, values);
            
            if (values.quantity > 0 && values.unit_price > 0) {
                const subtotal = values.quantity * values.unit_price;
                const discountAmount = subtotal * (values.discount / 100);
                const net = subtotal - discountAmount;
                const tax = net * (values.iva_rate / 100);
                
                totalSubtotal += net;
                totalTax += tax;
                
                // Agrupar por tasa de IVA
                const rate = values.iva_rate.toString();
                if (!breakdown[rate]) {
                    breakdown[rate] = { rate: values.iva_rate, base: 0, tax: 0 };
                }
                breakdown[rate].base += net;
                breakdown[rate].tax += tax;
                
                // Actualizar total de la línea si existe el campo
                const lineTotalInput = row.querySelector('input[name$="-line_total"], input[id*="line_total"]');
                if (lineTotalInput) {
                    lineTotalInput.value = (net + tax).toFixed(2);
                }
            }
        });
        
        console.log('📊 Breakdown calculado:', breakdown);
        console.log(`💰 Totales: Subtotal=$${totalSubtotal.toFixed(2)}, IVA=$${totalTax.toFixed(2)}`);
        
        // Actualizar campos de totales
        updateTotalFields(totalSubtotal, totalTax);
        
        // Mostrar desglose dinámico
        showBreakdownDisplay(breakdown, totalTax, totalSubtotal);
        
        isCalculating = false;
    }
    
    // Actualizar campos de totales
    function updateTotalFields(subtotal, tax) {
        const { subtotalField, taxField, totalField } = findTotalFields();
        
        if (subtotalField) {
            subtotalField.value = subtotal.toFixed(2);
            console.log('✅ Subtotal actualizado:', subtotal.toFixed(2));
        } else {
            console.log('⚠️ Campo subtotal no encontrado');
        }
        
        if (taxField) {
            taxField.value = tax.toFixed(2);
            console.log('✅ IVA actualizado:', tax.toFixed(2));
        } else {
            console.log('⚠️ Campo IVA no encontrado');
        }
        
        if (totalField) {
            totalField.value = (subtotal + tax).toFixed(2);
            console.log('✅ Total actualizado:', (subtotal + tax).toFixed(2));
        } else {
            console.log('⚠️ Campo total no encontrado');
        }
    }
    
    // Mostrar desglose dinámico
    function showBreakdownDisplay(breakdown, totalTax, subtotal) {
        const breakdownContainer = findTaxBreakdownContainer();
        if (!breakdownContainer) {
            console.log('⚠️ No se encontró contenedor para el desglose');
            return;
        }
        
        // Crear contenido del resumen
        const contentHtml = createBreakdownContent(breakdown, totalTax, subtotal);
        
        // Si es la ventana flotante
        if (breakdownContainer.id === 'floating-content') {
            breakdownContainer.innerHTML = contentHtml;
            
            // Hacer la ventana visible con animación si estaba oculta
            const floatingWindow = document.querySelector('#floating-invoice-summary');
            if (floatingWindow) {
                floatingWindow.style.opacity = '1';
                floatingWindow.style.transform = 'scale(1)';
                
                // Mostrar indicador si la ventana está minimizada y hay contenido
                const isMinimized = breakdownContainer.style.display === 'none';
                const indicator = document.querySelector('#minimized-indicator');
                const hasContent = Object.keys(breakdown).length > 0;
                
                if (isMinimized && hasContent && indicator) {
                    indicator.style.display = 'block';
                    // Actualizar el título para indicar que hay datos
                    const titleText = floatingWindow.querySelector('#floating-title-bar span');
                    if (titleText) {
                        titleText.textContent = '📋 Resumen de Factura (actualizado)';
                        setTimeout(() => {
                            titleText.textContent = '📋 Resumen de Factura';
                        }, 3000);
                    }
                }
                
                // Efecto de pulso suave cuando se actualiza (solo si no está minimizada)
                if (!isMinimized) {
                    floatingWindow.style.transition = 'all 0.2s ease';
                    floatingWindow.style.boxShadow = '0 8px 32px rgba(0, 123, 255, 0.5)';
                    setTimeout(() => {
                        floatingWindow.style.boxShadow = '0 8px 32px rgba(0, 123, 255, 0.3)';
                    }, 200);
                }
            }
            
        } else {
            // Fallback: crear resumen básico en el contenedor de líneas
            console.log('⚠️ Usando fallback - creando resumen simple');
            let container = document.getElementById('js-tax-breakdown');
            
            if (!container) {
                container = document.createElement('div');
                container.id = 'js-tax-breakdown';
                container.innerHTML = `
                    <div style="margin: 10px 0; padding: 12px; background: #e8f5e8; border: 2px solid #28a745; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="text-align: center; margin-bottom: 8px;">
                            <strong style="color: #155724; font-size: 14px;">⚡ RESUMEN DINÁMICO DE FACTURA</strong>
                        </div>
                        <div id="breakdown-details" style="font-size: 12px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;"></div>
                    </div>
                `;
                
                if (breakdownContainer && breakdownContainer.parentNode) {
                    breakdownContainer.parentNode.insertBefore(container, breakdownContainer.nextSibling);
                }
            }
            
            const detailsDiv = document.getElementById('breakdown-details');
            if (detailsDiv) {
                detailsDiv.innerHTML = contentHtml;
            }
        }
    }
    
    // Función para crear el contenido del desglose
    function createBreakdownContent(breakdown, totalTax, subtotal) {
        let html = '';
        
        if (Object.keys(breakdown).length === 0) {
            return `
                <div style="text-align: center; padding: 15px; color: #999;">
                    <div style="font-size: 11px;">Sin datos</div>
                </div>
            `;
        }
        
        // Subtotal estilo Django admin minimalista
        html += `
            <div style="padding: 6px 0; border-bottom: 1px solid #eee;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #666; font-size: 11px;">Subtotal</span>
                    <span style="font-weight: bold; color: #333; font-size: 12px;">$${subtotal.toFixed(2)}</span>
                </div>
            </div>
        `;
        
        // Sección de impuestos minimalista
        html += `
            <div style="padding: 6px 0;">
                <div style="color: #666; margin-bottom: 4px; font-size: 10px; text-transform: uppercase;">IVA</div>
        `;
        
        const sortedRates = Object.keys(breakdown).sort((a, b) => parseFloat(b) - parseFloat(a));
        
        sortedRates.forEach(rate => {
            const data = breakdown[rate];
            const rateLabel = parseFloat(rate) > 0 ? `IVA ${rate}%` : 'Exento (0%)';
            html += `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px; padding: 3px 0;">
                    <div>
                        <div style="color: #333; font-size: 11px;">${rateLabel}</div>
                        <div style="font-size: 9px; color: #999;">Base: $${data.base.toFixed(2)}</div>
                    </div>
                    <span style="color: #666; font-size: 11px;">$${data.tax.toFixed(2)}</span>
                </div>
            `;
        });
        
        // Total de impuestos si hay múltiples tasas
        if (sortedRates.length > 1) {
            html += `
                <div style="margin-top: 6px; padding-top: 6px; border-top: 1px solid #eee;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #666; font-size: 10px;">Total IVA</span>
                        <span style="color: #333; font-size: 11px;">$${totalTax.toFixed(2)}</span>
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
        
        // Total final estilo Django admin
        const totalFinal = subtotal + totalTax;
        html += `
            </div>
            <div style="padding: 8px 0; border-top: 2px solid #79aec8; margin-top: 6px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #333; font-weight: bold; font-size: 12px;">TOTAL</span>
                    <span style="color: #79aec8; font-weight: bold; font-size: 14px;">$${totalFinal.toFixed(2)}</span>
                </div>
            </div>
        `;
        
        return html;
    }
    
    // Configurar event listeners
    function setupEventListeners() {
        // Event delegation para inputs
        document.addEventListener('input', function(e) {
            if (!e.target.name) return;
            
            const relevantFields = ['quantity', 'unit_price', 'discount', 'iva_rate'];
            const isRelevant = relevantFields.some(field => e.target.name.includes(field));
            
            if (isRelevant) {
                console.log('📝 Campo relevante modificado:', e.target.name, '=', e.target.value);
                console.log('🎯 Tipo de evento:', e.type);
                clearTimeout(updateTimeout);
                updateTimeout = setTimeout(calculateTotals, 300);
            }
        });
        
        // Observar cambios en el DOM (nuevas líneas)
        if (window.MutationObserver) {
            const observer = new MutationObserver(function(mutations) {
                let shouldRecalculate = false;
                
                mutations.forEach(function(mutation) {
                    if (mutation.addedNodes.length > 0 || mutation.removedNodes.length > 0) {
                        shouldRecalculate = true;
                    }
                });
                
                if (shouldRecalculate) {
                    console.log('🔄 DOM modificado, recalculando...');
                    clearTimeout(updateTimeout);
                    updateTimeout = setTimeout(calculateTotals, 500);
                }
            });
            
            const inlineGroup = document.querySelector('#invoiceline_set-group, .inline-group, .tabular');
            if (inlineGroup) {
                observer.observe(inlineGroup, { childList: true, subtree: true });
                console.log('✅ Observer configurado');
            }
        }
        
        console.log('✅ Event listeners configurados');
    }
    
    // Función de inicialización
    function initialize() {
        console.log('🔧 Inicializando calculadora...');
        
        // Verificar si estamos en la página correcta
        const invoiceForm = document.querySelector('#invoiceline_set-group, .inline-group');
        console.log('🔍 Buscando formulario de factura...');
        console.log('📋 Formulario encontrado:', invoiceForm);
        
        if (!invoiceForm) {
            console.log('⚠️ No se detectó formulario de factura, cancelando inicialización');
            console.log('🔍 Elementos disponibles:', document.querySelectorAll('[id*="invoice"], .inline-group, .tabular'));
            return;
        }
        
        setupEventListeners();
        
        // Cálculo inicial con delay para asegurar que el DOM esté listo
        setTimeout(calculateTotals, 800);
        
        console.log('🎉 Calculadora de desglose iniciada correctamente');
    }
    
    // Auto-inicialización
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
    
    // Exponer funciones globalmente para debugging y testing
    window.findInfoBasicaFieldset = findInfoBasicaFieldset;
    window.positionModalCorrectly = positionModalCorrectly;
    window.attachModalToFieldset = attachModalToFieldset;
    window.fallbackToFixedPosition = fallbackToFixedPosition;
    window.modalAttachmentState = modalAttachmentState;
    
    console.log('🔧 Funciones de debugging disponibles globalmente');
    
})();