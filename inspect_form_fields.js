// INSPECTOR DE CAMPOS DEL FORMULARIO - Pega esto en la consola
console.clear();
console.log("🔍 INSPECCIONANDO ESTRUCTURA DEL FORMULARIO");

// 1. Buscar todos los campos de input
console.log("\n📋 TODOS LOS CAMPOS INPUT:");
const allInputs = document.querySelectorAll('input[type="number"], input[type="text"]');
allInputs.forEach((input, i) => {
    if (input.name && (input.name.includes('total') || input.name.includes('tax') || input.name.includes('subtotal'))) {
        console.log(`  ${i+1}. ${input.name} = "${input.value}" (id: ${input.id})`);
    }
});

// 2. Buscar por patrones comunes
console.log("\n🎯 BÚSQUEDA POR PATRONES:");
const patterns = ['total', 'tax', 'subtotal', 'amount', 'impuesto'];
patterns.forEach(pattern => {
    const fields = document.querySelectorAll(`input[name*="${pattern}"], input[id*="${pattern}"]`);
    if (fields.length > 0) {
        console.log(`  ${pattern.toUpperCase()}:`);
        fields.forEach(field => {
            console.log(`    - ${field.name || field.id} = "${field.value}"`);
        });
    }
});

// 3. Inspeccionar estructura de la factura
console.log("\n📄 ESTRUCTURA DE LA FACTURA:");
const invoiceForm = document.querySelector('form');
if (invoiceForm) {
    const formRows = invoiceForm.querySelectorAll('.form-row');
    formRows.forEach((row, i) => {
        const label = row.querySelector('label')?.textContent?.trim();
        const input = row.querySelector('input');
        if (label && input && (label.includes('Total') || label.includes('IVA') || label.includes('Subtotal') || label.includes('Impuesto'))) {
            console.log(`  Fila ${i+1}: "${label}" → ${input.name} = "${input.value}"`);
        }
    });
}

// 4. Buscar contenedor donde mostrar el desglose
console.log("\n🎨 POSIBLES CONTENEDORES PARA DESGLOSE:");
const containers = document.querySelectorAll('.form-row, .field-row, .fieldset');
containers.forEach((container, i) => {
    const text = container.textContent?.trim();
    if (text && (text.includes('Total') || text.includes('IVA') || text.includes('Impuesto'))) {
        console.log(`  ${i+1}. ${container.className} → "${text.substring(0, 50)}..."`);
    }
});

// 5. Buscar fieldset de totales
console.log("\n📊 FIELDSETS DISPONIBLES:");
const fieldsets = document.querySelectorAll('fieldset');
fieldsets.forEach((fieldset, i) => {
    const legend = fieldset.querySelector('legend')?.textContent?.trim();
    if (legend) {
        console.log(`  ${i+1}. "${legend}"`);
        const inputs = fieldset.querySelectorAll('input');
        inputs.forEach(input => {
            if (input.name) {
                console.log(`    - ${input.name} = "${input.value}"`);
            }
        });
    }
});

console.log("\n✅ INSPECCIÓN COMPLETA - Busca los nombres reales de los campos arriba");