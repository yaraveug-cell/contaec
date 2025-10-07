#!/usr/bin/env python3
"""
Script para generar código de test para la consola del navegador
"""

print("🧪 CÓDIGO PARA PROBAR EN LA CONSOLA DEL NAVEGADOR")
print("=" * 70)
print()
print("1. Ve a: http://127.0.0.1:8000/admin/invoicing/invoice/add/")
print("2. Presiona Ctrl+F5 para recargar el JavaScript actualizado")  
print("3. Abre Developer Tools (F12) → Console")
print("4. Copia y pega el siguiente código:")
print()
print("=" * 70)

test_code = """
// 🧪 TEST COMPLETO DEL FILTRADO DINÁMICO CON LOGS DETALLADOS

console.log('🚀 INICIANDO DIAGNÓSTICO COMPLETO DEL FILTRADO');
console.log('📍 URL actual:', window.location.href);
console.log('📄 Título página:', document.title);

// Verificar que los campos existen
const company = document.getElementById('id_company');
const payment = document.getElementById('id_payment_form');
const account = document.getElementById('id_account');

console.log('🔍 VERIFICACIÓN DE CAMPOS:');
console.log('   Company field:', company ? '✅ Encontrado' : '❌ No encontrado');
console.log('   Payment field:', payment ? '✅ Encontrado' : '❌ No encontrado');
console.log('   Account field:', account ? '✅ Encontrado' : '❌ No encontrado');

if (!company || !payment || !account) {
    console.error('❌ Faltan campos requeridos. Verifica que estás en la página correcta.');
} else {
    console.log('✅ Todos los campos encontrados');
    
    // Mostrar opciones disponibles
    console.log('🏢 EMPRESAS DISPONIBLES:');
    Array.from(company.options).forEach((opt, idx) => {
        if (opt.value) console.log(`   ${idx}: ${opt.text} (ID: ${opt.value})`);
    });
    
    console.log('💳 FORMAS DE PAGO DISPONIBLES:');
    Array.from(payment.options).forEach((opt, idx) => {
        if (opt.value) console.log(`   ${idx}: ${opt.text} (ID: ${opt.value})`);
    });
    
    console.log('📋 CUENTAS ORIGINALES:');
    Array.from(account.options).forEach((opt, idx) => {
        if (opt.value) console.log(`   ${idx}: ${opt.text} (ID: ${opt.value})`);
    });
    
    // Función de test
    function testFiltering() {
        console.log('\\n🧪 EJECUTANDO TEST DE FILTRADO...');
        
        // 1. Seleccionar GUEBER
        const gueberOption = Array.from(company.options).find(opt => 
            opt.text.toUpperCase().includes('GUEBER'));
        
        if (!gueberOption) {
            console.error('❌ Empresa GUEBER no encontrada');
            return;
        }
        
        console.log('🏢 Seleccionando empresa GUEBER...');
        company.value = gueberOption.value;
        $(company).trigger('change');
        
        setTimeout(() => {
            console.log('💳 Estado después de seleccionar empresa:');
            console.log('   Forma de pago actual:', payment.options[payment.selectedIndex]?.text);
            
            // 2. Cambiar a Efectivo
            const efectivoOption = Array.from(payment.options).find(opt => 
                opt.text.toUpperCase().includes('EFECTIVO'));
            
            if (!efectivoOption) {
                console.error('❌ Forma de pago EFECTIVO no encontrada');
                return;
            }
            
            console.log('💰 Cambiando forma de pago a EFECTIVO...');
            payment.value = efectivoOption.value;
            $(payment).trigger('change');
            
            setTimeout(() => {
                console.log('\\n📊 RESULTADO FINAL:');
                const finalAccounts = Array.from(account.options).filter(opt => opt.value);
                console.log(`   Total cuentas disponibles: ${finalAccounts.length}`);
                
                finalAccounts.forEach((opt, idx) => {
                    console.log(`   ${idx + 1}: ${opt.text}`);
                    if (opt.text.toUpperCase().includes('CAJA GENERAL')) {
                        console.log('      ✅ ¡CAJA GENERAL ENCONTRADA!');
                    }
                });
                
                const cajaGeneral = finalAccounts.find(opt => 
                    opt.text.toUpperCase().includes('CAJA GENERAL'));
                
                if (cajaGeneral) {
                    console.log('\\n🎉 ¡ÉXITO! El filtrado funciona correctamente');
                    console.log('✅ CAJA GENERAL está disponible');
                } else {
                    console.log('\\n❌ PROBLEMA: CAJA GENERAL no aparece en las cuentas filtradas');
                    console.log('🔍 Investigando posibles causas...');
                    
                    // Verificar si hay handler disponible
                    if (window.globalFilteringHandler) {
                        console.log('✅ Handler global disponible');
                        console.log('📋 Configuraciones:', {
                            companies: Object.keys(window.globalFilteringHandler.companyPaymentMethods || {}),
                            methods: Object.keys(window.globalFilteringHandler.paymentMethodAccounts || {})
                        });
                    } else {
                        console.log('❌ Handler global no disponible');
                    }
                }
            }, 1500);
        }, 1500);
    }
    
    // Ejecutar test
    console.log('\\n⚡ Iniciando test en 2 segundos...');
    setTimeout(testFiltering, 2000);
}

// Si hay handler global disponible, también puedes usar:
// window.testFiltering('GUEBER', 'Efectivo');
"""

print(test_code)
print("=" * 70)
print()
print("5. El test se ejecutará automáticamente y mostrará logs detallados")
print("6. Busca los emojis para identificar rápidamente los resultados:")
print("   🎉 = Éxito")
print("   ❌ = Error") 
print("   ✅ = Verificación exitosa")
print("   🔍 = Información de debugging")
print()
print("Si el test falla, los logs te dirán exactamente dónde está el problema.")
print("=" * 70)