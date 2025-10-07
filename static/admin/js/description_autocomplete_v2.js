/**
 * Autocompletado de descripción de productos - Versión 2
 * Usa event delegation para funcionar en todas las líneas dinámicas
 */
(function() {
    'use strict';
    
    let searchTimeouts = new Map(); // Timeouts individuales por campo
    let dropdowns = new Map(); // Dropdowns por campo
    
    // Función para buscar productos
    function searchProducts(query, callback) {
        if (!query || query.length < 2) {
            callback([]);
            return;
        }
        
        fetch('/invoicing/ajax/product-description-autocomplete/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: 'query=' + encodeURIComponent(query)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Productos encontrados:', data.results?.length || 0);
            callback(data.results || []);
        })
        .catch(error => {
            console.error('Error en búsqueda:', error);
            callback([]);
        });
    }
    
    // Función para crear dropdown si no existe
    function getOrCreateDropdown(input) {
        if (dropdowns.has(input)) {
            return dropdowns.get(input);
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
        dropdowns.set(input, dropdown);
        
        return dropdown;
    }
    
    // Función para mostrar sugerencias
    function showSuggestions(input, products) {
        const dropdown = getOrCreateDropdown(input);
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
            
            // Click handler
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
        
        // Actualizar campo descripción
        descriptionInput.value = productData.text;
        
        // Encontrar y actualizar otros campos de la misma fila
        const productField = row.querySelector('select[name*="product"]');
        const quantityField = row.querySelector('input[name*="quantity"]');
        const unitPriceField = row.querySelector('input[name*="unit_price"]');
        const discountField = row.querySelector('input[name*="discount_percentage"]');
        const ivaField = row.querySelector('input[name*="iva_rate"]');
        
        if (productField && productData.id) {
            productField.value = productData.id;
            // Trigger change event para actualizar otros scripts
            productField.dispatchEvent(new Event('change', { bubbles: true }));
        }
        
        if (unitPriceField && productData.sale_price) {
            unitPriceField.value = productData.sale_price;
            unitPriceField.dispatchEvent(new Event('input', { bubbles: true }));
        }
        
        if (ivaField && productData.iva_rate) {
            ivaField.value = productData.iva_rate;
            ivaField.dispatchEvent(new Event('input', { bubbles: true }));
        }
        
        // Trigger calculation
        if (window.calculateLineTotal) {
            window.calculateLineTotal(row);
        }
        
        console.log('Campos actualizados para producto:', productData.text);
    }
    
    // Event delegation para input en campos descripción
    document.addEventListener('input', function(e) {
        const target = e.target;
        
        // Verificar si es un campo de descripción
        if (target.tagName === 'INPUT' && target.name && target.name.includes('description')) {
            console.log('Input detectado en campo descripción:', target.name);
            
            const query = target.value.trim();
            const fieldId = target.name + '_' + (target.closest('tr')?.rowIndex || Math.random());
            
            // Limpiar timeout anterior para este campo
            if (searchTimeouts.has(fieldId)) {
                clearTimeout(searchTimeouts.get(fieldId));
            }
            
            // Establecer nuevo timeout
            const timeoutId = setTimeout(() => {
                if (query.length >= 2) {
                    console.log('Iniciando búsqueda para:', query);
                    searchProducts(query, (products) => {
                        showSuggestions(target, products);
                    });
                } else {
                    // Ocultar dropdown si query es muy corta
                    const dropdown = dropdowns.get(target);
                    if (dropdown) {
                        dropdown.style.display = 'none';
                    }
                }
            }, 300);
            
            searchTimeouts.set(fieldId, timeoutId);
        }
    });
    
    // Event delegation para keydown (Escape)
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            // Ocultar todos los dropdowns
            dropdowns.forEach((dropdown) => {
                dropdown.style.display = 'none';
            });
        }
    });
    
    // Event delegation para clicks fuera del dropdown
    document.addEventListener('click', function(e) {
        dropdowns.forEach((dropdown, input) => {
            if (!input.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });
    });
    
    // Limpiar dropdowns huérfanos periódicamente
    setInterval(() => {
        dropdowns.forEach((dropdown, input) => {
            if (!document.contains(input)) {
                dropdown.remove();
                dropdowns.delete(input);
                console.log('Dropdown huérfano eliminado');
            }
        });
    }, 5000);
    
    console.log('Sistema de autocompletado de descripción v2 inicializado con event delegation');
    
})();