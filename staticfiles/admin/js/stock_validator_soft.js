// Validador de stock no invasivo usando mensajes de Django Admin
document.addEventListener('DOMContentLoaded', function() {
    // Stock validator iniciado
    
    // Función para crear mensaje de stock como elemento DOM
    function mostrarMensajeStock(mensaje, tipo = 'info') {
        // Remover mensajes de stock previos
        const mensajesPrevios = document.querySelectorAll('.stock-message');
        mensajesPrevios.forEach(msg => msg.remove());
        
        // Crear elemento de mensaje
        const messageDiv = document.createElement('div');
        messageDiv.className = `messagelist stock-message`;
        
        const messageItem = document.createElement('div');
        let claseCSS = 'info';
        let icono = 'ℹ️';
        
        if (tipo === 'warning') {
            claseCSS = 'warning';
            icono = '⚠️';
        } else if (tipo === 'error') {
            claseCSS = 'error';
            icono = '❌';
        }
        
        messageItem.className = claseCSS;
        messageItem.innerHTML = `${icono} ${mensaje}`;
        
        messageDiv.appendChild(messageItem);
        
        // Insertar después del título de la página
        const content = document.querySelector('#content') || document.querySelector('.colM');
        if (content) {
            const titulo = content.querySelector('h1') || content.firstElementChild;
            if (titulo && titulo.nextSibling) {
                content.insertBefore(messageDiv, titulo.nextSibling);
            } else {
                content.insertBefore(messageDiv, content.firstChild);
            }
        }
        
        // Auto-remover después de 8 segundos
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 8000);
    }
    
    // Función para verificar stock de una línea
    async function verificarStock(fila) {
        try {
            const inputs = fila.querySelectorAll('input');
            let productoId = null, cantidad = 0;
            
            inputs.forEach(input => {
                if (input.name.includes('product') && input.value) {
                    productoId = input.value;
                } else if (input.name.includes('quantity') && input.value) {
                    cantidad = parseFloat(input.value) || 0;
                }
            });
            
            if (!productoId || !cantidad || cantidad <= 0) {
                return; // No hay datos suficientes para verificar
            }
            
            // Hacer petición AJAX para verificar stock
            const url = `/admin/invoicing/invoice/check-product-stock/${productoId}/`;
            const params = new URLSearchParams({ quantity: cantidad });
            
            const response = await fetch(`${url}?${params}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (!data.has_sufficient_stock) {
                    mostrarMensajeStock(
                        `Stock insuficiente para ${data.product_name}: Disponible ${data.available_stock}, Solicitado ${data.requested_quantity}, Faltante ${data.shortage}`,
                        'warning'
                    );
                } else if (data.available_stock - data.requested_quantity <= 5) {
                    mostrarMensajeStock(
                        `Stock bajo para ${data.product_name}: quedarán ${(data.available_stock - data.requested_quantity).toFixed(1)} unidades`,
                        'info'
                    );
                }
            }
        } catch (error) {
            // Error verificando stock
            // No mostrar error al usuario, es opcional
        }
    }
    
    // Función para añadir listeners a las filas
    function inicializarValidador() {
        const filas = document.querySelectorAll('.form-row:not(.add-row)');
        
        filas.forEach(fila => {
            const camposStock = fila.querySelectorAll('input[name*="product"], input[name*="quantity"]');
            
            camposStock.forEach(campo => {
                // Usar debounce para evitar múltiples peticiones
                let timeout;
                campo.addEventListener('change', () => {
                    clearTimeout(timeout);
                    timeout = setTimeout(() => {
                        verificarStock(fila);
                    }, 500);
                });
                
                campo.addEventListener('blur', () => {
                    clearTimeout(timeout);
                    timeout = setTimeout(() => {
                        verificarStock(fila);
                    }, 300);
                });
            });
        });
        
        // Filas configuradas
    }
    
    // Inicializar
    setTimeout(inicializarValidador, 1000);
    
    // Re-inicializar cuando se añadan nuevas filas
    const observer = new MutationObserver(() => {
        setTimeout(inicializarValidador, 500);
    });
    
    if (document.body) {
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    // Stock validator configurado
});