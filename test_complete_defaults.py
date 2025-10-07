#!/usr/bin/env python3
"""
Generar test completo para verificar valores por defecto
"""

def generate_complete_test():
    """Generar test completo para valores por defecto"""
    
    test_code = '''// 🧪 TEST COMPLETO DE VALORES POR DEFECTO

console.log('🎯 INICIANDO VERIFICACIÓN COMPLETA DE VALORES POR DEFECTO');
console.log('📍 URL:', window.location.href);
console.log('⏰ Timestamp:', new Date().toLocaleString());

// 1. VERIFICAR CAMPOS PRINCIPALES
console.log('\\n🔍 VERIFICACIÓN DE CAMPOS:');
const companyField = document.getElementById('id_company');
const paymentField = document.getElementById('id_payment_form');
const accountField = document.getElementById('id_account');

console.log('   Company field:', companyField ? '✅ Encontrado' : '❌ No encontrado');
console.log('   Payment field:', paymentField ? '✅ Encontrado' : '❌ No encontrado');
console.log('   Account field:', accountField ? '✅ Encontrado' : '❌ No encontrado');

if (companyField && paymentField && accountField) {
    
    // 2. VERIFICAR VALOR POR DEFECTO DE EMPRESA
    console.log('\\n🏢 VERIFICACIÓN DE EMPRESA POR DEFECTO:');
    const companyValue = companyField.value;
    const companyText = companyField.options[companyField.selectedIndex]?.text || 'Ninguna';
    
    console.log('   Valor seleccionado:', companyValue);
    console.log('   Texto empresa:', companyText);
    
    if (companyValue && companyValue !== '') {
        console.log('   ✅ Empresa establecida automáticamente:', companyText);
        
        // Verificar si es readonly
        const isReadonly = companyField.hasAttribute('readonly') || 
                          companyField.readOnly;
        console.log('   🔒 Campo readonly:', isReadonly ? 'Sí' : 'No');
        
    } else {
        console.log('   ⚠️ No hay empresa seleccionada por defecto');
        console.log('   📋 Empresas disponibles:');
        Array.from(companyField.options).forEach((opt, idx) => {
            if (opt.value) console.log(`      ${idx}: ${opt.text} (ID: ${opt.value})`);
        });
    }
    
    // 3. VERIFICAR VALOR POR DEFECTO DE FORMA DE PAGO
    console.log('\\n💳 VERIFICACIÓN DE FORMA DE PAGO POR DEFECTO:');
    const paymentValue = paymentField.value;
    const paymentText = paymentField.options[paymentField.selectedIndex]?.text || 'Ninguna';
    
    console.log('   Valor seleccionado:', paymentValue);
    console.log('   Texto forma pago:', paymentText);
    
    if (paymentText.toUpperCase().includes('EFECTIVO')) {
        console.log('   ✅ EFECTIVO establecido correctamente por defecto');
    } else {
        console.log('   ⚠️ EFECTIVO no está seleccionado por defecto');
        console.log('   📋 Formas de pago disponibles:');
        Array.from(paymentField.options).forEach((opt, idx) => {
            if (opt.value) {
                const isEfectivo = opt.text.toUpperCase().includes('EFECTIVO') ? ' ⭐' : '';
                console.log(`      ${idx}: ${opt.text} (ID: ${opt.value})${isEfectivo}`);
            }
        });
    }
    
    // 4. VERIFICAR FILTRADO AUTOMÁTICO DE CUENTAS
    console.log('\\n📋 VERIFICACIÓN DE FILTRADO AUTOMÁTICO:');
    const accountOptions = Array.from(accountField.options).filter(opt => opt.value);
    console.log('   Cuentas disponibles:', accountOptions.length);
    
    if (companyValue && paymentValue) {
        console.log('   🔄 Ambos campos tienen valores, verificando filtrado...');
        
        const cajaGeneral = accountOptions.find(opt => 
            opt.text.toUpperCase().includes('CAJA GENERAL'));
        
        if (cajaGeneral && paymentText.toUpperCase().includes('EFECTIVO')) {
            console.log('   ✅ CAJA GENERAL disponible automáticamente');
            console.log('   📊 Cuenta:', cajaGeneral.text);
        } else if (paymentText.toUpperCase().includes('EFECTIVO')) {
            console.log('   ⚠️ CAJA GENERAL no encontrada para EFECTIVO');
        }
        
        // Mostrar primeras 5 cuentas disponibles
        console.log('   📝 Primeras cuentas disponibles:');
        accountOptions.slice(0, 5).forEach((opt, idx) => {
            console.log(`      ${idx + 1}: ${opt.text}`);
        });
        
        if (accountOptions.length > 5) {
            console.log(`      ... y ${accountOptions.length - 5} más`);
        }
    } else {
        console.log('   ⚠️ Falta empresa o forma de pago para filtrado');
    }
    
    // 5. RESUMEN FINAL
    console.log('\\n🎯 RESUMEN DE CONFIGURACIÓN:');
    
    const empresaOK = companyValue && companyValue !== '';
    const efectivoOK = paymentText.toUpperCase().includes('EFECTIVO');
    const filtradoOK = accountOptions.length > 0;
    
    console.log('   📍 Empresa por defecto:', empresaOK ? '✅ Configurado' : '❌ Falta');
    console.log('   💳 Efectivo por defecto:', efectivoOK ? '✅ Configurado' : '❌ Falta');
    console.log('   📋 Filtrado automático:', filtradoOK ? '✅ Funciona' : '❌ No funciona');
    
    if (empresaOK && efectivoOK && filtradoOK) {
        console.log('\\n🏆 ¡CONFIGURACIÓN PERFECTA!');
        console.log('✅ Todos los valores por defecto están funcionando correctamente');
    } else {
        console.log('\\n⚠️ CONFIGURACIÓN INCOMPLETA');
        console.log('Revisar los elementos marcados con ❌');
    }
    
} else {
    console.error('❌ CAMPOS PRINCIPALES NO ENCONTRADOS');
    console.log('💡 Asegúrate de estar en: /admin/invoicing/invoice/add/');
}

// 6. INFORMACIÓN ADICIONAL
console.log('\\n📖 INFORMACIÓN DEL SISTEMA:');
console.log('   🎛️ Handler global:', typeof globalFilteringHandler !== 'undefined' ? 'Disponible' : 'No disponible');
console.log('   🧪 Test function:', typeof window.testFiltering !== 'undefined' ? 'Disponible' : 'No disponible');
console.log('   🔧 User Agent:', navigator.userAgent.includes('Chrome') ? 'Chrome' : 'Otro navegador');'''
    
    print("🧪 CÓDIGO PARA VERIFICAR VALORES POR DEFECTO COMPLETOS")
    print("=" * 70)
    print()
    print("INSTRUCCIONES:")
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
    print("🎯 RESULTADOS ESPERADOS:")
    print("   ✅ Empresa establecida automáticamente")
    print("   ✅ EFECTIVO establecido por defecto")
    print("   ✅ CAJA GENERAL disponible automáticamente")
    print("   🏆 ¡CONFIGURACIÓN PERFECTA!")
    print()
    print("📝 NOTAS:")
    print("   • Para usuarios normales: empresa única aparecerá readonly")
    print("   • Para superusuarios: primera empresa disponible por defecto")
    print("   • EFECTIVO siempre por defecto para todos los usuarios")

if __name__ == '__main__':
    generate_complete_test()