#!/usr/bin/env python
"""
Script final de verificación del botón de impresión para asientos contables
Revisar todos los componentes y proporcionar información detallada para el debugging
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.contrib.auth.models import User
from apps.accounting.models import JournalEntry
from django.urls import reverse
from django.contrib.admin import site
from apps.accounting.admin import JournalEntryAdmin

def print_separator(title):
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)

def check_admin_registration():
    """Verificar que el admin está registrado correctamente"""
    print_separator("VERIFICACIÓN DE ADMIN REGISTRATION")
    
    if JournalEntry in site._registry:
        admin_class = site._registry[JournalEntry]
        print(f"✅ JournalEntry está registrado en admin")
        print(f"   Admin class: {admin_class.__class__.__name__}")
        
        # Verificar métodos personalizados
        if hasattr(admin_class, 'get_urls'):
            print(f"✅ Método get_urls() encontrado")
        else:
            print(f"❌ Método get_urls() NO encontrado")
            
        if hasattr(admin_class, 'print_journal_entry_pdf'):
            print(f"✅ Método print_journal_entry_pdf() encontrado")
        else:
            print(f"❌ Método print_journal_entry_pdf() NO encontrado")
            
    else:
        print(f"❌ JournalEntry NO está registrado en admin")

def check_urls():
    """Verificar que las URLs están configuradas"""
    print_separator("VERIFICACIÓN DE URLS")
    
    try:
        # Intentar obtener una entrada de ejemplo
        entry = JournalEntry.objects.first()
        if entry:
            url_name = f"admin:accounting_journalentry_print_pdf"
            print(f"✅ Asiento de prueba encontrado: ID {entry.id}")
            
            # Verificar que podemos hacer reverse de la URL
            try:
                pdf_url = reverse(url_name, args=[entry.id])
                print(f"✅ URL del PDF generada: {pdf_url}")
            except Exception as e:
                print(f"❌ Error al generar URL del PDF: {e}")
        else:
            print(f"⚠️  No hay asientos contables para probar")
            
    except Exception as e:
        print(f"❌ Error verificando URLs: {e}")

def check_template_files():
    """Verificar archivos de template"""
    print_separator("VERIFICACIÓN DE ARCHIVOS DE TEMPLATE")
    
    template_path = "templates/admin/accounting/journalentry/change_form.html"
    css_path = "static/admin/css/journal_print_button.css"
    
    if os.path.exists(template_path):
        print(f"✅ Template encontrado: {template_path}")
        
        # Leer contenido del template
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar elementos clave
        checks = [
            ("print-button-container", "div id='print-button-container'"),
            ("btn-print", "class='btn-print'"),
            ("JavaScript DOMContentLoaded", "DOMContentLoaded"),
            ("querySelectorAll", "querySelectorAll('.submit-row')"),
            ("cloneNode", "cloneNode(true)"),
            ("insertBefore", "insertBefore"),
        ]
        
        for check_name, check_content in checks:
            if check_content in content:
                print(f"   ✅ {check_name}")
            else:
                print(f"   ❌ {check_name} NO encontrado")
                
    else:
        print(f"❌ Template NO encontrado: {template_path}")
    
    if os.path.exists(css_path):
        print(f"✅ CSS encontrado: {css_path}")
    else:
        print(f"❌ CSS NO encontrado: {css_path}")

def check_pdf_generator():
    """Verificar el generador de PDF"""
    print_separator("VERIFICACIÓN DEL GENERADOR DE PDF")
    
    pdf_path = "apps/accounting/journal_pdf.py"
    
    if os.path.exists(pdf_path):
        print(f"✅ Generador PDF encontrado: {pdf_path}")
        
        try:
            from apps.accounting.journal_pdf import JournalEntryPDFGenerator
            print(f"✅ Clase JournalEntryPDFGenerator importada correctamente")
            
            # Verificar métodos
            generator = JournalEntryPDFGenerator()
            methods = ['generate_pdf', 'add_header', 'add_entry_info', 'add_lines_table']
            for method in methods:
                if hasattr(generator, method):
                    print(f"   ✅ Método {method}()")
                else:
                    print(f"   ❌ Método {method}() NO encontrado")
                    
        except Exception as e:
            print(f"❌ Error importando generador PDF: {e}")
    else:
        print(f"❌ Generador PDF NO encontrado: {pdf_path}")

def test_template_content():
    """Mostrar el contenido actual del template para debugging"""
    print_separator("CONTENIDO ACTUAL DEL TEMPLATE")
    
    template_path = "templates/admin/accounting/journalentry/change_form.html"
    
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("Contenido completo del template:")
        print("-" * 40)
        print(content)
        print("-" * 40)
    else:
        print("❌ Template no encontrado")

def show_admin_urls():
    """Mostrar información sobre las URLs del admin"""
    print_separator("INFORMACIÓN DE URLS DEL ADMIN")
    
    try:
        # Obtener la instancia del admin
        if JournalEntry in site._registry:
            admin_instance = site._registry[JournalEntry]
            
            # Obtener las URLs personalizadas
            if hasattr(admin_instance, 'get_urls'):
                custom_urls = admin_instance.get_urls()
                print(f"URLs personalizadas encontradas: {len(custom_urls)}")
                
                for url in custom_urls:
                    if hasattr(url, 'pattern'):
                        print(f"   - Patrón: {url.pattern}")
                    if hasattr(url, 'name'):
                        print(f"     Nombre: {url.name}")
            else:
                print("❌ Método get_urls() no encontrado en admin")
                
    except Exception as e:
        print(f"❌ Error obteniendo URLs del admin: {e}")

def main():
    print("🔍 DIAGNÓSTICO COMPLETO DEL BOTÓN DE IMPRESIÓN")
    print("📄 Sistema de Contabilidad - Asientos Contables")
    
    check_admin_registration()
    check_urls()
    check_template_files()
    check_pdf_generator()
    show_admin_urls()
    test_template_content()
    
    print_separator("RESUMEN Y RECOMENDACIONES")
    
    # Verificaciones finales
    entry_count = JournalEntry.objects.count()
    user_count = User.objects.filter(is_staff=True).count()
    
    print(f"📊 Estadísticas del sistema:")
    print(f"   - Asientos contables: {entry_count}")
    print(f"   - Usuarios admin: {user_count}")
    
    print(f"\n🚀 Para probar el botón:")
    print(f"   1. Acceder a: http://127.0.0.1:8000/admin/")
    print(f"   2. Ir a Contabilidad > Asientos contables")
    print(f"   3. Editar cualquier asiento existente")
    print(f"   4. Verificar que aparece el botón 🖨️ Imprimir PDF")
    print(f"   5. Revisar la consola del navegador (F12) para mensajes de JavaScript")
    
    if entry_count > 0:
        entry = JournalEntry.objects.first()
        print(f"\n🔗 URL directa para editar asiento de prueba:")
        print(f"   http://127.0.0.1:8000/admin/accounting/journalentry/{entry.id}/change/")
        print(f"   http://127.0.0.1:8000/admin/accounting/journalentry/{entry.id}/print-pdf/")

if __name__ == "__main__":
    main()