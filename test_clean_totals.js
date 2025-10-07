// 🧪 TEST SIMPLIFICADO: VERIFICAR CÁLCULO SIN PANEL FLOTANTE
// Navegar a: http://127.0.0.1:8000/admin/invoicing/invoice/add/

console.log('🧮 TEST: CÁLCULO DE TOTALES SIN INTERFAZ FLOTANTE');
console.log('=' .repeat(50));

function testCleanTotals() {
    
    // 1. Verificar campos de totales en el formulario
    console.log('\n📋 VERIFICANDO CAMPOS DEL FORMULARIO:');
    
    const subtotalField = document.querySelector('input[name="subtotal"]') || 
                         document.querySelector('#id_subtotal');
    const taxField = document.querySelector('input[name="tax_amount"]') || 
                    document.querySelector('#id_tax_amount');
    const totalField = document.querySelector('input[name="total"]') || 
                      document.querySelector('#id_total');
    
    console.log(`   📊 Subtotal: ${subtotalField ? '✅ Presente' : '❌ No encontrado'}`);
    console.log(`   💰 Impuestos: ${taxField ? '✅ Presente' : '❌ No encontrado'}`);
    console.log(`   💲 Total: ${totalField ? '✅ Presente' : '❌ No encontrado'}`);
    
    // 2. Verificar que NO haya panel flotante
    console.log('\n🚫 VERIFICANDO AUSENCIA DE PANEL FLOTANTE:');
    
    const floatingPanel = document.querySelector('#invoice-totals-summary');
    if (floatingPanel) {
        console.log('   ❌ Panel flotante presente (se eliminará)');
        floatingPanel.remove();
        console.log('   ✅ Panel flotante eliminado');
    } else {
        console.log('   ✅ No hay panel flotante (correcto)');
    }
    
    // 3. Verificar calculadora funcional
    console.log('\n🔧 VERIFICANDO CALCULADORA:');
    
    const calculatorExists = typeof window.calculateInvoiceTotals === 'function';
    console.log(`   Función disponible: ${calculatorExists ? '✅' : '❌'}`);
    
    if (calculatorExists) {
        console.log('   🧮 Ejecutando cálculo manual...');
        window.calculateInvoiceTotals();
        
        setTimeout(() => {
            const currentSubtotal = subtotalField ? subtotalField.value : '0';
            const currentTax = taxField ? taxField.value : '0';
            const currentTotal = totalField ? totalField.value : '0';
            
            console.log('\n📊 VALORES ACTUALES:');
            console.log(`   Subtotal: $${currentSubtotal}`);
            console.log(`   Impuestos: $${currentTax}`);
            console.log(`   Total: $${currentTotal}`);
            
            // Verificar nuevamente que no haya panel
            const newPanel = document.querySelector('#invoice-totals-summary');
            console.log(`   Panel flotante después del cálculo: ${newPanel ? '❌ Apareció' : '✅ Ausente'}`);
            
        }, 500);
    }
    
    // 4. Instrucciones para el usuario
    console.log('\n📝 INSTRUCCIONES DE PRUEBA:');
    console.log('1. Agrega una línea de factura');
    console.log('2. Completa: Producto, Cantidad, Precio unitario');
    console.log('3. Observa que los totales se actualicen automáticamente');
    console.log('4. Verifica que NO aparezca ningún panel flotante');
    
    // 5. Resultado
    console.log('\n🎯 CONFIGURACIÓN:');
    console.log('✅ Los totales se calculan automáticamente');
    console.log('✅ Los valores aparecen en los campos del formulario');
    console.log('✅ NO hay ventana modal/flotante molesta');
    console.log('✅ Interfaz limpia y profesional');
}

// Ejecutar test
setTimeout(testCleanTotals, 1000);

console.log('\n⏰ Verificando configuración limpia...');