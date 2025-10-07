#!/usr/bin/env python3
"""
Test simple para verificar valor por defecto en formulario
"""

test_code = '''// 🧪 TEST DE VALOR POR DEFECTO - EFECTIVO

console.log('🎯 VERIFICANDO VALOR POR DEFECTO DEL CAMPO FORMA DE PAGO');
console.log('📍 URL:', window.location.href);

// Verificar campo forma de pago
const paymentField = document.getElementById('id_payment_form');

if (paymentField) {
    console.log('✅ Campo forma de pago encontrado');
    
    // Mostrar valor actual
    const currentValue = paymentField.value;
    const selectedText = paymentField.options[paymentField.selectedIndex]?.text || 'Ninguno';
    
    console.log('💳 Valor actual del campo:', currentValue);
    console.log('📝 Texto seleccionado:', selectedText);
    
    // Verificar si es Efectivo
    if (selectedText.toUpperCase().includes('EFECTIVO')) {
        console.log('🎉 ¡ÉXITO! Efectivo está seleccionado por defecto');
        
        // Verificar que el sistema de filtrado también funciona
        const accountField = document.getElementById('id_account');
        if (accountField) {
            const accountOptions = Array.from(accountField.options).filter(opt => opt.value);
            console.log('📋 Cuentas disponibles:', accountOptions.length);
            
            const cajaGeneral = accountOptions.find(opt => 
                opt.text.toUpperCase().includes('CAJA GENERAL'));
            
            if (cajaGeneral) {
                console.log('✅ CAJA GENERAL disponible automáticamente');
                console.log('🏆 ¡CONFIGURACIÓN PERFECTA!');
            } else {
                console.log('⚠️ CAJA GENERAL no está filtrada automáticamente');
                console.log('💡 Puede necesitar seleccionar empresa primero');
            }
        }
    } else {
        console.log('⚠️ Efectivo NO está seleccionado por defecto');
        console.log('📋 Opciones disponibles:');
        Array.from(paymentField.options).forEach((opt, idx) => {
            if (opt.value) console.log(`   ${idx}: ${opt.text} (ID: ${opt.value})`);
        });
    }
} else {
    console.error('❌ Campo forma de pago no encontrado');
    console.log('💡 Asegúrate de estar en la página: /admin/invoicing/invoice/add/');
}'''

print("🧪 CÓDIGO PARA VERIFICAR VALOR POR DEFECTO")
print("=" * 50)
print()
print("1. Ve a: http://127.0.0.1:8000/admin/invoicing/invoice/add/")
print("2. Presiona Ctrl+F5 para recargar")
print("3. Abre Developer Tools (F12) → Console")
print("4. Pega este código:")
print()
print("=" * 50)
print()
print(test_code)
print()
print("=" * 50)
print()
print("🎯 RESULTADOS ESPERADOS:")
print("   ✅ Campo forma de pago encontrado")
print("   🎉 ¡ÉXITO! Efectivo está seleccionado por defecto")
print("   ✅ CAJA GENERAL disponible automáticamente")
print("   🏆 ¡CONFIGURACIÓN PERFECTA!")

if __name__ == '__main__':
    pass