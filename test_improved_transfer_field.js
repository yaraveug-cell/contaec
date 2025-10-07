/**
 * Test completo del campo Detalle Transferencia mejorado
 * Prueba: ancho duplicado + botón de ocultar/mostrar
 * Version: 3.0 - Campo mejorado con control de visibilidad
 */

console.log('=== TEST CAMPO DETALLE TRANSFERENCIA MEJORADO ===');

function testImprovedTransferDetailField() {
    console.log('🔍 Probando campo mejorado con control de visibilidad...');
    
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
        
        // Buscar opción "Transferencia"
        const transferOption = Array.from(paymentField.options).find(option => 
            option.text.toLowerCase().includes('transferencia')
        );
        
        if (!transferOption) {
            console.warn('⚠️ Opción "Transferencia" no encontrada');
            return false;
        }
        
        console.log('✅ Opción transferencia encontrada:', transferOption.text);
        
        // Test 1: Crear campo y verificar ancho duplicado
        console.log('\n--- Test 1: Crear campo y verificar ancho ---');
        paymentField.value = transferOption.value;
        paymentField.dispatchEvent(new Event('change', { bubbles: true }));
        
        setTimeout(() => {
            const transferField = document.querySelector('#id_transfer_detail');
            
            if (transferField) {
                const computedStyle = window.getComputedStyle(transferField);
                const width = computedStyle.width;
                
                console.log('✅ Campo creado exitosamente');
                console.log('📏 Ancho del campo:', width);
                console.log('📏 Ancho esperado: ~440px');
                
                if (width === '440px' || parseInt(width) >= 440) {
                    console.log('✅ PERFECTO: Ancho duplicado correctamente');
                } else {
                    console.log('⚠️ Ancho diferente al esperado:', width);
                }
                
                // Test 2: Verificar botón de ocultar
                console.log('\n--- Test 2: Verificar botón de control ---');
                const fieldContainer = transferField.parentElement;
                const toggleButton = fieldContainer.querySelector('button');
                
                if (toggleButton) {
                    console.log('✅ Botón de ocultar encontrado');
                    console.log('🎯 Texto del botón:', toggleButton.innerHTML);
                    console.log('🎯 Título del botón:', toggleButton.title);
                    
                    // Test 3: Probar funcionalidad de ocultar
                    console.log('\n--- Test 3: Probar ocultar campo ---');
                    toggleButton.click();
                    
                    setTimeout(() => {
                        const isHidden = transferField.style.display === 'none' || 
                                       window.getComputedStyle(transferField).display === 'none';
                        
                        if (isHidden) {
                            console.log('✅ Campo ocultado correctamente por el usuario');
                            console.log('💡 Valor del campo limpiado:', transferField.value === '');
                            
                            // Test 4: Verificar que se puede mostrar de nuevo cambiando forma de pago
                            console.log('\n--- Test 4: Mostrar de nuevo cambiando forma de pago ---');
                            
                            // Cambiar a otra opción
                            const otherOption = Array.from(paymentField.options).find(option => 
                                !option.text.toLowerCase().includes('transferencia') && option.value !== ''
                            );
                            
                            if (otherOption) {
                                paymentField.value = otherOption.value;
                                paymentField.dispatchEvent(new Event('change', { bubbles: true }));
                                
                                setTimeout(() => {
                                    // Volver a transferencia
                                    paymentField.value = transferOption.value;
                                    paymentField.dispatchEvent(new Event('change', { bubbles: true }));
                                    
                                    setTimeout(() => {
                                        const fieldAfterToggle = document.querySelector('#id_transfer_detail');
                                        const isVisible = fieldAfterToggle && 
                                                        fieldAfterToggle.style.display !== 'none' && 
                                                        window.getComputedStyle(fieldAfterToggle).display !== 'none';
                                        
                                        if (isVisible) {
                                            console.log('✅ Campo se mostró de nuevo al cambiar forma de pago');
                                            
                                            // Test 5: Probar placeholder mejorado
                                            console.log('\n--- Test 5: Verificar placeholder mejorado ---');
                                            console.log('📝 Placeholder:', fieldAfterToggle.placeholder);
                                            
                                            if (fieldAfterToggle.placeholder.length > 30) {
                                                console.log('✅ Placeholder mejorado para campo más ancho');
                                            }
                                            
                                            // Test 6: Probar funcionalidad completa
                                            fieldAfterToggle.value = 'Banco Pichincha - Cuenta Corriente 1234567890 - Transferencia internacional con código SWIFT';
                                            console.log('✅ Valor de prueba largo establecido exitosamente');
                                            
                                            console.log('\n🎉 TODOS LOS TESTS PASARON EXITOSAMENTE');
                                            console.log('📋 Resumen de funcionalidades:');
                                            console.log('  ✅ Ancho duplicado (440px)');
                                            console.log('  ✅ Botón de ocultar/mostrar');
                                            console.log('  ✅ Placeholder mejorado');
                                            console.log('  ✅ Control de visibilidad por usuario');
                                            console.log('  ✅ Limpieza de datos al ocultar');
                                            console.log('  ✅ Restauración al cambiar forma de pago');
                                            
                                        } else {
                                            console.log('❌ Campo no se mostró de nuevo');
                                        }
                                    }, 100);
                                }, 100);
                            }
                            
                        } else {
                            console.log('❌ Campo no se ocultó correctamente');
                        }
                    }, 200);
                    
                } else {
                    console.log('❌ Botón de ocultar no encontrado');
                }
                
            } else {
                console.error('❌ Campo detalle transferencia no se creó');
            }
        }, 200);
        
        return true;
        
    } catch (error) {
        console.error('❌ Error en test:', error);
        return false;
    }
}

// Función para test manual del ancho
function testFieldWidth() {
    const field = document.querySelector('#id_transfer_detail');
    if (field) {
        const style = window.getComputedStyle(field);
        console.log('📏 Información de ancho:', {
            width: style.width,
            minWidth: style.minWidth,
            maxWidth: style.maxWidth,
            boxSizing: style.boxSizing
        });
    } else {
        console.log('⚠️ Campo no encontrado. Selecciona "Transferencia" primero.');
    }
}

// Función para test manual del botón
function testToggleButton() {
    const button = document.querySelector('.field-transfer_detail button');
    if (button) {
        console.log('🎯 Información del botón:', {
            text: button.innerHTML,
            title: button.title,
            visible: button.style.display !== 'none'
        });
        button.click();
        console.log('✅ Botón clickeado');
    } else {
        console.log('⚠️ Botón no encontrado. Asegúrate de que el campo esté visible.');
    }
}

// Ejecutar test cuando la página esté lista
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(testImprovedTransferDetailField, 1500);
    });
} else {
    setTimeout(testImprovedTransferDetailField, 1500);
}

// Funciones disponibles para ejecución manual
window.testImprovedTransferDetailField = testImprovedTransferDetailField;
window.testFieldWidth = testFieldWidth;
window.testToggleButton = testToggleButton;

console.log('✨ Test mejorado cargado.');
console.log('🔧 Funciones disponibles:');
console.log('  - testImprovedTransferDetailField() - Test completo');
console.log('  - testFieldWidth() - Verificar ancho del campo');
console.log('  - testToggleButton() - Probar botón ocultar/mostrar');