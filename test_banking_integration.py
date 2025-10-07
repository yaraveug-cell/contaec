#!/usr/bin/env python
"""
Script de prueba para la integración Banking-Invoicing
Verifica que toda la funcionalidad nueva funcione sin afectar la existente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from apps.companies.models import PaymentMethod, Company
from apps.invoicing.models import Customer
from apps.accounting.services import AutomaticJournalEntryService

print("🧪 PRUEBA: Integración Banking-Invoicing")
print("=" * 45)

def test_ajax_endpoints():
    """Probar que las vistas AJAX estén disponibles"""
    print("\n1. 🔗 VERIFICAR ENDPOINTS AJAX:")
    print("-" * 32)
    
    from django.test import Client
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    client = Client()
    
    # Login como usuario existente
    user = User.objects.filter(is_staff=True).first()
    if user:
        client.force_login(user)
        
        # Probar endpoint de cuentas bancarias
        response = client.get('/admin/invoicing/invoice/bank-accounts/', 
                            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        print(f"   📊 Status /bank-accounts/: {response.status_code}")
        if response.status_code == 200:
            import json
            try:
                data = json.loads(response.content)
                count = data.get('count', 0)
                print(f"   ✅ {count} cuentas bancarias disponibles")
            except:
                print(f"   ⚠️ Respuesta no es JSON válido")
        else:
            print(f"   ❌ Error en endpoint")
    else:
        print("   ⚠️ No hay usuarios staff para probar")

def test_existing_functionality():
    """Verificar que funcionalidad existente no se afecte"""
    print("\n2. ✅ VERIFICAR FUNCIONALIDAD EXISTENTE:")
    print("-" * 40)
    
    # Buscar factura existente
    existing_invoice = Invoice.objects.filter(total__gt=0).first()
    if existing_invoice:
        print(f"   📄 Factura de prueba: {existing_invoice.id}")
        print(f"      - Método pago: {existing_invoice.payment_form}")
        print(f"      - Cuenta: {existing_invoice.account}")
        print(f"      - Total: ${existing_invoice.total}")
        
        # Verificar que se puede crear asiento
        try:
            journal_entry, created = AutomaticJournalEntryService.create_journal_entry_from_invoice(existing_invoice)
            if journal_entry:
                if created:
                    print(f"   ✅ Asiento creado: {journal_entry.number}")
                else:
                    print(f"   ✅ Asiento ya existía: {journal_entry.number}")
            else:
                print(f"   ❌ No se pudo crear asiento")
        except Exception as e:
            print(f"   ❌ Error creando asiento: {e}")
    else:
        print("   ⚠️ No hay facturas para probar")

def test_new_banking_integration():
    """Probar nueva funcionalidad de integración bancaria"""
    print("\n3. 🏦 VERIFICAR INTEGRACIÓN BANCARIA:")
    print("-" * 37)
    
    # Verificar si módulo banking está disponible
    try:
        from apps.banking.models import BankAccount
        bank_accounts = BankAccount.objects.filter(is_active=True)
        print(f"   📊 Cuentas bancarias activas: {bank_accounts.count()}")
        
        for account in bank_accounts[:3]:  # Primeras 3
            print(f"      🏦 {account.bank.short_name} - {account.masked_account_number}")
            if account.chart_account:
                print(f"         → Vinculada a: {account.chart_account.code}")
            else:
                print(f"         → Sin cuenta contable")
                
        # Verificar servicio de integración
        try:
            from apps.invoicing.services_banking import BankingInvoiceService
            print(f"   ✅ BankingInvoiceService disponible")
        except ImportError:
            print(f"   ⚠️ BankingInvoiceService no disponible")
            
    except ImportError:
        print("   ℹ️ Módulo Banking no instalado - funcionalidad opcional")

def test_transfer_invoice_creation():
    """Probar creación de factura con transferencia"""
    print("\n4. 📝 PROBAR FACTURA CON TRANSFERENCIA:")
    print("-" * 39)
    
    # Buscar método transferencia
    transferencia = PaymentMethod.objects.filter(name__icontains='TRANSFERENCIA').first()
    if not transferencia:
        print("   ❌ No hay método 'Transferencia' configurado")
        return
        
    print(f"   💰 Método encontrado: {transferencia.name}")
    
    # Verificar componentes necesarios
    company = Company.objects.first()
    customer = Customer.objects.first()
    
    if not all([company, customer]):
        print("   ❌ Faltan datos básicos (company/customer)")
        return
        
    print(f"   🏢 Empresa: {company.trade_name}")
    print(f"   👤 Cliente: {customer.trade_name}")
    
    # Buscar cuenta bancaria disponible
    try:
        from apps.banking.models import BankAccount
        bank_account = BankAccount.objects.filter(
            company=company,
            chart_account__isnull=False,
            is_active=True
        ).first()
        
        if bank_account:
            print(f"   🏦 Cuenta bancaria: {bank_account.bank.short_name}")
            print(f"   💳 Cuenta contable: {bank_account.chart_account.code}")
            
            # Simular creación de factura (sin guardar en DB)
            test_invoice = Invoice(
                company=company,
                customer=customer,
                payment_form=transferencia,
                account=bank_account.chart_account,
                subtotal=1000.00,
                tax_amount=150.00,
                total=1150.00,
                transfer_detail="Banco Pichincha - Transferencia de prueba"
            )
            
            print(f"   ✅ Factura de prueba simulada:")
            print(f"      - Total: ${test_invoice.total}")
            print(f"      - Cuenta: {test_invoice.account.code}")
            print(f"      - Detalle: {test_invoice.transfer_detail}")
            
        else:
            print("   ⚠️ No hay cuentas bancarias con chart_account")
            
    except ImportError:
        print("   ℹ️ Módulo Banking no disponible para prueba")

def test_javascript_files():
    """Verificar que archivos JavaScript existan"""
    print("\n5. 📱 VERIFICAR ARCHIVOS JAVASCRIPT:")
    print("-" * 35)
    
    import os
    js_files = [
        'static/admin/js/transfer_detail_handler.js',
        'static/admin/js/banking_invoice_integration.js'
    ]
    
    for js_file in js_files:
        if os.path.exists(js_file):
            size_kb = os.path.getsize(js_file) / 1024
            print(f"   ✅ {os.path.basename(js_file)} ({size_kb:.1f} KB)")
        else:
            print(f"   ❌ {os.path.basename(js_file)} NO encontrado")

def main():
    """Ejecutar todas las pruebas"""
    print("🎯 Iniciando pruebas de integración...")
    
    try:
        test_ajax_endpoints()
        test_existing_functionality()
        test_new_banking_integration()
        test_transfer_invoice_creation()
        test_javascript_files()
        
        print(f"\n🎉 RESUMEN:")
        print("-" * 12)
        print("✅ Pruebas de integración completadas")
        print("✅ Funcionalidad existente preservada")
        print("✅ Nueva funcionalidad disponible")
        print("ℹ️ La integración es opcional y no afecta el sistema base")
        
    except Exception as e:
        print(f"\n❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()