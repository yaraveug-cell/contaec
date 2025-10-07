#!/usr/bin/env python
"""
Test simplificado del sistema de botón de impresión
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import JournalEntry

def test_components():
    print("🔍 VERIFICACIÓN RÁPIDA DEL SISTEMA DE IMPRESIÓN")
    print("="*60)
    
    # 1. Verificar asientos disponibles
    entries = JournalEntry.objects.all()[:3]
    print(f"📊 Asientos disponibles: {JournalEntry.objects.count()}")
    
    if entries:
        entry = entries[0]
        print(f"✅ Asiento de prueba: ID {entry.id}")
        
        # 2. Verificar archivos clave
        files_to_check = [
            ("Template", "templates/admin/accounting/journalentry/change_form.html"),
            ("CSS", "static/admin/css/journal_print_button.css"),
            ("PDF Generator", "apps/accounting/journal_pdf.py"),
        ]
        
        all_files_ok = True
        for name, filepath in files_to_check:
            if os.path.exists(filepath):
                print(f"✅ {name}: OK")
            else:
                print(f"❌ {name}: NO encontrado")
                all_files_ok = False
        
        # 3. Verificar template contiene elementos clave
        template_path = "templates/admin/accounting/journalentry/change_form.html"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            key_elements = [
                ("ID del contenedor", "print-button-container"),
                ("Clase del botón", "btn-print"),
                ("JavaScript", "DOMContentLoaded"),
                ("URL del PDF", "accounting_journalentry_print_pdf"),
            ]
            
            template_ok = True
            for name, element in key_elements:
                if element in content:
                    print(f"✅ {name}: OK")
                else:
                    print(f"❌ {name}: FALTA")
                    template_ok = False
        
        # 4. URLs de acceso directo
        print(f"\n🌐 URLs PARA PROBAR:")
        print(f"   📝 Admin: http://127.0.0.1:8000/admin/")
        print(f"   ✏️  Editar: http://127.0.0.1:8000/admin/accounting/journalentry/{entry.id}/change/")
        print(f"   📄 PDF: http://127.0.0.1:8000/admin/accounting/journalentry/{entry.id}/print-pdf/")
        
        print(f"\n🔧 PASOS PARA VERIFICAR:")
        print(f"   1. Abrir la URL de editar en el navegador")
        print(f"   2. Presionar F12 para abrir Herramientas de Desarrollador")
        print(f"   3. Verificar mensajes en la consola (pestaña Console)")
        print(f"   4. Buscar el botón 🖨️ 'Imprimir PDF' en las filas de botones")
        print(f"   5. Si no aparece, revisar la pestaña Elements para inspeccionar el DOM")
        
        if all_files_ok and template_ok:
            print(f"\n✅ TODOS LOS COMPONENTES ESTÁN LISTOS")
            print(f"🚀 El botón debería aparecer correctamente")
        else:
            print(f"\n⚠️  HAY PROBLEMAS EN LA CONFIGURACIÓN")
    
    else:
        print("❌ No hay asientos contables para probar")

if __name__ == "__main__":
    test_components()