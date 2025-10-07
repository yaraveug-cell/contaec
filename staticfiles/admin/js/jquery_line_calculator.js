// Calculadora de totales usando jQuery (respaldo)
(function($) {
    'use strict';
    
    console.log('[JQUERY_CALCULATOR] 🚀 Iniciando calculadora con jQuery...');
    
    function calculateTotal() {
        console.log('[JQUERY_CALCULATOR] 🧮 Calculando totales...');
        
        // Buscar todas las filas que NO sean la plantilla de añadir
        $('tr.form-row').not('.add-row').each(function(index) {
            var $row = $(this);
            console.log(`[JQUERY_CALCULATOR] 📝 Procesando fila ${index + 1}`);
            
            // Buscar campos en la fila actual
            var $quantity = $row.find('input[name*="quantity"]');
            var $price = $row.find('input[name*="unit_price"]');
            var $discount = $row.find('input[name*="discount"]');
            var $iva = $row.find('input[name*="iva_rate"]');
            var $total = $row.find('input[name*="line_total"]');
            
            console.log(`[JQUERY_CALCULATOR] 🔍 Campos encontrados en fila ${index + 1}:`, {
                quantity: $quantity.length ? $quantity.attr('name') : 'NO',
                price: $price.length ? $price.attr('name') : 'NO', 
                discount: $discount.length ? $discount.attr('name') : 'NO',
                iva: $iva.length ? $iva.attr('name') : 'NO',
                total: $total.length ? $total.attr('name') : 'NO'
            });
            
            // Solo calcular si tenemos los campos básicos
            if ($quantity.length && $price.length && $total.length) {
                var quantity = parseFloat($quantity.val()) || 0;
                var unitPrice = parseFloat($price.val()) || 0;
                var discount = parseFloat($discount.val()) || 0;
                var ivaRate = parseFloat($iva.val()) || 15;
                
                // Cálculo
                var subtotal = quantity * unitPrice;
                var discountAmount = subtotal * (discount / 100);
                var subtotalAfterDiscount = subtotal - discountAmount;
                var ivaAmount = subtotalAfterDiscount * (ivaRate / 100);
                var lineTotal = subtotalAfterDiscount + ivaAmount;
                
                // Actualizar el campo total
                var finalTotal = lineTotal.toFixed(2);
                $total.val(finalTotal);
                
                console.log(`[JQUERY_CALCULATOR] ✅ Fila ${index + 1} calculada: ${quantity} x ${unitPrice} - ${discount}% + ${ivaRate}% IVA = ${finalTotal}`);
            }
        });
    }
    
    function attachListeners() {
        console.log('[JQUERY_CALCULATOR] 🔗 Añadiendo listeners...');
        
        // Usar delegación de eventos para campos dinámicos
        $(document).on('input change keyup blur', 'input[name*="quantity"], input[name*="unit_price"], input[name*="discount"], input[name*="iva_rate"]', function() {
            console.log('[JQUERY_CALCULATOR] 🔥 Campo cambiado:', $(this).attr('name'));
            setTimeout(calculateTotal, 50);
        });
        
        // Calcular al cargar la página
        setTimeout(calculateTotal, 500);
    }
    
    // Inicializar cuando jQuery y el DOM estén listos
    $(document).ready(function() {
        console.log('[JQUERY_CALCULATOR] 📋 DOM listo, inicializando...');
        attachListeners();
    });
    
    // También inicializar cuando la ventana se cargue completamente
    $(window).on('load', function() {
        console.log('[JQUERY_CALCULATOR] 🌐 Ventana cargada, reinicializando...');
        setTimeout(attachListeners, 1000);
    });
    
})(django.jQuery || jQuery || $);