#!/usr/bin/env python3
"""
Generar test final para sistema JavaScript vanilla
"""

def generate_final_test():
    """Generar test final optimizado para JavaScript vanilla"""
    
    test_code = '''// 🧪 TEST FINAL - SISTEMA JAVASCRIPT VANILLA

console.log('🎯 INICIANDO TEST FINAL DEL SISTEMA DE FILTRADO');
console.log('📍 URL:', window.location.href);
console.log('⏰ Timestamp:', new Date().toLocaleString());
console.log('🔧 Sistema: JavaScript Vanilla (sin jQuery)');

// 1. VERIFICAR ESTADO DEL SISTEMA
console.log('\\n🔍 VERIFICACIÓN DEL SISTEMA:');
console.log('   globalFilteringHandler:', typeof globalFilteringHandler !== 'undefined' ? '✅ Disponible' : '❌ No disponible');
console.log('   window.testFiltering:', typeof window.testFiltering !== 'undefined' ? '✅ Disponible' : '❌ No disponible');
console.log('   IntegratedPaymentAccountHandler:', typeof IntegratedPaymentAccountHandler !== 'undefined' ? '✅ Disponible' : '❌ No disponible');

// 2. VERIFICAR CAMPOS
console.log('\\n🔍 VERIFICACIÓN DE CAMPOS:');
const companyField = document.getElementById('id_company');
const paymentField = document.getElementById('id_payment_form');
const accountField = document.getElementById('id_account');

console.log('   Company field:', companyField ? '✅ Encontrado' : '❌ No encontrado');
console.log('   Payment field:', paymentField ? '✅ Encontrado' : '❌ No encontrado');
console.log('   Account field:', accountField ? '✅ Encontrado' : '❌ No encontrado');

if (companyField && paymentField && accountField) {
    // 3. MOSTRAR OPCIONES DISPONIBLES
    console.log('\\n🏢 EMPRESAS DISPONIBLES:');
    Array.from(companyField.options).forEach((opt, idx) => {
        if (opt.value) console.log(`   ${idx}: ${opt.text} (ID: ${opt.value})`);
    });

    console.log('\\n💳 FORMAS DE PAGO DISPONIBLES:');
    Array.from(paymentField.options).forEach((opt, idx) => {
        if (opt.value) console.log(`   ${idx}: ${opt.text} (ID: ${opt.value})`);
    });

    console.log('\\n📋 CUENTAS TOTALES DISPONIBLES:');
    const totalAccounts = Array.from(accountField.options).filter(opt => opt.value);
    console.log(`   Total: ${totalAccounts.length} cuentas`);
    totalAccounts.forEach((opt, idx) => {
        if (idx < 10) { // Solo mostrar primeras 10
            console.log(`   ${idx + 1}: ${opt.text}`);
        }
    });
    if (totalAccounts.length > 10) {
        console.log(`   ... y ${totalAccounts.length - 10} más`);
    }

    // 4. EJECUTAR TEST AUTOMÁTICO
    console.log('\\n🚀 INICIANDO TEST AUTOMÁTICO...');
    
    function runAutomaticTest() {
        if (typeof window.testFiltering === 'function') {
            console.log('✅ Función testFiltering disponible, ejecutando...');
            window.testFiltering('GUEBER', 'Efectivo');
        } else if (typeof globalFilteringHandler !== 'undefined' && globalFilteringHandler) {
            console.log('✅ Handler global disponible, ejecutando test directo...');
            globalFilteringHandler.testFiltering('GUEBER', 'Efectivo');
        } else {
            console.log('⚠️ Sistema no inicializado completamente, ejecutando test manual...');
            manualTest();
        }
    }
    
    function manualTest() {
        console.log('\\n🔧 EJECUTANDO TEST MANUAL...');
        
        // Buscar GUEBER
        const gueberOption = Array.from(companyField.options).find(opt =>
            opt.text.toUpperCase().includes('GUEBER'));
        
        if (!gueberOption) {
            console.error('❌ Empresa GUEBER no encontrada');
            return;
        }
        
        console.log('🏢 Seleccionando GUEBER...');
        companyField.value = gueberOption.value;
        companyField.dispatchEvent(new Event('change', { bubbles: true }));
        
        setTimeout(() => {
            console.log('💳 Formas de pago después de seleccionar empresa:');
            Array.from(paymentField.options).forEach((opt, idx) => {
                if (opt.value) {
                    const status = opt.selected ? ' (SELECCIONADO)' : '';
                    console.log(`   ${idx}: ${opt.text}${status}`);
                }
            });
            
            // Buscar Efectivo
            const efectivoOption = Array.from(paymentField.options).find(opt =>
                opt.text.toUpperCase().includes('EFECTIVO'));
            
            if (efectivoOption) {
                console.log('💰 Cambiando a EFECTIVO...');
                paymentField.value = efectivoOption.value;
                paymentField.dispatchEvent(new Event('change', { bubbles: true }));
                
                setTimeout(() => {
                    console.log('\\n📊 RESULTADO FINAL:');
                    const finalAccounts = Array.from(accountField.options).filter(opt => opt.value);
                    console.log(`   Cuentas filtradas: ${finalAccounts.length}`);
                    
                    finalAccounts.forEach((opt, idx) => {
                        const isCaja = opt.text.toUpperCase().includes('CAJA GENERAL');
                        console.log(`   ${idx + 1}: ${opt.text}${isCaja ? ' ⭐ ¡OBJETIVO!' : ''}`);
                    });
                    
                    const cajaGeneral = finalAccounts.find(opt =>
                        opt.text.toUpperCase().includes('CAJA GENERAL'));
                    
                    if (cajaGeneral) {
                        console.log('\\n🎉 ¡ÉXITO TOTAL! ');
                        console.log('✅ CAJA GENERAL aparece correctamente');
                        console.log('✅ El filtrado funciona perfectamente');
                    } else {
                        console.log('\\n❌ PROBLEMA PERSISTENTE:');
                        console.log('❌ CAJA GENERAL no aparece');
                        console.log('🔍 Revisar configuración de datos');
                    }
                }, 2000);
            } else {
                console.error('❌ Opción EFECTIVO no encontrada');
            }
        }, 1500);
    }
    
    // Ejecutar test en 2 segundos
    setTimeout(runAutomaticTest, 2000);
    
} else {
    console.error('❌ CAMPOS REQUERIDOS NO ENCONTRADOS');
    console.log('💡 Asegúrate de estar en la página: /admin/invoicing/invoice/add/');
}

console.log('\\n⚡ Test configurado, resultados en unos segundos...');'''
    
    print("🎯 CÓDIGO DE TEST FINAL PARA JAVASCRIPT VANILLA")
    print("=" * 70)
    print()
    print("1. Ve a: http://127.0.0.1:8000/admin/invoicing/invoice/add/")
    print("2. Presiona Ctrl+F5 para recargar JavaScript actualizado")
    print("3. Abre Developer Tools (F12) → Console")
    print("4. Copia y pega el siguiente código:")
    print()
    print("=" * 70)
    print()
    print(test_code)
    print()
    print("=" * 70)
    print()
    print("🎯 ESTE TEST VERIFICARÁ:")
    print("   ✓ Sistema vanilla JavaScript funcionando")
    print("   ✓ Campos disponibles y configurados")
    print("   ✓ Test GUEBER + Efectivo → CAJA GENERAL")
    print("   ✓ Resultado final del filtrado")
    print()
    print("🎉 RESULTADOS ESPERADOS:")
    print("   🎉 = ¡Éxito total!")
    print("   ❌ = Problema identificado")
    print("   ⭐ = CAJA GENERAL encontrada")

if __name__ == '__main__':
    generate_final_test()