console.log('🔍 DEBUG: Transfer Detail en modo edición');
console.log('==========================================');

// 1. Verificar modo edición
const isEdit = window.location.pathname.includes('/change/');
console.log('📝 Modo edición:', isEdit);

if (isEdit) {
    console.log('\n🔍 Buscando campo transfer_detail...');
    
    // 2. Buscar campo Django oculto
    const djangoField = document.getElementById('id_transfer_detail');
    console.log('🎯 Campo Django (id_transfer_detail):', djangoField);
    if (djangoField) {
        console.log('   Valor:', djangoField.value);
        console.log('   Tipo:', djangoField.type);
        console.log('   Name:', djangoField.name);
    }
    
    // 3. Buscar por name attribute
    const nameField = document.querySelector('[name="transfer_detail"]');
    console.log('🎯 Campo por name:', nameField);
    if (nameField) {
        console.log('   Valor:', nameField.value);
    }
    
    // 4. Buscar todos los campos relacionados
    const allTransferFields = document.querySelectorAll('[name*="transfer"], [id*="transfer"]');
    console.log('🎯 Todos los campos transfer:', allTransferFields.length);
    allTransferFields.forEach((field, index) => {
        console.log(`   ${index + 1}. ID: ${field.id}, Name: ${field.name}, Valor: "${field.value}"`);
    });
    
    // 5. Verificar window.invoiceData
    console.log('\n📊 Window data:');
    console.log('   invoiceData:', window.invoiceData);
    if (window.invoiceData) {
        console.log('   transfer_detail:', window.invoiceData.transfer_detail);
    }
    
    // 6. Buscar en data attributes del form
    const forms = document.querySelectorAll('form');
    console.log('\n📋 Forms encontrados:', forms.length);
    forms.forEach((form, index) => {
        console.log(`   Form ${index + 1}:`, form.dataset);
        if (form.dataset.transferDetail) {
            console.log('     transfer_detail en dataset:', form.dataset.transferDetail);
        }
    });
    
    // 7. Test del TransferDetailHandler
    setTimeout(() => {
        console.log('\n🧪 Test del handler después de 2 segundos...');
        
        if (typeof window.transferDetailHandler !== 'undefined') {
            console.log('✅ TransferDetailHandler existe');
            
            // Verificar campo creado
            const createdField = document.getElementById('transfer_detail_field');
            if (createdField) {
                console.log('✅ Campo transfer_detail_field creado');
                console.log('   Visible:', createdField.style.display !== 'none');
                
                const input = createdField.querySelector('input');
                if (input) {
                    console.log('   Input valor:', input.value);
                } else {
                    console.log('❌ Input no encontrado dentro del campo');
                }
            } else {
                console.log('❌ Campo transfer_detail_field NO creado');
            }
        } else {
            console.log('❌ TransferDetailHandler NO existe');
        }
        
    }, 2000);
    
} else {
    console.log('⚪ Modo creación - no hay valor previo');
}

// 8. Función para forzar carga
window.forceLoadTransferDetail = function() {
    console.log('\n🔧 Forzando carga de transfer_detail...');
    
    const djangoField = document.getElementById('id_transfer_detail');
    const createdField = document.getElementById('transfer_detail_field');
    
    if (djangoField && createdField) {
        const input = createdField.querySelector('input');
        if (input) {
            input.value = djangoField.value;
            console.log('✅ Valor cargado manualmente:', djangoField.value);
        }
    } else {
        console.log('❌ Campos no encontrados');
    }
};

console.log('\n💡 Para forzar carga: forceLoadTransferDetail()');
console.log('🏁 Debug iniciado');