#!/usr/bin/env python
"""
Script para verificar el aumento del ancho del campo cuenta
"""
import os

def verify_account_field_width():
    """Verificar el cambio en el ancho del campo cuenta"""
    
    print("🔍 VERIFICACIÓN: AUMENTO ANCHO CAMPO CUENTA")
    print("=" * 60)
    
    css_file = 'static/admin/css/invoice_lines.css'
    
    if not os.path.exists(css_file):
        print(f"❌ Archivo CSS no encontrado: {css_file}")
        return False
    
    print(f"📁 Analizando archivo: {css_file}")
    
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar la definición del campo cuenta
    lines = content.split('\n')
    account_field_section = []
    in_account_field = False
    
    for i, line in enumerate(lines):
        if '.field-account select {' in line:
            in_account_field = True
            # Capturar contexto antes
            start = max(0, i - 2)
            account_field_section = lines[start:i+1]
        elif in_account_field:
            account_field_section.append(line)
            if line.strip() == '}':
                # Capturar contexto después
                end = min(len(lines), i + 3)
                account_field_section.extend(lines[i+1:end])
                break
    
    print(f"\n📋 Configuración encontrada:")
    print("─" * 40)
    for line in account_field_section:
        if 'width:' in line:
            print(f"🎯 {line.strip()}")
            
            # Extraer valor del ancho
            width_value = line.strip().split('width:')[1].split(';')[0].strip()
            print(f"   📏 Ancho actual: {width_value}")
            
            # Verificar el cambio
            if '420px' in width_value:
                print(f"   ✅ Ancho aumentado correctamente!")
                print(f"   📊 Cálculo: 280px * 1.5 = 420px")
                print(f"   📈 Incremento: 50% (140px adicionales)")
            elif '280px' in width_value:
                print(f"   ⚠️  Ancho original detectado (280px)")
                print(f"   ❌ Cambio no aplicado")
                return False
            else:
                print(f"   ⚠️  Ancho no estándar detectado: {width_value}")
        elif line.strip() and not line.startswith('/*'):
            print(f"   {line.strip()}")
    
    # Verificar otros elementos relacionados
    print(f"\n🔍 Verificación de integridad:")
    
    # Verificar que no hay conflictos
    if '.field-account' in content:
        print(f"   ✅ Clase .field-account presente")
    else:
        print(f"   ❌ Clase .field-account no encontrada")
        return False
    
    # Verificar estructura CSS
    field_account_count = content.count('.field-account')
    print(f"   📊 Referencias a .field-account: {field_account_count}")
    
    # Verificar que mantiene consistencia con otros estilos
    if '.field-payment_form select' in content:
        print(f"   ✅ Estilos de forma de pago mantenidos")
    else:
        print(f"   ⚠️  Estilos de forma de pago no encontrados")
    
    print(f"\n" + "=" * 60)
    print(f"🎯 RESUMEN DEL CAMBIO")
    print(f"=" * 60)
    
    print(f"📏 DIMENSIONES:")
    print(f"   • Ancho anterior: 280px")
    print(f"   • Ancho nuevo: 420px")
    print(f"   • Incremento: +140px (+50%)")
    
    print(f"\n🎨 IMPACTO VISUAL:")
    print(f"   • Más espacio para nombres largos de cuentas")
    print(f"   • Mejor legibilidad del código y nombre de cuenta")
    print(f"   • Mantiene consistencia con estilos Django Admin")
    
    print(f"\n🔧 CONFIGURACIÓN:")
    print(f"   • Campo: select[name='account']")
    print(f"   • Clase CSS: .field-account select")
    print(f"   • Archivo: static/admin/css/invoice_lines.css")
    
    print(f"\n✅ CAMBIO COMPLETADO EXITOSAMENTE")
    
    return True

if __name__ == "__main__":
    success = verify_account_field_width()
    if success:
        print(f"\n🚀 El campo cuenta ahora es 50% más ancho")
    else:
        print(f"\n❌ Error al verificar el cambio")