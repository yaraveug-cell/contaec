#!/usr/bin/env python3
"""
Script de prueba para el filtro en cascada - Forma de Pago → Cuenta Contable
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def main():
    print("🧪 PRUEBA DEL FILTRO EN CASCADA")
    print("=" * 50)
    
    # Simular llamada AJAX para cada forma de pago
    from apps.companies.models import PaymentMethod
    from apps.accounting.models import ChartOfAccounts
    from apps.companies.models import Company
    
    gueber = Company.objects.get(trade_name="GUEBER")
    payment_methods = PaymentMethod.objects.all()
    
    print(f"🏢 Empresa de prueba: {gueber.trade_name}")
    print()
    
    for method in payment_methods:
        print(f"💳 Probando: {method.name}")
        
        if not method.parent_account:
            print(f"   ❌ Sin cuenta padre configurada")
            continue
            
        # Simular la lógica del endpoint
        parent_code = method.parent_account.code
        filtered_accounts = ChartOfAccounts.objects.filter(
            company=gueber,
            code__startswith=parent_code,
            accepts_movement=True
        ).exclude(
            code=parent_code
        ).order_by('code')
        
        print(f"   📋 Cuenta padre: {parent_code} - {method.parent_account.name}")
        print(f"   🎯 Cuentas filtradas ({filtered_accounts.count()}):")
        
        for account in filtered_accounts:
            print(f"      ├─ {account.code} - {account.name}")
        
        if not filtered_accounts.exists():
            print(f"      └─ (Sin cuentas hijas disponibles)")
        
        print()
    
    print("🌐 URLs DE PRUEBA:")
    print("-" * 30)
    print("1. Crear nueva factura:")
    print("   http://localhost:8000/admin/invoicing/invoice/add/")
    print()
    print("2. Editar factura existente:")
    print("   http://localhost:8000/admin/invoicing/invoice/99/change/")
    print()
    print("3. Endpoint AJAX (GET):")
    print("   http://localhost:8000/admin/invoicing/invoice/filter-accounts-by-payment/?payment_method_id=2&company_id=1")
    print()
    
    print("🎯 PASOS PARA PROBAR:")
    print("-" * 30)
    print("1. Abrir formulario de factura")
    print("2. Abrir consola del navegador (F12)")
    print("3. Seleccionar diferentes formas de pago")
    print("4. Verificar que el campo 'Cuenta' se filtra automáticamente")
    print("5. Verificar logs en consola del navegador")

if __name__ == '__main__':
    main()