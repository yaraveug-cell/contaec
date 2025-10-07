/**
 * Validación de stock en tiempo real para líneas de factura
 * Verifica stock disponible cuando se cambia la cantidad
 */

(function() {
    'use strict';

    class StockValidator {
        constructor() {
            this.init();
        }

        init() {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.setup());
            } else {
                this.setup();
            }
        }

        setup() {
            console.log('🔍 Iniciando validador de stock...');
            
            // Validar stock en líneas existentes y nuevas
            this.attachValidators();
            
            // Observar cambios en el DOM para líneas agregadas dinámicamente
            this.observeNewLines();
        }

        attachValidators() {
            // Validar líneas existentes
            const quantityFields = document.querySelectorAll('input[name*="quantity"]');
            
            quantityFields.forEach(field => {
                if (!field.dataset.stockValidatorAttached) {
                    this.attachQuantityValidator(field);
                    field.dataset.stockValidatorAttached = 'true';
                }
            });
        }

        attachQuantityValidator(quantityField) {
            const row = quantityField.closest('.dynamic-invoiceline_set') || quantityField.closest('tr');
            if (!row) return;

            const productField = row.querySelector('select[name*="product"]');
            if (!productField) return;

            // Validar cuando cambie la cantidad
            quantityField.addEventListener('blur', () => {
                this.validateStock(productField, quantityField);
            });

            quantityField.addEventListener('input', () => {
                // Limpiar mensaje de error previo al escribir
                this.clearStockError(quantityField);
            });

            // Validar cuando cambie el producto
            productField.addEventListener('change', () => {
                this.validateStock(productField, quantityField);
            });
        }

        validateStock(productField, quantityField) {
            const productId = productField.value;
            const quantity = parseFloat(quantityField.value) || 0;

            if (!productId || quantity <= 0) {
                this.clearStockError(quantityField);
                return;
            }

            // Hacer petición AJAX para verificar stock
            this.checkProductStock(productId, quantity, quantityField);
        }

        checkProductStock(productId, quantity, quantityField) {
            fetch(`/admin/inventory/product/${productId}/stock/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                }
            })
            .then(response => {
                if (!response.ok) {
                    // Si no existe el endpoint, usar validación básica
                    return null;
                }
                return response.json();
            })
            .then(data => {
                if (data && data.manages_inventory && data.product_type === 'product') {
                    if (quantity > data.current_stock) {
                        this.showStockError(
                            quantityField,
                            `⚠️ Stock insuficiente. Disponible: ${data.current_stock}, Solicitado: ${quantity}`
                        );
                    } else {
                        this.clearStockError(quantityField);
                        this.showStockInfo(quantityField, `✅ Stock disponible: ${data.current_stock}`);
                    }
                } else {
                    this.clearStockError(quantityField);
                }
            })
            .catch(error => {
                console.log('ℹ️ Validación de stock no disponible:', error.message);
                // No mostrar error si el endpoint no existe
            });
        }

        showStockError(quantityField, message) {
            this.clearStockError(quantityField);

            // Crear elemento de error
            const errorDiv = document.createElement('div');
            errorDiv.className = 'stock-error';
            errorDiv.style.cssText = `
                color: #e74c3c;
                font-size: 12px;
                margin-top: 3px;
                padding: 5px 8px;
                background-color: #fdf2f2;
                border: 1px solid #fecaca;
                border-radius: 4px;
                display: flex;
                align-items: center;
                gap: 5px;
            `;
            errorDiv.innerHTML = `<span style="font-weight: bold;">⚠️</span> ${message}`;

            // Insertar después del campo
            quantityField.parentNode.appendChild(errorDiv);

            // Marcar campo con borde rojo
            quantityField.style.borderColor = '#e74c3c';
            quantityField.style.backgroundColor = '#fdf2f2';
        }

        showStockInfo(quantityField, message) {
            // Remover errores previos
            this.clearStockError(quantityField);

            // Crear elemento de información
            const infoDiv = document.createElement('div');
            infoDiv.className = 'stock-info';
            infoDiv.style.cssText = `
                color: #27ae60;
                font-size: 12px;
                margin-top: 3px;
                padding: 3px 8px;
                background-color: #f8fff8;
                border: 1px solid #c3e6cb;
                border-radius: 4px;
                display: flex;
                align-items: center;
                gap: 5px;
            `;
            infoDiv.innerHTML = message;

            // Insertar después del campo
            quantityField.parentNode.appendChild(infoDiv);

            // Marcar campo con borde verde
            quantityField.style.borderColor = '#27ae60';
            quantityField.style.backgroundColor = '#f8fff8';

            // Remover mensaje después de 3 segundos
            setTimeout(() => {
                if (infoDiv.parentNode) {
                    infoDiv.parentNode.removeChild(infoDiv);
                }
                this.resetFieldStyle(quantityField);
            }, 3000);
        }

        clearStockError(quantityField) {
            // Remover mensajes existentes
            const errorDiv = quantityField.parentNode.querySelector('.stock-error');
            const infoDiv = quantityField.parentNode.querySelector('.stock-info');

            if (errorDiv) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
            if (infoDiv) {
                infoDiv.parentNode.removeChild(infoDiv);
            }

            this.resetFieldStyle(quantityField);
        }

        resetFieldStyle(quantityField) {
            quantityField.style.borderColor = '';
            quantityField.style.backgroundColor = '';
        }

        observeNewLines() {
            // Observar cambios en el DOM para líneas agregadas dinámicamente
            const observer = new MutationObserver((mutations) => {
                let shouldReattach = false;

                mutations.forEach((mutation) => {
                    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                        mutation.addedNodes.forEach((node) => {
                            if (node.nodeType === 1 && // Element node
                                (node.classList.contains('dynamic-invoiceline_set') || 
                                 node.querySelector && node.querySelector('input[name*="quantity"]'))) {
                                shouldReattach = true;
                            }
                        });
                    }
                });

                if (shouldReattach) {
                    setTimeout(() => this.attachValidators(), 100);
                }
            });

            // Observar el contenedor de líneas de factura
            const linesContainer = document.querySelector('#invoiceline_set-group') || 
                                 document.querySelector('.inline-group');
            
            if (linesContainer) {
                observer.observe(linesContainer, {
                    childList: true,
                    subtree: true
                });
            }
        }
    }

    // Inicializar validador
    new StockValidator();

    // Hacer disponible globalmente para debugging
    window.StockValidator = StockValidator;

    console.log('✅ Validador de stock cargado');

})();