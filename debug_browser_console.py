#!/usr/bin/env python3
"""
Debug final: Script para generar código de prueba en consola del navegador
"""
print("=== CÓDIGO PARA CONSOLA DEL NAVEGADOR ===\n")

print("// PASO 1: Verificar datos de productos")
print("console.log('Datos de productos:', window.productsData);")
print("console.log('Cantidad de productos:', Object.keys(window.productsData || {}).length);")
print()

print("// PASO 2: Inspeccionar selects de producto")
print("const productSelects = document.querySelectorAll('select');")
print("console.log('Todos los selects:', productSelects);")
print("productSelects.forEach((select, i) => {")
print("    console.log(`Select ${i}:`, select.name, select.id);")
print("});")
print()

print("// PASO 3: Buscar selects de producto específicos")
print("const productSelects2 = document.querySelectorAll('select[name*=\"product\"]');")
print("console.log('Selects de producto encontrados:', productSelects2.length);")
print("productSelects2.forEach(select => console.log('Select producto:', select.name));")
print()

print("// PASO 4: Inspeccionar campos de la primera fila")
print("const firstRow = document.querySelector('tr.form-row, .form-row, fieldset');")
print("console.log('Primera fila encontrada:', firstRow);")
print("if (firstRow) {")
print("    const allInputs = firstRow.querySelectorAll('input, textarea, select');")
print("    console.log('Campos en primera fila:', allInputs.length);")
print("    allInputs.forEach(input => {")
print("        console.log(`Campo: ${input.tagName} name=\"${input.name}\" id=\"${input.id}\"`);")
print("    });")
print("}")
print()

print("// PASO 5: Probar función de autocompletado manualmente")
print("function testAutocomplete() {")
print("    const productSelect = document.querySelector('select[name*=\"product\"]');")
print("    if (productSelect && window.productsData) {")
print("        const firstProductId = Object.keys(window.productsData)[0];")
print("        console.log('Simulando selección de producto:', firstProductId);")
print("        productSelect.value = firstProductId;")
print("        productSelect.dispatchEvent(new Event('change', {bubbles: true}));")
print("    }")
print("}")
print()

print("// EJECUTAR PRUEBA:")
print("testAutocomplete();")
print()

print("=== INSTRUCCIONES ===")
print("1. Ir a: http://127.0.0.1:8000/admin/invoicing/invoice/add/")
print("2. Abrir Developer Tools (F12)")
print("3. Copiar y pegar cada sección en la consola")
print("4. Analizar los resultados para identificar el problema")
print("5. Si testAutocomplete() no funciona, revisar nombres de campos")