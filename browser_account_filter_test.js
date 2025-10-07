/**
 * 🧪 TEST DIRECTO DEL FILTRADO DE CUENTAS
 * 
 * Copia y pega este código en la consola del navegador
 * mientras estés en la página de crear factura (/admin/invoicing/invoice/add/)
 */

// 1. Test de la configuración actual del handler
console.log('🧪 TEST: Filtrado de cuentas');
console.log('================================');

// Verificar si existe el handler
if (typeof window.paymentHandler !== 'undefined') {
    console.log('✅ PaymentHandler existe');
    console.log('📋 Configuración métodos:', window.paymentHandler.paymentMethodAccounts);
} else {
    console.log('❌ PaymentHandler NO existe');
}

// 2. Test directo del endpoint
console.log('\n📡 Testeando endpoint directamente...');
fetch('/admin/invoicing/invoice/payment-method-accounts/', {
    headers: {
        'X-Requested-With': 'XMLHttpRequest'
    }
})
.then(response => response.json())
.then(data => {
    console.log('✅ Endpoint responde correctamente:');
    console.log(data);
    
    // Buscar Transferencia
    let transferConfig = null;
    for (let [methodId, config] of Object.entries(data)) {
        if (config.method_name === 'Transferencia') {
            transferConfig = config;
            console.log('\n🏦 Transferencia encontrada:');
            console.log('   ID:', methodId);
            console.log('   Cuenta padre:', config.parent_account);
            break;
        }
    }
    
    if (transferConfig) {
        // 3. Test directo de filtrado
        console.log('\n🔍 Test directo de filtrado...');
        const accountSelect = document.getElementById('id_account');
        if (accountSelect) {
            console.log('✅ Campo cuenta encontrado');
            console.log('📊 Total opciones:', accountSelect.options.length);
            
            // Listar todas las cuentas que empiecen con 1.1.02
            console.log('\n🏦 Cuentas que empiezan con 1.1.02:');
            Array.from(accountSelect.options).forEach((option, index) => {
                if (option.text && option.text.match(/^1\.1\.02/)) {
                    console.log(`   ${index}: ${option.text}`);
                }
            });
            
            // Test de la lógica JavaScript directamente
            const parentCode = transferConfig.parent_account.code;
            console.log(`\n🧮 Test lógica JavaScript con padre: ${parentCode}`);
            
            let normalizedParent = parentCode;
            if (normalizedParent.endsWith('.')) {
                normalizedParent = normalizedParent.slice(0, -1);
            }
            console.log(`   Código normalizado: ${normalizedParent}`);
            
            Array.from(accountSelect.options).forEach(option => {
                if (!option.text || !option.value) return;
                
                const codeMatch = option.text.match(/^(\d+(?:\.\d+)*)/);
                if (codeMatch) {
                    const accountCode = codeMatch[1];
                    const isChild = accountCode.startsWith(normalizedParent + '.') && 
                                   accountCode !== normalizedParent;
                    
                    if (accountCode.includes('1.1.02')) {
                        console.log(`   ${option.text}: ${isChild ? '✅ ES HIJA' : '❌ NO es hija'}`);
                        console.log(`      Código: ${accountCode}, Prefijo: ${normalizedParent + '.'}`);
                    }
                }
            });
            
        } else {
            console.log('❌ Campo cuenta NO encontrado');
        }
    } else {
        console.log('❌ Transferencia no encontrada en configuración');
    }
})
.catch(error => {
    console.error('❌ Error en endpoint:', error);
});

console.log('\n🏁 Test completado. Revisa los resultados arriba.');