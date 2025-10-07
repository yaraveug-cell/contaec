// Calculadora SIMPLE de totales - Optimizada
document.addEventListener('DOMContentLoaded', function() {
    
    let calculadoraInicializada = false;
    
    function calcularTotal(fila) {
        // Reducir logs - solo cuando sea necesario
        if (!fila) return;
        
        // Buscar inputs en la fila
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
        
        if (totalField && (cantidad > 0 && precio > 0)) {
            // Cálculo simple
            const subtotal = cantidad * precio;
            const conDescuento = subtotal * (1 - descuento / 100);
            const conIva = conDescuento * (1 + iva / 100);
            const total = conIva.toFixed(2);
            
            // Solo actualizar si cambió
            if (totalField.value !== total) {
                // Total actualizado
                
                // Remover readonly temporalmente
                totalField.removeAttribute('readonly');
                totalField.value = total;
                totalField.setAttribute('readonly', 'readonly');
                
                // Disparar evento
                totalField.dispatchEvent(new Event('change'));
            }
        } else if (totalField && (cantidad === 0 || precio === 0)) {
            // Limpiar total si no hay cantidad o precio
            if (totalField.value !== '0.00') {
                totalField.removeAttribute('readonly');
                totalField.value = '0.00';
                totalField.setAttribute('readonly', 'readonly');
            }
        }
    }
    
    function inicializar() {
        if (calculadoraInicializada) return;
        
        const filas = document.querySelectorAll('.form-row.dynamic-lines');
        
        filas.forEach((fila, index) => {
            // Saltar la fila template
            if (fila.classList.contains('empty-form')) return;
            
            // Marcar como configurada
            if (fila.hasAttribute('data-calculator-attached')) return;
            fila.setAttribute('data-calculator-attached', 'true');
            
            // Buscar campos de entrada
            const camposCalcular = fila.querySelectorAll('input[name*="quantity"], input[name*="unit_price"], input[name*="discount"], input[name*="iva_rate"]');
            
            camposCalcular.forEach(campo => {
                // Listener añadido
                
                // Solo eventos esenciales
                campo.addEventListener('input', () => {
                    calcularTotal(fila);
                });
                campo.addEventListener('change', () => {
                    calcularTotal(fila);
                });
            });
        });
        
        calculadoraInicializada = true;
        console.log('✅ CALCULADORA SIMPLE: Configurada');
    }
    
    // Ejecutar inicial
    setTimeout(inicializar, 500);
    
    // Observer para nuevas filas
    const observer = new MutationObserver(() => {
        setTimeout(inicializar, 100);
    });
    
    const targetNode = document.querySelector('#lines-group, .inline-group');
    if (targetNode) {
        observer.observe(targetNode, { childList: true, subtree: true });
    }
    
    console.log('✅ CALCULADORA SIMPLE: Lista');
});