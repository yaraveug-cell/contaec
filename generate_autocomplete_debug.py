#!/usr/bin/env python3
"""
Script para crear página de prueba del autocompletado de campos
Autor: Sistema ContaEC
Fecha: 2 de octubre, 2025
Objetivo: Generar HTML de debug para probar autocompletado
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.inventory.models import Product
import json

def generate_debug_html():
    """
    Generar archivo HTML para probar el autocompletado
    """
    print("🔧 GENERANDO ARCHIVO DE DEBUG PARA AUTOCOMPLETADO")
    print("=" * 60)
    
    # Obtener productos para el JavaScript
    products = Product.objects.filter(is_active=True)[:5]
    
    products_data = {}
    for product in products:
        products_data[str(product.id)] = {
            'id': product.id,
            'code': getattr(product, 'code', '') or f'P{product.id:06d}',
            'name': str(product.name),
            'description': str(product.description or product.name),
            'sale_price': float(product.sale_price or 0),
            'iva_rate': float(getattr(product, 'iva_rate', 15.00)),
        }
    
    products_json = json.dumps(products_data, ensure_ascii=False, indent=2)
    
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Debug - Autocompletado de Productos</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .test-section {{ margin-bottom: 30px; padding: 20px; border: 1px solid #ccc; }}
        .form-row {{ margin-bottom: 15px; }}
        label {{ display: block; font-weight: bold; margin-bottom: 5px; }}
        input, select, textarea {{ width: 300px; padding: 8px; border: 1px solid #ccc; }}
        .log {{ background: #f0f0f0; padding: 10px; height: 200px; overflow-y: scroll; font-family: monospace; font-size: 12px; }}
        .btn {{ padding: 10px 20px; background: #007cba; color: white; border: none; cursor: pointer; }}
        .btn:hover {{ background: #005a87; }}
    </style>
</head>
<body>
    <h1>🧪 Debug - Autocompletado de Productos en Facturas</h1>
    
    <div class="test-section">
        <h2>📋 Datos de Productos Disponibles</h2>
        <p>Productos cargados: <strong>{len(products_data)}</strong></p>
        <ul>
        {chr(10).join([f'<li><strong>{data["code"]}</strong> - {data["name"]} (${data["sale_price"]}, IVA: {data["iva_rate"]}%)</li>' for data in products_data.values()])}
        </ul>
    </div>
    
    <div class="test-section">
        <h2>🔧 Formulario de Prueba - Línea de Factura</h2>
        <form>
            <div class="form-row">
                <label for="product">Producto (Select tradicional):</label>
                <select id="product" name="invoiceline-0-product">
                    <option value="">--- Seleccionar producto ---</option>
                    {chr(10).join([f'<option value="{pid}">{data["code"]} - {data["name"]}</option>' for pid, data in products_data.items()])}
                </select>
            </div>
            
            <div class="form-row">
                <label for="description">Descripción:</label>
                <textarea id="description" name="invoiceline-0-description" rows="3"></textarea>
            </div>
            
            <div class="form-row">
                <label for="unit_price">Precio Unitario:</label>
                <input type="number" id="unit_price" name="invoiceline-0-unit_price" step="0.01">
            </div>
            
            <div class="form-row">
                <label for="iva_rate">Tasa IVA (%):</label>
                <input type="number" id="iva_rate" name="invoiceline-0-iva_rate" step="0.01">
            </div>
            
            <div class="form-row">
                <label for="quantity">Cantidad:</label>
                <input type="number" id="quantity" name="invoiceline-0-quantity" step="0.01" value="1">
            </div>
        </form>
    </div>
    
    <div class="test-section">
        <h2>📝 Log de Eventos</h2>
        <div id="log" class="log"></div>
        <button class="btn" onclick="clearLog()">Limpiar Log</button>
    </div>
    
    <script>
        // Datos de productos (simulando window.productsData)
        window.productsData = {products_json};
        
        // Log de eventos
        function log(message) {{
            const logDiv = document.getElementById('log');
            const timestamp = new Date().toLocaleTimeString();
            logDiv.innerHTML += '[' + timestamp + '] ' + message + '\\n';
            logDiv.scrollTop = logDiv.scrollHeight;
        }}
        
        function clearLog() {{
            document.getElementById('log').innerHTML = '';
        }}
        
        // Override console.log para mostrar en el log
        const originalConsoleLog = console.log;
        console.log = function(...args) {{
            originalConsoleLog.apply(console, args);
            log(args.join(' '));
        }};
        
        log('🚀 Página de debug cargada');
        log('📦 Productos disponibles: ' + Object.keys(window.productsData).length);
    </script>
    
    <!-- Cargar el JavaScript de autocompletado -->
    <script src="/static/admin/js/invoice_line_autocomplete.js"></script>
    
    <script>
        // Verificar que el script se cargó
        document.addEventListener('DOMContentLoaded', function() {{
            log('✅ DOM cargado completamente');
            log('🔍 Verificando configuración de autocompletado...');
            
            // Simular selección de producto después de 2 segundos
            setTimeout(function() {{
                log('🧪 Iniciando prueba automática...');
                const productSelect = document.getElementById('product');
                if (productSelect.options.length > 1) {{
                    productSelect.value = productSelect.options[1].value;
                    log('📋 Producto seleccionado: ' + productSelect.options[1].text);
                    
                    // Disparar evento change
                    const changeEvent = new Event('change', {{ bubbles: true }});
                    productSelect.dispatchEvent(changeEvent);
                    log('🔄 Evento change disparado');
                }}
            }}, 3000);
        }});
    </script>
</body>
</html>"""
    
    # Guardar archivo
    debug_file_path = os.path.join(os.getcwd(), 'debug_autocomplete.html')
    with open(debug_file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Archivo de debug generado: {debug_file_path}")
    print(f"🌐 Para probar, abrir en navegador: file://{debug_file_path}")
    print(f"📋 Productos incluidos: {len(products_data)}")
    
    return debug_file_path

if __name__ == "__main__":
    debug_file = generate_debug_html()
    print(f"\n🔧 INSTRUCCIONES DE USO:")
    print(f"1. Abrir el archivo en un navegador web")
    print(f"2. Observar el log de eventos")  
    print(f"3. Seleccionar un producto del dropdown")
    print(f"4. Verificar que se completen automáticamente:")
    print(f"   - Descripción")
    print(f"   - Precio unitario") 
    print(f"   - Tasa de IVA")
    print(f"5. Revisar mensajes en el log para debugging")