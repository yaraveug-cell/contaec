#!/usr/bin/env python
"""
Diagnóstico: Carga de observaciones bancarias en modo edición
Verificar por qué no se cargan las observaciones al editar facturas
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from apps.companies.models import PaymentMethod

def diagnose_edit_mode_loading():
    """Diagnosticar carga de datos en modo edición"""
    
    print("🔍 DIAGNÓSTICO: Carga de observaciones en edición")
    print("=" * 50)
    
    # 1. Buscar facturas con transferencia
    print("\n📋 1. FACTURAS CON TRANSFERENCIA:")
    print("-" * 35)
    
    transfer_method = PaymentMethod.objects.filter(
        name__icontains='transferencia',
        is_active=True
    ).first()
    
    if not transfer_method:
        print("❌ No hay método 'Transferencia' configurado")
        return
    
    print(f"✅ Método encontrado: {transfer_method.name} (ID: {transfer_method.id})")
    
    # Buscar facturas con este método
    transfer_invoices = Invoice.objects.filter(payment_form=transfer_method).order_by('-id')[:5]
    
    print(f"📊 Facturas con transferencia: {transfer_invoices.count()}")
    
    for invoice in transfer_invoices:
        print(f"\n📄 Factura #{invoice.number} (ID: {invoice.id}):")
        print(f"   💳 Forma de pago: {invoice.payment_form}")
        print(f"   🏦 Cuenta: {invoice.account}")
        print(f"   💬 bank_observations: '{invoice.bank_observations}'")
        print(f"   📝 transfer_detail: '{invoice.transfer_detail}'")
        
        # Verificar si tiene observaciones
        has_bank_obs = bool(invoice.bank_observations and invoice.bank_observations.strip())
        has_transfer_detail = bool(invoice.transfer_detail and invoice.transfer_detail.strip())
        
        print(f"   ✅ Tiene bank_observations: {'✓' if has_bank_obs else '✗'}")
        print(f"   ✅ Tiene transfer_detail: {'✓' if has_transfer_detail else '✗'}")
    
    # 2. Verificar admin fieldsets
    print("\n🔧 2. VERIFICACIÓN ADMIN:")
    print("-" * 26)
    
    from apps.invoicing.admin import InvoiceAdmin
    admin = InvoiceAdmin(Invoice, None)
    
    # Verificar get_form
    print("📋 Verificando método get_form...")
    
    # Simular request para edición
    class MockRequest:
        def __init__(self):
            self.user = None
            self.method = 'GET'
    
    mock_request = MockRequest()
    
    # Probar con una factura existente
    if transfer_invoices.exists():
        test_invoice = transfer_invoices.first()
        form_class = admin.get_form(mock_request, obj=test_invoice)
        form = form_class(instance=test_invoice)
        
        print(f"✅ Form class obtenida: {form_class}")
        
        # Verificar si bank_observations está en el form
        if 'bank_observations' in form.fields:
            widget = form.fields['bank_observations'].widget
            print(f"✅ Campo bank_observations presente")
            print(f"   Widget: {type(widget).__name__}")
            print(f"   Valor inicial: '{form.initial.get('bank_observations', 'NO ENCONTRADO')}'")
            
            # Verificar valor del objeto
            if hasattr(test_invoice, 'bank_observations'):
                actual_value = getattr(test_invoice, 'bank_observations', '')
                print(f"   Valor del objeto: '{actual_value}'")
            
        else:
            print("❌ Campo bank_observations NO presente en form")
            print(f"   Campos disponibles: {list(form.fields.keys())}")
    
    # 3. Verificar JavaScript
    print("\n💻 3. VERIFICACIÓN JAVASCRIPT:")
    print("-" * 32)
    
    js_file = "static/admin/js/unified_banking_integration.js"
    
    try:
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Buscar método de carga inicial
        has_load_initial = 'loadInitialState' in js_content
        has_populate_from_django = 'populateFromDjangoField' in js_content
        has_sync_method = 'syncWithDjangoField' in js_content
        
        print(f"✅ Método loadInitialState: {'✓' if has_load_initial else '✗'}")
        print(f"✅ Método populateFromDjangoField: {'✓' if has_populate_from_django else '✗'}")
        print(f"✅ Método syncWithDjangoField: {'✓' if has_sync_method else '✗'}")
        
        # Buscar inicialización automática
        has_dom_ready = 'DOMContentLoaded' in js_content or 'document.ready' in js_content
        print(f"✅ Inicialización DOM: {'✓' if has_dom_ready else '✗'}")
        
        if not (has_load_initial and has_populate_from_django):
            print("❌ PROBLEMA: Faltan métodos de carga inicial en JavaScript")
        
    except FileNotFoundError:
        print(f"❌ Archivo JavaScript no encontrado: {js_file}")
    
    # 4. Crear factura de prueba para verificar guardado
    print("\n🧪 4. PRUEBA DE GUARDADO:")
    print("-" * 26)
    
    from django.db import transaction
    from decimal import Decimal
    import time
    
    try:
        with transaction.atomic():
            # Crear factura de prueba
            test_number = f"TEST-EDIT-{int(time.time())}"
            
            from django.contrib.auth import get_user_model
            User = get_user_model()
            test_user = User.objects.first()
            
            from apps.invoicing.models import Customer
            from apps.companies.models import Company
            from apps.accounting.models import ChartOfAccounts
            
            company = Company.objects.first()
            customer = Customer.objects.filter(company=company).first()
            bank_account = ChartOfAccounts.objects.filter(
                company=company,
                aux_type='bank'
            ).first()
            
            if all([company, customer, test_user, transfer_method, bank_account]):
                test_observations = f"Prueba edición - {test_number} - Transferencia Banco Prueba"
                
                test_invoice = Invoice.objects.create(
                    company=company,
                    customer=customer,
                    number=test_number,
                    payment_form=transfer_method,
                    account=bank_account,
                    created_by=test_user,
                    bank_observations=test_observations,
                    status='draft'
                )
                
                print(f"✅ Factura de prueba creada: {test_invoice.number}")
                print(f"   💬 Observaciones guardadas: '{test_invoice.bank_observations}'")
                
                # Recargar desde DB
                test_invoice.refresh_from_db()
                print(f"   💬 Observaciones tras refresh: '{test_invoice.bank_observations}'")
                
                # Limpiar
                test_invoice.delete()
                print(f"✅ Factura de prueba eliminada")
                
            else:
                print("❌ No se pueden crear datos de prueba (faltan datos)")
                
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    diagnose_edit_mode_loading()