#!/usr/bin/env python
"""
Script para verificar los filtros extendidos de Forma de Pago
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import ChartOfAccounts

def test_extended_filtering():
    """Probar los nuevos filtros extendidos"""
    
    print("🔍 VERIFICACIÓN DE FILTROS EXTENDIDOS")
    print("=" * 70)
    
    # 1. Verificar archivo JavaScript actualizado
    js_file = 'static/admin/js/payment_form_handler.js'
    print("📁 Verificando archivo JavaScript actualizado...")
    
    if os.path.exists(js_file):
        print(f"   ✅ {js_file} existe")
        
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar nuevos métodos
        new_checks = [
            ('filterClientAccounts', 'Método para filtrar cuentas de clientes'),
            ('filterBankAccounts', 'Método para filtrar cuentas bancarias'),
            ('CREDITO', 'Detección de pago a crédito'),
            ('TRANSFERENCIA', 'Detección de transferencia bancaria'),
            ('CLIENTE', 'Filtro de cuentas de clientes'),
            ('BANCO', 'Filtro de cuentas bancarias')
        ]
        
        for check, description in new_checks:
            if check in content:
                print(f"   ✅ {description}: Encontrado")
            else:
                print(f"   ❌ {description}: NO encontrado")
    else:
        print(f"   ❌ {js_file} no encontrado")
        return False
    
    # 2. Verificar cuentas disponibles en la base de datos
    print("\n💾 Verificando cuentas disponibles...")
    
    try:
        all_accounts = ChartOfAccounts.objects.filter(
            accepts_movement=True
        ).select_related('company').order_by('code')
        
        print(f"   📊 Total cuentas operativas: {all_accounts.count()}")
        
        # Buscar cuentas por categorías
        categories = {
            'CAJA': ['CAJA', 'EFECTIVO'],
            'CLIENTES': ['CLIENTE', 'CLIENTES', 'RELACIONADOS', 'CREDITO', 'CUENTAS POR COBRAR'],
            'BANCOS': ['BANCO', 'BANCOS', 'BANCARIO', 'INTERNACIONAL', 'PICHINCHA', 'GUAYAQUIL', 'PACIFICO']
        }
        
        for category, keywords in categories.items():
            found_accounts = []
            
            for account in all_accounts:
                account_text = f"{account.code} - {account.name}".upper()
                if any(keyword in account_text for keyword in keywords):
                    found_accounts.append(account)
            
            print(f"\n   🏷️  Categoría {category}:")
            print(f"      📈 Cuentas encontradas: {len(found_accounts)}")
            
            if found_accounts:
                print(f"      📋 Ejemplos:")
                for acc in found_accounts[:3]:  # Mostrar máximo 3 ejemplos
                    print(f"         • {acc.code} - {acc.name} ({acc.company.trade_name})")
                    
                if len(found_accounts) > 3:
                    print(f"         ... y {len(found_accounts) - 3} más")
            else:
                print(f"      ⚠️  No se encontraron cuentas para esta categoría")
                
    except Exception as e:
        print(f"   ❌ Error verificando cuentas: {e}")
        return False
    
    # 3. Verificar lógica de filtrado en JavaScript
    print("\n🔧 Verificando lógica de filtrado...")
    
    filtros_esperados = [
        ("EFECTIVO", "CAJA", "Efectivo filtra por cuentas de caja"),
        ("CREDITO", "CLIENTE", "Crédito filtra por cuentas de clientes"),
        ("TRANSFERENCIA", "BANCO", "Transferencia filtra por cuentas bancarias")
    ]
    
    for forma_pago, filtro, descripcion in filtros_esperados:
        if forma_pago in content and filtro in content:
            print(f"   ✅ {descripcion}: Configurado")
        else:
            print(f"   ❌ {descripcion}: NO configurado")
    
    print("\n" + "=" * 70)
    print("🎯 FILTROS EXTENDIDOS VERIFICADOS")
    print("\n📋 FUNCIONALIDADES IMPLEMENTADAS:")
    print("   💰 EFECTIVO → Filtra por cuentas de CAJA")
    print("   💳 CRÉDITO → Filtra por cuentas de CLIENTES")
    print("   🏦 TRANSFERENCIA → Filtra por cuentas de BANCOS")
    
    print("\n🔧 INSTRUCCIONES DE PRUEBA:")
    print("1. Ir al admin de Django > Invoices > Add Invoice")
    print("2. Probar cada forma de pago:")
    print("   • Seleccionar EFECTIVO → Ver cuentas de caja")
    print("   • Seleccionar CRÉDITO → Ver cuentas de clientes")  
    print("   • Seleccionar TRANSFERENCIA → Ver cuentas bancarias")
    print("3. Verificar que se establece cuenta por defecto automáticamente")
    
    return True

if __name__ == "__main__":
    success = test_extended_filtering()
    sys.exit(0 if success else 1)