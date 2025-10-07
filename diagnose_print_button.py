#!/usr/bin/env python3
"""
Diagnóstico del problema del botón de impresión no visible
Verificar todos los componentes y encontrar la causa raíz
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append(str(Path(__file__).parent))

django.setup()

def diagnose_print_button_issue():
    """Diagnosticar por qué el botón no se ve"""
    
    print("=" * 80)
    print("🔍 DIAGNÓSTICO: BOTÓN DE IMPRESIÓN NO VISIBLE")
    print("=" * 80)
    
    # 1. Verificar estructura del template
    print(f"\n📄 1. ANALIZANDO TEMPLATE:")
    print("-" * 50)
    
    template_file = Path("templates/admin/accounting/journalentry/change_form.html")
    if template_file.exists():
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        print(f"   ✅ Template existe: {template_file}")
        
        # Buscar problemas comunes
        issues = []
        
        # Verificar bloques
        if 'submit_buttons_top' not in template_content:
            issues.append("❌ Bloque submit_buttons_top faltante")
        else:
            print(f"   ✅ Bloque submit_buttons_top: Presente")
            
        if '{% if original %}' not in template_content:
            issues.append("❌ Condición original faltante")
        else:
            print(f"   ✅ Condición if original: Presente")
            
        if 'print-button-inline' not in template_content:
            issues.append("❌ Clase print-button-inline faltante")
        else:
            print(f"   ✅ Clase print-button-inline: Presente")
            
        if 'repositionPrintButtons' not in template_content:
            issues.append("❌ JavaScript repositionPrintButtons faltante")
        else:
            print(f"   ✅ JavaScript repositionPrintButtons: Presente")
        
        # Verificar estructura HTML básica
        if 'btn-print' not in template_content:
            issues.append("❌ Clase btn-print faltante")
        else:
            print(f"   ✅ Clase btn-print: Presente")
            
        if issues:
            print(f"\n   🚨 PROBLEMAS ENCONTRADOS EN TEMPLATE:")
            for issue in issues:
                print(f"      {issue}")
        else:
            print(f"   ✅ Template estructura: Correcta")
            
    else:
        print(f"   ❌ Template no existe: {template_file}")
    
    # 2. Verificar CSS
    print(f"\n🎨 2. ANALIZANDO CSS:")
    print("-" * 50)
    
    css_file = Path("static/admin/css/journal_print_button.css")
    if css_file.exists():
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
            
        print(f"   ✅ CSS existe: {css_file}")
        
        # Verificar estilos críticos
        css_issues = []
        
        if '.print-button-inline' not in css_content:
            css_issues.append("❌ Estilo .print-button-inline faltante")
        else:
            print(f"   ✅ Estilo .print-button-inline: Presente")
            
        if '.btn-print' not in css_content:
            css_issues.append("❌ Estilo .btn-print faltante")
        else:
            print(f"   ✅ Estilo .btn-print: Presente")
            
        if '.repositioned' not in css_content:
            css_issues.append("❌ Estilo .repositioned faltante")
        else:
            print(f"   ✅ Estilo .repositioned: Presente")
            
        # Verificar si hay display: none problemático
        if 'display: none' in css_content:
            print(f"   ⚠️ display: none encontrado - verificando contexto")
            lines = css_content.split('\n')
            for i, line in enumerate(lines):
                if 'display: none' in line:
                    context_start = max(0, i-2)
                    context_end = min(len(lines), i+3)
                    print(f"      Línea {i+1}: {line.strip()}")
                    for j in range(context_start, context_end):
                        if j != i:
                            print(f"         {j+1}: {lines[j].strip()}")
        
        if css_issues:
            print(f"\n   🚨 PROBLEMAS CSS:")
            for issue in css_issues:
                print(f"      {issue}")
                
    else:
        print(f"   ❌ CSS no existe: {css_file}")
    
    # 3. Verificar admin y URLs
    print(f"\n⚙️ 3. VERIFICANDO ADMIN Y URLs:")
    print("-" * 50)
    
    try:
        from apps.accounting.admin import JournalEntryAdmin
        from apps.accounting.models import JournalEntry
        from django.contrib import admin
        
        if JournalEntry in admin.site._registry:
            admin_instance = admin.site._registry[JournalEntry]
            print(f"   ✅ JournalEntry registrado en admin")
            
            # Verificar URL personalizada
            if hasattr(admin_instance, 'get_urls'):
                print(f"   ✅ Método get_urls: Presente")
            else:
                print(f"   ❌ Método get_urls: Faltante")
                
            # Verificar vista PDF
            if hasattr(admin_instance, 'print_journal_entry_pdf'):
                print(f"   ✅ Vista print_journal_entry_pdf: Presente")
            else:
                print(f"   ❌ Vista print_journal_entry_pdf: Faltante")
                
            # Probar generar URL
            try:
                from django.urls import reverse
                test_entry = JournalEntry.objects.first()
                if test_entry:
                    url = reverse('admin:accounting_journalentry_print_pdf', args=[test_entry.pk])
                    print(f"   ✅ URL generada: {url}")
                else:
                    print(f"   ⚠️ No hay asientos para probar URL")
            except Exception as e:
                print(f"   ❌ Error generando URL: {e}")
                
        else:
            print(f"   ❌ JournalEntry no registrado")
            
    except Exception as e:
        print(f"   ❌ Error verificando admin: {e}")
    
    # 4. Análisis del problema más probable
    print(f"\n🔍 4. ANÁLISIS DE CAUSAS PROBABLES:")
    print("-" * 50)
    
    probable_causes = [
        {
            'cause': 'Template no se está cargando',
            'check': template_file.exists(),
            'solution': 'Verificar ruta y herencia del template'
        },
        {
            'cause': 'JavaScript no se ejecuta',
            'check': 'repositionPrintButtons' in template_content if template_file.exists() else False,
            'solution': 'Verificar errores de JavaScript en consola'
        },
        {
            'cause': 'CSS display: none permanente',
            'check': True,  # Siempre verificar
            'solution': 'Revisar lógica de display en CSS'
        },
        {
            'cause': 'Condición {% if original %} falsa',
            'check': True,  # Siempre verificar
            'solution': 'Verificar que se esté editando (no creando) asiento'
        }
    ]
    
    for i, cause_info in enumerate(probable_causes, 1):
        status = "✅" if cause_info['check'] else "❌"
        print(f"   {i}. {status} {cause_info['cause']}")
        if not cause_info['check']:
            print(f"      💡 Solución: {cause_info['solution']}")
    
    # 5. Crear test HTML simple
    print(f"\n🧪 5. GENERANDO TEST HTML SIMPLE:")
    print("-" * 50)
    
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Botón Impresión</title>
        <style>
            .btn-print {
                background: green;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 6px;
            }
            .print-button-inline {
                display: none;
            }
        </style>
    </head>
    <body>
        <h1>Test Botón de Impresión</h1>
        
        <div class="submit-row">
            <input type="submit" value="Guardar" />
            <input type="submit" value="Guardar y continuar editando" />
        </div>
        
        <a href="#" class="btn-print print-button-inline" style="display: none;">
            <span class="icon">🖨️</span>
            <span class="text">Imprimir PDF</span>
        </a>
        
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                console.log('🔍 Test: DOM cargado');
                
                function repositionPrintButtons() {
                    console.log('🔍 Test: Ejecutando repositionPrintButtons');
                    
                    const printButtons = document.querySelectorAll('.print-button-inline');
                    console.log('🔍 Test: Botones encontrados:', printButtons.length);
                    
                    printButtons.forEach(function(button) {
                        const submitRow = document.querySelector('.submit-row');
                        if (submitRow) {
                            console.log('🔍 Test: Submit-row encontrado');
                            
                            const clonedButton = button.cloneNode(true);
                            clonedButton.style.display = 'inline-flex';
                            clonedButton.classList.add('repositioned');
                            
                            submitRow.appendChild(clonedButton);
                            console.log('🔍 Test: Botón clonado y agregado');
                        } else {
                            console.log('❌ Test: Submit-row NO encontrado');
                        }
                    });
                }
                
                repositionPrintButtons();
            });
        </script>
    </body>
    </html>
    """
    
    test_file = Path("test_print_button.html")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_html)
    
    print(f"   ✅ Test HTML creado: {test_file}")
    print(f"   💡 Abrir en navegador para ver si funciona la lógica básica")
    
    # 6. Recomendaciones específicas
    print(f"\n💡 6. RECOMENDACIONES DE DEBUGGING:")
    print("-" * 50)
    
    print(f"   📋 PASOS PARA DEBUGGEAR:")
    print(f"   1. Ir al Django Admin → Contabilidad → Asientos")
    print(f"   2. Abrir un asiento EXISTENTE (no crear nuevo)")
    print(f"   3. Abrir DevTools (F12) → Console")
    print(f"   4. Buscar errores JavaScript")
    print(f"   5. Verificar en Elements si existe el HTML del botón")
    
    print(f"\n   🔧 COMANDOS DE CONSOLA PARA DEBUGGING:")
    print(f"   • document.querySelector('.print-button-inline')")
    print(f"   • document.querySelector('.submit-row')")  
    print(f"   • console.log('repositionPrintButtons ejecutándose')")
    
    print(f"\n   ⚠️ VERIFICACIONES CRÍTICAS:")
    print(f"   • ¿Estás en modo EDICIÓN (no creación)?")
    print(f"   • ¿El template se está cargando?")
    print(f"   • ¿Hay errores JavaScript en consola?")
    print(f"   • ¿El CSS se está aplicando?")
    
    return True

if __name__ == "__main__":
    diagnose_print_button_issue()