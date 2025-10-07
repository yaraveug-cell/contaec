/**
 * JavaScript principal para el admin de facturas
 * Maneja datos de productos y los hace disponibles para autocompletado
 */
(function() {
    'use strict';
    
    // Invoice admin inicializado
    
    // Función para procesar y hacer disponibles los datos de productos
    function setupProductsData() {
        // Buscar datos en diferentes lugares posibles
        let productsData = null;
        
        // Opción 1: Datos ya en window.productsData
        if (typeof window.productsData !== 'undefined') {
            productsData = window.productsData;
        }
        
        // Opción 2: Datos en elemento script
        const dataScript = document.getElementById('products-data');
        if (dataScript && !productsData) {
            try {
                productsData = JSON.parse(dataScript.textContent);
            } catch (e) {
                console.error('❌ Error parseando datos del script:', e);
            }
        }
        
        // Opción 3: Buscar en variables globales del template
        if (!productsData && typeof window.products_data_json !== 'undefined') {
            try {
                productsData = JSON.parse(window.products_data_json);
            } catch (e) {
                console.error('❌ Error parseando products_data_json:', e);
            }
        }
        
        // Si encontramos datos, asegurar que estén disponibles globalmente
        if (productsData) {
            // Hacer disponible en window para otros scripts
            window.productsData = productsData;
            
            // También crear elemento en DOM si no existe
            if (!document.getElementById('products-data')) {
                const dataElement = document.createElement('script');
                dataElement.id = 'products-data';
                dataElement.type = 'application/json';
                dataElement.textContent = JSON.stringify(productsData);
                document.head.appendChild(dataElement);
                console.log('✅ Elemento products-data creado en DOM');
            }
            
            console.log('🎉 Datos de productos configurados exitosamente');
            return true;
        } else {
            console.warn('⚠️ No se encontraron datos de productos');
            return false;
        }
    }
    
    // Función de inicialización
    function init() {
        console.log('🔧 Inicializando invoice_admin.js...');
        
        // Intentar configurar datos inmediatamente
        if (!setupProductsData()) {
            // Si no hay datos, intentar después de un delay
            setTimeout(function() {
                console.log('🔄 Reintentando configuración de datos...');
                setupProductsData();
            }, 500);
        }
    }
    
    // Ejecutar inicialización
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // También exponer función para uso manual si es necesario
    window.setupProductsData = setupProductsData;
    
})();