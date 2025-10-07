// 🧪 TEST CORRECCIÓN GUEBER - Pegar en consola del navegador
// Navegar a: http://127.0.0.1:8000/admin/invoicing/invoice/add/

console.log('🔧 TEST DE CORRECCIÓN: VALORES POR DEFECTO GUEBER');
console.log('=' .repeat(60));

// Función principal de test
function testCorrection() {
    
    // 1. Verificar campos disponibles
    console.log('\n📋 VERIFICANDO CAMPOS:');
    const companyField = document.querySelector('select[name="company"]');
    const paymentField = document.querySelector('select[name="payment_form"]');
    const accountField = document.querySelector('select[name="account"]');
    
    if (!companyField || !paymentField || !accountField) {
        console.error('❌ Algunos campos no están disponibles');
        return;
    }
    
    console.log('✅ Todos los campos encontrados');
    
    // 2. Verificar valores actuales
    console.log('\n📊 VALORES ACTUALES:');
    const companyText = companyField.options[companyField.selectedIndex]?.text || 'Sin seleccionar';
    const paymentText = paymentField.options[paymentField.selectedIndex]?.text || 'Sin seleccionar';
    const accountText = accountField.options[accountField.selectedIndex]?.text || 'Sin seleccionar';
    
    console.log(`🏢 Empresa: ${companyText}`);
    console.log(`💳 Forma de Pago: ${paymentText}`);
    console.log(`📊 Cuenta: ${accountText}`);
    
    // 3. Verificar si los valores son correctos
    console.log('\n🎯 ANÁLISIS DE CORRECCIÓN:');
    
    const isGueberSelected = companyText.includes('GUEBER');
    const isEfectivoSelected = paymentText.toLowerCase().includes('efectivo');
    const isCajaAccount = accountText.toLowerCase().includes('caja');
    
    console.log(`🏢 GUEBER seleccionada: ${isGueberSelected ? '✅' : '❌'}`);
    console.log(`💳 Efectivo seleccionado: ${isEfectivoSelected ? '✅' : '❌'}`);
    console.log(`📊 Cuenta de CAJA: ${isCajaAccount ? '✅' : '❌'}`);
    
    // 4. Test de funcionamiento del handler
    console.log('\n🔧 VERIFICANDO HANDLER JAVASCRIPT:');
    
    if (window.paymentAccountHandler) {
        console.log('✅ Handler encontrado');
        
        // Simular cambio de empresa para activar el handler
        console.log('🔄 Simulando cambio de empresa...');
        companyField.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Verificar después de un momento
        setTimeout(() => {
            const newPaymentText = paymentField.options[paymentField.selectedIndex]?.text || 'Sin seleccionar';
            console.log(`💳 Forma de pago después del handler: ${newPaymentText}`);
            
            const isEfectivoAfter = newPaymentText.toLowerCase().includes('efectivo');
            console.log(`💳 Efectivo establecido por handler: ${isEfectivoAfter ? '✅' : '❌'}`);
            
            // Verificar cuentas disponibles
            setTimeout(() => {
                console.log('\n📊 CUENTAS DISPONIBLES DESPUÉS DEL FILTRADO:');
                const accountOptions = Array.from(accountField.options).filter(opt => opt.value !== '');
                
                if (accountOptions.length > 0) {
                    accountOptions.forEach((opt, idx) => {
                        const isCajaOption = opt.text.toLowerCase().includes('caja');
                        const marker = isCajaOption ? '🎯' : '  ';
                        console.log(`${marker} ${idx + 1}. ${opt.text}`);
                    });
                    
                    const hasCajaOptions = accountOptions.some(opt => opt.text.toLowerCase().includes('caja'));
                    console.log(`\n📊 Cuentas de CAJA disponibles: ${hasCajaOptions ? '✅' : '❌'}`);
                    
                    // Resultado final
                    console.log('\n🏆 RESULTADO FINAL:');
                    if (isEfectivoAfter && hasCajaOptions) {
                        console.log('✅ ¡CORRECCIÓN EXITOSA!');
                        console.log('✅ Efectivo establecido por defecto');
                        console.log('✅ Cuentas de CAJA filtradas correctamente');
                        console.log('✅ El problema ha sido resuelto');
                    } else {
                        console.log('❌ La corrección necesita ajustes adicionales');
                    }
                    
                } else {
                    console.log('❌ No hay cuentas disponibles después del filtrado');
                }
                
            }, 1000);
            
        }, 500);
        
    } else {
        console.log('❌ Handler no encontrado');
    }
}

// Ejecutar test
setTimeout(testCorrection, 1000);

console.log('\n⏰ Test iniciado - Resultados en unos segundos...');