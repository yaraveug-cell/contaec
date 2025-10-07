#!/usr/bin/env python3
"""
Script simple para verificar el estado de la ventana modal del resumen de factura
"""

import os

def test_modal_javascript():
    """Verifica que el JavaScript de la modal esté correctamente configurado"""
    
    js_file_path = 'static/admin/js/tax_breakdown_calculator.js'
    
    if not os.path.exists(js_file_path):
        print("❌ Archivo JavaScript no encontrado")
        return False
    
    with open(js_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar que el código tiene la configuración correcta
    checks = [
        ("Estado inicial desplegado", "let isMinimized = false;" in content),
        ("Display block inicial", "contentContainer.style.display = 'block';" in content),
        ("Botón minimizar inicial", "minimizeBtn.innerHTML = '▲';" in content),
        ("Título inicial correcto", "titleText.textContent = 'Resumen de Factura';" in content),
        ("Tooltip minimizar inicial", "minimizeBtn.title = 'Minimizar';" in content),
    ]
    
    print("🔍 Verificando configuración del JavaScript:")
    print("-" * 50)
    
    all_passed = True
    for check_name, condition in checks:
        if condition:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
            all_passed = False
    
    # Buscar posibles problemas
    print("\n🔍 Análisis adicional:")
    print("-" * 30)
    
    if "isMinimized = true" in content:
        print("⚠️ PROBLEMA: Encontrado 'isMinimized = true' en el código")
        
    if "'Resumen (minimizado)'" in content:
        print("⚠️ PROBLEMA: Texto 'minimizado' encontrado en el código")
    
    # Mostrar líneas relevantes
    lines = content.split('\n')
    print("\n📋 Líneas relevantes del código:")
    print("-" * 40)
    
    relevant_lines = []
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        if any(keyword in line_stripped for keyword in [
            'isMinimized = ', 
            'contentContainer.style.display = ',
            'minimizeBtn.innerHTML = ',
            "titleText.textContent = 'Resumen",
            "minimizeBtn.title = '"
        ]):
            relevant_lines.append((i, line_stripped))
    
    for line_num, line_content in relevant_lines:
        print(f"Línea {line_num:3}: {line_content}")
    
    # Verificar contexto alrededor de la configuración inicial
    print("\n📋 Contexto de configuración inicial:")
    print("-" * 45)
    
    for i, line in enumerate(lines):
        if "Funcionalidad de botones" in line:
            start = max(0, i-2)
            end = min(len(lines), i+15)
            for j in range(start, end):
                marker = ">>> " if j == i else "    "
                print(f"{marker}Línea {j+1:3}: {lines[j].strip()}")
            break
    
    return all_passed

def main():
    print("🧪 Test del Estado de la Ventana Modal del Resumen")
    print("=" * 60)
    
    # Test: Verificar JavaScript
    js_ok = test_modal_javascript()
    
    # Resumen
    print("\n📊 RESUMEN")
    print("=" * 30)
    
    if js_ok:
        print("✅ JavaScript configurado correctamente")
        print("\n🔧 SOLUCIÓN AL PROBLEMA DE CACHÉ:")
        print("1. Abre el navegador en modo incógnito")
        print("2. O presiona Ctrl+Shift+R para forzar recarga")
        print("3. O ve a DevTools (F12) > Network > marca 'Disable cache'")
    else:
        print("❌ Problemas en la configuración JavaScript")
        print("🔧 Se requiere revisar el código")

if __name__ == "__main__":
    main()