#!/usr/bin/env python3
"""
Script para debuggear el problema del filtrado y verificar las cuentas hijas
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def debug_filtering_problem():
    """Debuggear el problema específico del filtrado"""
    print("🔍 DEBUGGING DEL PROBLEMA DE FILTRADO")
    print("=" * 60)
    
    from apps.companies.models import Company, PaymentMethod
    from apps.accounting.models import ChartOfAccounts
    
    # Verificar GUEBER específicamente
    try:
        gueber = Company.objects.get(trade_name__icontains="GUEBER")
        print(f"🏢 Empresa: {gueber.trade_name}")
        
        if gueber.payment_method:
            print(f"💳 Método de pago configurado: {gueber.payment_method.name}")
            print(f"📋 Cuenta padre: {gueber.payment_method.parent_account}")
        else:
            print("❌ No hay método de pago configurado")
            
        print("\n📊 TODOS LOS MÉTODOS DE PAGO DISPONIBLES:")
        all_methods = PaymentMethod.objects.filter(is_active=True)
        for method in all_methods:
            print(f"   - {method.name} (ID: {method.id})")
            if method.parent_account:
                parent = method.parent_account
                print(f"     └ Cuenta Padre: {parent.code} - {parent.name}")
                
                # Buscar cuentas hijas para esta empresa
                children = ChartOfAccounts.objects.filter(
                    company=gueber,
                    code__startswith=parent.code,
                    level=parent.level + 1,
                    accepts_movement=True
                ).order_by('code')
                
                print(f"     └ Cuentas hijas para {gueber.trade_name}: {children.count()}")
                for child in children:
                    print(f"       • {child.code} - {child.name}")
                
                # También buscar por patrón diferente si no hay resultados
                if children.count() == 0:
                    print("     🔍 Buscando con criterios alternativos...")
                    
                    # Buscar cuentas que empiecen con el mismo patrón
                    alt_children1 = ChartOfAccounts.objects.filter(
                        company=gueber,
                        code__startswith=parent.code[:4],  # Primeros 4 caracteres
                        accepts_movement=True
                    ).exclude(id=parent.id).order_by('code')
                    
                    print(f"     └ Por patrón {parent.code[:4]}*: {alt_children1.count()}")
                    for child in alt_children1[:5]:
                        print(f"       • {child.code} - {child.name}")
                
        print("\n🔍 TODAS LAS CUENTAS DE GUEBER:")
        all_accounts = ChartOfAccounts.objects.filter(
            company=gueber,
            accepts_movement=True
        ).order_by('code')
        
        print(f"Total cuentas que aceptan movimiento: {all_accounts.count()}")
        for account in all_accounts:
            print(f"   - {account.code} - {account.name} (Nivel {account.level})")
            
        # Buscar específicamente "Caja General"
        print("\n🎯 BUSCANDO 'CAJA GENERAL':")
        caja_general = ChartOfAccounts.objects.filter(
            company=gueber,
            name__icontains="caja",
            accepts_movement=True
        )
        
        for caja in caja_general:
            print(f"   ✅ Encontrada: {caja.code} - {caja.name} (Nivel {caja.level})")
            
        # Buscar método de pago "Efectivo"
        print("\n💰 VERIFICANDO MÉTODO 'EFECTIVO':")
        try:
            efectivo = PaymentMethod.objects.get(name__icontains="efectivo", is_active=True)
            print(f"   ✅ Método Efectivo encontrado: {efectivo.name}")
            if efectivo.parent_account:
                parent = efectivo.parent_account
                print(f"   📋 Cuenta padre del efectivo: {parent.code} - {parent.name}")
                
                # Buscar cuentas hijas del efectivo para GUEBER
                efectivo_children = ChartOfAccounts.objects.filter(
                    company=gueber,
                    code__startswith=parent.code,
                    level=parent.level + 1,
                    accepts_movement=True
                ).order_by('code')
                
                print(f"   🎯 Cuentas hijas del efectivo para GUEBER: {efectivo_children.count()}")
                for child in efectivo_children:
                    print(f"      • {child.code} - {child.name}")
                    
                # Si no hay cuentas hijas directas, buscar alternativas
                if efectivo_children.count() == 0:
                    print("   🔍 Buscando alternativas...")
                    alt_caja = ChartOfAccounts.objects.filter(
                        company=gueber,
                        name__icontains="caja",
                        accepts_movement=True
                    ).order_by('code')
                    
                    print(f"   🏦 Cuentas que contienen 'caja': {alt_caja.count()}")
                    for caja in alt_caja:
                        print(f"      • {caja.code} - {caja.name}")
                        # Verificar si podría ser hija del efectivo
                        if caja.code.startswith(parent.code[:4]):
                            print(f"        └ ✅ Podría ser hija de {parent.name}")
                            
        except PaymentMethod.DoesNotExist:
            print("   ❌ Método 'Efectivo' no encontrado")
            
    except Company.DoesNotExist:
        print("❌ Empresa GUEBER no encontrada")

def check_javascript_logic():
    """Verificar la lógica del JavaScript"""
    print("\n🔧 VERIFICANDO LÓGICA JAVASCRIPT:")
    
    js_file = "static/admin/js/integrated_payment_account_handler.js"
    if os.path.exists(js_file):
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar función isChildAccount
        if 'isChildAccount' in content:
            print("   ✅ Función isChildAccount encontrada")
            
            # Extraer la función para analizar
            lines = content.split('\n')
            in_function = False
            function_lines = []
            
            for line in lines:
                if 'isChildAccount(' in line:
                    in_function = True
                if in_function:
                    function_lines.append(line)
                    if line.strip().endswith('}') and len(function_lines) > 1:
                        break
            
            print("   📝 Lógica actual:")
            for line in function_lines[:10]:  # Mostrar primeras 10 líneas
                print(f"      {line}")
        else:
            print("   ❌ Función isChildAccount no encontrada")
    else:
        print("   ❌ Archivo JavaScript no encontrado")

if __name__ == "__main__":
    debug_filtering_problem()
    check_javascript_logic()
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNÓSTICO COMPLETADO")
    print("=" * 60)