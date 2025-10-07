#!/usr/bin/env python3
"""
Script para crear código JavaScript adicional que verifique estilos CSS específicos
Este código debe ejecutarse DESPUÉS del análisis principal en la consola del navegador
"""

def generate_css_analysis_code():
    """Genera código JavaScript para analizar estilos CSS específicos"""
    
    js_code = '''
console.log("\\n🎨 === ANÁLISIS DETALLADO DE CSS ===");

// Función para obtener todos los estilos que afectan un elemento
function getAppliedStyles(element) {
    const styles = getComputedStyle(element);
    const relevantProps = ['width', 'minWidth', 'maxWidth', 'flex', 'flexBasis', 'flexGrow', 'flexShrink', 'display', 'boxSizing'];
    
    const appliedStyles = {};
    relevantProps.forEach(prop => {
        appliedStyles[prop] = styles[prop];
    });
    
    return appliedStyles;
}

// Verificar si hay reglas CSS específicas de Django admin
console.log("\\n🔍 Verificando reglas CSS de Django admin...");

// Obtener todas las hojas de estilo
const styleSheets = Array.from(document.styleSheets);
console.log(`📄 Hojas de estilo encontradas: ${styleSheets.length}`);

// Buscar reglas específicas que puedan afectar las filas
const relevantRules = [];
styleSheets.forEach((sheet, sheetIndex) => {
    try {
        const rules = sheet.cssRules || sheet.rules;
        if (rules) {
            Array.from(rules).forEach((rule, ruleIndex) => {
                if (rule.selectorText && (
                    rule.selectorText.includes('tabular') ||
                    rule.selectorText.includes('form-row') ||
                    rule.selectorText.includes('field-product') ||
                    rule.selectorText.includes('inline')
                )) {
                    relevantRules.push({
                        sheet: sheetIndex,
                        rule: ruleIndex,
                        selector: rule.selectorText,
                        cssText: rule.cssText,
                        href: sheet.href || 'inline'
                    });
                }
            });
        }
    } catch (e) {
        console.log(`⚠️  No se pudo acceder a la hoja de estilo ${sheetIndex}: ${e.message}`);
    }
});

console.log(`\\n📋 Reglas CSS relevantes encontradas: ${relevantRules.length}`);
relevantRules.forEach((rule, index) => {
    console.log(`\\n${index + 1}. ${rule.selector}`);
    console.log(`   📄 Archivo: ${rule.href}`);
    console.log(`   🎨 CSS: ${rule.cssText}`);
});

// Análisis de diferencias específicas entre filas
console.log("\\n🔬 === ANÁLISIS DE DIFERENCIAS ESPECÍFICAS ===");

const rows = document.querySelectorAll('.form-row:not(.add-row)');
if (rows.length >= 4) {
    const row1 = rows[0];
    const row4 = rows[3];
    
    console.log("\\n📊 Comparando elementos HTML:");
    
    // Comparar estructura HTML
    const row1HTML = row1.outerHTML.substring(0, 200) + '...';
    const row4HTML = row4.outerHTML.substring(0, 200) + '...';
    
    console.log("\\n🔍 HTML Fila 1 (primeros 200 chars):");
    console.log(row1HTML);
    console.log("\\n🔍 HTML Fila 4 (primeros 200 chars):");  
    console.log(row4HTML);
    
    // Verificar atributos específicos
    console.log("\\n📋 Atributos comparados:");
    ['class', 'id', 'style'].forEach(attr => {
        const row1Attr = row1.getAttribute(attr) || 'none';
        const row4Attr = row4.getAttribute(attr) || 'none';
        console.log(`   ${attr}:`);
        console.log(`     Fila 1: "${row1Attr}"`);
        console.log(`     Fila 4: "${row4Attr}"`);
        console.log(`     ✅ Iguales: ${row1Attr === row4Attr}`);
    });
    
    // Comparar campos de producto específicamente
    const product1 = row1.querySelector('.field-product, [class*="field-product"], td.field-product');
    const product4 = row4.querySelector('.field-product, [class*="field-product"], td.field-product');
    
    if (product1 && product4) {
        console.log("\\n🎯 Análisis detallado campo producto:");
        
        const styles1 = getAppliedStyles(product1);
        const styles4 = getAppliedStyles(product4);
        
        Object.keys(styles1).forEach(prop => {
            const match = styles1[prop] === styles4[prop];
            console.log(`   ${prop}: Fila1="${styles1[prop]}" | Fila4="${styles4[prop]}" | ✅ ${match}`);
        });
        
        // Verificar jerarquía de elementos padre
        console.log("\\n🌳 Jerarquía de elementos padre:");
        console.log("   Fila 1 - Padres:");
        let parent1 = product1.parentElement;
        let level = 1;
        while (parent1 && level <= 3) {
            console.log(`     Nivel ${level}: ${parent1.tagName}.${parent1.className}`);
            parent1 = parent1.parentElement;
            level++;
        }
        
        console.log("   Fila 4 - Padres:");
        let parent4 = product4.parentElement;
        level = 1;
        while (parent4 && level <= 3) {
            console.log(`     Nivel ${level}: ${parent4.tagName}.${parent4.className}`);
            parent4 = parent4.parentElement;
            level++;
        }
    }
}

// Verificar timing de aplicación de estilos
console.log("\\n⏰ === ANÁLISIS DE TIMING ===");
console.log("Verificando cuándo se aplican los estilos...");

// Simular la adición de una nueva fila para ver qué pasa
console.log("\\n🧪 Para probar, ejecuta estos comandos paso a paso:");
console.log("1. Agrega una nueva fila manualmente");
console.log("2. Ejecuta: forceFieldWidths()");
console.log("3. Ejecuta este análisis nuevamente para ver diferencias");

console.log("\\n✅ === ANÁLISIS CSS COMPLETADO ===");
'''
    
    return js_code

if __name__ == "__main__":
    print("🎨 GENERANDO CÓDIGO DE ANÁLISIS CSS DETALLADO")
    print("=" * 60)
    
    css_analysis_code = generate_css_analysis_code()
    
    print("📋 CÓDIGO JAVASCRIPT CSS ANALYSIS:")
    print("=" * 60)
    print("EJECUTAR DESPUÉS DEL ANÁLISIS PRINCIPAL:")
    print("=" * 60)
    print()
    print(css_analysis_code)
    print()
    print("=" * 60)
    print("✅ USO:")
    print("1. Ejecuta primero el análisis principal de estructura")
    print("2. Luego ejecuta este código CSS para análisis profundo")
    print("3. Compara los resultados para identificar el problema exacto")