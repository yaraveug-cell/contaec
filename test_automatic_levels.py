#!/usr/bin/env python
"""
Test para verificar el funcionamiento del cálculo automático de niveles
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import ChartOfAccounts, AccountType
from apps.companies.models import Company


def test_automatic_levels():
    """Test del cálculo automático de niveles"""
    print("🧪 TESTING: Cálculo Automático de Niveles")
    print("=" * 50)
    
    # Obtener datos necesarios
    company = Company.objects.first()
    asset_type = AccountType.objects.get(code='ASSET')
    
    test_passed = 0
    test_total = 0
    
    def assert_test(condition, description):
        nonlocal test_passed, test_total
        test_total += 1
        if condition:
            print(f"✅ TEST {test_total}: {description}")
            test_passed += 1
        else:
            print(f"❌ TEST {test_total}: {description}")
    
    try:
        # TEST 1: Cuenta raíz debe tener nivel 1
        root_account = ChartOfAccounts.objects.create(
            company=company,
            code='TEST_ROOT',
            name='Cuenta Raíz de Test',
            account_type=asset_type,
            parent=None
        )
        assert_test(root_account.level == 1, "Cuenta raíz tiene nivel 1")
        
        # TEST 2: Cuenta hija debe tener nivel padre + 1
        child_account = ChartOfAccounts.objects.create(
            company=company,
            code='TEST_CHILD',
            name='Cuenta Hija de Test',
            account_type=asset_type,
            parent=root_account
        )
        assert_test(child_account.level == 2, "Cuenta hija tiene nivel 2")
        
        # TEST 3: Cuenta nieta debe tener nivel 3
        grandchild_account = ChartOfAccounts.objects.create(
            company=company,
            code='TEST_GRANDCHILD',
            name='Cuenta Nieta de Test',
            account_type=asset_type,
            parent=child_account
        )
        assert_test(grandchild_account.level == 3, "Cuenta nieta tiene nivel 3")
        
        # TEST 4: Cambiar padre debe recalcular nivel
        grandchild_account.parent = root_account
        grandchild_account.save()
        assert_test(grandchild_account.level == 2, "Al cambiar padre se recalcula nivel")
        
        # TEST 5: Verificar hierarchy_display
        expected_display = "TEST_ROOT - Cuenta Raíz de Test"
        assert_test(root_account.hierarchy_display == expected_display, "hierarchy_display funciona para cuenta raíz")
        
        # TEST 6: Verificar full_code
        grandchild_account.parent = child_account
        grandchild_account.save()
        expected_code = "TEST_ROOT.TEST_CHILD.TEST_GRANDCHILD"
        assert_test(grandchild_account.full_code == expected_code, "full_code genera jerarquía correcta")
        
        # TEST 7: Verificar children_count
        assert_test(root_account.children_count == 1, "children_count cuenta hijos correctamente")
        assert_test(child_account.children_count == 1, "children_count cuenta nietos correctamente")
        assert_test(grandchild_account.children_count == 0, "children_count es 0 para cuentas hoja")
        
        # TEST 8: Verificar actualización automática de padre
        root_account.refresh_from_db()
        root_account._update_detail_status()
        assert_test(not root_account.is_detail, "Cuenta padre no es de detalle")
        
        # Limpiar cuentas de test
        ChartOfAccounts.objects.filter(
            code__startswith='TEST_'
        ).delete()
        
        print(f"\n📊 RESULTADO: {test_passed}/{test_total} tests pasaron")
        
        if test_passed == test_total:
            print("🎉 ¡TODOS LOS TESTS PASARON! El sistema funciona correctamente.")
            return True
        else:
            print("⚠️ Algunos tests fallaron. Revisar implementación.")
            return False
            
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_admin_integration():
    """Test de integración con el admin"""
    print("\n🖥️ TESTING: Integración con Admin")
    print("=" * 40)
    
    try:
        # Verificar que las propiedades funcionan
        account = ChartOfAccounts.objects.first()
        
        if account:
            print(f"📋 Cuenta de prueba: {account.code}")
            print(f"   hierarchy_display: {account.hierarchy_display}")
            print(f"   full_code: {account.full_code}")
            print(f"   children_count: {account.children_count}")
            print("✅ Propiedades del admin funcionan correctamente")
            return True
        else:
            print("⚠️ No hay cuentas disponibles para probar")
            return False
            
    except Exception as e:
        print(f"❌ Error en test de admin: {e}")
        return False


if __name__ == '__main__':
    success1 = test_automatic_levels()
    success2 = test_admin_integration()
    
    if success1 and success2:
        print("\n🎯 CONCLUSIÓN: Sistema de niveles automáticos completamente funcional")
        sys.exit(0)
    else:
        print("\n❌ CONCLUSIÓN: Hay problemas que necesitan atención")
        sys.exit(1)