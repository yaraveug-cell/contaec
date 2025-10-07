/* JavaScript para asegurar que el campo descripción sea input de una línea */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Iniciando optimización de campos de descripción...');
    
    function optimizeDescriptionFields() {
        // Buscar todos los textareas de descripción en líneas de asiento
        const descriptionTextareas = document.querySelectorAll('textarea[name*="description"]');
        
        descriptionTextareas.forEach(function(textarea) {
            console.log('📝 Convirtiendo textarea a input:', textarea.name);
            
            // Crear nuevo input
            const input = document.createElement('input');
            input.type = 'text';
            input.name = textarea.name;
            input.id = textarea.id;
            input.value = textarea.value;
            input.placeholder = 'Descripción de la línea del asiento...';
            input.className = textarea.className + ' description-single-line';
            input.style.width = '600px';
            input.style.height = '28px';
            input.maxLength = 200;
            
            // Copiar atributos necesarios
            if (textarea.required) input.required = true;
            if (textarea.disabled) input.disabled = true;
            
            // Reemplazar textarea con input
            textarea.parentNode.replaceChild(input, textarea);
            
            console.log('✅ Descripción convertida exitosamente');
        });
    }
    
    // Ejecutar al cargar la página
    optimizeDescriptionFields();
    
    // También ejecutar cuando se agregan nuevas líneas (formset dinámico)
    document.addEventListener('formset:added', function(event) {
        console.log('📋 Nueva línea agregada, optimizando...');
        setTimeout(optimizeDescriptionFields, 100);
    });
    
    console.log('✅ Optimización de descripción completada');
});