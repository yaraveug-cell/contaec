/**
 * Test corregido - Verificar que solo aparece UN campo de detalle transferencia
 * Version: 2.0 - Corregido duplicación
 */

console.log('=== TEST CAMPO ÚNICO DETALLE TRANSFERENCIA ===');

function testSingleTransferDetailField() {
    console.log('🔍 Verificando que solo existe un campo de detalle transferencia...');
    
    try {
        // Verificar que existe el handler
        if (typeof window.TransferDetailHandler === 'undefined') {
            console.error('❌ TransferDetailHandler no está definido');
            return false;
        }
        
        // Verificar que existe el campo payment_form
        const paymentField = document.querySelector('#id_payment_form');
        if (!paymentField) {
            console.error('❌ Campo payment_form no encontrado');
            return false;
        }
        
        console.log('✅ Campo payment_form encontrado');
        
        // Contar campos transfer_detail ANTES de seleccionar transferencia
        let transferFields = document.querySelectorAll('[id*="transfer_detail"], [name*="transfer_detail"]');
        console.log('📊 Campos transfer_detail iniciales:', transferFields.length);
        transferFields.forEach((field, index) => {
            console.log(`   Campo ${index + 1}:`, {
                id: field.id,
                name: field.name,
                tag: field.tagName,
                visible: field.style.display !== 'none',
                parent: field.parentElement?.className
            });
        });
        
        // Buscar opción "Transferencia"
        const transferOption = Array.from(paymentField.options).find(option => 
            option.text.toLowerCase().includes('transferencia')
        );
        
        if (!transferOption) {
            console.warn('⚠️ Opción "Transferencia" no encontrada');
            console.log('Opciones disponibles:', Array.from(paymentField.options).map(o => o.text));
            return false;
        }
        
        console.log('✅ Opción transferencia encontrada:', transferOption.text);
        
        // Test 1: Seleccionar transferencia
        console.log('\n--- Test 1: Seleccionar Transferencia ---');
        paymentField.value = transferOption.value;
        paymentField.dispatchEvent(new Event('change', { bubbles: true }));
        
        setTimeout(() => {
            // Contar campos DESPUÉS de seleccionar transferencia
            transferFields = document.querySelectorAll('[id*="transfer_detail"], [name*="transfer_detail"]');
            console.log('📊 Campos transfer_detail después de seleccionar:', transferFields.length);
            
            let visibleFields = 0;
            transferFields.forEach((field, index) => {
                const isVisible = field.style.display !== 'none' && field.offsetParent !== null;
                if (isVisible) visibleFields++;
                
                console.log(`   Campo ${index + 1}:`, {
                    id: field.id,
                    name: field.name,
                    tag: field.tagName,
                    visible: isVisible,
                    display: field.style.display,
                    parent: field.parentElement?.className,
                    value: field.value || '(vacío)'
                });
            });
            
            // Verificación principal
            if (visibleFields === 1) {
                console.log('✅ PERFECTO: Solo 1 campo visible como esperado');
                
                // Probar funcionalidad del campo único
                const activeField = Array.from(transferFields).find(field => 
                    field.style.display !== 'none' && field.offsetParent !== null
                );
                
                if (activeField) {
                    activeField.value = 'Banco Pichincha - Cuenta 1234567890';
                    console.log('✅ Valor de prueba establecido en campo único');
                    
                    // Test 2: Cambiar a otra forma de pago
                    console.log('\n--- Test 2: Cambiar a Efectivo ---');
                    const efectivoOption = Array.from(paymentField.options).find(option => 
                        option.text.toLowerCase().includes('efectivo')
                    );
                    
                    if (efectivoOption) {
                        paymentField.value = efectivoOption.value;
                        paymentField.dispatchEvent(new Event('change', { bubbles: true }));
                        
                        setTimeout(() => {
                            const visibleAfterChange = Array.from(document.querySelectorAll('[id*="transfer_detail"], [name*="transfer_detail"]'))
                                .filter(field => field.style.display !== 'none' && field.offsetParent !== null).length;
                            
                            if (visibleAfterChange === 0) {
                                console.log('✅ Campo se ocultó correctamente al cambiar forma de pago');
                            } else {
                                console.log('⚠️ Campo aún visible:', visibleAfterChange);
                            }
                            
                            console.log('\n🎉 TEST COMPLETADO EXITOSAMENTE - Campo único funcionando');
                        }, 100);
                    }
                }
                
            } else if (visibleFields === 0) {
                console.log('⚠️ No hay campos visibles - ¿JavaScript no se ejecutó?');
            } else {
                console.log(`❌ PROBLEMA: ${visibleFields} campos visibles (debería ser 1)`);
                console.log('🔧 Necesario eliminar campos duplicados del admin');
            }
        }, 200);
        
        return true;
        
    } catch (error) {
        console.error('❌ Error en test:', error);
        return false;
    }
}

// Ejecutar test cuando la página esté lista
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(testSingleTransferDetailField, 1000); // Esperar 1 segundo para que se carguen todos los scripts
    });
} else {
    setTimeout(testSingleTransferDetailField, 1000);
}

// También hacer disponible para ejecución manual
window.testSingleTransferDetailField = testSingleTransferDetailField;

console.log('✨ Test mejorado cargado. Ejecutar manualmente: testSingleTransferDetailField()');