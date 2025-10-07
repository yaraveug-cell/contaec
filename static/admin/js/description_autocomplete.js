/**
 * Autocompletado de descripción de productos
 * Permite buscar productos por descripción y actualiza todos los campos
 */
(function() {
    'use strict';
    
    let searchTimeout;
    
    // Función para crear el dropdown de sugerencias
    function createSuggestionsDropdown(input) {
        // Verificar si ya existe un dropdown para este input
        const existingDropdown = input.parentNode.querySelector('.description-autocomplete-dropdown');
        if (existingDropdown) {
            return existingDropdown;
        }
        
        const dropdown = document.createElement('div');
        dropdown.className = 'description-autocomplete-dropdown';
        dropdown.style.cssText = `
            position: absolute;
            background: white;
            border: 1px solid #ccc;
            border-top: none;
            max-height: 200px;
            overflow-y: auto;
            z-index: 1000;
            width: 100%;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            display: none;
        `;
        
        input.parentNode.style.position = 'relative';
        input.parentNode.appendChild(dropdown);
        
        return dropdown;
    }
    
    // Función para mostrar sugerencias
    function showSuggestions(input, dropdown, products) {
        if (!dropdown) {
            console.error('No dropdown available for input:', input.name);
            return;
        }
        
        dropdown.innerHTML = '';
        
        if (!products || products.length === 0) {
            dropdown.style.display = 'none';
            return;
        }
        
        products.forEach(product => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.style.cssText = `
                padding: 8px 12px;
                cursor: pointer;
                border-bottom: 1px solid #eee;
                font-size: 12px;
            `;
            
            item.innerHTML = `
                <div style="font-weight: bold;">${product.text}</div>
                <div style="color: #666; font-size: 11px;">
                    ${product.code} - $${product.sale_price} - ${product.company}
                </div>
            `;
            
            // Hover effects
            item.addEventListener('mouseenter', function() {
                this.style.backgroundColor = '#f0f0f0';
            });
            
            item.addEventListener('mouseleave', function() {
                this.style.backgroundColor = 'white';
            });
            
            // Click handler con prevención de propagación
            item.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                selectProduct(input, product);
                dropdown.style.display = 'none';
                console.log('Producto seleccionado desde descripción:', product.text);
            });
            
            dropdown.appendChild(item);
        });
        
        dropdown.style.display = 'block';
    }
    
    // Función para seleccionar un producto y actualizar campos
    function selectProduct(descriptionInput, productData) {
        const row = descriptionInput.closest('tr') || descriptionInput.closest('.form-row') || descriptionInput.closest('fieldset');
        if (!row) return;
        
        // Buscar campos en la fila
        const productSelect = row.querySelector('select[name*="product"]');
        const unitPriceField = row.querySelector('input[name*="unit_price"]');
        const ivaRateField = row.querySelector('input[name*="iva_rate"]');
        
        console.log('Seleccionado desde descripción:', productData.text);
        
        // Actualizar campos
        descriptionInput.value = productData.description;
        
        if (productSelect) {
            productSelect.value = productData.id;
        }
        
        if (unitPriceField) {
            unitPriceField.value = productData.sale_price;
        }
        
        if (ivaRateField) {
            ivaRateField.value = productData.iva_rate;
        }
        
        // Disparar eventos para que la calculadora recalcule
        if (unitPriceField) {
            unitPriceField.dispatchEvent(new Event('input', { bubbles: true }));
            unitPriceField.dispatchEvent(new Event('change', { bubbles: true }));
        }
        
        console.log('Campos actualizados desde descripción');
    }
    
    // Función para buscar productos
    function searchProducts(query, callback) {
        if (query.length < 2) {
            callback([]);
            return;
        }
        
        const url = `/api/v1/invoicing/ajax/product-description-autocomplete/?q=${encodeURIComponent(query)}`;
        
        fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            callback(data.results || []);
        })
        .catch(error => {
            console.error('Error en búsqueda de productos:', error);
            callback([]);
        });
    }
    
    // Función para configurar autocompletado en un campo descripción
    function setupDescriptionAutocomplete(input) {
        if (input.hasAttribute('data-description-autocomplete')) return;
        input.setAttribute('data-description-autocomplete', 'true');
        
        const dropdown = createSuggestionsDropdown(input);
        let inputSearchTimeout;
        
        // Evento input con debounce específico para cada campo
        input.addEventListener('input', function() {
            const query = this.value.trim();
            
            clearTimeout(inputSearchTimeout);
            inputSearchTimeout = setTimeout(() => {
                searchProducts(query, (products) => {
                    showSuggestions(input, dropdown, products);
                });
            }, 300);
        });
        
        // Cerrar dropdown al hacer clic fuera (usar delegación de eventos)
        document.addEventListener('click', function(event) {
            if (!input.contains(event.target) && !dropdown.contains(event.target)) {
                dropdown.style.display = 'none';
            }
        });
        
        // Cerrar dropdown con Escape
        input.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                dropdown.style.display = 'none';
            }
        });
        
        // Agregar clase visual para indicar que tiene autocompletado
        input.classList.add('has-autocomplete');
        
        console.log('Autocompletado de descripción configurado para:', input.name);
    }
    
    // Mapas para gestionar dropdowns y timeouts por campo
    let fieldDropdowns = new Map();
    let fieldTimeouts = new Map();
    
    // Event delegation para input en campos de descripción
    document.addEventListener('input', function(e) {
        const target = e.target;
        
        // Verificar si es un campo de descripción
        if (target.tagName === 'INPUT' && target.name && target.name.includes('description')) {
            console.log('Event delegation: Input en campo descripción', target.name);
            
            const query = target.value.trim();
            const fieldKey = target.name + '_' + (target.closest('tr')?.rowIndex || Date.now());
            
            // Limpiar timeout anterior
            if (fieldTimeouts.has(fieldKey)) {
                clearTimeout(fieldTimeouts.get(fieldKey));
            }
            
            // Crear dropdown si no existe
            if (!fieldDropdowns.has(target)) {
                const dropdown = createSuggestionsDropdown(target);
                fieldDropdowns.set(target, dropdown);
            }
            
            // Establecer nuevo timeout
            const timeoutId = setTimeout(() => {
                if (query.length >= 2) {
                    console.log('Iniciando búsqueda para:', query);
                    searchProducts(query, (products) => {
                        showSuggestions(target, fieldDropdowns.get(target), products);
                    });
                } else {
                    const dropdown = fieldDropdowns.get(target);
                    if (dropdown) {
                        dropdown.style.display = 'none';
                    }
                }
            }, 300);
            
            fieldTimeouts.set(fieldKey, timeoutId);
        }
    });
    
    // Event delegation para Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            fieldDropdowns.forEach(dropdown => {
                dropdown.style.display = 'none';
            });
        }
    });
    
    // Event delegation para clicks fuera
    document.addEventListener('click', function(e) {
        fieldDropdowns.forEach((dropdown, input) => {
            if (!input.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });
    });
    
    // Limpiar dropdowns de campos eliminados
    setInterval(() => {
        fieldDropdowns.forEach((dropdown, input) => {
            if (!document.contains(input)) {
                dropdown.remove();
                fieldDropdowns.delete(input);
                console.log('Dropdown de campo eliminado limpiado');
            }
        });
    }, 5000);
    
    console.log('Sistema de autocompletado con event delegation puro inicializado');    // No necesita inicialización especial - event delegation funciona inmediatamente
    
})();