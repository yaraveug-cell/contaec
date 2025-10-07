#!/usr/bin/env python3
"""
Test final: Verificar corrección de valores por defecto
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append('.')
django.setup()

def test_default_configuration():
    """Test final de configuración de valores por defecto"""
    
    from apps.companies.models import Company, PaymentMethod
    
    print("🧪 TEST FINAL: VALORES POR DEFECTO")
    print("=" * 50)
    
    # 1. Verificar que todas las empresas tengan Efectivo
    print("🏢 VERIFICACIÓN DE EMPRESAS:")
    companies = Company.objects.all()
    
    efectivo_count = 0
    for company in companies:
        method_name = company.payment_method.name if company.payment_method else "Sin configurar"
        is_efectivo = method_name.lower() == 'efectivo'
        
        status = "✅" if is_efectivo else "❌"
        print(f"   {status} {company.trade_name} → {method_name}")
        
        if is_efectivo:
            efectivo_count += 1
    
    print(f"\n📊 RESULTADO: {efectivo_count}/{len(companies)} empresas con Efectivo")
    
    # 2. Verificar método Efectivo y su cuenta
    print(f"\n💰 VERIFICACIÓN MÉTODO EFECTIVO:")
    try:
        efectivo = PaymentMethod.objects.get(name__icontains='efectivo', is_active=True)
        print(f"   ✅ Método: {efectivo.name} (ID: {efectivo.id})")
        
        if efectivo.parent_account:
            print(f"   ✅ Cuenta padre: {efectivo.parent_account.code} - {efectivo.parent_account.name}")
            
            # Buscar cuentas hijas de CAJA
            from apps.accounting.models import ChartOfAccounts
            caja_children = ChartOfAccounts.objects.filter(
                company=efectivo.parent_account.company,
                code__startswith=efectivo.parent_account.code,
                is_active=True
            ).exclude(id=efectivo.parent_account.id)
            
            print(f"   📋 Cuentas disponibles para filtrado:")
            for child in caja_children:
                print(f"      - {child.code} - {child.name}")
                if 'GENERAL' in child.name.upper():
                    print(f"        ✅ CAJA GENERAL encontrada!")
                    
        else:
            print(f"   ❌ Sin cuenta padre configurada")
            
    except PaymentMethod.DoesNotExist:
        print(f"   ❌ Método Efectivo no encontrado")
    
    # 3. Resumen del test
    print(f"\n🎯 RESUMEN DEL TEST:")
    
    all_efectivo = efectivo_count == len(companies)
    has_parent_account = efectivo.parent_account is not None
    
    if all_efectivo and has_parent_account:
        print(f"   ✅ CONFIGURACIÓN CORRECTA")
        print(f"   ✅ Todas las empresas: Efectivo")
        print(f"   ✅ Cuenta padre configurada: {efectivo.parent_account.code}")
        print(f"\n🚀 RESULTADO ESPERADO AL ABRIR FACTURA:")
        print(f"   🏢 Empresa: GUEBER (autoseleccionada)")
        print(f"   💳 Forma de Pago: Efectivo (por defecto universal)")
        print(f"   📊 Cuenta: Cuentas de CAJA disponibles (filtradas)")
    else:
        print(f"   ❌ CONFIGURACIÓN INCOMPLETA")
        if not all_efectivo:
            print(f"   ❌ No todas las empresas tienen Efectivo")
        if not has_parent_account:
            print(f"   ❌ Método Efectivo sin cuenta padre")

if __name__ == '__main__':
    try:
        test_default_configuration()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()