console.log('🔧 TEST: Transfer Detail Value Loading Fix');
console.log('==========================================');

// 1. Verificar estado inicial
const isEdit = window.location.pathname.includes('/change/');
console.log('📝 Modo edición:', isEdit);

if (isEdit) {
    // 2. Buscar campo Django
    const djangoField = document.getElementById('id_transfer_detail');
    console.log('🎯 Campo Django encontrado:', !!djangoField);
    if (djangoField) {
        console.log('   Valor Django:', djangoField.value);
        console.log('   Name:', djangoField.name);
        console.log('   Type:', djangoField.type);
    }

    // 3. Verificar window.invoiceData
    console.log('📊 Invoice Data:', window.invoiceData);
    if (window.invoiceData && window.invoiceData.transfer_detail) {
        console.log('   Transfer detail disponible:', window.invoiceData.transfer_detail);
    }

    // 4. Test después de que se cree el campo
    setTimeout(() => {
        console.log('\n🧪 Test después de 3 segundos...');
        
        const createdField = document.getElementById('transfer_detail_field');
        if (createdField) {
            console.log('✅ Campo dinámico creado');
            
            const input = createdField.querySelector('input');
            if (input) {
                console.log('✅ Input encontrado');
                console.log('   Valor actual del input:', input.value);
                console.log('   Placeholder:', input.placeholder);
                
                // Test manual: cargar valor del campo Django
                if (djangoField && djangoField.value && !input.value) {
                    console.log('🔧 Cargando valor manualmente...');
                    input.value = djangoField.value;
                    console.log('✅ Valor aplicado:', input.value);
                    
                    // Disparar evento input para sincronizar
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                }
                
            } else {
                console.log('❌ Input NO encontrado');
            }
        } else {
            console.log('❌ Campo dinámico NO creado');
        }
        
    }, 3000);

    // 5. Test después de 5 segundos para verificar sincronización
    setTimeout(() => {
        console.log('\n🔄 Test de sincronización...');
        
        const createdField = document.getElementById('transfer_detail_field');
        const input = createdField?.querySelector('input');
        
        if (input && djangoField) {
            console.log('Input valor:', input.value);
            console.log('Django valor:', djangoField.value);
            console.log('¿Sincronizados?:', input.value === djangoField.value);
        }
        
    }, 5000);

} else {
    console.log('⚪ Modo creación - no hay valor previo');
}

// Función para forzar carga manual
window.forceTransferDetailLoad = function() {
    console.log('\n🔧 FORZANDO CARGA MANUAL...');
    
    const djangoField = document.getElementById('id_transfer_detail');
    const createdField = document.getElementById('transfer_detail_field');
    const input = createdField?.querySelector('input');
    
    if (djangoField && input) {
        const value = djangoField.value || window.invoiceData?.transfer_detail || '';
        if (value) {
            input.value = value;
            console.log('✅ Valor aplicado manualmente:', value);
            
            // Sincronizar de vuelta
            djangoField.value = value;
            input.dispatchEvent(new Event('input', { bubbles: true }));
            console.log('✅ Sincronización completada');
        } else {
            console.log('❌ No hay valor para cargar');
        }
    } else {
        console.log('❌ Campos no encontrados');
        console.log('   Django field:', !!djangoField);
        console.log('   Input field:', !!input);
    }
};

console.log('\n💡 Para forzar carga: forceTransferDetailLoad()');
console.log('🏁 Test iniciado');