#!/usr/bin/env python3
"""
Script para generar análisis de estructura de filas de factura
Este script genera código JavaScript que debe ejecutarse en la consola del navegador
para analizar las diferencias entre las primeras 3 filas y las nuevas filas agregadas.
"""

def generate_analysis_code():
    """Genera código JavaScript para analizar la estructura de las filas"""
    
    js_code = '''
console.log("🔍 === ANÁLISIS DE ESTRUCTURA DE FILAS DE FACTURA ===");

// Función para analizar una fila específica
function analyzeRow(rowElement, rowNumber) {
    if (!rowElement) {
        console.log(`❌ Fila ${rowNumber} no encontrada`);
        return null;
    }
    
    console.log(`\\n📋 === ANÁLISIS FILA ${rowNumber} ===`);
    console.log(`🏷️  Elemento:`, rowElement);
    console.log(`🏷️  Clases:`, rowElement.className);
    console.log(`🏷️  ID:`, rowElement.id || 'Sin ID');
    
    // Analizar campo de producto
    const productField = rowElement.querySelector('.field-product, [class*="field-product"], td.field-product');
    if (productField) {
        console.log(`\\n🎯 Campo Producto - Fila ${rowNumber}:`);
        console.log(`   📐 width:`, getComputedStyle(productField).width);
        console.log(`   📐 minWidth:`, getComputedStyle(productField).minWidth);
        console.log(`   📐 maxWidth:`, getComputedStyle(productField).maxWidth);
        console.log(`   📐 flex:`, getComputedStyle(productField).flex);
        console.log(`   📐 display:`, getComputedStyle(productField).display);
        console.log(`   📐 boxSizing:`, getComputedStyle(productField).boxSizing);
        console.log(`   🏷️  Clases:`, productField.className);
        console.log(`   🏷️  Inline styles:`, productField.style.cssText);
        
        // Buscar el select dentro del campo
        const selectElement = productField.querySelector('select');
        if (selectElement) {
            console.log(`   🔽 Select element:`, selectElement);
            console.log(`   🔽 Select width:`, getComputedStyle(selectElement).width);
            console.log(`   🔽 Select classes:`, selectElement.className);
            console.log(`   🔽 Select styles:`, selectElement.style.cssText);
        }
    } else {
        console.log(`❌ Campo producto no encontrado en fila ${rowNumber}`);
    }
    
    // Analizar otros campos
    const fieldTypes = ['quantity', 'unit_price', 'discount', 'iva_rate', 'line_total'];
    fieldTypes.forEach(fieldType => {
        const field = rowElement.querySelector(`.field-${fieldType}, [class*="field-${fieldType}"], td.field-${fieldType}`);
        if (field) {
            const computedStyle = getComputedStyle(field);
            console.log(`   📊 ${fieldType}: width=${computedStyle.width}, classes="${field.className}"`);
        }
    });
    
    return {
        element: rowElement,
        productField: productField,
        hasCorrectStyles: productField ? getComputedStyle(productField).width.includes('35') : false
    };
}

// Obtener todas las filas (excluyendo la fila de agregar)
const allRows = document.querySelectorAll('.form-row:not(.add-row)');
console.log(`\\n📊 Total de filas encontradas: ${allRows.length}`);

// Analizar las primeras 3 filas
console.log("\\n🎯 === ANÁLISIS DE PRIMERAS 3 FILAS ===");
const firstThreeRows = [];
for (let i = 0; i < Math.min(3, allRows.length); i++) {
    firstThreeRows.push(analyzeRow(allRows[i], i + 1));
}

// Analizar las filas adicionales (4ta en adelante)
if (allRows.length > 3) {
    console.log("\\n🆕 === ANÁLISIS DE FILAS ADICIONALES (4ta+) ===");
    const additionalRows = [];
    for (let i = 3; i < allRows.length; i++) {
        additionalRows.push(analyzeRow(allRows[i], i + 1));
    }
    
    // Comparar estructuras
    console.log("\\n⚖️  === COMPARACIÓN ESTRUCTURAL ===");
    const firstRowData = firstThreeRows[0];
    const fourthRowData = additionalRows[0];
    
    if (firstRowData && fourthRowData) {
        console.log("🔍 Comparando fila 1 vs fila 4:");
        
        // Comparar clases del contenedor
        console.log(`   📋 Clases fila 1: "${firstRowData.element.className}"`);
        console.log(`   📋 Clases fila 4: "${fourthRowData.element.className}"`);
        console.log(`   ✅ Clases iguales: ${firstRowData.element.className === fourthRowData.element.className}`);
        
        // Comparar campo producto
        if (firstRowData.productField && fourthRowData.productField) {
            const field1Styles = getComputedStyle(firstRowData.productField);
            const field4Styles = getComputedStyle(fourthRowData.productField);
            
            console.log(`\\n🎯 Comparación campo producto:`);
            console.log(`   📐 Fila 1 width: ${field1Styles.width}`);
            console.log(`   📐 Fila 4 width: ${field4Styles.width}`);
            console.log(`   📐 Fila 1 classes: "${firstRowData.productField.className}"`);
            console.log(`   📐 Fila 4 classes: "${fourthRowData.productField.className}"`);
            
            // Verificar si tienen los mismos estilos aplicados
            const stylesMatch = field1Styles.width === field4Styles.width;
            console.log(`   ✅ Estilos coinciden: ${stylesMatch}`);
            
            if (!stylesMatch) {
                console.log(`\\n🚨 PROBLEMA DETECTADO:`);
                console.log(`   La fila 4 tiene diferentes estilos que la fila 1`);
                console.log(`   Esto explica por qué el campo producto se ve pequeño`);
            }
        }
    }
} else {
    console.log("ℹ️  Solo hay 3 filas o menos, agrega más filas para comparar");
}

// Función para mostrar todos los selectores CSS que pueden estar afectando
console.log("\\n🎨 === ANÁLISIS DE SELECTORES CSS ===");
const productFields = document.querySelectorAll('.field-product, [class*="field-product"], td.field-product');
productFields.forEach((field, index) => {
    console.log(`\\n📋 Campo producto ${index + 1}:`);
    console.log(`   🏷️  Elemento:`, field);
    console.log(`   🏷️  Padre:`, field.parentElement);
    console.log(`   🎨 Estilos computados:`, {
        width: getComputedStyle(field).width,
        minWidth: getComputedStyle(field).minWidth,
        maxWidth: getComputedStyle(field).maxWidth,
        flex: getComputedStyle(field).flex,
        display: getComputedStyle(field).display
    });
});

console.log("\\n✅ === ANÁLISIS COMPLETADO ===");
console.log("Para aplicar estilos manualmente, usa: forceFieldWidths()");
'''
    
    return js_code

if __name__ == "__main__":
    print("🔍 GENERANDO CÓDIGO DE ANÁLISIS DE ESTRUCTURA DE FILAS")
    print("=" * 60)
    
    analysis_code = generate_analysis_code()
    
    print("📋 CÓDIGO JAVASCRIPT GENERADO:")
    print("=" * 60)
    print("Copia y pega el siguiente código en la consola del navegador:")
    print("=" * 60)
    print()
    print(analysis_code)
    print()
    print("=" * 60)
    print("✅ INSTRUCCIONES:")
    print("1. Abre la página de crear factura")
    print("2. Agrega al menos 4 filas de factura")
    print("3. Abre las herramientas de desarrollador (F12)")
    print("4. Pega el código en la consola y presiona Enter")
    print("5. Revisa el análisis detallado en la consola")