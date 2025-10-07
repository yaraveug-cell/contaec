// Función de prueba para el stock updater
function testStockUpdater() {
    console.log('🧪 INICIANDO PRUEBA DE STOCK UPDATER');
    
    // Buscar el primer select de producto
    const firstProductSelect = document.querySelector('select[name="lines-0-product"]');
    if (!firstProductSelect) {
        console.log('❌ No se encontró el primer select de producto');
        return;
    }
    
    console.log('✅ Select encontrado:', firstProductSelect.name);
    console.log('   - Clase:', firstProductSelect.className);
    console.log('   - Valor actual:', firstProductSelect.value);
    
    // Verificar si hay datos de productos
    if (typeof window.productsData !== 'undefined') {
        const productIds = Object.keys(window.productsData);
        console.log('📦 Productos disponibles:', productIds.length);
        
        if (productIds.length > 0) {
            const firstProductId = productIds[0];
            const productData = window.productsData[firstProductId];
            console.log('🔍 Primer producto:', productData);
            
            // Simular selección
            console.log('🎯 Simulando selección del producto:', firstProductId);
            
            // Crear opción si no existe
            let option = firstProductSelect.querySelector(`option[value="${firstProductId}"]`);
            if (!option) {
                option = document.createElement('option');
                option.value = firstProductId;
                option.textContent = productData.name || `Producto ${firstProductId}`;
                option.selected = true;
                firstProductSelect.appendChild(option);
            }
            
            // Establecer el valor
            firstProductSelect.value = firstProductId;
            
            // Disparar eventos
            firstProductSelect.dispatchEvent(new Event('change', { bubbles: true }));
            
            // Verificar campo de stock después
            setTimeout(() => {
                const stockField = document.querySelector('input[name="lines-0-stock"]');
                if (stockField) {
                    console.log('📊 Campo stock encontrado:', stockField.name);
                    console.log('   - Valor actual:', stockField.value);
                    console.log('   - Stock esperado:', productData.current_stock);
                    
                    if (stockField.value === String(productData.current_stock)) {
                        console.log('✅ PRUEBA EXITOSA: Stock actualizado correctamente');
                    } else {
                        console.log('❌ PRUEBA FALLIDA: Stock no se actualizó');
                    }
                } else {
                    console.log('❌ Campo stock no encontrado');
                }
            }, 1000);
        }
    } else {
        console.log('❌ No hay datos de productos disponibles');
    }
}

// Hacer la función disponible globalmente
window.testStockUpdater = testStockUpdater;

console.log('🧪 Función de prueba cargada. Ejecuta: testStockUpdater()');