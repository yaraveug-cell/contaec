// 🧪 TEST: VERIFICAR CAMPOS EN LA MISMA FILA
// Navegar a: http://127.0.0.1:8000/admin/invoicing/invoice/add/ o /change/

console.log('📐 TEST: VERIFICAR LAYOUT DE CAMPOS');
console.log('=' .repeat(50));

function testFieldLayout() {
    
    // 1. Detectar modo actual
    const url = window.location.pathname;
    const isAddMode = url.includes('/add/');
    const isChangeMode = url.includes('/change/') || /\/\d+\//.test(url);
    
    console.log('\n🔍 MODO DETECTADO:');
    console.log(`   ${isAddMode ? '📝 Añadir' : '✏️ Modificar'} Factura`);
    
    // 2. Buscar sección Estado
    console.log('\n🔍 BUSCANDO SECCIÓN ESTADO:');
    
    const estadoFieldset = Array.from(document.querySelectorAll('fieldset')).find(fieldset => {
        const legend = fieldset.querySelector('h2');
        return legend && legend.textContent.toLowerCase().includes('estado');
    });
    
    if (!estadoFieldset) {
        console.log('   ❌ Sección "Estado" no encontrada');
        return;
    }
    
    console.log('   ✅ Sección "Estado" encontrada');
    
    // 3. Buscar campos dentro de la sección Estado
    console.log('\n📋 VERIFICANDO CAMPOS EN SECCIÓN ESTADO:');
    
    const statusField = estadoFieldset.querySelector('select[name="status"]') ||
                       estadoFieldset.querySelector('#id_status');
    const createdByField = estadoFieldset.querySelector('select[name="created_by"]') ||
                          estadoFieldset.querySelector('#id_created_by');
    
    console.log(`   Campo Status: ${statusField ? '✅ Presente' : '❌ Ausente'}`);
    console.log(`   Campo Creado por: ${createdByField ? '✅ Presente' : '❌ Ausente'}`);
    
    // 4. Verificar si están en la misma fila
    if (statusField && createdByField) {
        console.log('\n📐 VERIFICANDO LAYOUT (MISMA FILA):');
        
        // Buscar el contenedor común más cercano
        const statusRow = statusField.closest('.form-row') || statusField.closest('div');
        const createdByRow = createdByField.closest('.form-row') || createdByField.closest('div');
        
        const sameRow = statusRow === createdByRow || 
                       (statusRow && createdByRow && statusRow.contains(createdByField)) ||
                       (createdByRow && statusRow && createdByRow.contains(statusField));
        
        console.log(`   Misma fila: ${sameRow ? '✅ Sí' : '❌ No'}`);
        
        if (sameRow) {
            console.log('   ✅ Los campos están correctamente en la misma fila');
            
            // Verificar labels
            const statusLabel = statusRow.querySelector('label[for*="status"]');
            const createdByLabel = statusRow.querySelector('label[for*="created_by"]');
            
            console.log(`   Label Status: ${statusLabel ? statusLabel.textContent.trim() : 'No encontrado'}`);
            console.log(`   Label Creado por: ${createdByLabel ? createdByLabel.textContent.trim() : 'No encontrado'}`);
            
        } else {
            console.log('   ❌ Los campos están en filas separadas');
            
            // Información de debugging
            console.log('   🔧 Información de debugging:');
            console.log(`      Status container: ${statusRow ? statusRow.className || 'sin clase' : 'no encontrado'}`);
            console.log(`      CreatedBy container: ${createdByRow ? createdByRow.className || 'sin clase' : 'no encontrado'}`);
        }
        
    } else {
        console.log('\n⚠️ No se pueden verificar las filas porque faltan campos');
    }
    
    // 5. Verificar otros fieldsets para comparación
    console.log('\n📊 OTROS FIELDSETS PARA COMPARACIÓN:');
    
    const allFieldsets = document.querySelectorAll('fieldset');
    allFieldsets.forEach((fieldset, index) => {
        const legend = fieldset.querySelector('h2');
        const legendText = legend ? legend.textContent.trim() : `Fieldset ${index + 1}`;
        
        const fields = fieldset.querySelectorAll('input, select, textarea');
        console.log(`   ${legendText}: ${fields.length} campos`);
        
        // Verificar si algún fieldset tiene campos en la misma fila (como payment_form y account)
        const paymentForm = fieldset.querySelector('[name="payment_form"]');
        const account = fieldset.querySelector('[name="account"]');
        
        if (paymentForm && account) {
            const paymentRow = paymentForm.closest('.form-row') || paymentForm.closest('div');
            const accountRow = account.closest('.form-row') || account.closest('div');
            const samePARow = paymentRow === accountRow || 
                            (paymentRow && accountRow && paymentRow.contains(account));
            
            console.log(`      💳 Forma de Pago y Cuenta en misma fila: ${samePARow ? '✅' : '❌'}`);
        }
    });
    
    // 6. Resultado final
    console.log('\n🏆 RESULTADO FINAL:');
    
    if (statusField && createdByField) {
        const statusRow = statusField.closest('.form-row') || statusField.closest('div');
        const createdByRow = createdByField.closest('.form-row') || createdByField.closest('div');
        
        const correctLayout = statusRow === createdByRow || 
                             (statusRow && createdByRow && statusRow.contains(createdByField)) ||
                             (createdByRow && statusRow && createdByRow.contains(statusField));
        
        if (correctLayout) {
            console.log('🎉 ¡LAYOUT CORRECTO!');
            console.log('✅ Estado y Creado por están en la misma fila');
        } else {
            console.log('⚠️ Layout necesita ajustes');
            console.log('❌ Estado y Creado por están en filas separadas');
        }
    } else {
        console.log('⚠️ No se puede verificar layout completo');
    }
}

// Ejecutar test
setTimeout(testFieldLayout, 1000);

console.log('\n⏰ Verificando layout de campos...');