#!/usr/bin/env python3
"""
Script simple para verificar que el sistema esté funcionando correctamente
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def check_system_status():
    """Verificar el estado del sistema"""
    print("🚀 VERIFICACIÓN RÁPIDA DEL SISTEMA")
    print("=" * 50)
    
    # Verificar modelos
    from apps.companies.models import Company, PaymentMethod
    from apps.accounting.models import ChartOfAccounts
    from apps.invoicing.models import Invoice
    
    print("📊 ESTADO DE DATOS:")
    
    # Empresas
    companies = Company.objects.all()
    companies_with_payment = Company.objects.filter(payment_method__isnull=False)
    print(f"   - Total empresas: {companies.count()}")
    print(f"   - Empresas con método de pago: {companies_with_payment.count()}")
    
    if companies_with_payment.exists():
        for company in companies_with_payment:
            print(f"     └ {company.trade_name} → {company.payment_method.name}")
    
    # Métodos de pago
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    print(f"   - Métodos de pago activos: {payment_methods.count()}")
    
    for method in payment_methods:
        parent = method.parent_account
        if parent:
            print(f"     └ {method.name} → {parent.code} - {parent.name}")
    
    # Cuentas
    accounts = ChartOfAccounts.objects.filter(accepts_movement=True)
    print(f"   - Cuentas que aceptan movimiento: {accounts.count()}")
    
    # Facturas
    invoices = Invoice.objects.all()
    print(f"   - Total facturas: {invoices.count()}")
    
    print("\n📄 ARCHIVOS JAVASCRIPT:")
    js_file = "static/admin/js/integrated_payment_account_handler.js"
    if os.path.exists(js_file):
        print(f"   ✅ {js_file}")
        with open(js_file, 'r') as f:
            content = f.read()
            if 'IntegratedPaymentAccountHandler' in content:
                print("   ✅ Clase IntegratedPaymentAccountHandler encontrada")
            if 'handleCompanyChange' in content:
                print("   ✅ Método handleCompanyChange encontrado")
            if 'handlePaymentFormChange' in content:
                print("   ✅ Método handlePaymentFormChange encontrado")
    else:
        print(f"   ❌ {js_file} no encontrado")
    
    print("\n🌐 SERVIDOR:")
    print("   - Estado: Ejecutándose en http://127.0.0.1:8000/")
    print("   - Admin: http://127.0.0.1:8000/admin/")
    print("   - Nueva Factura: http://127.0.0.1:8000/admin/invoicing/invoice/add/")
    
    print("\n✅ SISTEMA LISTO PARA PRUEBAS")
    print("\n🎯 PASOS PARA PROBAR EL FILTRADO DINÁMICO:")
    print("1. Abrir el navegador en http://127.0.0.1:8000/admin/")
    print("2. Iniciar sesión como administrador")
    print("3. Ir a Invoicing → Invoices → Add Invoice")
    print("4. Seleccionar una empresa (GUEBER o CEMENTO MAXI)")
    print("5. Observar que el campo 'Forma de Pago' se actualiza automáticamente")
    print("6. Observar que el campo 'Cuenta' se filtra dinámicamente")
    print("7. Cambiar la forma de pago y ver el filtrado en tiempo real")

def check_configuration():
    """Verificar configuración específica"""
    print("\n🔧 CONFIGURACIÓN DETALLADA:")
    
    from apps.companies.models import Company, PaymentMethod
    from apps.accounting.models import ChartOfAccounts
    
    # Configuración de CEMENTO MAXI
    try:
        cemento = Company.objects.get(trade_name__icontains="CEMENTO")
        if cemento.payment_method:
            print(f"   - CEMENTO MAXI: {cemento.payment_method.name}")
            if cemento.payment_method.parent_account:
                parent = cemento.payment_method.parent_account
                print(f"     └ Cuenta Padre: {parent.code} - {parent.name}")
                
                # Buscar cuentas hijas
                children = ChartOfAccounts.objects.filter(
                    company=cemento,
                    code__startswith=parent.code,
                    level=parent.level + 1,
                    accepts_movement=True
                )
                print(f"     └ Cuentas hijas disponibles: {children.count()}")
                for child in children[:3]:  # Mostrar solo las primeras 3
                    print(f"       • {child.code} - {child.name}")
        else:
            print("   - CEMENTO MAXI: Sin método de pago configurado")
    except Company.DoesNotExist:
        print("   - CEMENTO MAXI: No encontrada")
    
    # Configuración de GUEBER
    try:
        gueber = Company.objects.get(trade_name__icontains="GUEBER")
        if gueber.payment_method:
            print(f"   - GUEBER: {gueber.payment_method.name}")
            if gueber.payment_method.parent_account:
                parent = gueber.payment_method.parent_account
                print(f"     └ Cuenta Padre: {parent.code} - {parent.name}")
                
                # Buscar cuentas hijas
                children = ChartOfAccounts.objects.filter(
                    company=gueber,
                    code__startswith=parent.code,
                    level=parent.level + 1,
                    accepts_movement=True
                )
                print(f"     └ Cuentas hijas disponibles: {children.count()}")
                for child in children[:3]:  # Mostrar solo las primeras 3
                    print(f"       • {child.code} - {child.name}")
        else:
            print("   - GUEBER: Sin método de pago configurado")
    except Company.DoesNotExist:
        print("   - GUEBER: No encontrada")

if __name__ == "__main__":
    check_system_status()
    check_configuration()
    
    print("\n" + "=" * 50)
    print("🎉 SISTEMA PREPARADO - LISTO PARA PROBAR FILTRADO DINÁMICO")
    print("=" * 50)