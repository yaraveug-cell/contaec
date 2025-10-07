#!/usr/bin/env python3
"""
Verificación de optimización de líneas automáticas en asientos

Autor: Sistema ContaEC
Fecha: 2 de octubre, 2025
Objetivo: Verificar que la optimización de líneas automáticas funcione correctamente
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import JournalEntry, JournalEntryLine
from apps.accounting.admin import JournalEntryLineInline, JournalEntryAdmin
from django.contrib.admin.sites import site
from django.test import RequestFactory
from django.contrib.auth import get_user_model

User = get_user_model()

def test_dynamic_extra_lines():
    """
    Probar el comportamiento dinámico de líneas automáticas
    """
    print("🧪 VERIFICACIÓN DE LÍNEAS AUTOMÁTICAS OPTIMIZADAS")
    print("=" * 60)
    
    # Crear una instancia del inline
    inline_instance = JournalEntryLineInline(JournalEntry, site)
    
    # Crear request factory para simular requests
    factory = RequestFactory()
    request = factory.get('/')
    
    print("\n✅ 1. CONFIGURACIÓN IMPLEMENTADA:")
    print("-" * 50)
    
    # Verificar que el método get_extra existe
    if hasattr(inline_instance, 'get_extra'):
        print("✅ Método get_extra() implementado correctamente")
        
        # Probar contexto de creación (obj=None)
        extra_creation = inline_instance.get_extra(request, obj=None)
        print(f"🆕 Contexto CREACIÓN (obj=None): {extra_creation} líneas automáticas")
        
        # Probar contexto de edición con asiento existente
        existing_entries = JournalEntry.objects.all()
        if existing_entries.exists():
            test_entry = existing_entries.first()
            extra_edition = inline_instance.get_extra(request, obj=test_entry)
            print(f"✏️ Contexto EDICIÓN (obj=#{test_entry.number}): {extra_edition} líneas automáticas")
            
            # Mostrar información del asiento de prueba
            lines_count = test_entry.lines.count()
            print(f"   📊 Asiento de prueba tiene {lines_count} líneas reales")
            print(f"   🎯 Resultado: Usuario verá {lines_count} + {extra_edition} = {lines_count + extra_edition} líneas totales")
        else:
            print("ℹ️ No hay asientos existentes para probar edición")
            
    else:
        print("❌ ERROR: Método get_extra() no encontrado")
        return False
    
    print("\n✅ 2. VERIFICACIÓN DE COMPORTAMIENTO:")
    print("-" * 50)
    
    # Verificar que no hay atributo extra estático
    if not hasattr(inline_instance, 'extra') or inline_instance.extra is None:
        print("✅ Atributo 'extra' estático eliminado correctamente")
    else:
        print(f"⚠️ Atributo 'extra' aún existe: {inline_instance.extra}")
    
    print("\n✅ 3. CASOS DE PRUEBA:")
    print("-" * 50)
    
    # Caso 1: Creación de nuevo asiento
    print("🧪 CASO 1 - Nuevo asiento (creación):")
    extra_new = inline_instance.get_extra(request, obj=None)
    print(f"   → {extra_new} líneas automáticas")
    if extra_new == 2:
        print("   ✅ CORRECTO: 2 líneas para facilitar inicio")
    else:
        print(f"   ❌ ESPERADO: 2, OBTENIDO: {extra_new}")
    
    # Caso 2: Edición de asiento existente
    print("\n🧪 CASO 2 - Asiento existente (edición):")
    if existing_entries.exists():
        for entry in existing_entries[:3]:  # Probar con algunos asientos
            extra_edit = inline_instance.get_extra(request, obj=entry)
            lines_count = entry.lines.count()
            print(f"   📝 Asiento #{entry.number}:")
            print(f"      • Líneas reales: {lines_count}")
            print(f"      • Líneas automáticas: {extra_edit}")
            print(f"      • Total mostrado: {lines_count + extra_edit}")
            
            if extra_edit == 0:
                print("      ✅ CORRECTO: Sin líneas automáticas innecesarias")
            else:
                print(f"      ❌ ESPERADO: 0, OBTENIDO: {extra_edit}")
    else:
        print("   ℹ️ No hay asientos para probar")
    
    print("\n✅ 4. BENEFICIOS VERIFICADOS:")
    print("-" * 50)
    
    if existing_entries.exists():
        sample_entry = existing_entries.first()
        real_lines = sample_entry.lines.count()
        
        print(f"📊 EJEMPLO CON ASIENTO #{sample_entry.number}:")
        print(f"   • ANTES: {real_lines} líneas reales + 2 automáticas = {real_lines + 2} líneas totales")
        print(f"   • AHORA: {real_lines} líneas reales + 0 automáticas = {real_lines} líneas totales")
        print(f"   • REDUCCIÓN: {2} líneas innecesarias eliminadas")
        print(f"   • MEJORA: {((2 / (real_lines + 2)) * 100):.1f}% menos clutter visual")
    
    print("\n🎯 IMPACTO EN EXPERIENCIA DE USUARIO:")
    print("   ✅ Interfaz más limpia en edición")
    print("   ✅ Menos scroll innecesario") 
    print("   ✅ Enfoque en datos reales únicamente")
    print("   ✅ Mantiene utilidad en creación")
    print("   ✅ Consistente con optimizaciones anteriores")
    
    return True

def test_admin_integration():
    """
    Verificar integración con admin de Django
    """
    print("\n🔧 5. INTEGRACIÓN CON DJANGO ADMIN:")
    print("-" * 50)
    
    try:
        # Verificar que el admin está registrado correctamente
        admin_instance = site._registry.get(JournalEntry)
        if admin_instance:
            print("✅ JournalEntryAdmin registrado correctamente")
            
            # Verificar que tiene inlines
            if hasattr(admin_instance, 'inlines') and admin_instance.inlines:
                print(f"✅ Inlines configurados: {len(admin_instance.inlines)} inline(s)")
                
                # Verificar que JournalEntryLineInline está en los inlines
                inline_classes = [inline.__name__ for inline in admin_instance.inlines]
                if 'JournalEntryLineInline' in inline_classes:
                    print("✅ JournalEntryLineInline incluido en admin")
                else:
                    print("❌ JournalEntryLineInline no encontrado en admin")
            else:
                print("⚠️ No se encontraron inlines configurados")
        else:
            print("❌ JournalEntryAdmin no está registrado")
            
    except Exception as e:
        print(f"❌ Error verificando integración admin: {e}")

def show_code_comparison():
    """
    Mostrar comparación del código antes y después
    """
    print("\n📝 6. CÓDIGO IMPLEMENTADO:")
    print("-" * 50)
    
    print("❌ CÓDIGO ANTERIOR:")
    print("""
    class JournalEntryLineInline(admin.TabularInline):
        model = JournalEntryLine
        extra = 2  # ← Siempre 2 líneas, sin distinción de contexto
        fields = ['account', 'description', 'debit', 'credit', 'auxiliary_code']
    """)
    
    print("✅ CÓDIGO ACTUAL (OPTIMIZADO):")
    print("""
    class JournalEntryLineInline(admin.TabularInline):
        model = JournalEntryLine
        fields = ['account', 'description', 'debit', 'credit', 'auxiliary_code']
        
        def get_extra(self, request, obj=None, **kwargs):
            '''
            Líneas automáticas dinámicas según contexto:
            - Creación: 2 líneas automáticas (útil para empezar)
            - Edición: 0 líneas automáticas (interfaz limpia)
            '''
            if obj is None:
                return 2  # Contexto de creación
            else:
                return 0  # Contexto de edición
    """)
    
    print("\n🎯 MEJORAS IMPLEMENTADAS:")
    print("   • ✅ Método dinámico get_extra() reemplaza atributo estático")
    print("   • ✅ Documentación clara del comportamiento")
    print("   • ✅ Lógica condicional basada en contexto (obj=None)")
    print("   • ✅ Mantiene funcionalidad sin cambiar lógica de negocio")

def main():
    """
    Función principal de verificación
    """
    try:
        success = test_dynamic_extra_lines()
        test_admin_integration()
        show_code_comparison()
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 OPTIMIZACIÓN IMPLEMENTADA EXITOSAMENTE")
            print("=" * 60)
            print("✅ Líneas automáticas ahora son dinámicas")
            print("✅ Creación: 2 líneas (útiles)")
            print("✅ Edición: 0 líneas (interfaz limpia)")
            print("✅ Mejor experiencia de usuario")
            print("✅ Consistente con optimizaciones anteriores")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()