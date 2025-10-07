#!/usr/bin/env python
"""
Debug específico: Por qué no aparece el botón de impresión
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import JournalEntry
from django.template.loader import get_template
from django.template import Context, Template
from django.http import HttpRequest
from django.contrib.auth import get_user_model

User = get_user_model()

def debug_template_rendering():
    """Verificar que el template se renderiza correctamente"""
    print("🔍 DEBUGGING ESPECÍFICO: RENDERIZADO DE TEMPLATE")
    print("="*70)
    
    # 1. Verificar que existe un asiento
    entry = JournalEntry.objects.first()
    if not entry:
        print("❌ No hay asientos para probar")
        return
    
    print(f"✅ Asiento encontrado: ID {entry.id}")
    
    # 2. Verificar template path
    template_path = "admin/accounting/journalentry/change_form.html"
    
    try:
        template = get_template(template_path)
        print(f"✅ Template cargado: {template_path}")
    except Exception as e:
        print(f"❌ Error cargando template: {e}")
        return
    
    # 3. Simular context del admin
    context = {
        'original': entry,
        'opts': entry._meta,
        'change': True,
        'is_popup': False,
        'save_as': False,
        'has_delete_permission': True,
        'has_change_permission': True,
        'has_absolute_url': False,
    }
    
    # 4. Renderizar template
    try:
        rendered_content = template.render(context)
        print(f"✅ Template renderizado exitosamente")
        
        # Verificar elementos específicos en el HTML renderizado
        checks = [
            ("print-button-container", "Contenedor del botón"),
            ("btn-print", "Clase del botón"),
            ("Imprimir PDF", "Texto del botón"),
            ("🖨️", "Icono del botón"),
            ("DOMContentLoaded", "JavaScript"),
            ("querySelectorAll", "Selector de filas"),
        ]
        
        print("\n📋 VERIFICACIÓN DEL HTML RENDERIZADO:")
        for check_text, description in checks:
            if check_text in rendered_content:
                print(f"   ✅ {description}: ENCONTRADO")
            else:
                print(f"   ❌ {description}: NO ENCONTRADO")
        
        # Mostrar fragmento relevante del HTML
        print(f"\n📄 FRAGMENTO DEL HTML GENERADO:")
        print("-" * 50)
        
        # Buscar la sección del botón
        if "print-button-container" in rendered_content:
            start = rendered_content.find("print-button-container")
            if start != -1:
                # Mostrar contexto alrededor del botón
                context_start = max(0, start - 200)
                context_end = min(len(rendered_content), start + 500)
                fragment = rendered_content[context_start:context_end]
                print(fragment)
        else:
            print("⚠️  No se encontró el contenedor del botón en el HTML")
        
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Error renderizando template: {e}")

def check_javascript_syntax():
    """Verificar que el JavaScript no tenga errores de sintaxis"""
    print(f"\n🔧 VERIFICACIÓN DE JAVASCRIPT:")
    print("-" * 40)
    
    template_file = "templates/admin/accounting/journalentry/change_form.html"
    if os.path.exists(template_file):
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraer la sección de JavaScript
        js_start = content.find("<script")
        js_end = content.find("</script>") + 9
        
        if js_start != -1 and js_end != -1:
            js_content = content[js_start:js_end]
            print("✅ JavaScript encontrado en template")
            
            # Verificar elementos críticos del JS
            js_checks = [
                ("document.addEventListener", "Event listener"),
                ("DOMContentLoaded", "DOM ready"),
                ("getElementById('print-button-container')", "Buscar contenedor"),
                ("querySelectorAll('.submit-row')", "Buscar filas"),
                ("cloneNode(true)", "Clonar botón"),
                ("insertBefore", "Insertar botón"),
            ]
            
            for check_text, description in js_checks:
                if check_text in js_content:
                    print(f"   ✅ {description}: OK")
                else:
                    print(f"   ❌ {description}: FALTA")
        else:
            print("❌ No se encontró JavaScript en el template")

def check_css_loading():
    """Verificar que el CSS se carga correctamente"""
    print(f"\n🎨 VERIFICACIÓN DE CSS:")
    print("-" * 30)
    
    css_file = "static/admin/css/journal_print_button.css"
    if os.path.exists(css_file):
        print(f"✅ Archivo CSS existe: {css_file}")
        
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Verificar reglas CSS críticas
        css_checks = [
            (".btn-print", "Clase principal del botón"),
            ("background:", "Estilos de fondo"),
            ("hover", "Efectos hover"),
            (".loading", "Estado de carga"),
        ]
        
        for check_text, description in css_checks:
            if check_text in css_content:
                print(f"   ✅ {description}: OK")
            else:
                print(f"   ❌ {description}: FALTA")
    else:
        print(f"❌ Archivo CSS no encontrado: {css_file}")

def suggest_solutions():
    """Sugerir soluciones basadas en los hallazgos"""
    print(f"\n🔧 POSIBLES SOLUCIONES:")
    print("=" * 50)
    
    print("1. 🌐 VERIFICAR EN EL NAVEGADOR:")
    print("   • Abrir: http://127.0.0.1:8000/admin/accounting/journalentry/21/change/")
    print("   • Presionar F12 (Herramientas de Desarrollador)")
    print("   • Revisar pestaña 'Console' para errores de JavaScript")
    print("   • Revisar pestaña 'Network' para archivos CSS no cargados")
    print("   • Revisar pestaña 'Elements' para inspeccionar DOM")
    
    print("\n2. 🔍 BÚSQUEDA MANUAL EN EL DOM:")
    print("   • En Elements, buscar: #print-button-container")
    print("   • Verificar si el div existe pero está oculto")
    print("   • Buscar elementos con clase .submit-row")
    print("   • Verificar si el botón se clonó pero no es visible")
    
    print("\n3. 🐛 DEBUGGING DE JAVASCRIPT:")
    print("   • Verificar errores en Console")
    print("   • Buscar mensajes que empiecen con '🔍'")
    print("   • Verificar que no hay conflictos con otros scripts")
    
    print("\n4. 📱 VERIFICAR CSS:")
    print("   • En Network, verificar que journal_print_button.css se carga")
    print("   • En Elements > Styles, verificar reglas .btn-print")
    print("   • Verificar que no hay conflictos de CSS")

def main():
    print("🚨 DEBUGGING: ¿POR QUÉ NO APARECE EL BOTÓN?")
    
    debug_template_rendering()
    check_javascript_syntax()
    check_css_loading()
    suggest_solutions()
    
    print(f"\n📞 PRÓXIMOS PASOS:")
    print("1. Revisar output de este script")
    print("2. Abrir navegador en modo desarrollador")
    print("3. Seguir las sugerencias de debugging")
    print("4. Reportar hallazgos específicos para solución dirigida")

if __name__ == "__main__":
    main()