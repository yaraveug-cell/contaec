#!/usr/bin/env python
"""
Script de prueba para verificar las mejoras en el generador de PDF
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import JournalEntry
from apps.accounting.journal_pdf import generate_journal_entry_pdf
import tempfile
import webbrowser

def test_pdf_improvements():
    print("🧪 PRUEBA DE MEJORAS EN GENERADOR PDF")
    print("="*50)
    
    # Buscar un asiento para probar
    entry = JournalEntry.objects.first()
    if not entry:
        print("❌ No hay asientos contables para probar")
        return
    
    print(f"📄 Probando con asiento ID {entry.id}: {entry.number}")
    
    try:
        # Generar PDF
        print("🔄 Generando PDF con mejoras...")
        pdf_buffer = generate_journal_entry_pdf(entry)
        
        # Guardar temporalmente para visualizar
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf.write(pdf_buffer.getvalue())
            temp_pdf_path = temp_pdf.name
        
        print(f"✅ PDF generado exitosamente")
        print(f"📁 Archivo temporal: {temp_pdf_path}")
        
        # Mostrar información del asiento
        print(f"\n📋 INFORMACIÓN DEL ASIENTO PROBADO:")
        print(f"   - Número: {entry.number}")
        print(f"   - Empresa: {entry.company.trade_name}")
        print(f"   - Descripción: {entry.description or 'Sin descripción'}")
        print(f"   - Líneas: {entry.lines.count()}")
        
        # Mostrar información de las líneas
        print(f"\n📊 LÍNEAS DEL ASIENTO:")
        for i, line in enumerate(entry.lines.all(), 1):
            account_name = line.account.name
            description = line.description or 'Sin descripción'
            print(f"   {i}. {line.account.code} - {account_name[:30]}{'...' if len(account_name) > 30 else ''}")
            print(f"      Descripción: {description[:40]}{'...' if len(description) > 40 else ''}")
            print(f"      Débito: ${line.debit:,.2f} | Crédito: ${line.credit:,.2f}")
        
        print(f"\n🚀 MEJORAS IMPLEMENTADAS:")
        print(f"   ✅ Márgenes optimizados (50px vs 72px anteriores)")
        print(f"   ✅ Anchos de columna ajustados para mejor distribución")
        print(f"   ✅ Manejo de texto largo con Paragraphs")
        print(f"   ✅ Truncamiento inteligente de texto excesivo")
        print(f"   ✅ Separación de código y nombre de cuenta")
        print(f"   ✅ Tamaño de fuente optimizado (10px)")
        print(f"   ✅ Alineación mejorada (TOP para celdas)")
        
        # Preguntar si quiere abrir el PDF
        try:
            response = input(f"\n¿Desea abrir el PDF generado? (s/n): ").lower().strip()
            if response in ['s', 'si', 'sí', 'yes', 'y']:
                print(f"🌐 Abriendo PDF...")
                webbrowser.open(f"file://{temp_pdf_path}")
            else:
                print(f"📁 PDF guardado en: {temp_pdf_path}")
        except:
            print(f"📁 PDF guardado en: {temp_pdf_path}")
        
        print(f"\n🎯 PARA PROBAR EN EL SISTEMA:")
        print(f"   1. Ir a: http://127.0.0.1:8000/admin/accounting/journalentry/{entry.id}/change/")
        print(f"   2. Hacer clic en el botón '🖨️ Imprimir PDF'")
        print(f"   3. Verificar que el texto se muestra correctamente sin desbordamientos")
        
    except Exception as e:
        print(f"❌ Error generando PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_improvements()