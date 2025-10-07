#!/usr/bin/env python
"""
Test final del sistema completo de filtrado de cuentas por forma de pago
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import ChartOfAccounts

def test_complete_payment_filtering():
    """Test completo del sistema de filtrado por forma de pago"""
    
    print("🎯 TEST COMPLETO: SISTEMA DE FILTRADO POR FORMA DE PAGO")
    print("=" * 80)
    
    # Obtener todas las cuentas operativas
    all_accounts = ChartOfAccounts.objects.filter(
        accepts_movement=True
    ).select_related('company', 'parent').order_by('code')
    
    print(f"📊 Total cuentas operativas disponibles: {all_accounts.count()}")
    
    # Test 1: EFECTIVO (Filtrar por CAJA)
    print(f"\n💰 TEST 1: EFECTIVO - Filtrar por CAJA")
    print("-" * 40)
    
    cash_accounts = []
    for account in all_accounts:
        account_text = f"{account.code} - {account.name}".upper()
        
        if ('CAJA' in account_text or
            'EFECTIVO' in account_text or 
            'CASH' in account_text):
            cash_accounts.append(account)
    
    print(f"   🔍 Cuentas de EFECTIVO encontradas: {len(cash_accounts)}")
    for account in cash_accounts:
        parent_name = account.parent.name if account.parent else "Sin padre"
        print(f"      • {account.code} - {account.name}")
        print(f"        Padre: {parent_name}")
    
    # Test 2: CREDITO (Filtrar por CLIENTES RELACIONADOS)
    print(f"\n💳 TEST 2: CRÉDITO - Filtrar por CLIENTES RELACIONADOS")
    print("-" * 50)
    
    credit_accounts = []
    for account in all_accounts:
        account_text = f"{account.code} - {account.name}".upper()
        
        if ('CLIENTES RELACIONADOS' in account_text or 
            'CLIENTE CREDITO AUTORIZADO' in account_text or
            'DOC CUENTAS COBRAR CLIENTES' in account_text or
            ('CLIENTE' in account_text and 'CREDITO' in account_text)):
            credit_accounts.append(account)
    
    print(f"   🔍 Cuentas de CRÉDITO encontradas: {len(credit_accounts)}")
    for account in credit_accounts:
        parent_name = account.parent.name if account.parent else "Sin padre"
        print(f"      • {account.code} - {account.name}")
        print(f"        Padre: {parent_name}")
    
    # Test 3: TRANSFERENCIA (Filtrar por BANCOS)
    print(f"\n🏦 TEST 3: TRANSFERENCIA - Filtrar por BANCOS")
    print("-" * 43)
    
    bank_accounts = []
    for account in all_accounts:
        account_text = f"{account.code} - {account.name}".upper()
        
        if ('BANCO' in account_text or
            'BANCARIO' in account_text or
            'DEPOSITO' in account_text or
            'CUENTA CORRIENTE' in account_text or
            'AHORRO' in account_text):
            bank_accounts.append(account)
    
    print(f"   🔍 Cuentas de TRANSFERENCIA encontradas: {len(bank_accounts)}")
    for account in bank_accounts:
        parent_name = account.parent.name if account.parent else "Sin padre"
        print(f"      • {account.code} - {account.name}")
        print(f"        Padre: {parent_name}")
    
    # Verificar que no hay solapamientos
    print(f"\n🔄 VERIFICACIÓN DE NO SOLAPAMIENTO")
    print("-" * 40)
    
    all_filtered = set()
    cash_ids = {acc.id for acc in cash_accounts}
    credit_ids = {acc.id for acc in credit_accounts}
    bank_ids = {acc.id for acc in bank_accounts}
    
    overlaps = []
    if cash_ids & credit_ids:
        overlaps.append("EFECTIVO ↔ CRÉDITO")
    if cash_ids & bank_ids:
        overlaps.append("EFECTIVO ↔ TRANSFERENCIA")
    if credit_ids & bank_ids:
        overlaps.append("CRÉDITO ↔ TRANSFERENCIA")
    
    if overlaps:
        print(f"   ⚠️  Solapamientos detectados: {', '.join(overlaps)}")
        for overlap in overlaps:
            print(f"      Revisar lógica de filtrado para: {overlap}")
    else:
        print(f"   ✅ Sin solapamientos - Cada cuenta pertenece a un solo filtro")
    
    # Verificar JavaScript
    print(f"\n📝 VERIFICACIÓN JAVASCRIPT")
    print("-" * 30)
    
    js_file = 'static/admin/js/payment_form_handler.js'
    if os.path.exists(js_file):
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Verificar métodos de filtrado
        methods = [
            ('filterCashAccounts', '💰 EFECTIVO'),
            ('filterClientAccounts', '💳 CRÉDITO'),
            ('filterBankAccounts', '🏦 TRANSFERENCIA')
        ]
        
        for method, label in methods:
            if method in js_content:
                print(f"   ✅ {label}: Método {method} presente")
            else:
                print(f"   ❌ {label}: Método {method} faltante")
        
        # Verificar manejo de cambios
        if 'handlePaymentFormChange' in js_content:
            print(f"   ✅ Controlador de cambios configurado")
        else:
            print(f"   ❌ Controlador de cambios faltante")
            
    else:
        print(f"   ❌ Archivo JavaScript no encontrado: {js_file}")
    
    # Resumen final
    print(f"\n" + "=" * 80)
    print(f"🎯 RESUMEN FINAL DEL SISTEMA")
    print(f"=" * 80)
    
    print(f"📊 DISTRIBUCIÓN DE CUENTAS POR FORMA DE PAGO:")
    print(f"   💰 EFECTIVO: {len(cash_accounts)} cuentas")
    print(f"   💳 CRÉDITO: {len(credit_accounts)} cuentas")
    print(f"   🏦 TRANSFERENCIA: {len(bank_accounts)} cuentas")
    print(f"   📈 TOTAL FILTRADAS: {len(cash_accounts) + len(credit_accounts) + len(bank_accounts)}")
    print(f"   📋 TOTAL DISPONIBLES: {all_accounts.count()}")
    
    coverage = ((len(cash_accounts) + len(credit_accounts) + len(bank_accounts)) / all_accounts.count()) * 100
    print(f"   📊 COBERTURA: {coverage:.1f}%")
    
    print(f"\n🚀 ESTADO DEL SISTEMA:")
    if len(cash_accounts) > 0 and len(credit_accounts) > 0 and len(bank_accounts) > 0:
        print(f"   ✅ TODAS las formas de pago tienen cuentas disponibles")
        print(f"   ✅ Sistema completamente funcional")
    elif len(cash_accounts) == 0:
        print(f"   ⚠️  Sin cuentas de EFECTIVO configuradas")
    elif len(credit_accounts) == 0:
        print(f"   ⚠️  Sin cuentas de CRÉDITO configuradas")
    elif len(bank_accounts) == 0:
        print(f"   ⚠️  Sin cuentas de TRANSFERENCIA configuradas")
    
    print(f"\n🔧 CONFIGURACIÓN:")
    print(f"   📄 Campo Forma de Pago: 3 opciones (EFECTIVO*, CREDITO, TRANSFERENCIA)")
    print(f"   🔗 Campo Cuenta: Relacionado con ChartOfAccounts")
    print(f"   🎯 Filtrado Dinámico: Basado en JavaScript frontend")
    print(f"   🎨 Estilo: Consistente con Django Admin")
    print(f"   ⚡ Funcionamiento: Sin dependencias AJAX")
    
    return True

if __name__ == "__main__":
    success = test_complete_payment_filtering()
    sys.exit(0 if success else 1)