// 🧪 TEST: VERIFICAR QUE DUE_DATE NO APARECE EN EL FORMULARIO
// Navegar a: http://127.0.0.1:8000/admin/invoicing/invoice/add/

console.log('🔍 TEST: VERIFICACIÓN CAMPOS FORMULARIO FACTURA');
console.log('=' .repeat(50));

function checkFormFields() {
    
    // 1. Verificar que due_date NO esté presente
    console.log('\n📋 VERIFICANDO CAMPOS DEL FORMULARIO:');
    
    const dueDateField = document.querySelector('input[name="due_date"]') || 
                        document.querySelector('select[name="due_date"]') ||
                        document.querySelector('[name="due_date"]');
    
    if (dueDateField) {
        console.log('❌ PROBLEMA: Campo due_date SÍ está presente en el formulario');
        console.log('   Elemento:', dueDateField);
        return false;
    } else {
        console.log('✅ CORRECTO: Campo due_date NO está presente en el formulario');
    }
    
    // 2. Verificar campos que SÍ deben estar presentes
    const expectedFields = [
        'company',
        'customer', 
        'date',
        'payment_form',
        'account'
    ];
    
    console.log('\n📝 VERIFICANDO CAMPOS REQUERIDOS:');
    let allFieldsPresent = true;
    
    for (let fieldName of expectedFields) {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (field) {
            console.log(`   ✅ ${fieldName}: Presente`);
        } else {
            console.log(`   ❌ ${fieldName}: NO encontrado`);
            allFieldsPresent = false;
        }
    }
    
    // 3. Verificar labels para due_date
    console.log('\n🏷️ VERIFICANDO LABELS:');
    const labels = document.querySelectorAll('label');
    let foundDueDateLabel = false;
    
    for (let label of labels) {
        if (label.textContent.toLowerCase().includes('vencimiento') || 
            label.textContent.toLowerCase().includes('due_date')) {
            console.log(`   ❌ Label sospechoso encontrado: "${label.textContent}"`);
            foundDueDateLabel = true;
        }
    }
    
    if (!foundDueDateLabel) {
        console.log('   ✅ No se encontraron labels de fecha de vencimiento');
    }
    
    // 4. Resultado final
    console.log('\n🎯 RESULTADO FINAL:');
    if (!dueDateField && allFieldsPresent && !foundDueDateLabel) {
        console.log('🏆 ¡CONFIGURACIÓN PERFECTA!');
        console.log('✅ Campo due_date oculto correctamente');
        console.log('✅ Todos los campos necesarios presentes');
        console.log('✅ No hay referencias a fecha de vencimiento');
        return true;
    } else {
        console.log('⚠️ Hay algunos problemas en la configuración');
        return false;
    }
}

// Ejecutar verificación
setTimeout(() => {
    const success = checkFormFields();
    
    if (success) {
        console.log('\n✅ PRUEBA FINAL: Intenta crear una factura para confirmar que no hay errores');
    } else {
        console.log('\n❌ ACCIÓN REQUERIDA: Revisar configuración del formulario');
    }
}, 1000);

console.log('\n⏰ Verificando formulario...');