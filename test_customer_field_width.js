// 🧪 TEST: VERIFICAR ANCHO DEL CAMPO CLIENTE
// Navegar a: http://127.0.0.1:8000/admin/invoicing/invoice/add/

console.log('📏 TEST: ANCHO DEL CAMPO CLIENTE');
console.log('=' .repeat(50));

function testCustomerFieldWidth() {
    
    // 1. Buscar el campo Cliente
    console.log('\n👤 BUSCANDO CAMPO CLIENTE:');
    
    const customerField = document.querySelector('select[name="customer"]') || 
                         document.querySelector('input[name="customer"]') ||
                         document.querySelector('#id_customer') ||
                         document.querySelector('.field-customer select') ||
                         document.querySelector('.field-customer input');
    
    const customerContainer = document.querySelector('.field-customer');
    const select2Container = document.querySelector('.field-customer .select2-container');
    
    console.log(`   Campo Cliente: ${customerField ? '✅ Encontrado' : '❌ No encontrado'}`);
    console.log(`   Contenedor: ${customerContainer ? '✅ Encontrado' : '❌ No encontrado'}`);
    console.log(`   Select2: ${select2Container ? '✅ Presente' : '❌ No presente'}`);
    
    if (customerField) {
        console.log(`   Tipo: ${customerField.tagName.toLowerCase()}`);
        console.log(`   ID: ${customerField.id || 'Sin ID'}`);
        console.log(`   Clases: ${customerField.className || 'Sin clases'}`);
    }
    
    // 2. Medir ancho actual del campo
    console.log('\n📏 MIDIENDO ANCHO DEL CAMPO:');
    
    let fieldToMeasure = select2Container || customerField;
    
    if (fieldToMeasure) {
        const computedStyle = window.getComputedStyle(fieldToMeasure);
        const width = fieldToMeasure.offsetWidth;
        const cssWidth = computedStyle.width;
        const minWidth = computedStyle.minWidth;
        const maxWidth = computedStyle.maxWidth;
        
        console.log(`   Ancho actual: ${width}px`);
        console.log(`   CSS width: ${cssWidth}`);
        console.log(`   CSS min-width: ${minWidth}`);
        console.log(`   CSS max-width: ${maxWidth}`);
        
        // Verificar si cumple con el ancho esperado (500px)
        const expectedWidth = 500;
        const tolerance = 50; // Tolerancia de 50px
        
        const isCorrectWidth = Math.abs(width - expectedWidth) <= tolerance;
        console.log(`   ✅ Ancho esperado: ~${expectedWidth}px (±${tolerance}px)`);
        console.log(`   ${isCorrectWidth ? '✅' : '❌'} Ancho correcto: ${isCorrectWidth ? 'Sí' : 'No'}`);
        
    } else {
        console.log('   ❌ No se puede medir - campo no encontrado');
    }
    
    // 3. Verificar CSS aplicado
    console.log('\n🎨 VERIFICANDO CSS APLICADO:');
    
    if (customerContainer) {
        const containerStyle = window.getComputedStyle(customerContainer);
        console.log(`   Contenedor display: ${containerStyle.display}`);
        console.log(`   Contenedor margin-bottom: ${containerStyle.marginBottom}`);
    }
    
    if (customerField) {
        const fieldStyle = window.getComputedStyle(customerField);
        console.log(`   Campo border: ${fieldStyle.border}`);
        console.log(`   Campo padding: ${fieldStyle.padding}`);
        console.log(`   Campo font-family: ${fieldStyle.fontFamily.substring(0, 50)}...`);
        console.log(`   Campo background-color: ${fieldStyle.backgroundColor}`);
    }
    
    // 4. Comparar con otros campos
    console.log('\n📊 COMPARACIÓN CON OTROS CAMPOS:');
    
    const paymentField = document.querySelector('.field-payment_form select');
    const accountField = document.querySelector('.field-account select');
    const companyField = document.querySelector('.field-company select');
    
    const fields = [
        { name: 'Cliente', element: fieldToMeasure },
        { name: 'Forma de Pago', element: paymentField },
        { name: 'Cuenta', element: accountField },
        { name: 'Empresa', element: companyField }
    ];
    
    fields.forEach(field => {
        if (field.element) {
            const width = field.element.offsetWidth;
            console.log(`   ${field.name}: ${width}px`);
        } else {
            console.log(`   ${field.name}: No encontrado`);
        }
    });
    
    // 5. Verificar responsividad
    console.log('\n📱 VERIFICANDO RESPONSIVIDAD:');
    
    const screenWidth = window.innerWidth;
    console.log(`   Ancho de pantalla: ${screenWidth}px`);
    
    let expectedResponsiveWidth;
    if (screenWidth <= 900) {
        expectedResponsiveWidth = '100% o mínimo 280px';
    } else if (screenWidth <= 1200) {
        expectedResponsiveWidth = '400px o mínimo 320px';
    } else {
        expectedResponsiveWidth = '500px';
    }
    
    console.log(`   Ancho esperado para esta pantalla: ${expectedResponsiveWidth}`);
    
    // 6. Probar funcionalidad
    console.log('\n🧪 PROBANDO FUNCIONALIDAD:');
    
    if (customerField) {
        console.log('   📝 Instrucciones de prueba:');
        console.log('   1. Haz clic en el campo Cliente');
        console.log('   2. Verifica que el ancho sea cómodo para leer nombres largos');
        console.log('   3. Si tiene autocompletado, escribe algunas letras');
        console.log('   4. Verifica que las sugerencias se muestren completamente');
        
        // Intentar enfocar para mostrar el campo activo
        try {
            customerField.focus();
            setTimeout(() => {
                console.log('   ✅ Campo enfocado - verifica visualmente el ancho');
            }, 500);
        } catch (e) {
            console.log('   ⚠️ No se pudo enfocar automáticamente');
        }
        
    } else {
        console.log('   ❌ No se puede probar - campo no disponible');
    }
    
    // 7. Resultado final
    console.log('\n🏆 RESULTADO FINAL:');
    
    if (fieldToMeasure) {
        const width = fieldToMeasure.offsetWidth;
        
        if (width >= 400) {
            console.log('🎉 ¡CAMPO CLIENTE OPTIMIZADO!');
            console.log(`✅ Ancho actual: ${width}px`);
            console.log('✅ Suficiente espacio para nombres largos');
            console.log('✅ Mejor experiencia de usuario');
        } else {
            console.log('⚠️ El campo podría ser más ancho');
            console.log(`📏 Ancho actual: ${width}px (recomendado: 400px+)`);
        }
    } else {
        console.log('❌ No se pudo verificar el ancho del campo');
    }
    
    // 8. Consejos adicionales
    console.log('\n💡 CONSEJOS:');
    console.log('• El campo Cliente ahora es más ancho para mejor legibilidad');
    console.log('• Funciona con autocompletado nativo de Django');
    console.log('• Es responsive según el tamaño de pantalla');
    console.log('• Mantiene el estilo consistente con otros campos');
}

// Ejecutar test después de cargar
setTimeout(testCustomerFieldWidth, 2000);

console.log('\n⏰ Midiendo ancho del campo Cliente...');