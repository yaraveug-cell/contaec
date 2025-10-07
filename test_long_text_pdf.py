#!/usr/bin/env python
"""
Crear asiento de prueba con texto largo para verificar el manejo de desbordamientos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import JournalEntry, JournalEntryLine, ChartOfAccounts, Company
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone

User = get_user_model()

def create_test_entry_long_text():
    print("🧪 CREANDO ASIENTO DE PRUEBA CON TEXTO LARGO")
    print("="*55)
    
    # Obtener datos necesarios
    company = Company.objects.first()
    if not company:
        print("❌ No hay empresas disponibles")
        return None
    
    user = User.objects.filter(is_staff=True).first()
    if not user:
        print("❌ No hay usuarios administrativos")
        return None
    
    accounts = ChartOfAccounts.objects.all()[:3]
    if len(accounts) < 2:
        print("❌ No hay suficientes cuentas contables")
        return None
    
    try:
        # Crear asiento con texto muy largo
        journal_entry = JournalEntry.objects.create(
            company=company,
            date=timezone.now().date(),
            description="PRUEBA DE MANEJO DE TEXTO EXTREMADAMENTE LARGO EN DESCRIPCIÓN DEL ASIENTO CONTABLE PARA VERIFICAR QUE NO SE PRODUZCAN DESBORDAMIENTOS EN EL PDF GENERADO Y QUE EL TEXTO SE AJUSTE CORRECTAMENTE DENTRO DE LAS CELDAS ASIGNADAS",
            reference="REF-PRUEBA-TEXTO-LARGO-PARA-VERIFICAR-DESBORDAMIENTOS-EN-PDF-GENERADO-SISTEMA-CONTABLE-2025",
            created_by=user,
            state='posted',
            posted_by=user,
            posted_at=timezone.now()
        )
        
        # Crear líneas con texto largo
        JournalEntryLine.objects.create(
            journal_entry=journal_entry,
            account=accounts[0],
            description="LÍNEA DE PRUEBA CON DESCRIPCIÓN EXTREMADAMENTE LARGA PARA VERIFICAR EL COMPORTAMIENTO DEL GENERADOR PDF CUANDO SE ENCUENTRAN TEXTOS QUE EXCEDEN EL ANCHO NORMAL DE LAS COLUMNAS ESTABLECIDAS",
            debit=Decimal('5000.00'),
            credit=Decimal('0.00')
        )
        
        JournalEntryLine.objects.create(
            journal_entry=journal_entry,
            account=accounts[1],
            description="SEGUNDA LÍNEA DE PRUEBA CON DESCRIPCIÓN IGUALMENTE LARGA PARA ASEGURAR QUE MÚLTIPLES LÍNEAS CON TEXTO EXTENSO NO CAUSEN PROBLEMAS DE FORMATO O VISUALIZACIÓN",
            debit=Decimal('0.00'),
            credit=Decimal('5000.00')
        )
        
        print(f"✅ Asiento de prueba creado: ID {journal_entry.id}")
        print(f"📄 Número: {journal_entry.number}")
        print(f"📝 Descripción: {journal_entry.description[:60]}...")
        print(f"🔗 Referencia: {journal_entry.reference[:60]}...")
        print(f"📊 Líneas creadas: {journal_entry.lines.count()}")
        
        return journal_entry
        
    except Exception as e:
        print(f"❌ Error creando asiento de prueba: {e}")
        return None

def test_long_text_pdf(journal_entry):
    print(f"\n🧪 PROBANDO PDF CON TEXTO LARGO")
    print("="*40)
    
    from apps.accounting.journal_pdf import generate_journal_entry_pdf
    import tempfile
    import webbrowser
    
    try:
        # Generar PDF
        print("🔄 Generando PDF con texto largo...")
        pdf_buffer = generate_journal_entry_pdf(journal_entry)
        
        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf.write(pdf_buffer.getvalue())
            temp_pdf_path = temp_pdf.name
        
        print(f"✅ PDF generado exitosamente")
        print(f"📁 Archivo: {temp_pdf_path}")
        
        print(f"\n📋 VERIFICACIONES A REALIZAR:")
        print(f"   ✅ Descripción del asiento no se desborda")
        print(f"   ✅ Referencia del asiento se muestra correctamente")
        print(f"   ✅ Nombres de cuentas se ajustan al espacio disponible")
        print(f"   ✅ Descripciones de líneas no sobresalen de sus celdas")
        print(f"   ✅ El PDF se ve profesional y legible")
        
        # Abrir PDF
        try:
            response = input(f"\n¿Abrir PDF para verificar formato? (s/n): ").lower().strip()
            if response in ['s', 'si', 'sí', 'yes', 'y']:
                webbrowser.open(f"file://{temp_pdf_path}")
                
                # Verificación manual
                print(f"\n🔍 VERIFICACIÓN MANUAL:")
                print(f"   1. ¿Se ve todo el texto sin cortarse? ")
                print(f"   2. ¿Las columnas mantienen su ancho? ")
                print(f"   3. ¿No hay superposición de texto? ")
                print(f"   4. ¿El formato se ve profesional? ")
                
                verification = input(f"\n¿El PDF se ve correctamente? (s/n): ").lower().strip()
                if verification in ['s', 'si', 'sí', 'yes', 'y']:
                    print(f"✅ ¡VERIFICACIÓN EXITOSA!")
                    print(f"🎉 Las mejoras del PDF funcionan correctamente")
                else:
                    print(f"⚠️  Puede necesitar ajustes adicionales")
            
        except:
            print(f"📁 PDF guardado en: {temp_pdf_path}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error generando PDF: {e}")
        return False

def main():
    print("🎯 PRUEBA COMPLETA DE MEJORAS EN PDF")
    print("="*45)
    
    # Crear asiento de prueba
    test_entry = create_test_entry_long_text()
    
    if test_entry:
        # Probar PDF
        success = test_long_text_pdf(test_entry)
        
        if success:
            print(f"\n🌐 PARA PROBAR EN EL NAVEGADOR:")
            print(f"   URL: http://127.0.0.1:8000/admin/accounting/journalentry/{test_entry.id}/change/")
            print(f"   Hacer clic en '🖨️ Imprimir PDF' y verificar el resultado")
        
        # Preguntar si eliminar el asiento de prueba
        try:
            delete_response = input(f"\n¿Eliminar asiento de prueba? (s/n): ").lower().strip()
            if delete_response in ['s', 'si', 'sí', 'yes', 'y']:
                test_entry.delete()
                print(f"🗑️  Asiento de prueba eliminado")
            else:
                print(f"💾 Asiento de prueba conservado: ID {test_entry.id}")
        except:
            print(f"💾 Asiento de prueba conservado: ID {test_entry.id}")

if __name__ == "__main__":
    main()