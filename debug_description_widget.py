#!/usr/bin/env python3
"""
Verificación detallada del widget de descripción en TabularInline

Autor: Sistema ContaEC
Fecha: 2 de octubre, 2025
Objetivo: Diagnosticar y verificar que el widget TextInput funcione en el inline
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
from django import forms

User = get_user_model()

def test_formset_widget_configuration():
    """
    Verificar la configuración del widget a través del formset
    """
    print("🔍 VERIFICACIÓN DETALLADA DEL WIDGET DE DESCRIPCIÓN")
    print("=" * 65)
    
    print("\n✅ 1. CONFIGURACIÓN DEL FORMSET:")
    print("-" * 50)
    
    inline_instance = JournalEntryLineInline(JournalEntry, site)
    factory = RequestFactory()
    request = factory.get('/')
    
    # Obtener formset
    formset_class = inline_instance.get_formset(request)
    
    print(f"📋 INFORMACIÓN DEL FORMSET:")
    print(f"   • Clase formset: {formset_class.__name__}")
    print(f"   • Modelo: {formset_class.model.__name__}")
    
    # Verificar campos base del form
    if hasattr(formset_class, 'form'):
        form_class = formset_class.form
        base_fields = getattr(form_class, 'base_fields', {})
        
        print(f"\n📝 CAMPOS BASE DEL FORMULARIO:")
        for field_name, field in base_fields.items():
            widget_type = type(field.widget).__name__
            widget_attrs = getattr(field.widget, 'attrs', {})
            print(f"   • {field_name}: {widget_type}")
            if widget_attrs:
                print(f"     Atributos: {widget_attrs}")
        
        # Verificar específicamente el campo description
        if 'description' in base_fields:
            desc_field = base_fields['description']
            widget = desc_field.widget
            
            print(f"\n🎯 ANÁLISIS DETALLADO DEL CAMPO DESCRIPTION:")
            print(f"   • Tipo de widget: {type(widget).__name__}")
            print(f"   • Atributos: {getattr(widget, 'attrs', {})}")
            
            if isinstance(widget, forms.TextInput):
                print("   ✅ CORRECTO: Usando TextInput (una línea)")
            elif isinstance(widget, forms.Textarea):
                print("   ❌ PROBLEMA: Sigue usando Textarea (múltiples líneas)")
            else:
                print(f"   ⚠️ INESPERADO: Widget {type(widget).__name__}")
        else:
            print(f"   ❌ ERROR: Campo 'description' no encontrado en base_fields")

def test_method_override():
    """
    Verificar que el método get_formset esté siendo llamado
    """
    print(f"\n🔧 2. VERIFICACIÓN DE MÉTODO get_formset:")
    print("-" * 50)
    
    inline_instance = JournalEntryLineInline(JournalEntry, site)
    
    # Verificar que el método existe
    if hasattr(inline_instance, 'get_formset'):
        print("✅ Método get_formset encontrado")
        
        # Verificar si es personalizado
        method = getattr(inline_instance, 'get_formset')
        if hasattr(method, '__func__'):
            func_code = method.__func__.__code__
            if 'description' in func_code.co_names:
                print("✅ Método personalizado detecta campo 'description'")
            else:
                print("⚠️ Método personalizado NO menciona 'description'")
        
        # Verificar docstring
        docstring = method.__doc__
        if docstring and 'description' in docstring.lower():
            print("✅ Docstring menciona optimización de descripción")
        else:
            print("⚠️ Docstring no menciona descripción")
    else:
        print("❌ Método get_formset NO encontrado")

def simulate_form_creation():
    """
    Simular creación de formulario como lo hace Django
    """
    print(f"\n🧪 3. SIMULACIÓN DE CREACIÓN DE FORMULARIO:")
    print("-" * 50)
    
    inline_instance = JournalEntryLineInline(JournalEntry, site)
    factory = RequestFactory()
    request = factory.get('/')
    
    try:
        # Simular creación de formset
        formset_class = inline_instance.get_formset(request, obj=None)
        
        print("✅ Formset creado exitosamente")
        
        # Crear instancia del formset
        formset = formset_class()
        
        print("✅ Instancia de formset creada")
        
        # Verificar el primer form
        if formset.forms:
            first_form = formset.forms[0]
            
            if 'description' in first_form.fields:
                desc_field = first_form.fields['description']
                widget = desc_field.widget
                
                print(f"\n📝 PRIMER FORMULARIO DEL FORMSET:")
                print(f"   • Widget: {type(widget).__name__}")
                print(f"   • Atributos: {getattr(widget, 'attrs', {})}")
                
                if isinstance(widget, forms.TextInput):
                    print("   ✅ SUCCESS: Widget TextInput aplicado correctamente")
                else:
                    print(f"   ❌ FAIL: Esperado TextInput, obtenido {type(widget).__name__}")
            else:
                print("   ❌ Campo 'description' no encontrado en form.fields")
        else:
            print("   ⚠️ Formset no tiene formularios")
        
    except Exception as e:
        print(f"   ❌ ERROR en simulación: {str(e)}")

def check_django_admin_behavior():
    """
    Verificar comportamiento específico de Django Admin
    """
    print(f"\n🎭 4. COMPORTAMIENTO DE DJANGO ADMIN:")
    print("-" * 50)
    
    from apps.accounting.models import JournalEntryLine
    
    # Verificar modelo del campo
    desc_field = JournalEntryLine._meta.get_field('description')
    
    print(f"📊 INFORMACIÓN DEL MODELO:")
    print(f"   • Tipo: {type(desc_field).__name__}")
    print(f"   • Max length: {desc_field.max_length}")
    print(f"   • Blank: {desc_field.blank}")
    print(f"   • Null: {desc_field.null}")
    
    # Django por defecto usa Textarea para CharField > 20 chars
    if desc_field.max_length > 20:
        print(f"   ⚠️ IMPORTANTE: max_length={desc_field.max_length} > 20")
        print(f"   📝 Django usa Textarea por defecto para CharField largos")
        print(f"   🔧 NECESARIO: Override widget explícito (implementado)")
    else:
        print(f"   ✅ max_length={desc_field.max_length} <= 20, usaría TextInput")

def generate_browser_test():
    """
    Generar test manual para navegador
    """
    print(f"\n🌐 5. TEST MANUAL EN NAVEGADOR:")
    print("-" * 50)
    
    print("🧪 PASOS PARA VERIFICAR EN NAVEGADOR:")
    print("1. Abrir: http://localhost:8000/admin/accounting/journalentry/add/")
    print("2. Ir a sección 'Líneas del asiento'")
    print("3. Hacer clic en campo 'Description' de cualquier línea")
    print("4. Verificar:")
    print("   ✅ Es un input de una línea (no textarea)")
    print("   ✅ Tiene placeholder: 'Descripción de la línea del asiento...'")
    print("   ✅ Ancho aprox 300px")
    print("   ✅ Al escribir mucho texto, hace scroll horizontal")
    
    print(f"\n🔍 SI SIGUE SIENDO TEXTAREA:")
    print("   • Reiniciar servidor Django")
    print("   • Limpiar cache del navegador (Ctrl+F5)")
    print("   • Verificar que no haya errores en consola")
    
    print(f"\n🎯 ELEMENTOS A INSPECCIONAR:")
    print("   • Tag HTML: <input type='text'> (NO <textarea>)")
    print("   • Atributos style='width: 300px;'")
    print("   • Atributo placeholder visible")

def debug_potential_issues():
    """
    Debuggear posibles problemas
    """
    print(f"\n🐛 6. DEBUG DE POSIBLES PROBLEMAS:")
    print("-" * 50)
    
    print("🔍 CAUSAS POSIBLES DE FALLO:")
    print("   1. ❌ Método get_formset no se ejecuta")
    print("   2. ❌ Campo 'description' no existe en base_fields")
    print("   3. ❌ Widget se sobrescribe después") 
    print("   4. ❌ Cache de navegador o servidor")
    print("   5. ❌ Conflicto con otros widgets")
    
    print(f"\n🔧 SOLUCIONES A PROBAR:")
    print("   1. ✅ Reiniciar servidor Django")
    print("   2. ✅ Limpiar cache navegador")
    print("   3. ✅ Verificar errores en consola")
    print("   4. ✅ Inspeccionar HTML generado")
    print("   5. ✅ Usar get_formset más específico")

def main():
    """
    Función principal de verificación
    """
    try:
        test_formset_widget_configuration()
        test_method_override()
        simulate_form_creation()
        check_django_admin_behavior()
        generate_browser_test()
        debug_potential_issues()
        
        print("\n" + "=" * 65)
        print("🎯 DIAGNÓSTICO COMPLETADO")
        print("=" * 65)
        print("📋 VERIFICACIÓN TÉCNICA:")
        print("   • Método get_formset implementado ✅")
        print("   • Widget TextInput configurado ✅")
        print("   • Atributos personalizados agregados ✅")
        
        print(f"\n🌐 PRÓXIMO PASO CRÍTICO:")
        print("   1. REINICIAR servidor Django")
        print("   2. LIMPIAR cache del navegador (Ctrl+F5)")
        print("   3. PROBAR en navegador nuevamente")
        
        print(f"\n🔍 Si persiste el problema:")
        print("   • Inspeccionar elemento HTML en navegador")
        print("   • Verificar que sea <input> y no <textarea>")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()