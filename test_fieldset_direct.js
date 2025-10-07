// TESTING DIRECTO DE DETECCIÓN DE FIELDSET
// Pegar este código en la consola del navegador para debugging inmediato

console.clear();
console.log('🎯 TESTING DIRECTO - DETECCIÓN DE FIELDSET');
console.log('==========================================');

// Función de testing simplificada
function testFieldsetDetection() {
    console.log('🔍 Iniciando test de detección...');
    
    // Test 1: Elementos básicos
    console.log('\n📋 TEST 1: ELEMENTOS BÁSICOS');
    console.log('Fieldsets:', document.querySelectorAll('fieldset').length);
    console.log('Modules:', document.querySelectorAll('.module').length);
    console.log('Form-rows:', document.querySelectorAll('.form-row').length);
    
    // Test 2: Campos específicos
    console.log('\n📋 TEST 2: CAMPOS ESPECÍFICOS');
    const fields = ['company', 'customer', 'payment_form', 'date', 'account'];
    fields.forEach(field => {
        const element = document.querySelector(`.field-${field}`) || document.querySelector(`#id_${field}`);
        console.log(`${field}:`, element ? '✅' : '❌');
        if (element) {
            console.log(`  Elemento:`, element);
            console.log(`  Padre:`, element.parentElement);
        }
    });
    
    // Test 3: Primer fieldset o module
    console.log('\n📋 TEST 3: PRIMER CONTENEDOR');
    const firstFieldset = document.querySelector('fieldset');
    const firstModule = document.querySelector('.module');
    
    console.log('Primer fieldset:', firstFieldset);
    console.log('Primer module:', firstModule);
    
    // Test 4: Mejor candidato
    console.log('\n📋 TEST 4: MEJOR CANDIDATO');
    const candidate = firstFieldset || firstModule || document.querySelector('.form-row')?.parentElement;
    console.log('Candidato seleccionado:', candidate);
    
    if (candidate) {
        const rect = candidate.getBoundingClientRect();
        console.log('Dimensiones:', `${rect.width}x${rect.height}`);
        console.log('Posición:', `${rect.left},${rect.top}`);
    }
    
    return candidate;
}

// Ejecutar test
const result = testFieldsetDetection();

console.log('\n🎯 RESULTADO FINAL:');
console.log('Fieldset detectado:', result);

// Si se encuentra, probar posicionamiento
if (result) {
    console.log('\n📐 PRUEBA DE POSICIONAMIENTO:');
    const rect = result.getBoundingClientRect();
    const modalWidth = 280;
    const viewportWidth = window.innerWidth;
    const rightEdge = rect.right;
    const availableSpace = viewportWidth - rightEdge;
    
    console.log('Borde derecho fieldset:', rightEdge);
    console.log('Ancho viewport:', viewportWidth);
    console.log('Espacio disponible:', availableSpace);
    console.log('Ancho modal:', modalWidth);
    console.log('¿Puede engancharse?', availableSpace >= modalWidth + 20);
    
    if (availableSpace >= modalWidth + 20) {
        const modalLeft = rightEdge + 10;
        const modalTop = rect.top + window.scrollY;
        console.log(`✅ Posición calculada: left=${modalLeft}, top=${modalTop}`);
    } else {
        console.log('❌ No hay espacio suficiente para enganchar');
    }
}