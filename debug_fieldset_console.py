#!/usr/bin/env python3
"""
Script para generar código de debugging de la detección de fieldset
Este código se puede ejecutar en la consola del navegador
"""

print("🔧 DEBUGGING CÓDIGO PARA CONSOLA DEL NAVEGADOR")
print("=" * 55)

debugging_js = '''
// ========================================
// DEBUGGING DETECCIÓN DE FIELDSET 
// ========================================
// Copiar y pegar este código en la consola del navegador

console.clear();
console.log('🔍 INICIANDO DEBUGGING DE DETECCIÓN DE FIELDSET');
console.log('=' * 50);

// 1. Información general de la página
console.log('📄 INFORMACIÓN DE LA PÁGINA:');
console.log('URL:', window.location.href);
console.log('Title:', document.title);
console.log('');

// 2. Buscar elementos estructurales
console.log('🏗️ ELEMENTOS ESTRUCTURALES:');
console.log('Fieldsets:', document.querySelectorAll('fieldset').length);
console.log('Modules:', document.querySelectorAll('.module').length);  
console.log('Form-rows:', document.querySelectorAll('.form-row').length);
console.log('Fields [class*="field-"]:', document.querySelectorAll('[class*="field-"]').length);
console.log('');

// 3. Buscar headers
console.log('📋 HEADERS ENCONTRADOS:');
const headers = document.querySelectorAll('h1, h2, h3, legend');
headers.forEach((header, index) => {
    console.log(`${index + 1}. "${header.textContent.trim()}" (${header.tagName})`);
    if (header.textContent.toLowerCase().includes('información') || 
        header.textContent.toLowerCase().includes('basic')) {
        console.log('   🎯 POSIBLE MATCH:', header);
    }
});
console.log('');

// 4. Probar estrategias de detección
console.log('🎯 PROBANDO ESTRATEGIAS DE DETECCIÓN:');

// Estrategia 1: Headers
console.log('📋 Estrategia 1: Headers...');
const targetHeaders = Array.from(headers).filter(h => {
    const text = h.textContent.toLowerCase();
    return text.includes('información básica') || text.includes('informacion basica') || 
           text.includes('basic') || text.includes('general');
});
if (targetHeaders.length > 0) {
    console.log('✅ Headers encontrados:', targetHeaders);
    targetHeaders.forEach(h => {
        const container = h.closest('fieldset, .module, .form-group, .section');
        console.log('   Contenedor:', container);
    });
} else {
    console.log('❌ No se encontraron headers relevantes');
}

// Estrategia 2: Fieldset module
console.log('📋 Estrategia 2: Fieldset module...');
const moduleFieldset = document.querySelector('fieldset.module.aligned, fieldset.module');
if (moduleFieldset) {
    console.log('✅ Fieldset module encontrado:', moduleFieldset);
} else {
    console.log('❌ No se encontró fieldset.module');
}

// Estrategia 3: Campos conocidos
console.log('📋 Estrategia 3: Campos conocidos...');
const knownFields = ['.field-company', '.field-customer', '.field-payment_form', '.field-date', '.field-account'];
knownFields.forEach(selector => {
    const field = document.querySelector(selector);
    console.log(`${selector}:`, field ? 'ENCONTRADO' : 'NO ENCONTRADO');
    if (field) {
        const containers = [
            field.closest('fieldset'),
            field.closest('.module'),
            field.closest('.form-group'),
            field.closest('.section')
        ].filter(Boolean);
        console.log(`   Contenedores posibles:`, containers.length);
        if (containers.length > 0) {
            console.log('   Mejor contenedor:', containers[0]);
        }
    }
});

// Estrategia 4: Contenedor padre común
console.log('📋 Estrategia 4: Contenedor padre común...');
const companyField = document.querySelector('.field-company, #id_company');
const customerField = document.querySelector('.field-customer, #id_customer');
console.log('Campo company:', companyField ? 'ENCONTRADO' : 'NO ENCONTRADO');
console.log('Campo customer:', customerField ? 'ENCONTRADO' : 'NO ENCONTRADO');

if (companyField && customerField) {
    let parent = companyField.parentElement;
    let level = 0;
    while (parent && parent !== document.body && level < 10) {
        if (parent.contains(customerField)) {
            console.log('✅ Contenedor padre común encontrado:', parent);
            console.log('   Nivel:', level);
            console.log('   Clase:', parent.className);
            console.log('   Tag:', parent.tagName);
            break;
        }
        parent = parent.parentElement;
        level++;
    }
}

// 5. Información final
console.log('');
console.log('📊 RESUMEN FINAL:');
console.log('Mejor candidato para fieldset:');

// Probar la función real si está disponible
if (typeof findInfoBasicaFieldset === 'function') {
    console.log('🧪 Probando función findInfoBasicaFieldset...');
    const result = findInfoBasicaFieldset();
    console.log('Resultado:', result);
} else {
    console.log('⚠️ Función findInfoBasicaFieldset no disponible');
}

console.log('');
console.log('🎯 ACCIÓN RECOMENDADA:');
console.log('Usar el elemento que mejor represente el contenedor de los campos básicos');
console.log('Priorizar: fieldset > .module > contenedor padre común');
'''

print("📋 CÓDIGO DE DEBUGGING:")
print("-" * 25)
print(debugging_js)

print("\n🎯 INSTRUCCIONES:")
print("-" * 17)
print("1. Abrir una factura en el admin Django")
print("2. Presionar F12 para abrir DevTools") 
print("3. Ir a la pestaña 'Console'")
print("4. Copiar y pegar el código anterior")
print("5. Presionar Enter para ejecutar")
print("6. Analizar los resultados")

print(f"\n💡 OBJETIVO:")
print("Identificar cuál estrategia detecta correctamente")
print("el fieldset 'Información Básica' en tu instalación")