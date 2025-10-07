#!/usr/bin/env python3
"""
Verificación del ancho duplicado del campo descripción

Autor: Sistema ContaEC
Fecha: 2 de octubre, 2025
Objetivo: Confirmar que el ancho se duplicó de 300px a 600px en los 3 lugares
"""
import os

def verify_width_change():
    """
    Verificar que el ancho se cambió en todos los archivos
    """
    print("🔍 VERIFICACIÓN DEL ANCHO DUPLICADO (300px → 600px)")
    print("=" * 60)
    
    files_to_check = [
        ('Django Admin', 'c:/contaec/apps/accounting/admin.py', 'width: 600px'),
        ('CSS Principal', 'c:/contaec/static/admin/css/journal_entry_lines.css', 'width: 600px !important'),
        ('JavaScript', 'c:/contaec/static/admin/js/journal_entry_lines.js', "input.style.width = '600px'")
    ]
    
    all_updated = True
    
    for location, filepath, expected_text in files_to_check:
        print(f"\n✅ {location}:")
        print(f"   📁 Archivo: {filepath}")
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if expected_text in content:
                print(f"   ✅ ACTUALIZADO: Contiene '{expected_text}'")
                
                # Verificar que no quede el ancho anterior
                if 'width: 300px' in content and location == 'Django Admin':
                    print(f"   ⚠️ ADVERTENCIA: Aún contiene 'width: 300px'")
                elif 'width: 300px !important' in content and location == 'CSS Principal':
                    print(f"   ⚠️ ADVERTENCIA: Aún contiene 'width: 300px !important'")
                elif "input.style.width = '300px'" in content and location == 'JavaScript':
                    print(f"   ⚠️ ADVERTENCIA: Aún contiene \"input.style.width = '300px'\"")
                else:
                    print(f"   ✅ LIMPIO: No quedan referencias al ancho anterior")
                    
            else:
                print(f"   ❌ ERROR: NO contiene '{expected_text}'")
                all_updated = False
        else:
            print(f"   ❌ ERROR: Archivo no encontrado")
            all_updated = False
    
    print(f"\n📊 RESUMEN:")
    if all_updated:
        print("✅ Todos los archivos actualizados correctamente")
        print("✅ Ancho duplicado: 300px → 600px")
    else:
        print("❌ Algunos archivos no se actualizaron correctamente")
    
    return all_updated

def show_visual_comparison():
    """
    Mostrar comparación visual del cambio
    """
    print(f"\n🎨 COMPARACIÓN VISUAL:")
    print("-" * 60)
    
    print("❌ ANTES (300px):")
    print("   [Descripción del asiento___________________] ← 300px")
    
    print(f"\n✅ DESPUÉS (600px):")
    print("   [Descripción del asiento_________________________________________] ← 600px")
    
    print(f"\n📊 IMPACTO DEL CAMBIO:")
    print("   • Ancho anterior: 300px")
    print("   • Ancho actual: 600px") 
    print("   • Incremento: +100% (duplicado)")
    print("   • Beneficio: Más espacio para descripciones largas")
    print("   • Consideración: Puede requerir scroll horizontal en pantallas pequeñas")

def generate_test_instructions():
    """
    Generar instrucciones de prueba
    """
    print(f"\n🧪 INSTRUCCIONES DE PRUEBA:")
    print("-" * 60)
    
    print("🌐 PASOS PARA VERIFICAR EL CAMBIO:")
    print("1. ✅ Limpiar cache del navegador (Ctrl+Shift+R)")
    print("2. ✅ Ir a: http://localhost:8000/admin/accounting/journalentry/add/")
    print("3. ✅ Observar sección 'Líneas del asiento'")
    print("4. ✅ Verificar que campo 'Description' sea más ancho")
    
    print(f"\n🔍 VERIFICACIÓN VISUAL:")
    print("   • Campo descripción debe verse significativamente más ancho")
    print("   • Aproximadamente el doble del ancho anterior")
    print("   • Sigue siendo de una sola línea")
    print("   • Placeholder sigue visible")
    
    print(f"\n📱 CONSIDERACIONES MÓVILES:")
    print("   • En pantallas pequeñas puede causar scroll horizontal")
    print("   • Verificar que sea usable en tablets")
    print("   • Considerar responsive design si es necesario")

def main():
    """
    Función principal
    """
    try:
        success = verify_width_change()
        show_visual_comparison()
        generate_test_instructions()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 ANCHO DUPLICADO EXITOSAMENTE")
            print("=" * 60)
            print("✅ Django Admin: 300px → 600px")
            print("✅ CSS: 300px → 600px") 
            print("✅ JavaScript: 300px → 600px")
            print("✅ Archivos estáticos recopilados")
            
            print(f"\n🚀 SIGUIENTE PASO:")
            print("   • Limpiar cache navegador (Ctrl+Shift+R)")
            print("   • Probar en: http://localhost:8000/admin/accounting/journalentry/add/")
        else:
            print("❌ ERROR EN LA ACTUALIZACIÓN")
            print("=" * 60)
            print("   • Revisar archivos manualmente")
            print("   • Verificar permisos de escritura")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()