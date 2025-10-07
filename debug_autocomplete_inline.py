#!/usr/bin/env python3
"""
Script para probar el autocompletado directamente en el admin
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.inventory.models import Product
from apps.invoicing.models import Invoice, InvoiceLine

def debug_autocomplete_issue():
    """
    Debuggear el problema del autocompletado
    """
    print("🔍 DEBUGGEANDO PROBLEMA DE AUTOCOMPLETADO")
    print("=" * 60)
    
    # 1. Verificar que los datos de productos estén disponibles
    print("\n📦 1. VERIFICANDO DATOS DE PRODUCTOS:")
    print("-" * 50)
    
    products = Product.objects.filter(is_active=True)[:3]
    
    if products.count() == 0:
        print("❌ No hay productos activos")
        return
    
    print(f"✅ Productos encontrados: {products.count()}")
    
    for product in products:
        print(f"   • ID: {product.id}")
        print(f"     Código: {product.code}")
        print(f"     Nombre: {product.name}")
        print(f"     Precio: ${product.sale_price}")
        print(f"     IVA: {product.iva_rate}%")
        print()
    
    # 2. Verificar estructura de nombres de campos en inline
    print("📝 2. ESTRUCTURA DE CAMPOS EN INLINE:")
    print("-" * 50)
    
    # Los nombres de campos en inline siguen el patrón:
    # invoiceline_set-0-product
    # invoiceline_set-0-description  
    # invoiceline_set-0-unit_price
    # invoiceline_set-0-iva_rate
    
    print("Nombres de campo esperados en el inline:")
    print("   • Producto: invoiceline_set-0-product")
    print("   • Descripción: invoiceline_set-0-description")
    print("   • Precio unitario: invoiceline_set-0-unit_price")
    print("   • Tasa IVA: invoiceline_set-0-iva_rate")
    
    # 3. Verificar el JavaScript actualizado
    print("\n🔧 3. VERIFICANDO JAVASCRIPT ACTUALIZADO:")
    print("-" * 50)
    
    js_file = 'static/admin/js/invoice_line_autocomplete.js'
    if os.path.exists(js_file):
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar características clave
        checks = [
            ('setupAutocompleteTriggers', 'Función para widgets de autocompletado'),
            ('admin-autocomplete', 'Detección de widgets Django'),
            ('autocompletechange', 'Evento de autocompletado'),
            ('console.log', 'Logging para debug'),
        ]
        
        for check, description in checks:
            if check in content:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ {description}")
    else:
        print(f"   ❌ Archivo JavaScript no encontrado: {js_file}")
    
    # 4. Crear JavaScript actualizado específico para inline
    print("\n🛠️ 4. CREANDO JAVASCRIPT ESPECÍFICO PARA INLINE:")
    print("-" * 50)
    
    updated_js = """
/**
 * Autocompletado específico para InvoiceLineInline con widget Django autocomplete
 */
(function() {
    'use strict';
    
    let productsData = {};
    
    // Cargar datos de productos del contexto Django
    function loadProductsData() {
        const dataScript = document.getElementById('products-data');
        if (dataScript) {
            try {
                productsData = JSON.parse(dataScript.textContent);
                console.log('📦 Productos cargados:', Object.keys(productsData).length);
            } catch (e) {
                console.error('❌ Error cargando productos:', e);
            }
        } else if (typeof window.productsData !== 'undefined') {
            productsData = window.productsData;
            console.log('📦 Productos desde window:', Object.keys(productsData).length);
        }
    }
    
    // Manejar selección de producto en widget de autocompletado
    function handleProductSelection(productField) {
        const productId = productField.value;
        
        console.log('🔍 Producto seleccionado:', productId);
        
        if (!productId || !productsData[productId]) {
            console.log('⚠️ Producto no encontrado:', productId);
            return;
        }
        
        const productData = productsData[productId];
        console.log('📦 Datos del producto:', productData);
        
        // Encontrar la fila contenedora
        const row = productField.closest('tr') || productField.closest('.inline-related');
        if (!row) {
            console.log('❌ Fila no encontrada');
            return;
        }
        
        // Buscar campos por nombre exacto del inline
        const prefix = productField.name.replace('-product', '');
        
        const descriptionField = document.querySelector(`[name="${prefix}-description"]`);
        const unitPriceField = document.querySelector(`[name="${prefix}-unit_price"]`); 
        const ivaRateField = document.querySelector(`[name="${prefix}-iva_rate"]`);
        
        console.log('🔍 Campos encontrados:', {
            prefix: prefix,
            description: !!descriptionField,
            unitPrice: !!unitPriceField,
            ivaRate: !!ivaRateField
        });
        
        // Completar campos automáticamente
        if (descriptionField && productData.description) {
            descriptionField.value = productData.description;
            console.log('✅ Descripción actualizada');
        }
        
        if (unitPriceField && productData.sale_price) {
            unitPriceField.value = productData.sale_price;
            unitPriceField.dispatchEvent(new Event('input', { bubbles: true }));
            console.log('✅ Precio actualizado');
        }
        
        if (ivaRateField && productData.iva_rate) {
            ivaRateField.value = productData.iva_rate;
            ivaRateField.dispatchEvent(new Event('input', { bubbles: true }));
            console.log('✅ IVA actualizado');
        }
    }
    
    // Configurar listeners para widgets de autocompletado
    function setupAutocompletedWidgets() {
        // Buscar widgets de autocompletado de producto existentes
        const productWidgets = document.querySelectorAll('input[name*="product"].admin-autocomplete');
        
        console.log(`🔧 Configurando ${productWidgets.length} widgets de producto`);
        
        productWidgets.forEach(function(widget) {
            // Escuchar cambios en el widget
            widget.addEventListener('change', function() {
                setTimeout(() => handleProductSelection(widget), 100);
            });
            
            widget.addEventListener('blur', function() {
                setTimeout(() => handleProductSelection(widget), 150);
            });
            
            console.log('✅ Widget configurado:', widget.name);
        });
    }
    
    // Observer para detectar nuevos widgets
    function setupMutationObserver() {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) {
                        const newWidgets = node.querySelectorAll ? 
                            node.querySelectorAll('input[name*="product"].admin-autocomplete') : [];
                        
                        newWidgets.forEach(function(widget) {
                            widget.addEventListener('change', function() {
                                setTimeout(() => handleProductSelection(widget), 100);
                            });
                        });
                    }
                });
            });
        });
        
        observer.observe(document.body, { childList: true, subtree: true });
    }
    
    // Inicialización
    function init() {
        console.log('🚀 Inicializando autocompletado específico para inline');
        
        loadProductsData();
        
        // Delay para asegurar que los widgets estén completamente cargados
        setTimeout(function() {
            setupAutocompletedWidgets();
            setupMutationObserver();
        }, 1000);
    }
    
    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();
"""
    
    # Guardar JavaScript actualizado
    updated_js_file = 'static/admin/js/invoice_line_autocomplete_fixed.js'
    with open(updated_js_file, 'w', encoding='utf-8') as f:
        f.write(updated_js)
    
    print(f"✅ JavaScript actualizado guardado en: {updated_js_file}")
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("-" * 50)
    print("1. Reemplazar el JavaScript actual con la versión corregida")
    print("2. Actualizar el Media del InvoiceAdmin para usar el nuevo archivo")
    print("3. Probar en el admin de Django")
    
    return updated_js_file

if __name__ == "__main__":
    debug_autocomplete_issue()