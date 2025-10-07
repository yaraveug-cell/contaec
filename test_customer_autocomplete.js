// 🧪 TEST: VERIFICAR AUTOCOMPLETADO DE CLIENTES
// Navegar a: http://127.0.0.1:8000/admin/invoicing/invoice/add/

console.log('🔍 TEST: AUTOCOMPLETADO DE CLIENTES');
console.log('=' .repeat(50));

function testCustomerAutocomplete() {
    
    // 1. Verificar que estamos en modo creación
    const url = window.location.pathname;
    const isAddMode = url.includes('/add/');
    
    console.log('\n📍 VERIFICANDO CONTEXTO:');
    console.log(`   URL: ${url}`);
    console.log(`   Modo Añadir: ${isAddMode ? '✅' : '❌'}`);
    
    if (!isAddMode) {
        console.log('⚠️ Este test está diseñado para la vista "Añadir Factura"');
        console.log('📌 Ve a: /admin/invoicing/invoice/add/');
        return;
    }
    
    // 2. Buscar el campo Cliente
    console.log('\n👤 BUSCANDO CAMPO CLIENTE:');
    
    // Buscar tanto input como select (el autocompletado puede usar diferentes elementos)
    const customerField = document.querySelector('select[name="customer"]') || 
                         document.querySelector('input[name="customer"]') ||
                         document.querySelector('#id_customer');
    
    const customerContainer = document.querySelector('.field-customer');
    
    console.log(`   Campo Cliente: ${customerField ? '✅ Encontrado' : '❌ No encontrado'}`);
    console.log(`   Contenedor: ${customerContainer ? '✅ Encontrado' : '❌ No encontrado'}`);
    
    if (customerField) {
        console.log(`   Tipo de elemento: ${customerField.tagName}`);
        console.log(`   Clases: ${customerField.className || 'Ninguna'}`);
        console.log(`   ID: ${customerField.id || 'Sin ID'}`);
    }
    
    // 3. Verificar si tiene funcionalidad de autocompletado
    console.log('\n🔍 VERIFICANDO AUTOCOMPLETADO:');
    
    // Buscar elementos típicos del autocompletado de Django
    const autocompleteElements = {
        select2: document.querySelector('.select2-container'),
        adminAutocomplete: document.querySelector('.admin-autocomplete'),
        selectFilter: document.querySelector('.selector'),
        autocompleteLight: document.querySelector('.autocomplete-light-widget')
    };
    
    let autocompleteType = null;
    for (const [type, element] of Object.entries(autocompleteElements)) {
        if (element) {
            console.log(`   ${type}: ✅ Detectado`);
            autocompleteType = type;
        } else {
            console.log(`   ${type}: ❌ No presente`);
        }
    }
    
    // 4. Verificar atributos de autocompletado
    if (customerField) {
        console.log('\n🔧 ATRIBUTOS DEL CAMPO:');
        
        const hasAutocomplete = customerField.hasAttribute('data-autocomplete-light-url') ||
                               customerField.hasAttribute('data-ajax--url') ||
                               customerField.classList.contains('admin-autocomplete') ||
                               customerField.parentElement.querySelector('.select2-container');
        
        console.log(`   Autocompletado habilitado: ${hasAutocomplete ? '✅' : '❌'}`);
        
        // Verificar URL de autocompletado
        const autocompleteUrl = customerField.getAttribute('data-autocomplete-light-url') ||
                               customerField.getAttribute('data-ajax--url');
        
        if (autocompleteUrl) {
            console.log(`   URL autocompletado: ${autocompleteUrl}`);
        }
        
        // Verificar si es un select múltiple o simple
        const isMultiple = customerField.hasAttribute('multiple');
        console.log(`   Selección múltiple: ${isMultiple ? '✅' : '❌'}`);
    }
    
    // 5. Test funcional básico
    console.log('\n🧪 TEST FUNCIONAL:');
    
    if (customerField && autocompleteType) {
        console.log('   📝 Instrucciones para test manual:');
        console.log('   1. Haz clic en el campo Cliente');
        console.log('   2. Escribe algunas letras (ej: "mar", "ana", "123")');
        console.log('   3. Verifica que aparezcan sugerencias de clientes');
        console.log('   4. Selecciona un cliente de la lista');
        
        // Intentar enfocar el campo para activar autocompletado
        try {
            customerField.focus();
            console.log('   ✅ Campo enfocado para activar autocompletado');
        } catch (e) {
            console.log('   ⚠️ No se pudo enfocar el campo automáticamente');
        }
        
    } else {
        console.log('   ❌ No se puede realizar test funcional');
        console.log('   ⚠️ Campo o autocompletado no detectado');
    }
    
    // 6. Verificar datos de clientes disponibles
    console.log('\n📊 VERIFICANDO DATOS:');
    
    // Si es un select tradicional, contar opciones
    if (customerField && customerField.tagName === 'SELECT') {
        const options = customerField.querySelectorAll('option');
        console.log(`   Opciones disponibles: ${options.length}`);
        
        if (options.length > 1) { // Excluyendo la opción vacía
            console.log('   📋 Primeros clientes:');
            Array.from(options).slice(1, 6).forEach((option, index) => {
                console.log(`      ${index + 1}. ${option.textContent.trim()}`);
            });
        }
    }
    
    // 7. Resultado final
    console.log('\n🏆 RESULTADO FINAL:');
    
    if (customerField && autocompleteType) {
        console.log('🎉 ¡AUTOCOMPLETADO DETECTADO!');
        console.log(`✅ Tipo: ${autocompleteType}`);
        console.log('✅ Campo Cliente configurado correctamente');
        console.log('📝 Prueba escribiendo en el campo para ver sugerencias');
    } else if (customerField) {
        console.log('⚠️ Campo Cliente encontrado pero sin autocompletado detectado');
        console.log('🔧 Puede necesitar configuración adicional');
    } else {
        console.log('❌ Campo Cliente no encontrado');
        console.log('⚠️ Verificar configuración del admin');
    }
    
    // 8. Enlaces útiles
    console.log('\n🔗 ENLACES DE VERIFICACIÓN:');
    console.log('📋 Lista de clientes: /admin/invoicing/customer/');
    console.log('➕ Agregar cliente: /admin/invoicing/customer/add/');
}

// Ejecutar test después de que cargue la página
setTimeout(testCustomerAutocomplete, 2000);

console.log('\n⏰ Iniciando verificación de autocompletado...');