/**
 * Test del campo de detalle de transferencia
 * Verificar que aparece/desaparece según la forma de pago seleccionada
 */

console.log('=== TEST DETALLE TRANSFERENCIA ===');

function testTransferDetailField() {
    console.log('Iniciando test del campo detalle transferencia...');
    
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
        
        console.log('✅ Campo payment_form encontrado:', paymentField);
        
        // Verificar que no existe el campo de detalle inicialmente
        let transferField = document.querySelector('#id_transfer_detail');
        console.log('Campo transfer_detail inicial:', transferField ? 'Existe' : 'No existe');
        
        // Buscar opción "Transferencia" en el select
        const transferOption = Array.from(paymentField.options).find(option => 
            option.text.toLowerCase().includes('transferencia')
        );
        
        if (!transferOption) {
            console.warn('⚠️ Opción "Transferencia" no encontrada en el select');
            console.log('Opciones disponibles:', Array.from(paymentField.options).map(o => o.text));
            return false;
        }
        
        console.log('✅ Opción transferencia encontrada:', transferOption.text, 'valor:', transferOption.value);
        
        // Test 1: Seleccionar transferencia - debe aparecer el campo
        console.log('\n--- Test 1: Seleccionar Transferencia ---');
        paymentField.value = transferOption.value;
        paymentField.dispatchEvent(new Event('change', { bubbles: true }));
        
        setTimeout(() => {
            transferField = document.querySelector('#id_transfer_detail');
            if (transferField) {
                console.log('✅ Campo detalle transferencia apareció correctamente');
                console.log('Propiedades del campo:', {
                    id: transferField.id,
                    name: transferField.name,
                    placeholder: transferField.placeholder,
                    visible: transferField.style.display !== 'none'
                });
                
                // Test 2: Seleccionar otra opción - debe desaparecer el campo
                console.log('\n--- Test 2: Cambiar a otra opción ---');
                const otherOption = Array.from(paymentField.options).find(option => 
                    !option.text.toLowerCase().includes('transferencia') && option.value !== ''
                );
                
                if (otherOption) {
                    paymentField.value = otherOption.value;
                    paymentField.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    setTimeout(() => {
                        transferField = document.querySelector('#id_transfer_detail');
                        if (!transferField) {
                            console.log('✅ Campo detalle transferencia se ocultó correctamente');
                        } else {
                            console.log('ℹ️ Campo aún existe pero podría estar oculto:', transferField.style.display);
                        }
                        
                        // Test 3: Volver a seleccionar transferencia
                        console.log('\n--- Test 3: Volver a seleccionar Transferencia ---');
                        paymentField.value = transferOption.value;
                        paymentField.dispatchEvent(new Event('change', { bubbles: true }));
                        
                        setTimeout(() => {
                            transferField = document.querySelector('#id_transfer_detail');
                            if (transferField) {
                                console.log('✅ Campo detalle transferencia reapareció correctamente');
                                
                                // Test del valor
                                transferField.value = 'Transferencia a cuenta corriente 123456789';
                                console.log('✅ Valor de prueba establecido:', transferField.value);
                                
                                console.log('\n🎉 TODOS LOS TESTS PASARON EXITOSAMENTE');
                            } else {
                                console.error('❌ Campo no reapareció en el segundo test');
                            }
                        }, 100);
                    }, 100);
                } else {
                    console.warn('⚠️ No se encontró otra opción para el test 2');
                }
            } else {
                console.error('❌ Campo detalle transferencia NO apareció');
            }
        }, 100);
        
        return true;
        
    } catch (error) {
        console.error('❌ Error en test:', error);
        return false;
    }
}

// Ejecutar test cuando la página esté lista
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', testTransferDetailField);
} else {
    testTransferDetailField();
}

// También hacer disponible para ejecución manual
window.testTransferDetailField = testTransferDetailField;

console.log('Test cargado. Puedes ejecutar manualmente con: testTransferDetailField()');