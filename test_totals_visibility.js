// 🧪 TEST: VERIFICAR VISIBILIDAD DE SECCIÓN TOTALES
// Ejecutar en ambas vistas:
// CREAR: http://127.0.0.1:8000/admin/invoicing/invoice/add/
// EDITAR: http://127.0.0.1:8000/admin/invoicing/invoice/X/change/ (donde X es el ID)

console.log('👁️ TEST: VISIBILIDAD SECCIÓN TOTALES');
console.log('=' .repeat(50));

function testTotalsVisibility() {
    
    // 1. Detectar modo actual
    const url = window.location.pathname;
    const isAddMode = url.includes('/add/');
    const isChangeMode = url.includes('/change/') || /\/\d+\//.test(url);
    
    console.log('\n🔍 DETECTANDO MODO:');
    console.log(`   URL: ${url}`);
    console.log(`   Modo Añadir: ${isAddMode ? '✅' : '❌'}`);
    console.log(`   Modo Modificar: ${isChangeMode ? '✅' : '❌'}`);
    
    // 2. Buscar sección de totales
    console.log('\n📊 BUSCANDO SECCIÓN TOTALES:');
    
    // Buscar fieldset que contenga los campos de totales
    const totalsFieldset = Array.from(document.querySelectorAll('fieldset')).find(fieldset => {
        const legend = fieldset.querySelector('h2');
        return legend && legend.textContent.toLowerCase().includes('totales');
    });
    
    // Buscar campos individuales de totales
    const subtotalField = document.querySelector('input[name="subtotal"]') || 
                         document.querySelector('#id_subtotal');
    const taxField = document.querySelector('input[name="tax_amount"]') || 
                    document.querySelector('#id_tax_amount');
    const totalField = document.querySelector('input[name="total"]') || 
                      document.querySelector('#id_total');
    
    console.log(`   Fieldset "Totales": ${totalsFieldset ? '✅ Encontrado' : '❌ No encontrado'}`);
    console.log(`   Campo Subtotal: ${subtotalField ? '✅ Presente' : '❌ Ausente'}`);
    console.log(`   Campo Impuestos: ${taxField ? '✅ Presente' : '❌ Ausente'}`);
    console.log(`   Campo Total: ${totalField ? '✅ Presente' : '❌ Ausente'}`);
    
    // 3. Verificar visibilidad según el modo
    console.log('\n🎯 VERIFICACIÓN DE COMPORTAMIENTO:');
    
    if (isAddMode) {
        // En modo AÑADIR, la sección NO debería aparecer
        console.log('   📝 MODO: Añadir Factura');
        
        if (!totalsFieldset && !subtotalField && !taxField && !totalField) {
            console.log('   ✅ CORRECTO: Sección Totales oculta');
            console.log('   ✅ Los campos de totales no están presentes');
        } else {
            console.log('   ❌ ERROR: Sección Totales visible cuando no debería');
            if (totalsFieldset) console.log('   ❌ Fieldset presente');
            if (subtotalField) console.log('   ❌ Campo subtotal presente');
            if (taxField) console.log('   ❌ Campo impuestos presente');
            if (totalField) console.log('   ❌ Campo total presente');
        }
        
    } else if (isChangeMode) {
        // En modo MODIFICAR, la sección SÍ debería aparecer
        console.log('   ✏️ MODO: Modificar Factura');
        
        const allFieldsPresent = subtotalField && taxField && totalField;
        
        if (totalsFieldset && allFieldsPresent) {
            console.log('   ✅ CORRECTO: Sección Totales visible');
            console.log('   ✅ Todos los campos de totales presentes');
            
            // Verificar valores actuales
            console.log('\n💰 VALORES ACTUALES:');
            console.log(`   Subtotal: $${subtotalField.value || '0.00'}`);
            console.log(`   Impuestos: $${taxField.value || '0.00'}`);
            console.log(`   Total: $${totalField.value || '0.00'}`);
            
        } else {
            console.log('   ❌ ERROR: Sección Totales no visible cuando debería');
            if (!totalsFieldset) console.log('   ❌ Fieldset ausente');
            if (!subtotalField) console.log('   ❌ Campo subtotal ausente');
            if (!taxField) console.log('   ❌ Campo impuestos ausente');
            if (!totalField) console.log('   ❌ Campo total ausente');
        }
        
    } else {
        console.log('   ⚠️ MODO DESCONOCIDO: No se pudo determinar el modo');
    }
    
    // 4. Verificar calculadora según el modo
    console.log('\n🧮 VERIFICACIÓN DE CALCULADORA:');
    
    const calculatorExists = typeof window.calculateInvoiceTotals === 'function';
    console.log(`   Función disponible: ${calculatorExists ? '✅' : '❌'}`);
    
    if (calculatorExists && isChangeMode) {
        console.log('   ✅ Calculadora debería estar activa en modo edición');
        
        // Probar calculadora
        console.log('   🔄 Ejecutando cálculo de prueba...');
        window.calculateInvoiceTotals();
        
    } else if (isAddMode) {
        console.log('   ℹ️ En modo creación, solo cálculo de líneas individuales');
    }
    
    // 5. Resultado final
    console.log('\n🏆 RESUMEN:');
    
    const correctBehavior = 
        (isAddMode && !totalsFieldset && !subtotalField) ||
        (isChangeMode && totalsFieldset && subtotalField);
    
    if (correctBehavior) {
        console.log('🎉 ¡COMPORTAMIENTO CORRECTO!');
        if (isAddMode) {
            console.log('✅ Modo Añadir: Totales ocultos correctamente');
        } else {
            console.log('✅ Modo Modificar: Totales visibles correctamente');
        }
    } else {
        console.log('⚠️ Comportamiento necesita ajustes');
    }
    
    // 6. Instrucciones
    console.log('\n📋 INSTRUCCIONES:');
    console.log('• Para probar modo AÑADIR: /admin/invoicing/invoice/add/');
    console.log('• Para probar modo MODIFICAR: Abrir factura existente');
    console.log('• La sección Totales solo debe aparecer al MODIFICAR');
}

// Ejecutar test
setTimeout(testTotalsVisibility, 1000);

console.log('\n⏰ Analizando visibilidad de sección Totales...');