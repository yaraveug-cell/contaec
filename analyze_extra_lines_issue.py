#!/usr/bin/env python3
"""
Análisis de líneas automáticas en asientos contables

Autor: Sistema ContaEC
Fecha: 2 de octubre, 2025
Objetivo: Evaluar si eliminar las 2 líneas automáticas en edición de asientos
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import JournalEntry, JournalEntryLine
from apps.accounting.admin import JournalEntryLineInline, JournalEntryAdmin
from django.contrib.admin.sites import site

def analyze_current_inline_configuration():
    """
    Analizar la configuración actual de líneas automáticas
    """
    print("📋 ANÁLISIS DE LÍNEAS AUTOMÁTICAS EN ASIENTOS CONTABLES")
    print("=" * 65)
    
    print("\n⚙️ 1. CONFIGURACIÓN ACTUAL:")
    print("-" * 50)
    
    inline_instance = JournalEntryLineInline(JournalEntry, site)
    
    print(f"🎯 CONFIGURACIÓN ACTUAL DE INLINE:")
    print(f"   • Modelo: {inline_instance.model.__name__}")
    print(f"   • Extra: {inline_instance.extra} líneas automáticas")
    print(f"   • Tipo: {type(inline_instance).__name__}")
    print(f"   • Campos: {inline_instance.fields}")
    
    print(f"\n📋 CÓDIGO ACTUAL:")
    print("""
    class JournalEntryLineInline(admin.TabularInline):
        model = JournalEntryLine
        extra = 2  ← Crea 2 líneas vacías automáticamente
        fields = ['account', 'description', 'debit', 'credit', 'auxiliary_code']
    """)

def analyze_existing_entries():
    """
    Analizar asientos existentes para entender el patrón de uso
    """
    print("\n📊 2. ANÁLISIS DE ASIENTOS EXISTENTES:")
    print("-" * 50)
    
    total_entries = JournalEntry.objects.count()
    print(f"✅ Total de asientos en sistema: {total_entries}")
    
    if total_entries > 0:
        print(f"\n🔍 ESTADÍSTICAS DE LÍNEAS POR ASIENTO:")
        
        # Analizar distribución de líneas
        line_distribution = {}
        total_lines = 0
        
        for entry in JournalEntry.objects.all():
            lines_count = entry.lines.count()
            total_lines += lines_count
            
            if lines_count in line_distribution:
                line_distribution[lines_count] += 1
            else:
                line_distribution[lines_count] = 1
        
        # Mostrar estadísticas
        print(f"   📈 Promedio de líneas por asiento: {total_lines / total_entries:.1f}")
        
        print(f"\n   📊 Distribución de líneas:")
        for lines_count, entries_count in sorted(line_distribution.items()):
            percentage = (entries_count / total_entries) * 100
            print(f"      • {lines_count} líneas: {entries_count} asientos ({percentage:.1f}%)")
        
        # Mostrar ejemplos específicos
        print(f"\n   🔍 EJEMPLOS DE ASIENTOS:")
        sample_entries = JournalEntry.objects.all()[:5]
        
        for entry in sample_entries:
            lines_count = entry.lines.count()
            print(f"\n      📝 Asiento #{entry.number}:")
            print(f"         • Total líneas: {lines_count}")
            print(f"         • Estado: {entry.get_state_display()}")
            print(f"         • Balanceado: {'✅' if entry.is_balanced else '❌'}")
            
            if lines_count > 0:
                for i, line in enumerate(entry.lines.all()[:3], 1):
                    debit_str = f"${line.debit}" if line.debit > 0 else "-"
                    credit_str = f"${line.credit}" if line.credit > 0 else "-"
                    print(f"         {i}. {line.account.code}: D:{debit_str} C:{credit_str}")
                
                if lines_count > 3:
                    print(f"         ... y {lines_count - 3} líneas más")

def evaluate_extra_lines_necessity():
    """
    Evaluar la necesidad de líneas automáticas
    """
    print("\n🤔 3. EVALUACIÓN: ¿ELIMINAR LÍNEAS AUTOMÁTICAS?")
    print("-" * 50)
    
    print("✅ ARGUMENTOS A FAVOR DE ELIMINAR:")
    print("   • CREACIÓN: Usuarios prefieren agregar líneas según necesidad")
    print("   • EDICIÓN: Asiento YA TIENE líneas, no necesita más vacías")
    print("   • INTERFAZ: Menos clutter visual en pantalla")
    print("   • MÓVIL: Menos scroll innecesario")
    print("   • EFICIENCIA: No hay que eliminar líneas no deseadas")
    print("   • PROFESIONALISMO: Interfaz más limpia y precisa")
    
    print("\n❌ ARGUMENTOS EN CONTRA DE ELIMINAR:")
    print("   • CONVENIENCIA: Líneas listas para usar inmediatamente")
    print("   • FLUJO RÁPIDO: Para usuarios que siempre agregan líneas")
    print("   • EXPECTATIVA: Algunos usuarios esperan líneas vacías")
    print("   • CONSISTENCIA: Con otros sistemas contables tradicionales")
    
    print("\n⚖️ ANÁLISIS POR CONTEXTO:")
    
    print("\n🆕 CONTEXTO DE CREACIÓN:")
    print("   • Usuario está CONSTRUYENDO el asiento desde cero")
    print("   • Necesita flexibilidad en número de líneas")
    print("   • Podría necesitar 2, 3, 5 o más líneas")
    print("   • 2 líneas vacías pueden ser útiles como punto de partida")
    print("   • RECOMENDACIÓN: Mantener 2 líneas automáticas")
    
    print("\n✏️ CONTEXTO DE EDICIÓN:")
    print("   • Asiento YA EXISTE con líneas reales")
    print("   • Usuario quiere VER/MODIFICAR líneas existentes")
    print("   • 2 líneas vacías adicionales son innecesarias")
    print("   • Causa scroll innecesario y confusión")
    print("   • RECOMENDACIÓN: Eliminar líneas automáticas (extra = 0)")

def analyze_user_workflow():
    """
    Analizar el flujo de trabajo del usuario
    """
    print("\n👤 4. FLUJO DE TRABAJO DEL USUARIO:")
    print("-" * 50)
    
    print("📝 ESCENARIO ACTUAL EN EDICIÓN:")
    print("   1. Usuario abre asiento existente")
    print("   2. Ve líneas reales del asiento (ej: 3 líneas)")
    print("   3. Ve 2 líneas vacías adicionales (innecesarias)")
    print("   4. Debe hacer scroll para ver toda la información")
    print("   5. Puede confundirse con las líneas vacías")
    print("   6. Si modifica líneas, debe evitar las vacías")
    
    print("\n🎯 ESCENARIO MEJORADO (SIN LÍNEAS AUTOMÁTICAS EN EDICIÓN):")
    print("   1. Usuario abre asiento existente")
    print("   2. Ve SOLO las líneas reales del asiento")
    print("   3. Interfaz limpia y enfocada")
    print("   4. Si necesita agregar línea, usa botón 'Add another'")
    print("   5. Experiencia más profesional y precisa")
    
    print("\n💡 BENEFICIOS DEL FLUJO MEJORADO:")
    print("   • ⚡ Interfaz más limpia en edición")
    print("   • 🎯 Enfoque en datos reales únicamente")
    print("   • 📱 Menos scroll en dispositivos móviles")
    print("   • 🔍 Mejor visión general del asiento")
    print("   • 🚫 Eliminación de elementos confusos")

def compare_with_other_patterns():
    """
    Comparar con otros patrones del sistema
    """
    print("\n🔄 5. COMPARACIÓN CON OTROS MÓDULOS:")
    print("-" * 50)
    
    print("🎯 PATRÓN OBSERVADO EN FACTURAS:")
    print("   • Líneas de factura: Se agregan según necesidad")
    print("   • En edición: Solo muestra líneas existentes")
    print("   • Usuario agrega líneas manualmente si necesita")
    
    print("\n🎯 PATRÓN EN SISTEMAS MODERNOS:")
    print("   • Gmail: No crea correos vacíos automáticamente")
    print("   • Excel: No agrega filas vacías en documentos existentes")
    print("   • Sistemas CRM: Muestran solo registros reales")
    
    print("\n✅ MEJORES PRÁCTICAS UX:")
    print("   • Mostrar solo información relevante")
    print("   • Evitar elementos vacíos que confundan")
    print("   • Permitir agregar elementos bajo demanda")
    print("   • Interfaz limpia y enfocada")

def analyze_technical_implementation():
    """
    Analizar la implementación técnica requerida
    """
    print("\n🛠️ 6. IMPLEMENTACIÓN TÉCNICA:")
    print("-" * 50)
    
    print("✅ OPCIÓN 1 - CONDICIONAL POR CONTEXTO:")
    print("   • Usar extra = 2 en creación")
    print("   • Usar extra = 0 en edición")
    print("   • Implementar método get_extra() dinámico")
    
    print("\n✅ OPCIÓN 2 - ELIMINAR COMPLETAMENTE:")
    print("   • Cambiar extra = 0 siempre")
    print("   • Usuario agrega líneas manualmente")
    print("   • Más consistente y simple")
    
    print("\n🔧 CÓDIGO SUGERIDO (OPCIÓN 1):")
    print("""
    class JournalEntryLineInline(admin.TabularInline):
        model = JournalEntryLine
        fields = ['account', 'description', 'debit', 'credit', 'auxiliary_code']
        
        def get_extra(self, request, obj=None, **kwargs):
            '''Líneas automáticas solo en creación'''
            if obj is None:
                return 2  # Creación: 2 líneas automáticas
            else:
                return 0  # Edición: sin líneas automáticas
    """)
    
    print("\n🔧 CÓDIGO SUGERIDO (OPCIÓN 2 - MÁS SIMPLE):")
    print("""
    class JournalEntryLineInline(admin.TabularInline):
        model = JournalEntryLine
        extra = 0  # Sin líneas automáticas nunca
        fields = ['account', 'description', 'debit', 'credit', 'auxiliary_code']
    """)

def provide_recommendation():
    """
    Proporcionar recomendación final
    """
    print("\n" + "=" * 65)
    print("🎯 RECOMENDACIÓN FINAL")
    print("=" * 65)
    
    print("\n✅ SÍ, ES ALTAMENTE RECOMENDABLE ELIMINAR LAS LÍNEAS AUTOMÁTICAS EN EDICIÓN")
    
    print("\n📊 JUSTIFICACIÓN PRINCIPAL:")
    print("   1. ✅ En EDICIÓN, el asiento YA tiene líneas reales")
    print("   2. ✅ Líneas vacías son innecesarias y confusas")
    print("   3. ✅ Mejora significativa de la experiencia visual")
    print("   4. ✅ Consistencia con principio de interfaz limpia")
    print("   5. ✅ Mejor experiencia móvil (menos scroll)")
    
    print("\n🎯 ESTRATEGIA RECOMENDADA:")
    print("   • OPCIÓN PREFERIDA: Implementar get_extra() condicional")
    print("   • CREACIÓN: extra = 2 (útil para empezar)")
    print("   • EDICIÓN: extra = 0 (interfaz limpia)")
    
    print("\n👥 BENEFICIOS PARA EL USUARIO:")
    print("   • 🎯 Interfaz más limpia en edición")
    print("   • ⚡ Menos elementos visuales innecesarios")
    print("   • 📱 Mejor experiencia móvil")
    print("   • 🔍 Enfoque en datos reales únicamente")
    print("   • ➕ Botón 'Add another' disponible si necesita más líneas")
    
    print("\n🛠️ IMPLEMENTACIÓN SUGERIDA:")
    print("   • Agregar método get_extra() dinámico")
    print("   • Mantener funcionalidad de agregar líneas manualmente")
    print("   • Sin cambios en lógica de negocio")
    
    print("\n⚖️ BALANCE COSTO-BENEFICIO:")
    print("   • Costo: Mínimo (pequeño cambio de método)")
    print("   • Beneficio: Alto (mejor UX + interfaz limpia)")
    print("   • Riesgo: Muy bajo (no afecta funcionalidad)")
    print("   • Impacto: Positivo (experiencia más profesional)")
    
    print("\n🚀 FLUJO RESULTANTE:")
    print("   Crear → 2 líneas automáticas (útil) → Agregar más si necesita")
    print("   Editar → Solo líneas reales (limpio) → Agregar manualmente si necesita")
    print("   ✅ Experiencia optimizada para cada contexto")

def main():
    """
    Función principal del análisis
    """
    try:
        analyze_current_inline_configuration()
        analyze_existing_entries()
        evaluate_extra_lines_necessity()
        analyze_user_workflow()
        compare_with_other_patterns()
        analyze_technical_implementation()
        provide_recommendation()
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()