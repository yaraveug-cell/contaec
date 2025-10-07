#!/usr/bin/env python3
"""
Script de prueba para validar la implementación de preservación de selecciones
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def main():
    print("🧪 VALIDACIÓN DE IMPLEMENTACIÓN - PRESERVACIÓN DE SELECCIONES")
    print("=" * 70)
    
    from apps.invoicing.models import Invoice
    from apps.companies.models import PaymentMethod
    from apps.accounting.models import ChartOfAccounts
    
    # 1. Verificar configuración de formas de pago
    print("💰 1. FORMAS DE PAGO CONFIGURADAS:")
    print("-" * 40)
    
    payment_methods = PaymentMethod.objects.filter(is_active=True).order_by('name')
    for pm in payment_methods:
        print(f"   📝 {pm.name} (ID: {pm.id})")
        if pm.parent_account:
            # Contar cuentas hijas disponibles
            from apps.companies.models import Company
            gueber = Company.objects.get(trade_name="GUEBER")
            child_accounts = ChartOfAccounts.objects.filter(
                company=gueber,
                code__startswith=pm.parent_account.code,
                accepts_movement=True
            ).exclude(code=pm.parent_account.code)
            
            print(f"      └─ Cuenta padre: {pm.parent_account.code}")
            print(f"      └─ Cuentas hijas: {child_accounts.count()}")
            if child_accounts.exists():
                first_account = child_accounts.first()
                print(f"      └─ Primera cuenta: {first_account.code} - {first_account.name}")
    
    print()
    
    # 2. Casos de prueba específicos
    print("🎯 2. CASOS DE PRUEBA:")
    print("-" * 40)
    
    print("A. CREAR NUEVA FACTURA:")
    print("   URL: http://localhost:8000/admin/invoicing/invoice/add/")
    print("   Esperado:")
    print("   ├─ 💳 Forma de pago: 'Efectivo' (Django por defecto)")
    print("   ├─ 🔄 JavaScript detecta: isNewInvoice = true")
    print("   ├─ 🎯 Auto-selecciona: '1.1.01.01 - CAJA GENERAL'")
    print("   └─ ✅ Resultado: Ambos campos preseleccionados")
    print()
    
    # Buscar facturas existentes para pruebas
    test_invoices = Invoice.objects.filter(
        payment_form__isnull=False, 
        account__isnull=False
    ).select_related('payment_form', 'account')[:3]
    
    print("B. EDITAR FACTURAS EXISTENTES:")
    for invoice in test_invoices:
        print(f"   📄 Factura ID {invoice.id}:")
        print(f"   URL: http://localhost:8000/admin/invoicing/invoice/{invoice.id}/change/")
        print(f"   Estado guardado:")
        print(f"   ├─ 💳 Forma de pago: '{invoice.payment_form.name}' (ID: {invoice.payment_form.id})")
        print(f"   ├─ 🏦 Cuenta: '{invoice.account.code} - {invoice.account.name}' (ID: {invoice.account.id})")
        print(f"   Esperado:")
        print(f"   ├─ 🔄 JavaScript detecta: isNewInvoice = false")
        print(f"   ├─ 🔍 Preserva: payment_form = '{invoice.payment_form.name}'")
        print(f"   ├─ 🔍 Preserva: account = '{invoice.account.code} - {invoice.account.name}'")
        print(f"   └─ ✅ Resultado: Valores originales mantenidos")
        print()
    
    # 3. Instrucciones de prueba detalladas
    print("📋 3. INSTRUCCIONES DE PRUEBA:")
    print("-" * 40)
    print("""
    PASOS PARA VALIDAR:
    
    🆕 NUEVA FACTURA:
    1. Abrir: http://localhost:8000/admin/invoicing/invoice/add/
    2. Abrir consola del navegador (F12)
    3. Verificar logs:
       - "Contexto detectado: NUEVA factura"
       - "Primera cuenta auto-seleccionada: 1.1.01.01 - CAJA GENERAL"
    4. Verificar UI:
       - Forma de pago: "Efectivo" ✅
       - Cuenta: "1.1.01.01 - CAJA GENERAL" ✅
    
    ✏️  EDITAR FACTURA:
    1. Abrir cualquier factura existente (ej. ID 101)
    2. Abrir consola del navegador (F12)
    3. Verificar logs:
       - "Contexto detectado: EDITAR factura"
       - "Selección preservada: [cuenta original]"
    4. Verificar UI:
       - Forma de pago: Valor original ✅
       - Cuenta: Valor original ✅
    
    🔄 CAMBIO MANUAL:
    1. En cualquier factura, cambiar forma de pago manualmente
    2. Verificar logs:
       - "Forma de pago cambiada manualmente"
    3. Verificar comportamiento:
       - Campo cuenta se resetea correctamente ✅
       - Muestra opciones filtradas apropiadas ✅
    
    VALIDACIONES CRÍTICAS:
    ✓ Nueva factura: Auto-selección funciona
    ✓ Editar factura: Preservación funciona  
    ✓ Cambio manual: Filtro normal funciona
    ✓ Sin errores JavaScript en consola
    """)
    
    print("🎪 4. COMPORTAMIENTOS ESPERADOS:")
    print("-" * 40)
    print("""
    ESCENARIO                   | PRESERVAR | AUTO-SELECT | RESULTADO
    ----------------------------|-----------|-------------|------------------
    Nueva factura (inicial)     | false     | true        | Primera cuenta
    Editar factura (inicial)    | true      | false       | Cuenta original
    Cambio manual forma pago    | false     | true        | Primera filtrada
    Error/sin cuentas          | -         | -           | Opciones originales
    """)

if __name__ == '__main__':
    main()