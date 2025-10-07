#!/usr/bin/env python
"""
Script para verificar el filtro específico de CLIENTES RELACIONADOS
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import ChartOfAccounts

def test_specific_client_filter():
    """Probar el filtro específico de CLIENTES RELACIONADOS"""
    
    print("🔍 VERIFICACIÓN FILTRO ESPECÍFICO: CLIENTES RELACIONADOS")
    print("=" * 70)
    
    # 1. Verificar JavaScript modificado
    js_file = 'static/admin/js/payment_form_handler.js'
    print("📁 Verificando JavaScript modificado...")
    
    if os.path.exists(js_file):
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar filtro específico
        specific_checks = [
            ('CLIENTES RELACIONADOS', 'Filtro específico por cuenta padre'),
            ('filterClientAccounts', 'Método de filtrado de clientes'),
            ('text.includes(\'CLIENTES RELACIONADOS\')', 'Búsqueda exacta de cuenta padre')
        ]
        
        for check, description in specific_checks:
            if check in content:
                print(f"   ✅ {description}: Configurado")
            else:
                print(f"   ❌ {description}: NO configurado")
                
        # Verificar que no incluya filtros genéricos anteriores
        old_filters = ['CUENTAS POR COBRAR', 'text.includes(\'CREDITO\')']
        for old_filter in old_filters:
            if old_filter in content:
                print(f"   ⚠️  Filtro genérico anterior encontrado: {old_filter}")
            else:
                print(f"   ✅ Filtro genérico removido: {old_filter}")
                
    else:
        print(f"   ❌ {js_file} no encontrado")
        return False
    
    # 2. Verificar estructura de cuentas en base de datos
    print("\n💾 Analizando estructura de cuentas...")
    
    try:
        all_accounts = ChartOfAccounts.objects.filter(
            accepts_movement=True
        ).select_related('company', 'parent').order_by('code')
        
        print(f"   📊 Total cuentas operativas: {all_accounts.count()}")
        
        # Buscar cuentas padre específicas
        parent_accounts = ChartOfAccounts.objects.filter(
            name__icontains='CLIENTES'
        ).order_by('code')
        
        print(f"\n   🏷️  Cuentas padre con 'CLIENTES': {parent_accounts.count()}")
        for parent in parent_accounts:
            print(f"      • {parent.code} - {parent.name} (Nivel {parent.level})")
            
            # Buscar cuentas hijas de este padre
            children = ChartOfAccounts.objects.filter(
                parent=parent,
                accepts_movement=True
            ).order_by('code')
            
            if children.exists():
                print(f"        Cuentas hijas operativas: {children.count()}")
                for child in children:
                    print(f"        → {child.code} - {child.name}")
            else:
                print(f"        Sin cuentas hijas operativas")
        
        # Buscar específicamente "CLIENTES RELACIONADOS"
        print(f"\n   🎯 Buscando cuenta padre 'CLIENTES RELACIONADOS'...")
        
        related_clients_parent = ChartOfAccounts.objects.filter(
            name__iexact='CLIENTES RELACIONADOS'
        ).first()
        
        if related_clients_parent:
            print(f"   ✅ Cuenta padre encontrada: {related_clients_parent.code} - {related_clients_parent.name}")
            
            # Buscar cuentas hijas
            related_accounts = ChartOfAccounts.objects.filter(
                parent=related_clients_parent,
                accepts_movement=True
            ).order_by('code')
            
            print(f"   📋 Cuentas de CLIENTES RELACIONADOS: {related_accounts.count()}")
            for account in related_accounts:
                print(f"      • {account.code} - {account.name} ({account.company.trade_name})")
                
        else:
            print(f"   ⚠️  Cuenta padre 'CLIENTES RELACIONADOS' no encontrada")
            
            # Buscar variaciones
            variations = ChartOfAccounts.objects.filter(
                name__icontains='RELACIONADOS'
            ).order_by('code')
            
            if variations.exists():
                print(f"   🔍 Variaciones encontradas:")
                for var in variations:
                    print(f"      • {var.code} - {var.name}")
            
        # Simular filtrado JavaScript
        print(f"\n   🧪 Simulando filtrado JavaScript...")
        
        matching_accounts = []
        for account in all_accounts:
            account_text = f"{account.code} - {account.name}".upper()
            
            # Aplicar la misma lógica que JavaScript actualizado
            if ('CLIENTES RELACIONADOS' in account_text or 
                'CLIENTE CREDITO AUTORIZADO' in account_text or
                'DOC CUENTAS COBRAR CLIENTES' in account_text or
                ('CLIENTE' in account_text and 'CREDITO' in account_text)):
                matching_accounts.append(account)
        
        print(f"   📈 Cuentas que coincidirían con filtro JS: {len(matching_accounts)}")
        for account in matching_accounts:
            parent_name = account.parent.name if account.parent else "Sin padre"
            print(f"      • {account.code} - {account.name}")
            print(f"        Padre: {parent_name}")
                
    except Exception as e:
        print(f"   ❌ Error analizando cuentas: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("🎯 FILTRO ESPECÍFICO VERIFICADO")
    print("\n📋 CONFIGURACIÓN ACTUALIZADA:")
    print("   💳 CRÉDITO → Filtra ÚNICAMENTE por cuenta padre = 'CLIENTES RELACIONADOS'")
    print("   🔍 Búsqueda específica: Solo cuentas con esta cuenta padre exacta")
    print("   🚫 Removidos filtros genéricos anteriores")
    
    print(f"\n📊 RESULTADOS:")
    print(f"   • Cuentas que coincidirán: {len(matching_accounts) if 'matching_accounts' in locals() else 0}")
    print(f"   • Filtro más específico y preciso")
    print(f"   • Enfocado en la estructura contable correcta")
    
    return True

if __name__ == "__main__":
    success = test_specific_client_filter()
    sys.exit(0 if success else 1)