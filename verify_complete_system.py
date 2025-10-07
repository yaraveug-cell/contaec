#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.invoicing.models import Invoice, InvoiceLine
from apps.invoicing.admin import InvoiceAdmin
from django.utils.html import format_html

def verify_system():
    print("=== VERIFICACIÓN COMPLETA DEL SISTEMA ===\n")
    
    # 1. Verificar que hay facturas
    invoice_count = Invoice.objects.count()
    print(f"📋 Total de facturas: {invoice_count}")
    
    if invoice_count == 0:
        print("❌ No hay facturas para probar")
        return
    
    # 2. Probar con la primera factura
    invoice = Invoice.objects.first()
    print(f"\n🧪 PROBANDO CON FACTURA #{invoice.number}")
    print(f"   Empresa: {invoice.company.trade_name}")
    print(f"   Líneas: {invoice.lines.count()}")
    
    # 3. Verificar líneas individuales
    lines = invoice.lines.all()
    print(f"\n📦 DETALLE DE LÍNEAS:")
    
    for i, line in enumerate(lines, 1):
        subtotal = line.quantity * line.unit_price
        discount_amount = subtotal * (line.discount / 100)
        net = subtotal - discount_amount
        tax = net * (line.iva_rate / 100)
        
        print(f"   Línea {i}: {line.product.name if line.product else 'Sin producto'}")
        print(f"      Cantidad: {line.quantity} x ${line.unit_price}")
        print(f"      Descuento: {line.discount}%")
        print(f"      IVA Rate: {line.iva_rate}%")
        print(f"      Neto: ${net:.2f}")
        print(f"      IVA: ${tax:.2f}")
        print(f"      Total línea: ${line.line_total}")
    
    # 4. Probar método get_tax_breakdown
    print(f"\n🧮 PROBANDO get_tax_breakdown():")
    try:
        breakdown = invoice.get_tax_breakdown()
        print(f"   ✅ Método ejecutado correctamente")
        print(f"   📊 Resultado: {breakdown}")
        
        if breakdown:
            total_calculated_tax = 0
            for rate, data in breakdown.items():
                print(f"      IVA {rate}%: Base=${data['base']:.2f}, Impuesto=${data['tax']:.2f}")
                total_calculated_tax += data['tax']
            print(f"   💰 Total IVA calculado: ${total_calculated_tax:.2f}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Probar método del admin
    print(f"\n🎨 PROBANDO tax_breakdown_display():")
    try:
        admin = InvoiceAdmin(Invoice, None)
        html_result = admin.tax_breakdown_display(invoice)
        print(f"   ✅ Método ejecutado correctamente")
        print(f"   📄 Tipo de resultado: {type(html_result)}")
        print(f"   📝 Longitud HTML: {len(str(html_result))} caracteres")
        
        # Verificar si es SafeString (resultado de format_html)
        from django.utils.safestring import SafeString
        if isinstance(html_result, SafeString):
            print(f"   🔒 Es SafeString (formato correcto)")
        else:
            print(f"   ⚠️  No es SafeString: {type(html_result)}")
        
        html_str = str(html_result)
        if "Error" in html_str:
            print(f"   ❌ Contiene error: {html_str}")
        else:
            print(f"   ✅ HTML generado sin errores")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # 6. Verificar archivos JavaScript
    print(f"\n📁 VERIFICANDO ARCHIVOS ESTÁTICOS:")
    
    js_files = [
        'static/admin/js/tax_breakdown_calculator.js',
        'static/admin/js/invoice_line_calculator.js',
        'static/admin/js/description_autocomplete.js',
        'static/admin/js/invoice_line_autocomplete.js'
    ]
    
    for js_file in js_files:
        if os.path.exists(js_file):
            size = os.path.getsize(js_file)
            print(f"   ✅ {js_file} ({size} bytes)")
        else:
            print(f"   ❌ {js_file} NO ENCONTRADO")
    
    # 7. Verificar configuración del admin
    print(f"\n⚙️  VERIFICANDO CONFIGURACIÓN:")
    print(f"   Media JS configurados en InvoiceLineInline:")
    
    from apps.invoicing.admin import InvoiceLineInline
    inline = InvoiceLineInline(Invoice, None)
    
    if hasattr(inline, 'Media'):
        if hasattr(inline.Media, 'js'):
            for js in inline.Media.js:
                print(f"      - {js}")
        else:
            print(f"   ❌ No hay archivos JS configurados")
    else:
        print(f"   ❌ No hay clase Media configurada")
    
    print(f"\n✅ VERIFICACIÓN COMPLETA")

if __name__ == "__main__":
    verify_system()