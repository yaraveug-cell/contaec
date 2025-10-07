// Test completo para la consola del navegador
// Ejecutar este código en la consola cuando estés en la página de añadir factura

console.log('🧪 TEST COMPLETO: Filtrado de cuentas v5.2');
console.log('==========================================');

// 1. Verificar que el handler existe y está funcionando
if (typeof window.paymentHandler !== 'undefined') {
    console.log('✅ PaymentHandler cargado exitosamente');
    
    // 2. Verificar que la función isInvoiceForm existe
    if (typeof window.paymentHandler.isInvoiceForm === 'function') {
        console.log('✅ Función isInvoiceForm definida');
        
        const isInvoice = window.paymentHandler.isInvoiceForm();
        console.log('📋 ¿Es formulario de factura?:', isInvoice);
    } else {
        console.log('❌ Función isInvoiceForm NO definida');
    }
    
    // 3. Verificar configuración de métodos
    console.log('💳 Configuración métodos:', window.paymentHandler.paymentMethodAccounts);
    
} else {
    console.log('❌ PaymentHandler NO cargado');
}

// Función para esperar a que se complete una operación
function waitAndCheck(description, checkFunction, maxWait = 3000) {
    return new Promise((resolve) => {
        console.log(`⏳ ${description}...`);
        let waited = 0;
        const interval = setInterval(() => {
            if (checkFunction() || waited >= maxWait) {
                clearInterval(interval);
                console.log(`✅ ${description} completado`);
                resolve();
            }
            waited += 100;
        }, 100);
    });
}

// Función principal de test
async function testIntegratedFiltering() {
    // Verificar que los campos existen
    const companyField = document.getElementById('id_company');
    const paymentField = document.getElementById('id_payment_form');
    const accountField = document.getElementById('id_account');
    
    if (!companyField || !paymentField || !accountField) {
        console.error('❌ Campos no encontrados');
        return;
    }
    
    console.log('✅ Campos encontrados');
    
    // 1. Test: Seleccionar GUEBER
    console.log('\n📋 PASO 1: Seleccionando empresa GUEBER');
    const gueberOption = Array.from(companyField.options).find(opt => opt.text.includes('GUEBER'));
    if (gueberOption) {
        companyField.value = gueberOption.value;
        $(companyField).trigger('change');
        console.log('✅ Empresa GUEBER seleccionada');
    } else {
        console.error('❌ Empresa GUEBER no encontrada');
        return;
    }
    
    // Esperar que se procese el cambio
    await waitAndCheck('Procesando cambio de empresa', () => {
        return paymentField.value !== '';
    });
    
    console.log(`📋 Forma de pago después de seleccionar GUEBER: ${paymentField.options[paymentField.selectedIndex]?.text}`);
    
    // 2. Test: Cambiar a Efectivo
    console.log('\n💰 PASO 2: Cambiando a forma de pago Efectivo');
    const efectivoOption = Array.from(paymentField.options).find(opt => opt.text.includes('Efectivo'));
    if (efectivoOption) {
        paymentField.value = efectivoOption.value;
        $(paymentField).trigger('change');
        console.log('✅ Forma de pago Efectivo seleccionada');
    } else {
        console.error('❌ Forma de pago Efectivo no encontrada');
        return;
    }
    
    // Esperar que se filtre las cuentas
    await waitAndCheck('Filtrando cuentas para Efectivo', () => {
        const options = Array.from(accountField.options).filter(opt => opt.value !== '');
        return options.length > 0;
    });
    
    // Verificar resultado
    const accountOptions = Array.from(accountField.options).filter(opt => opt.value !== '');
    console.log('\n🎯 RESULTADO FINAL:');
    console.log(`📊 Cuentas disponibles: ${accountOptions.length}`);
    
    accountOptions.forEach(option => {
        console.log(`   - ${option.text}`);
        if (option.text.includes('CAJA GENERAL')) {
            console.log('   ✅ ¡CAJA GENERAL ENCONTRADA!');
        }
    });
    
    const cajaGeneral = accountOptions.find(opt => opt.text.includes('CAJA GENERAL'));
    if (cajaGeneral) {
        console.log('\n🎉 ¡ÉXITO! El filtrado funciona correctamente');
        console.log(`✅ CAJA GENERAL está disponible: ${cajaGeneral.text}`);
    } else {
        console.log('\n❌ PROBLEMA: CAJA GENERAL no aparece en las opciones filtradas');
        console.log('Verificando configuración...');
        
        // Verificar configuración del handler
        if (window.integratedHandler) {
            console.log('Configuraciones cargadas:', {
                companies: Object.keys(window.integratedHandler.companyPaymentMethods).length,
                paymentMethods: Object.keys(window.integratedHandler.paymentMethodAccounts).length
            });
        }
    }
    
    // 3. Test adicional: Verificar con Crédito
    console.log('\n🔄 PASO 3: Probando con forma de pago Crédito');
    const creditoOption = Array.from(paymentField.options).find(opt => opt.text.includes('Crédito'));
    if (creditoOption) {
        paymentField.value = creditoOption.value;
        $(paymentField).trigger('change');
        
        await waitAndCheck('Filtrando cuentas para Crédito', () => true, 1000);
        
        const creditAccountOptions = Array.from(accountField.options).filter(opt => opt.value !== '');
        console.log(`📊 Cuentas para Crédito: ${creditAccountOptions.length}`);
        creditAccountOptions.forEach(option => {
            console.log(`   - ${option.text}`);
        });
    }
}

// Ejecutar test
testIntegratedFiltering();