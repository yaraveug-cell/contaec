// JavaScript agresivo para forzar el ancho del campo producto
(function() {
    'use strict';
    
    function forceProductWidth() {
        console.log('[PRODUCTO] Buscando campos producto...');
        
        // Buscar todos los selects de producto en líneas de factura
        const productSelects = document.querySelectorAll('select[name*="product"]');
        console.log(`[PRODUCTO] Encontrados ${productSelects.length} selects de producto`);
        
        productSelects.forEach((select, index) => {
            console.log(`[PRODUCTO] Procesando select ${index + 1}:`, select);
            
            // Aplicar estilos inline directamente al select
            select.style.width = '400px';
            select.style.minWidth = '400px';
            select.style.maxWidth = '500px';
            select.style.border = '3px solid red';
            select.style.backgroundColor = '#ffffcc';
            
            // Buscar el contenedor td y aplicar estilos
            const td = select.closest('td');
            if (td) {
                td.style.width = '450px';
                td.style.minWidth = '450px';
                td.style.maxWidth = '550px';
                td.style.border = '2px solid blue';
                console.log(`[PRODUCTO] TD configurado:`, td);
            }
            
            // Si es un Select2, también configurar su contenedor
            const select2Container = select.nextElementSibling;
            if (select2Container && select2Container.classList.contains('select2-container')) {
                select2Container.style.width = '400px';
                select2Container.style.minWidth = '400px';
                select2Container.style.border = '2px solid green';
                console.log(`[PRODUCTO] Select2 container configurado:`, select2Container);
                
                // Configurar el elemento de selección dentro de Select2
                const selection = select2Container.querySelector('.select2-selection');
                if (selection) {
                    selection.style.width = '100%';
                    selection.style.minWidth = '400px';
                    selection.style.border = '1px solid orange';
                }
            }
        });
    }
    
    // Ejecutar inmediatamente
    forceProductWidth();
    
    // Ejecutar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', forceProductWidth);
    }
    
    // Ejecutar periódicamente para cubrir contenido dinámico
    setInterval(forceProductWidth, 1000);
    
    // Observar cambios en el DOM para nuevas líneas
    if (window.MutationObserver) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Esperar un poco para que Django termine de procesar
                    setTimeout(forceProductWidth, 100);
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    console.log('[PRODUCTO] Script agresivo cargado y ejecutándose');
})();