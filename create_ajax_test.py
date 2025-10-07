"""
Script para generar HTML de prueba del JavaScript
"""

html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Prueba AJAX Conciliación</title>
</head>
<body>
    <h1>Prueba AJAX - Conciliación Bancaria</h1>
    
    <select id="id_bank_account">
        <option value="">Selecciona cuenta</option>
        <option value="1">PICHINCHA - 2201109377</option>
        <option value="2">INTERNACIONAL - 555544444</option>
        <option value="3">Banco Pacífico - 2100123456</option>
    </select>
    
    <select id="id_extracto">
        <option value="">Selecciona extracto</option>
    </select>
    
    <div id="debug"></div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const bankAccountSelect = document.getElementById('id_bank_account');
            const extractoSelect = document.getElementById('id_extracto');
            const debugDiv = document.getElementById('debug');
            
            function log(message) {
                console.log(message);
                debugDiv.innerHTML += '<p>' + message + '</p>';
            }
            
            if (bankAccountSelect) {
                bankAccountSelect.addEventListener('change', function() {
                    const bankAccountId = this.value;
                    log('Cuenta seleccionada: ' + bankAccountId);
                    
                    if (bankAccountId) {
                        const url = `ajax/?action=get_extractos&bank_account_id=${bankAccountId}`;
                        log('URL AJAX: ' + url);
                        
                        // Cargar extractos via AJAX
                        fetch(url)
                            .then(response => {
                                log('Response status: ' + response.status);
                                return response.json();
                            })
                            .then(data => {
                                log('Data received: ' + JSON.stringify(data));
                                
                                // Limpiar opciones existentes
                                extractoSelect.innerHTML = '<option value="">Selecciona un extracto bancario</option>';
                                
                                // Agregar nuevas opciones
                                if (data.extractos && data.extractos.length > 0) {
                                    data.extractos.forEach(extracto => {
                                        const option = document.createElement('option');
                                        option.value = extracto.id;
                                        option.textContent = extracto.text;
                                        extractoSelect.appendChild(option);
                                        log('Extracto agregado: ' + extracto.text);
                                    });
                                } else {
                                    log('No se encontraron extractos');
                                }
                            })
                            .catch(error => {
                                log('Error: ' + error.message);
                                console.error('Error cargando extractos:', error);
                            });
                    }
                });
            } else {
                log('Error: No se encontró el select de cuenta bancaria');
            }
        });
    </script>
</body>
</html>
"""

with open('test_ajax_debug.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ Archivo test_ajax_debug.html creado")
print("📝 Instrucciones:")
print("1. Abre http://localhost:8000/banking/conciliacion/")
print("2. Abre las Developer Tools (F12)")
print("3. Ve a Console")
print("4. Copia y pega este JavaScript:")
print("""
// Test AJAX directo
fetch('/banking/conciliacion/ajax/?action=get_extractos&bank_account_id=3')
    .then(response => {
        console.log('Status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
""")