"""
🔍 DEBUG: Inspeccionar widgets de autocompletado Django en el DOM
"""
import json

def generate_dom_inspector():
    """Genera JavaScript para inspeccionar los widgets de autocompletado"""
    
    js_code = """
    // 🔍 DIAGNÓSTICO: Inspeccionar widgets de autocompletado Django
    console.log('🚀 DIAGNÓSTICO: Iniciando inspección de widgets...');
    
    // 1. Buscar todos los inputs relacionados con productos
    const allInputs = document.querySelectorAll('input[name*="product"]');
    console.log('📋 Todos los inputs con "product":', allInputs.length);
    allInputs.forEach((input, index) => {
        console.log(`  Input ${index + 1}:`, {
            name: input.name,
            id: input.id,
            className: input.className,
            type: input.type,
            tagName: input.tagName
        });
    });
    
    // 2. Buscar widgets con clases de autocompletado
    const autoCompleteInputs = document.querySelectorAll('.admin-autocomplete, .select2-hidden-accessible, input[data-autocomplete-light-url]');
    console.log('🎯 Widgets de autocompletado encontrados:', autoCompleteInputs.length);
    autoCompleteInputs.forEach((input, index) => {
        console.log(`  Widget ${index + 1}:`, {
            name: input.name,
            id: input.id,
            className: input.className,
            'data-autocomplete-light-url': input.getAttribute('data-autocomplete-light-url'),
            'data-select2-id': input.getAttribute('data-select2-id')
        });
    });
    
    // 3. Buscar contenedores de líneas de factura
    const invoiceLines = document.querySelectorAll('#lines-group .form-row');
    console.log('📄 Líneas de factura encontradas:', invoiceLines.length);
    invoiceLines.forEach((line, index) => {
        console.log(`  Línea ${index + 1}:`);
        const productInputs = line.querySelectorAll('input[name*="product"]');
        console.log(`    Inputs de producto:`, productInputs.length);
        productInputs.forEach((input, i) => {
            console.log(`      Input ${i + 1}:`, {
                name: input.name,
                id: input.id,
                className: input.className
            });
        });
    });
    
    // 4. Buscar selects de productos (por si Django usa selects en lugar de inputs)
    const productSelects = document.querySelectorAll('select[name*="product"]');
    console.log('📋 Selects de productos encontrados:', productSelects.length);
    productSelects.forEach((select, index) => {
        console.log(`  Select ${index + 1}:`, {
            name: select.name,
            id: select.id,
            className: select.className
        });
    });
    
    // 5. Inspeccionar estructura completa del formulario
    const linesGroup = document.querySelector('#lines-group');
    if (linesGroup) {
        console.log('📊 Estructura del formulario de líneas:');
        console.log('  Contenedor principal:', linesGroup.className);
        console.log('  Atributos data:', Object.keys(linesGroup.dataset));
        
        // Buscar todos los campos en la primera línea
        const firstLine = linesGroup.querySelector('.form-row');
        if (firstLine) {
            console.log('  Primera línea encontrada:');
            const allFields = firstLine.querySelectorAll('input, select, textarea');
            console.log(`  Total de campos: ${allFields.length}`);
            allFields.forEach((field, index) => {
                console.log(`    Campo ${index + 1}:`, {
                    name: field.name,
                    id: field.id,
                    type: field.type || field.tagName,
                    className: field.className
                });
            });
        }
    }
    
    console.log('✅ DIAGNÓSTICO: Inspección completada');
    """
    
    return js_code

if __name__ == "__main__":
    js_code = generate_dom_inspector()
    print("📋 Código JavaScript generado para diagnóstico:")
    print("\n" + "="*60)
    print(js_code)
    print("="*60)
    print("\n🔧 Para usar:")
    print("1. Abrir página del admin de factura")
    print("2. Abrir consola del navegador (F12)")
    print("3. Copiar y pegar el código JavaScript")
    print("4. Presionar Enter para ejecutar")