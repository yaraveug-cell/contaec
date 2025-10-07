#!/usr/bin/env python
"""
Script completo para debugging del sistema de desglose de IVA
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.invoicing.models import Invoice, InvoiceLine
from apps.inventory.models import Product
from apps.companies.models import Company
from apps.invoicing.admin import InvoiceAdmin
from django.contrib.auth.models import User
from decimal import Decimal

def test_html_rendering():
    """Probar específicamente el renderizado HTML"""
    print("=== PROBANDO RENDERIZADO HTML ===")
    
    invoice = Invoice.objects.first()
    if not invoice:
        print("❌ No hay facturas para probar")
        return
    
    admin = InvoiceAdmin(Invoice, None)
    
    try:
        breakdown = invoice.get_tax_breakdown()
        print(f"📊 Breakdown: {breakdown}")
        
        # Generar HTML manualmente para comparar
        html_parts = []
        for rate, data in sorted(breakdown.items(), key=lambda x: float(x[0]), reverse=True):
            rate_float = float(rate)
            rate_str = f"IVA {rate_float}%" if rate_float > 0 else "Tarifa 0%"
            html_parts.append(
                f'<div class="tax-line">'
                f'<span class="tax-label">{rate_str}:</span> '
                f'<span class="tax-amount">${data["tax"]:,.2f}</span> '
                f'<small>(Base: ${data["base"]:,.2f})</small>'
                f'</div>'
            )
        
        raw_html = ''.join(html_parts)
        print(f"\n📝 HTML raw:")
        print(repr(raw_html))
        
        # Probar método del admin
        admin_result = admin.tax_breakdown_display(invoice)
        print(f"\n🎨 Admin result:")
        print(repr(admin_result))
        print(f"   Tipo: {type(admin_result)}")
        
        # Verificar si tiene allow_tags
        has_allow_tags = hasattr(admin.tax_breakdown_display, 'allow_tags')
        print(f"   allow_tags: {has_allow_tags}")
        if has_allow_tags:
            print(f"   allow_tags value: {admin.tax_breakdown_display.allow_tags}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def generate_console_debug_code():
    """Generar código JavaScript para pegar en la consola del navegador"""
    print("\n=== CÓDIGO PARA CONSOLA DEL NAVEGADOR ===")
    
    js_code = '''
// CÓDIGO DE DEBUGGING PARA LA CONSOLA DEL NAVEGADOR
console.clear();
console.log("🔧 INICIANDO DEBUG DEL DESGLOSE DE IVA");

// 1. Verificar elementos presentes
console.log("\\n1️⃣ VERIFICANDO ELEMENTOS:");
console.log("Formulario de factura:", document.querySelector('#invoiceline_set-group, .inline-group'));
console.log("Campo tax_amount:", document.querySelector('input[name="tax_amount"], #id_tax_amount'));
console.log("Filas de líneas:", document.querySelectorAll('#invoiceline_set-group .form-row:not(.add-row)').length);

// 2. Verificar valores actuales
console.log("\\n2️⃣ VALORES ACTUALES:");
const rows = document.querySelectorAll('#invoiceline_set-group .form-row:not(.add-row)');
rows.forEach((row, i) => {
    const qty = row.querySelector('input[name$="-quantity"]')?.value || 0;
    const price = row.querySelector('input[name$="-unit_price"]')?.value || 0;
    const iva = row.querySelector('input[name$="-iva_rate"]')?.value || 0;
    console.log(`  Línea ${i+1}: Qty=${qty}, Price=${price}, IVA=${iva}%`);
});

// 3. Simular cálculo manual
console.log("\\n3️⃣ CÁLCULO MANUAL:");
let totalTax = 0;
const breakdown = {};
rows.forEach((row, i) => {
    const qty = parseFloat(row.querySelector('input[name$="-quantity"]')?.value) || 0;
    const price = parseFloat(row.querySelector('input[name$="-unit_price"]')?.value) || 0;
    const iva = parseFloat(row.querySelector('input[name$="-iva_rate"]')?.value) || 0;
    
    if (qty > 0 && price > 0) {
        const net = qty * price;
        const tax = net * (iva / 100);
        totalTax += tax;
        
        if (!breakdown[iva]) breakdown[iva] = {base: 0, tax: 0};
        breakdown[iva].base += net;
        breakdown[iva].tax += tax;
        
        console.log(`  Línea ${i+1}: Net=$${net.toFixed(2)}, Tax=$${tax.toFixed(2)}`);
    }
});
console.log("Breakdown:", breakdown);
console.log(`Total IVA: $${totalTax.toFixed(2)}`);

// 4. Verificar si el script está cargado
console.log("\\n4️⃣ VERIFICANDO SCRIPTS:");
console.log("¿Script tax_breakdown_calculator cargado?", typeof window.taxBreakdownCalculator !== 'undefined');

// 5. Forzar actualización manual
console.log("\\n5️⃣ FORZANDO ACTUALIZACIÓN:");
const taxField = document.querySelector('input[name="tax_amount"], #id_tax_amount');
if (taxField) {
    taxField.value = totalTax.toFixed(2);
    console.log("✅ Campo tax_amount actualizado");
    
    // Crear desglose manual
    let container = document.getElementById('manual-tax-breakdown');
    if (!container) {
        container = document.createElement('div');
        container.id = 'manual-tax-breakdown';
        container.style.cssText = 'margin: 10px 0; padding: 10px; background: #ffe6e6; border: 2px solid #ff4444; border-radius: 4px;';
        container.innerHTML = '<strong style="color: #cc0000;">🔧 DEBUG: Desglose Manual</strong><div id="manual-breakdown-content"></div>';
        taxField.parentNode.insertBefore(container, taxField.nextSibling);
    }
    
    const content = document.getElementById('manual-breakdown-content');
    let html = '';
    Object.keys(breakdown).sort((a, b) => parseFloat(b) - parseFloat(a)).forEach(rate => {
        const data = breakdown[rate];
        html += `<div>IVA ${rate}%: $${data.tax.toFixed(2)} (Base: $${data.base.toFixed(2)})</div>`;
    });
    content.innerHTML = html;
    
    console.log("✅ Desglose manual creado");
} else {
    console.log("❌ No se encontró campo tax_amount");
}

console.log("\\n🎯 DEBUG COMPLETO. Ahora modifica algún valor y observa la consola.");
'''
    
    print("COPIA Y PEGA ESTE CÓDIGO EN LA CONSOLA DEL NAVEGADOR:")
    print("=" * 60)
    print(js_code)
    print("=" * 60)

if __name__ == "__main__":
    print("🚀 DEBUGGING COMPLETO DEL SISTEMA")
    
    # Probar renderizado HTML
    test_html_rendering()
    
    # Generar código para consola
    generate_console_debug_code()
    
    print("\n📋 INSTRUCCIONES:")
    print("1. Abre http://127.0.0.1:8000/admin/invoicing/invoice/")
    print("2. Edita una factura existente")
    print("3. Presiona F12 para abrir DevTools")
    print("4. Ve a la pestaña 'Console'")
    print("5. Copia y pega el código JavaScript de arriba")
    print("6. Presiona Enter para ejecutarlo")
    print("7. Modifica valores en las líneas y observa los logs")
    print("\n✅ LISTO PARA DEBUGGING")