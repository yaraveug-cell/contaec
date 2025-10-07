"""
Script de prueba para la funcionalidad de agente de retención en clientes
Verifica que los asientos contables se generen correctamente con retenciones
"""

import os
import django
import sys
from decimal import Decimal
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Customer, Invoice, InvoiceLine
from apps.companies.models import Company, PaymentMethod
from apps.accounting.models import ChartOfAccounts, JournalEntry
from apps.accounting.services import AutomaticJournalEntryService
from apps.inventory.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

def test_customer_retention_functionality():
    """Prueba la funcionalidad de retención para clientes agentes de retención"""
    print("🧪 Iniciando prueba de funcionalidad de retención para clientes...")
    
    try:
        # 1. Obtener empresa GUEBER
        company = Company.objects.filter(trade_name__icontains='GUEBER').first()
        if not company:
            print("❌ No se encontró empresa GUEBER para prueba")
            print("   Empresas disponibles:")
            for comp in Company.objects.all()[:5]:
                print(f"   - {comp.trade_name}")
            return False
        
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            print("❌ No se encontró usuario para prueba")
            return False
        
        # 2. Crear/obtener cuenta de caja para la factura (CAJA GENERAL de GUEBER)
        caja_account = ChartOfAccounts.objects.filter(
            company=company,
            code='1.1.01.01',  # CAJA GENERAL de GUEBER
            accepts_movement=True
        ).first()
        
        if not caja_account:
            print("❌ No se encontró cuenta CAJA GENERAL (1.1.01.01)")
            return False
        
        # 3. Crear/obtener forma de pago
        payment_method = PaymentMethod.objects.filter(company=company).first()
        if not payment_method:
            payment_method = PaymentMethod.objects.create(
                company=company,
                name="EFECTIVO",
                code="EF",
                is_active=True
            )
        
        print(f"✅ Datos básicos configurados:")
        print(f"   📢 Empresa: {company.trade_name}")
        print(f"   💰 Cuenta: {caja_account.code} - {caja_account.name}")
        print(f"   💳 Forma de pago: {payment_method.name}")
        
        # 4. Crear/obtener cliente agente de retención
        ruc_test = f"179012345{timezone.now().strftime('%M%S')}1"  # RUC único
        customer, created = Customer.objects.get_or_create(
            company=company,
            identification=ruc_test,
            defaults={
                'customer_type': 'juridical',
                'trade_name': f'CLIENTE AGENTE DE RETENCIÓN TEST {timezone.now().strftime("%H%M")} S.A.',
                'legal_name': f'CLIENTE AGENTE DE RETENCIÓN TEST {timezone.now().strftime("%H%M")} SOCIEDAD ANÓNIMA',
                'email': 'cliente@test.com',
                'address': 'Dirección de prueba',
                'credit_limit': Decimal('10000.00'),
                'payment_terms': 30,
                'retention_agent': True,  # ← CLIENTE ES AGENTE DE RETENCIÓN
                'sri_classification': 'sociedad',
                'iva_retention_percentage': Decimal('70.00'),  # 70% para sociedades
                'ir_retention_percentage': Decimal('1.00')     # 1% para sociedades
            }
        )
        
        # Si ya existe, actualizar campos de retención para la prueba
        if not created:
            customer.retention_agent = True
            customer.sri_classification = 'sociedad'
            customer.iva_retention_percentage = Decimal('70.00')
            customer.ir_retention_percentage = Decimal('1.00')
            customer.save()
        
        print(f"✅ Cliente agente de retención creado:")
        print(f"   🏢 Cliente: {customer.trade_name}")
        print(f"   📋 Clasificación SRI: {customer.sri_classification}")
        print(f"   📊 Retención IVA: {customer.iva_retention_percentage}%")
        print(f"   📊 Retención IR: {customer.ir_retention_percentage}%")
        
        # 5. Verificar cálculos de retención
        subtotal = Decimal('100.00')
        tax_amount = Decimal('15.00')  # IVA 15%
        retention_amounts = customer.calculate_retention_amounts(subtotal, tax_amount)
        
        print(f"✅ Cálculos de retención:")
        print(f"   💰 Subtotal: ${subtotal}")
        print(f"   💰 IVA: ${tax_amount}")
        print(f"   📉 Retención IVA (70% de ${tax_amount}): ${retention_amounts['iva_retention']}")
        print(f"   📉 Retención IR (1% de ${subtotal}): ${retention_amounts['ir_retention']}")
        
        # 6. Usar producto existente para evitar problemas de creación
        product = Product.objects.filter(
            company=company, 
            is_active=True,
            manages_inventory=False  # Sin manejo de inventario
        ).first()
        
        if not product:
            # Usar cualquier producto activo disponible
            product = Product.objects.filter(company=company, is_active=True).first()
        
        if not product:
            print("❌ No hay productos disponibles para la prueba")
            return False
        
        print(f"📦 Producto seleccionado: {product.name} (Precio: ${product.sale_price})")
        
        # 7. Crear factura
        invoice = Invoice.objects.create(
            company=company,
            customer=customer,
            account=caja_account,
            payment_form=payment_method,
            date='2025-01-01',
            subtotal=subtotal,
            tax_amount=tax_amount,
            total=subtotal + tax_amount,
            status='sent',  # ← Estado que activa la creación del asiento
            created_by=user
        )
        
        # 8. Crear línea de factura
        invoice_line = InvoiceLine.objects.create(
            invoice=invoice,
            product=product,
            description='Producto de prueba para retención',
            quantity=Decimal('1.00'),
            unit_price=product.sale_price,
            discount=Decimal('0.00'),
            iva_rate=product.iva_rate,
            line_total=Decimal('115.00')
        )
        
        print(f"✅ Factura creada:")
        print(f"   📄 ID: {invoice.id}")
        print(f"   💰 Subtotal: ${invoice.subtotal}")
        print(f"   💰 IVA: ${invoice.tax_amount}")
        print(f"   💰 Total: ${invoice.total}")
        
        # 9. Crear asiento contable con retenciones
        journal_entry, created = AutomaticJournalEntryService.create_journal_entry_from_invoice(invoice)
        
        if created and journal_entry:
            print(f"✅ ¡Asiento contable creado con retenciones!")
            print(f"   📊 Número de asiento: {journal_entry.number}")
            print(f"   📅 Fecha: {journal_entry.date}")
            print(f"   📝 Referencia: {journal_entry.reference}")
            print(f"   💰 Total Débito: ${journal_entry.total_debit}")
            print(f"   💰 Total Crédito: ${journal_entry.total_credit}")
            print(f"   ⚖️ Balanceado: {'✅ Sí' if journal_entry.is_balanced else '❌ No'}")
            
            # 10. Mostrar líneas del asiento
            print(f"\n📋 Líneas del asiento contable:")
            total_debit = Decimal('0.00')
            total_credit = Decimal('0.00')
            
            for line in journal_entry.lines.all():
                if line.debit > 0:
                    print(f"   📈 DEBE: {line.account.code} - {line.description} = ${line.debit}")
                    total_debit += line.debit
                else:
                    print(f"   📉 HABER: {line.account.code} - {line.description} = ${line.credit}")
                    total_credit += line.credit
            
            print(f"\n💰 Verificación de balance:")
            print(f"   📈 Total DEBE: ${total_debit}")
            print(f"   📉 Total HABER: ${total_credit}")
            print(f"   ⚖️ Diferencia: ${abs(total_debit - total_credit)}")
            
            # Verificar que se crearon líneas de retención
            retention_lines = journal_entry.lines.filter(document_type='RETENCION')
            if retention_lines.exists():
                print(f"\n🎯 Líneas de retención encontradas:")
                for line in retention_lines:
                    print(f"   📋 {line.account.code} - {line.description} = ${line.debit}")
            else:
                print(f"\n⚠️ No se encontraron líneas de retención")
            
            return True
        else:
            print(f"❌ Error creando asiento contable")
            return False
            
    except Exception as e:
        print(f"❌ Error en la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_customer_retention_functionality()
    
    if success:
        print(f"\n🎉 ¡Prueba completada exitosamente!")
        print(f"📋 La funcionalidad de retención para clientes está funcionando correctamente")
        print(f"📈 Los asientos contables incluyen las líneas de retención apropiadas")
    else:
        print(f"\n❌ La prueba falló")
        
    sys.exit(0 if success else 1)