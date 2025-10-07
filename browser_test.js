
// Test para ejecutar en la consola del navegador
console.log('🧪 INICIANDO TEST DE FILTRADO DINÁMICO');

// 1. Seleccionar GUEBER
const companyField = document.getElementById('id_company');
const gueberOption = Array.from(companyField.options).find(opt => opt.text.includes('GUEBER'));
if (gueberOption) {
    companyField.value = gueberOption.value;
    $(companyField).trigger('change');
    console.log('✅ Empresa GUEBER seleccionada');
} else {
    console.log('❌ Empresa GUEBER no encontrada');
}

// Esperar un momento para que se procesen los cambios
setTimeout(() => {
    // 2. Cambiar a Efectivo
    const paymentField = document.getElementById('id_payment_form');
    const efectivoOption = Array.from(paymentField.options).find(opt => opt.text.includes('Efectivo'));
    if (efectivoOption) {
        paymentField.value = efectivoOption.value;
        $(paymentField).trigger('change');
        console.log('✅ Forma de pago Efectivo seleccionada');
        
        // Verificar resultado después de un momento
        setTimeout(() => {
            const accountField = document.getElementById('id_account');
            const accounts = Array.from(accountField.options).filter(opt => opt.value !== '');
            console.log('📋 Cuentas disponibles después del filtrado:', accounts.map(opt => opt.text));
            
            const cajaGeneral = accounts.find(opt => opt.text.includes('CAJA GENERAL'));
            if (cajaGeneral) {
                console.log('✅ ¡ÉXITO! CAJA GENERAL está disponible:', cajaGeneral.text);
            } else {
                console.log('❌ CAJA GENERAL no encontrada en las opciones filtradas');
            }
        }, 1000);
    } else {
        console.log('❌ Forma de pago Efectivo no encontrada');
    }
}, 1000);
