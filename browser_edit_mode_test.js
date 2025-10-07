console.log('🧪 TEST MANUAL: Verificación modo edición v5.3');
console.log('===============================================');

// 1. Verificar que estamos en modo edición
const isEditMode = window.location.pathname.includes('/change/');
console.log('📝 ¿Modo edición?:', isEditMode);

if (isEditMode) {
    console.log('✅ MODO EDICIÓN DETECTADO');
    
    // 2. Verificar valores de campos
    const paymentField = document.getElementById('id_payment_form');
    const accountField = document.getElementById('id_account');
    
    if (paymentField) {
        const selectedOption = paymentField.options[paymentField.selectedIndex];
        console.log('💳 Forma de pago actual:', selectedOption?.text || 'Sin selección');
        console.log('   Valor ID:', paymentField.value);
    }
    
    if (accountField) {
        const selectedOption = accountField.options[accountField.selectedIndex];
        console.log('🏦 Cuenta actual:', selectedOption?.text || 'Sin selección');
        console.log('   Valor ID:', accountField.value);
    }
    
    // 3. Verificar transfer detail
    const transferField = document.getElementById('transfer_detail_field');
    if (transferField) {
        console.log('📄 Transfer Detail encontrado:', transferField.value);
    } else {
        console.log('📄 Transfer Detail: No visible (normal si no es Transferencia)');
    }
    
    // 4. Verificar que el handler respete los valores
    setTimeout(() => {
        console.log('\n🔍 Verificación después de inicialización:');
        
        if (paymentField) {
            const currentOption = paymentField.options[paymentField.selectedIndex];
            console.log('💳 Forma de pago tras init:', currentOption?.text || 'Sin selección');
        }
        
        if (accountField) {
            const currentOption = accountField.options[accountField.selectedIndex];
            console.log('🏦 Cuenta tras init:', currentOption?.text || 'Sin selección');
        }
        
        const transferFieldPost = document.getElementById('transfer_detail_field');
        if (transferFieldPost && transferFieldPost.style.display !== 'none') {
            console.log('📄 Transfer Detail visible con valor:', transferFieldPost.value);
        }
        
    }, 2000);
    
} else {
    console.log('🆕 MODO CREACIÓN DETECTADO');
    console.log('   Es normal que se apliquen valores por defecto');
}

// 5. Función para test manual
window.testEditMode = function() {
    console.log('\n🔧 TEST MANUAL: Estado actual de campos');
    
    const paymentField = document.getElementById('id_payment_form');
    const accountField = document.getElementById('id_account');
    const transferField = document.getElementById('transfer_detail_field');
    
    console.log('Estado actual:');
    console.log('  Forma pago:', paymentField?.options[paymentField.selectedIndex]?.text);
    console.log('  Cuenta:', accountField?.options[accountField.selectedIndex]?.text);
    console.log('  Transfer visible:', transferField && transferField.style.display !== 'none');
    console.log('  Transfer valor:', transferField?.value || 'Sin valor');
};

console.log('\n💡 Para verificar estado: testEditMode()');
console.log('🏁 Verificación iniciada');