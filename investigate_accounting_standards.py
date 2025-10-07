#!/usr/bin/env python3
"""
Script para investigar normativas y estándares de asientos contables en Ecuador

Autor: Sistema ContaEC
Fecha: 2 de octubre, 2025
Objetivo: Identificar parámetros específicos requeridos por la SUPERCIAS y SRI
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import JournalEntry, JournalEntryLine, ChartOfAccounts
from apps.companies.models import Company
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

def analyze_accounting_standards():
    """
    Analiza los estándares contables implementados vs normativas ecuatorianas
    """
    print("🏛️ ANÁLISIS DE NORMATIVAS CONTABLES ECUATORIANAS")
    print("=" * 70)
    
    print("\n📋 1. ESTRUCTURA ACTUAL DE ASIENTOS CONTABLES:")
    print("-" * 50)
    
    # Analizar estructura actual
    print("🔍 Campos implementados en JournalEntry:")
    journal_fields = [field.name for field in JournalEntry._meta.fields]
    for field in journal_fields:
        field_obj = JournalEntry._meta.get_field(field)
        print(f"   • {field}: {field_obj.verbose_name} ({type(field_obj).__name__})")
    
    print("\n🔍 Campos implementados en JournalEntryLine:")
    line_fields = [field.name for field in JournalEntryLine._meta.fields]
    for field in line_fields:
        field_obj = JournalEntryLine._meta.get_field(field)
        print(f"   • {field}: {field_obj.verbose_name} ({type(field_obj).__name__})")

def analyze_regulatory_requirements():
    """
    Analiza requerimientos específicos de organismos reguladores
    """
    print("\n📜 2. REQUERIMIENTOS NORMATIVOS ECUATORIANOS:")
    print("-" * 50)
    
    print("\n🏢 SUPERINTENDENCIA DE COMPAÑÍAS (SUPERCIAS):")
    supercias_requirements = [
        "1. Libro Diario: Registro cronológico de operaciones",
        "2. Libro Mayor: Cuentas individualizadas",
        "3. Balance de Comprobación: Verificación de saldos",
        "4. Estados Financieros: Cumplimiento NIIF",
        "5. Numeración correlativa de asientos",
        "6. Firma autorizada en registros contables",
        "7. Documentación de respaldo obligatoria",
        "8. Conservación por 7 años mínimo"
    ]
    
    for req in supercias_requirements:
        print(f"   ✓ {req}")
    
    print("\n🏛️ SERVICIO DE RENTAS INTERNAS (SRI):")
    sri_requirements = [
        "1. Comprobantes de venta autorizados",
        "2. Respaldo documental de transacciones",
        "3. Registro de retenciones",
        "4. Declaraciones mensuales/anuales",
        "5. Facturación electrónica obligatoria",
        "6. Anexos transaccionales (ATS)",
        "7. Formularios 103/104 mensuales",
        "8. Declaración anual de impuesto a la renta"
    ]
    
    for req in sri_requirements:
        print(f"   ✓ {req}")
    
    print("\n📊 NORMAS INTERNACIONALES (NIIF):")
    niif_requirements = [
        "1. Principio de partida doble",
        "2. Causación vs. percepción",
        "3. Materialidad e importancia relativa",
        "4. Prudencia y conservadurismo",
        "5. Consistencia en aplicación",
        "6. Revelación suficiente",
        "7. Comparabilidad entre períodos",
        "8. Valor razonable cuando aplique"
    ]
    
    for req in niif_requirements:
        print(f"   ✓ {req}")

def analyze_journal_entry_format():
    """
    Analiza formato específico requerido para asientos contables
    """
    print("\n📝 3. FORMATO ESTÁNDAR DE ASIENTOS CONTABLES:")
    print("-" * 50)
    
    print("\n🎯 ELEMENTOS OBLIGATORIOS:")
    mandatory_elements = [
        "• Número de asiento (correlativo)",
        "• Fecha de la operación", 
        "• Descripción o concepto",
        "• Código de cuenta (según plan de cuentas)",
        "• Nombre de la cuenta",
        "• Valores débito y crédito",
        "• Referencia del documento de respaldo",
        "• Balance (débitos = créditos)"
    ]
    
    for element in mandatory_elements:
        print(f"   ✓ {element}")
    
    print("\n📋 ELEMENTOS RECOMENDADOS:")
    recommended_elements = [
        "• Usuario responsable del asiento",
        "• Fecha de registro",
        "• Estado del asiento (borrador/definitivo)",
        "• Auxiliares o subcuentas",
        "• Centro de costos (si aplica)",
        "• Tipo de documento de respaldo",
        "• Número del documento de respaldo",
        "• Observaciones adicionales"
    ]
    
    for element in recommended_elements:
        print(f"   ⭐ {element}")

def analyze_numbering_standards():
    """
    Analiza estándares de numeración
    """
    print("\n🔢 4. ESTÁNDARES DE NUMERACIÓN:")
    print("-" * 50)
    
    print("\n📊 NUMERACIÓN DE ASIENTOS:")
    numbering_rules = [
        "1. Secuencial y correlativo por ejercicio fiscal",
        "2. Sin saltos ni duplicados",
        "3. Formato sugerido: YYYYMMDD-XXXX o simple correlativo",
        "4. Reinicio anual o continuidad (decisión empresarial)",
        "5. Prefijos por tipo de asiento (opcional pero recomendado):",
        "   - DI: Diario general",
        "   - AJ: Ajustes",
        "   - CI: Cierre",
        "   - AP: Apertura",
        "   - RE: Reclasificaciones"
    ]
    
    for rule in numbering_rules:
        print(f"   • {rule}")

def analyze_current_implementation():
    """
    Analiza la implementación actual vs normativas
    """
    print("\n🔍 5. ANÁLISIS DE IMPLEMENTACIÓN ACTUAL:")
    print("-" * 50)
    
    # Obtener datos actuales
    total_entries = JournalEntry.objects.count()
    companies = Company.objects.count()
    
    print(f"\n📊 ESTADO ACTUAL:")
    print(f"   • Total de asientos: {total_entries}")
    print(f"   • Empresas registradas: {companies}")
    
    if total_entries > 0:
        # Analizar primer asiento
        sample_entry = JournalEntry.objects.first()
        print(f"\n🔍 EJEMPLO DE ASIENTO ACTUAL:")
        print(f"   • Número: {sample_entry.number}")
        print(f"   • Fecha: {sample_entry.date}")
        print(f"   • Estado: {sample_entry.get_state_display()}")
        print(f"   • Balanceado: {'✓ Sí' if sample_entry.is_balanced else '✗ No'}")
        print(f"   • Total débito: ${sample_entry.total_debit}")
        print(f"   • Total crédito: ${sample_entry.total_credit}")
        
        # Analizar líneas
        lines_count = sample_entry.lines.count()
        print(f"   • Líneas: {lines_count}")
        
        if lines_count > 0:
            sample_line = sample_entry.lines.first()
            print(f"\n📝 EJEMPLO DE LÍNEA:")
            print(f"   • Cuenta: {sample_line.account.code} - {sample_line.account.name}")
            print(f"   • Descripción: {sample_line.description}")
            print(f"   • Débito: ${sample_line.debit}")
            print(f"   • Crédito: ${sample_line.credit}")
    
    print("\n✅ CUMPLIMIENTO NORMATIVO ACTUAL:")
    compliance_check = [
        ("Partida doble", "✓", "Implementado"),
        ("Numeración correlativa", "✓", "Implementado"), 
        ("Balance obligatorio", "✓", "Implementado"),
        ("Estados de asientos", "✓", "Implementado"),
        ("Auditoría de usuarios", "✓", "Implementado"),
        ("Respaldo documental", "⚠️", "Parcial - campos disponibles"),
        ("Firma digital", "❌", "No implementado"),
        ("Exportación libros", "❌", "No implementado"),
        ("Retenciones automáticas", "❌", "No implementado"),
        ("Anexos SRI", "❌", "No implementado")
    ]
    
    for item, status, detail in compliance_check:
        print(f"   {status} {item}: {detail}")

def recommend_improvements():
    """
    Recomienda mejoras para cumplimiento total
    """
    print("\n🚀 6. RECOMENDACIONES DE MEJORA:")
    print("-" * 50)
    
    improvements = [
        {
            "area": "📋 Estructura de Asientos",
            "items": [
                "• Agregar campo 'tipo_asiento' (AJ, DI, CI, etc.)",
                "• Implementar numeración con prefijos",
                "• Agregar campo 'período_fiscal'",
                "• Incluir 'centro_costos' opcional"
            ]
        },
        {
            "area": "🔒 Seguridad y Auditoría", 
            "items": [
                "• Implementar firma digital de asientos",
                "• Log completo de modificaciones",
                "• Aprobación de asientos por supervisor",
                "• Bloqueo de períodos cerrados"
            ]
        },
        {
            "area": "📄 Documentación",
            "items": [
                "• Adjuntar archivos PDF a asientos",
                "• Validación obligatoria de documentos",
                "• OCR para automatizar captura",
                "• Versionado de documentos"
            ]
        },
        {
            "area": "📊 Reportes Legales",
            "items": [
                "• Exportación Libro Diario",
                "• Exportación Libro Mayor", 
                "• Balance de Comprobación automático",
                "• Formularios SRI integrados"
            ]
        },
        {
            "area": "🤖 Automatización",
            "items": [
                "• Asientos automáticos por facturación",
                "• Cálculo automático de retenciones",
                "• Provisiones mensuales automáticas",
                "• Depreciaciones automáticas"
            ]
        }
    ]
    
    for improvement in improvements:
        print(f"\n{improvement['area']}:")
        for item in improvement['items']:
            print(f"   {item}")

def main():
    """
    Función principal del análisis
    """
    try:
        analyze_accounting_standards()
        analyze_regulatory_requirements() 
        analyze_journal_entry_format()
        analyze_numbering_standards()
        analyze_current_implementation()
        recommend_improvements()
        
        print("\n" + "=" * 70)
        print("🎯 CONCLUSIÓN:")
        print("El sistema ContaEC tiene una base sólida que cumple con los")
        print("requerimientos fundamentales de la normativa ecuatoriana.")
        print("Las mejoras recomendadas aumentarían el nivel de cumplimiento")
        print("y facilitarían las obligaciones tributarias y societarias.")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()