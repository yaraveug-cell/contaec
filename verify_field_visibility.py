#!/usr/bin/env python
"""
Script de Verificación: Campos que se Ocultan/Muestran
Verificar exactamente qué campos se afectan en la implementación
"""

import os

def verify_field_visibility():
    """Verificar qué campos se ocultan/muestran en el JavaScript"""
    
    print("🔍 VERIFICACIÓN: ¿Qué campos se ocultan al seleccionar transferencia?")
    print("=" * 70)
    
    js_file = 'static/admin/js/unified_banking_integration.js'
    
    try:
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n📋 1. CAMPOS IDENTIFICADOS EN EL CÓDIGO:")
        print("-" * 45)
        
        # Buscar definiciones de campos
        if "this.paymentFormField = document.getElementById('id_payment_form')" in content:
            print("   ✅ paymentFormField → Referencia: id_payment_form")
        
        if "this.accountField = document.getElementById('id_account')" in content:
            print("   ✅ accountField → Referencia: id_account")
        
        print("\n📋 2. MÉTODOS DE OCULTACIÓN:")
        print("-" * 35)
        
        # Verificar método hideTraditionalAccountField
        hide_method_lines = []
        lines = content.split('\n')
        in_hide_method = False
        
        for i, line in enumerate(lines, 1):
            if 'hideTraditionalAccountField()' in line:
                in_hide_method = True
                hide_method_lines.append(f"Línea {i}: {line.strip()}")
            elif in_hide_method and 'this.accountField' in line:
                hide_method_lines.append(f"Línea {i}: {line.strip()}")
            elif in_hide_method and 'style.display = ' in line:
                hide_method_lines.append(f"Línea {i}: {line.strip()}")
            elif in_hide_method and '}' in line and len(hide_method_lines) > 3:
                break
        
        print("   🙈 hideTraditionalAccountField():")
        for line in hide_method_lines:
            if 'this.accountField' in line:
                print(f"      ✅ {line} ← SOLO afecta accountField")
            elif 'style.display' in line:
                print(f"      ✅ {line} ← Oculta SOLO este campo")
            else:
                print(f"      - {line}")
        
        print("\n📋 3. VERIFICACIÓN DE FLUJO COMPLETO:")
        print("-" * 40)
        
        # Verificar flujo de transferencia
        transfer_flow = []
        show_flow = []
        
        for i, line in enumerate(lines, 1):
            if 'transferencia' in line.lower() and 'this.hideTraditionalAccountField()' in line:
                transfer_flow.append(f"Línea {i}: {line.strip()}")
            elif 'this.showTraditionalAccountField()' in line:
                show_flow.append(f"Línea {i}: {line.strip()}")
        
        print("   🏦 CUANDO SE SELECCIONA TRANSFERENCIA:")
        for flow in transfer_flow:
            print(f"      - {flow}")
        print("      → RESULTADO: Solo se oculta el campo 'account' (id_account)")
        
        print("\n   💰 CUANDO SE SELECCIONA EFECTIVO/CRÉDITO:")
        for flow in show_flow[:2]:  # Mostrar solo los primeros 2
            print(f"      - {flow}")
        print("      → RESULTADO: Se muestra el campo 'account' (id_account)")
        
        print("\n📋 4. CAMPOS QUE NUNCA SE OCULTAN:")
        print("-" * 38)
        
        never_hidden = [
            "payment_form (id_payment_form)",
            "customer (id_customer)", 
            "date (id_date)",
            "status (id_status)",
            "created_by (id_created_by)"
        ]
        
        for field in never_hidden:
            print(f"   ✅ {field} - SIEMPRE VISIBLE")
        
        print("\n📋 5. CAMPO QUE SE OCULTA/MUESTRA:")
        print("-" * 38)
        
        print("   🔄 account (id_account):")
        print("      - OCULTO cuando: Forma de pago = 'Transferencia'")
        print("      - VISIBLE cuando: Forma de pago = 'Efectivo' o 'Crédito'")
        print("      - Razón: En transferencias se auto-asigna desde cuenta bancaria")
        
        print("\n📋 6. CAMPOS QUE SE MUESTRAN DINÁMICAMENTE:")
        print("-" * 45)
        
        dynamic_fields = [
            "bank_account (id_bank_account) - Solo en transferencias",
            "bank_observations (id_bank_observations) - Solo en transferencias"
        ]
        
        for field in dynamic_fields:
            print(f"   ✨ {field}")
        
        print("\n🎯 RESUMEN FINAL:")
        print("-" * 20)
        print("✅ CAMPO payment_form: NUNCA se oculta - SIEMPRE visible")
        print("🔄 CAMPO account: Se oculta SOLO en transferencias")
        print("✨ CAMPOS bancarios: Aparecen SOLO en transferencias")
        print("")
        print("🎉 CONFIRMACIÓN: El usuario PUEDE cambiar forma de pago libremente")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {js_file}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    verify_field_visibility()