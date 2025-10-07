#!/usr/bin/env python3
"""
Generar código de test actualizado con verificaciones mejoradas
"""
import os
import datetime

def generate_improved_test():
    """Generar test mejorado con verificaciones de jQuery"""
    
    test_code = '''// 🧪 TEST MEJORADO DE FILTRADO DINÁMICO - VERSION 2.0

console.log('🧪 INICIANDO DIAGNÓSTICO COMPLETO DEL FILTRADO v2.0');
console.log('📍 URL actual:', window.location.href);
console.log('📄 Título página:', document.title);
console.log('⏰ Timestamp:', new Date().toLocaleString());

// 1. VERIFICAR JQUERY PRIMERO
console.log('\\n🔍 VERIFICACIÓN DE DEPENDENCIAS:');
console.log('   jQuery disponible:', typeof $ !== 'undefined' ? '✅ Sí' : '❌ No');
console.log('   jQuery.fn disponible:', typeof $.fn !== 'undefined' ? '✅ Sí' : '❌ No');
if (typeof $.fn !== 'undefined') {
    console.log('   jQuery version:', $.fn.jquery || 'Desconocida');
}

// 2. VERIFICAR HANDLER GLOBAL
console.log('\\n🎛️ VERIFICACIÓN DE HANDLER:');
console.log('   globalFilteringHandler:', typeof globalFilteringHandler !== 'undefined' ? '✅ Disponible' : '❌ No disponible');
console.log('   window.testFiltering:', typeof window.testFiltering !== 'undefined' ? '✅ Disponible' : '❌ No disponible');
console.log('   IntegratedPaymentAccountHandler:', typeof IntegratedPaymentAccountHandler !== 'undefined' ? '✅ Disponible' : '❌ No disponible');

// 3. VERIFICAR CAMPOS CON Y SIN JQUERY
console.log('\\n🔍 VERIFICACIÓN DE CAMPOS (Vanilla JS):');
const companyVanilla = document.getElementById('id_company');
const paymentVanilla = document.getElementById('id_payment_form');
const accountVanilla = document.getElementById('id_account');

console.log('   Company field (vanilla):', companyVanilla ? '✅ Encontrado' : '❌ No encontrado');
console.log('   Payment field (vanilla):', paymentVanilla ? '✅ Encontrado' : '❌ No encontrado');
console.log('   Account field (vanilla):', accountVanilla ? '✅ Encontrado' : '❌ No encontrado');

if (typeof $ !== 'undefined') {
    console.log('\\n🔍 VERIFICACIÓN DE CAMPOS (jQuery):');
    const companyJQuery = $('#id_company');
    const paymentJQuery = $('#id_payment_form');
    const accountJQuery = $('#id_account');
    
    console.log('   Company field (jQuery):', companyJQuery.length > 0 ? '✅ Encontrado' : '❌ No encontrado');
    console.log('   Payment field (jQuery):', paymentJQuery.length > 0 ? '✅ Encontrado' : '❌ No encontrado');
    console.log('   Account field (jQuery):', accountJQuery.length > 0 ? '✅ Encontrado' : '❌ No encontrado');
    
    if (companyVanilla) {
        console.log('\\n🏢 EMPRESAS DISPONIBLES:');
        Array.from(companyVanilla.options).forEach((opt, idx) => {
            if (opt.value) console.log(`   ${idx}: ${opt.text} (ID: ${opt.value})`);
        });
    }
    
    if (paymentVanilla) {
        console.log('\\n💳 FORMAS DE PAGO DISPONIBLES:');
        Array.from(paymentVanilla.options).forEach((opt, idx) => {
            if (opt.value) console.log(`   ${idx}: ${opt.text} (ID: ${opt.value})`);
        });
    }
    
    if (accountVanilla) {
        console.log('\\n📋 CUENTAS ORIGINALES:');
        Array.from(accountVanilla.options).forEach((opt, idx) => {
            if (opt.value) console.log(`   ${idx}: ${opt.text} (ID: ${opt.value})`);
        });
    }
}

// 4. INTENTAR INICIALIZACIÓN MANUAL SI NO EXISTE
if (typeof globalFilteringHandler === 'undefined' && typeof IntegratedPaymentAccountHandler !== 'undefined') {
    console.log('\\n🔄 INTENTANDO INICIALIZACIÓN MANUAL...');
    try {
        window.globalFilteringHandler = new IntegratedPaymentAccountHandler();
        console.log('✅ Handler inicializado manualmente');
    } catch (error) {
        console.error('❌ Error en inicialización manual:', error);
    }
}

// 5. FUNCIÓN DE TEST MEJORADA
function testFilteringImproved() {
    console.log('\\n🧪 EJECUTANDO TEST DE FILTRADO MEJORADO...');
    
    if (!companyVanilla || !paymentVanilla || !accountVanilla) {
        console.error('❌ Campos requeridos no encontrados');
        return;
    }
    
    // 1. Seleccionar GUEBER
    const gueberOption = Array.from(companyVanilla.options).find(opt =>
        opt.text.toUpperCase().includes('GUEBER'));
    
    if (!gueberOption) {
        console.error('❌ Empresa GUEBER no encontrada');
        return;
    }
    
    console.log('🏢 Seleccionando empresa GUEBER...');
    companyVanilla.value = gueberOption.value;
    
    // Disparar evento con jQuery si está disponible
    if (typeof $ !== 'undefined') {
        $(companyVanilla).trigger('change');
    } else {
        // Disparar evento vanilla
        const event = new Event('change', { bubbles: true });
        companyVanilla.dispatchEvent(event);
    }
    
    setTimeout(() => {
        console.log('💳 Estado después de seleccionar empresa:');
        console.log('   Forma de pago actual:', paymentVanilla.options[paymentVanilla.selectedIndex]?.text);
        
        // 2. Cambiar a Efectivo
        const efectivoOption = Array.from(paymentVanilla.options).find(opt =>
            opt.text.toUpperCase().includes('EFECTIVO'));
        
        if (!efectivoOption) {
            console.error('❌ Forma de pago EFECTIVO no encontrada');
            return;
        }
        
        console.log('💰 Cambiando forma de pago a EFECTIVO...');
        paymentVanilla.value = efectivoOption.value;
        
        // Disparar evento
        if (typeof $ !== 'undefined') {
            $(paymentVanilla).trigger('change');
        } else {
            const event = new Event('change', { bubbles: true });
            paymentVanilla.dispatchEvent(event);
        }
        
        setTimeout(() => {
            console.log('\\n📊 RESULTADO FINAL:');
            const finalAccounts = Array.from(accountVanilla.options).filter(opt => opt.value);
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
                
                // Debugging adicional
                console.log('🔍 Información de debugging:');
                if (typeof globalFilteringHandler !== 'undefined') {
                    console.log('   Handler disponible: ✅');
                    console.log('   Configuraciones:', globalFilteringHandler.companyPaymentMethods);
                    console.log('   Métodos de pago:', globalFilteringHandler.paymentMethodAccounts);
                } else {
                    console.log('   Handler disponible: ❌');
                }
            }
        }, 1500);
    }, 1500);
}

// 6. EJECUTAR TEST AUTOMÁTICAMENTE
console.log('\\n⚡ Iniciando test automático en 3 segundos...');
setTimeout(testFilteringImproved, 3000);'''
    
    print("🧪 CÓDIGO DE TEST MEJORADO PARA LA CONSOLA DEL NAVEGADOR")
    print("=" * 70)
    print()
    print("1. Ve a: http://127.0.0.1:8000/admin/invoicing/invoice/add/")
    print("2. Presiona Ctrl+F5 para recargar completamente")
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
    print("   ✓ Si jQuery está disponible")
    print("   ✓ Si el handler se inicializó correctamente")
    print("   ✓ Si los campos existen")
    print("   ✓ Si el filtrado funciona")
    print("   ✓ Si CAJA GENERAL aparece con GUEBER + Efectivo")
    print()
    print("📋 RESULTADOS ESPERADOS:")
    print("   🎉 = Éxito")
    print("   ❌ = Error específico")
    print("   ✅ = Verificación exitosa")

if __name__ == '__main__':
    generate_improved_test()