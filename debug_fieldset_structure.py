#!/usr/bin/env python3
"""
Script para analizar la estructura HTML del admin Django
y mejorar la detección del fieldset
"""

print("🔍 ANÁLISIS DE ESTRUCTURA HTML DEL ADMIN DJANGO")
print("=" * 55)

print("""
🎯 ESTRUCTURA ESPERADA EN DJANGO ADMIN:

1. FIELDSET TRADICIONAL:
   <fieldset class="module aligned">
       <h2>Información Básica</h2>
       <div class="form-row">...</div>
   </fieldset>

2. MODULE SIN FIELDSET:
   <div class="module">
       <h2>Información Básica</h2>
       <div class="form-row">...</div>
   </div>

3. INLINE GROUP:
   <div class="inline-group">
       <div class="tabular inline-related">...</div>
   </div>

4. FORM-ROW DIRECTO:
   <div class="form-row field-company">...</div>
   <div class="form-row field-customer">...</div>
""")

print("🔧 SELECTORES A PROBAR:")
print("-" * 25)
print("1. fieldset.module.aligned")
print("2. .module:has(h2)")
print("3. .form-row.field-company (parent)")
print("4. .field-payment_form (parent)")
print("5. [class*='field-']:first-child (parent)")

print("\n🧪 JAVASCRIPT DE DEBUGGING MEJORADO:")
print("-" * 42)

js_debug = '''
// Debugging en consola del navegador:
console.log('=== DEBUGGING FIELDSET DETECTION ===');

// 1. Buscar por diferentes selectores
const selectors = [
    'fieldset.module.aligned',
    '.module',
    '.form-row',
    '.field-company',
    '.field-customer', 
    '.field-payment_form'
];

selectors.forEach(selector => {
    const elements = document.querySelectorAll(selector);
    console.log(`${selector}: ${elements.length} elementos`);
    if (elements.length > 0) {
        console.log('  Primer elemento:', elements[0]);
    }
});

// 2. Buscar headers
const headers = document.querySelectorAll('h1, h2, h3, legend');
headers.forEach(h => {
    if (h.textContent.toLowerCase().includes('información') || 
        h.textContent.toLowerCase().includes('basic')) {
        console.log('Header encontrado:', h.textContent, h);
    }
});

// 3. Buscar contenedor principal del form
const forms = document.querySelectorAll('form');
console.log('Forms encontrados:', forms.length);
if (forms.length > 0) {
    console.log('Primer form:', forms[0]);
    console.log('Children del form:', forms[0].children);
}
'''

print(js_debug)

print("\n📋 PLAN DE MEJORA:")
print("-" * 20)
print("1. ✅ Usar múltiples estrategias de detección")
print("2. ✅ Buscar por estructura de campos conocidos") 
print("3. ✅ Detectar contenedor padre común")
print("4. ✅ Fallback robusto a elementos conocidos")
print("5. ✅ Logging detallado para debugging")

print(f"\n🚀 ACCIÓN REQUERIDA:")
print("=" * 20)
print("Probar este JavaScript en la consola del navegador")
print("para entender la estructura real del HTML")