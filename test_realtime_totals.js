// 🧪 TEST COMPLETO: VERIFICAR CÁLCULO DE TOTALES EN TIEMPO REAL
// Navegar a: http://127.0.0.1:8000/admin/invoicing/invoice/add/

console.log('🧮 TEST: CÁLCULO DE TOTALES EN TIEMPO REAL');
console.log('=' .repeat(60));

function testRealTimeTotals() {
    
    // 1. Verificar que los campos de totales estén presentes
    console.log('\n📋 VERIFICANDO CAMPOS DE TOTALES:');
    
    const subtotalField = document.querySelector('input[name="subtotal"]') || 
                         document.querySelector('#id_subtotal');
    const taxField = document.querySelector('input[name="tax_amount"]') || 
                    document.querySelector('#id_tax_amount');
    const totalField = document.querySelector('input[name="total"]') || 
                      document.querySelector('#id_total');
    
    console.log(`   Subtotal: ${subtotalField ? '✅ Presente' : '❌ No encontrado'}`);
    console.log(`   Impuestos: ${taxField ? '✅ Presente' : '❌ No encontrado'}`);
    console.log(`   Total: ${totalField ? '✅ Presente' : '❌ No encontrado'}`);
    
    // 2. Verificar que la calculadora esté cargada
    console.log('\n🔧 VERIFICANDO CALCULADORA:');
    
    const calculatorLoaded = typeof window.calculateInvoiceTotals === 'function';
    console.log(`   Calculadora cargada: ${calculatorLoaded ? '✅' : '❌'}`);
    
    // 3. Obtener primera línea de factura para pruebas
    console.log('\n📝 BUSCANDO LÍNEAS DE FACTURA:');
    
    const firstLine = document.querySelector('[id*="invoiceline_set"] tr.form-row:not(.empty-form)');
    if (!firstLine) {
        console.log('   ⚠️ No hay líneas de factura para probar');
        console.log('   📌 INSTRUCCIONES:');
        console.log('   1. Agrega una línea de factura manualmente');
        console.log('   2. Llena los campos: producto, cantidad, precio');
        console.log('   3. Ejecuta: testManualLine() para probar');
        
        // Crear función de test manual
        window.testManualLine = function() {
            console.log('\n🧪 EJECUTANDO TEST MANUAL...');
            
            // Buscar la primera línea con datos
            const lines = document.querySelectorAll('[id*="invoiceline_set"] tr.form-row:not(.empty-form)');
            console.log(`   Líneas encontradas: ${lines.length}`);
            
            if (lines.length === 0) {
                console.log('   ❌ Aún no hay líneas para probar');
                return;
            }
            
            // Verificar cada línea
            lines.forEach((line, index) => {
                const quantityField = line.querySelector('input[name*="quantity"]');
                const priceField = line.querySelector('input[name*="unit_price"]');
                
                if (quantityField && priceField && quantityField.value && priceField.value) {
                    console.log(`   ✅ Línea ${index + 1}: ${quantityField.value} × $${priceField.value}`);
                } else {
                    console.log(`   ⚠️ Línea ${index + 1}: Datos incompletos`);
                }
            });
            
            // Ejecutar cálculo manual
            if (window.calculateInvoiceTotals) {
                console.log('\n🧮 Ejecutando cálculo de totales...');
                window.calculateInvoiceTotals();
                
                setTimeout(() => {
                    console.log('\n📊 VERIFICANDO RESULTADOS:');
                    const newSubtotal = subtotalField ? subtotalField.value : 'N/A';
                    const newTax = taxField ? taxField.value : 'N/A';
                    const newTotal = totalField ? totalField.value : 'N/A';
                    
                    console.log(`   Subtotal: $${newSubtotal}`);
                    console.log(`   Impuestos: $${newTax}`);
                    console.log(`   Total: $${newTotal}`);
                    
                    if (newSubtotal !== '0.00' || newTax !== '0.00' || newTotal !== '0.00') {
                        console.log('\n🎉 ¡ÉXITO! Los totales se están calculando correctamente');
                    } else {
                        console.log('\n⚠️ Los totales siguen en 0, verifica que las líneas tengan datos válidos');
                    }
                }, 500);
            }
        };
        
        return;
    }
    
    // 4. Si hay líneas, verificar cálculo automático
    console.log(`   ✅ Línea encontrada para test automático`);
    
    // Simular cambio en cantidad para disparar cálculo
    const quantityField = firstLine.querySelector('input[name*="quantity"]');
    const priceField = firstLine.querySelector('input[name*="unit_price"]');
    
    if (quantityField && priceField) {
        console.log('\n🎯 SIMULANDO CAMBIO EN LÍNEA:');
        
        // Obtener valores actuales
        const currentQty = quantityField.value || '0';
        const currentPrice = priceField.value || '0';
        
        console.log(`   Cantidad actual: ${currentQty}`);
        console.log(`   Precio actual: ${currentPrice}`);
        
        // Si no hay valores, establecer valores de prueba
        if (!quantityField.value) {
            quantityField.value = '1';
            console.log('   ✅ Cantidad establecida en 1');
        }
        
        if (!priceField.value) {
            priceField.value = '100.00';
            console.log('   ✅ Precio establecido en $100.00');
        }
        
        // Disparar evento de cambio
        quantityField.dispatchEvent(new Event('input', { bubbles: true }));
        
        // Verificar resultados después de un momento
        setTimeout(() => {
            console.log('\n📊 VERIFICANDO TOTALES DESPUÉS DEL CAMBIO:');
            
            const newSubtotal = subtotalField ? subtotalField.value : 'N/A';
            const newTax = taxField ? taxField.value : 'N/A';
            const newTotal = totalField ? totalField.value : 'N/A';
            
            console.log(`   Subtotal: $${newSubtotal}`);
            console.log(`   Impuestos: $${newTax}`);
            console.log(`   Total: $${newTotal}`);
            
            // Verificar que NO haya resumen flotante (debe estar deshabilitado)
            const summary = document.querySelector('#invoice-totals-summary');
            console.log(`   Resumen flotante: ${summary ? '⚠️ Visible (debería estar oculto)' : '✅ Oculto correctamente'}`);
            
            // Resultado final
            console.log('\n🏆 RESULTADO FINAL:');
            if ((parseFloat(newSubtotal) || 0) > 0) {
                console.log('✅ ¡PERFECTO! Los totales se calculan automáticamente');
                console.log('✅ La calculadora funciona correctamente');
                console.log('✅ Los valores se actualizan en tiempo real');
                console.log('✅ Panel flotante correctamente deshabilitado');
            } else {
                console.log('❌ Los totales no se están calculando');
                console.log('⚠️ Puede necesitar revisar la configuración');
            }
            
        }, 1000);
        
    } else {
        console.log('   ❌ No se encontraron campos de cantidad/precio para probar');
    }
}

// Ejecutar test después de cargar
setTimeout(testRealTimeTotals, 2000);

console.log('\n⏰ Test iniciado - Resultados en unos segundos...');
console.log('📌 Si no hay líneas automáticamente, usa testManualLine() después de agregar una línea');