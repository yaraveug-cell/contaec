"""
Script simple para probar la funcionalidad de asientos contables
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from decimal import Decimal
from apps.invoicing.models import Invoice, Customer
from apps.companies.models import Company, PaymentMethod
from apps.accounting.models import ChartOfAccounts, JournalEntry
from apps.accounting.services import AutomaticJournalEntryService
from django.contrib.auth import get_user_model

User = get_user_model()

def test_journal_entry_service():
    """Prueba básica del servicio de asientos contables"""
    
    print("🚀 Iniciando prueba del servicio de asientos contables...")
    
    try:
        # Buscar empresa con cuentas contables
        company = Company.objects.filter(legal_name="Yolanda Bermeo").first()
        if not company:
            company = Company.objects.first()
        if not company:
            print("❌ No se encontró ninguna empresa")
            return False
            
        customer = Customer.objects.filter(company=company).first()
        if not customer:
            print("❌ No se encontró ningún cliente")
            return False
            
        payment_method = PaymentMethod.objects.filter(is_active=True).first()
        if not payment_method:
            print("❌ No se encontró ningún método de pago")
            return False
            
        account = ChartOfAccounts.objects.filter(
            company=company, 
            accepts_movement=True
        ).first()
        if not account:
            print("❌ No se encontró ninguna cuenta que acepte movimientos")
            return False
            
        user = User.objects.first()
        if not user:
            print("❌ No se encontró ningún usuario")
            return False
        
        print(f"✅ Datos encontrados:")
        print(f"   📄 Empresa: {company.legal_name}")
        print(f"   👤 Cliente: {customer.trade_name}")
        print(f"   💳 Método de pago: {payment_method.name}")
        print(f"   🏦 Cuenta: {account.code} - {account.name}")
        
        # Crear factura de prueba
        invoice = Invoice.objects.create(
            company=company,
            customer=customer,
            account=account,
            payment_form=payment_method,
            subtotal=Decimal('100.00'),
            tax_amount=Decimal('15.00'),
            total=Decimal('115.00'),
            status='sent',  # Estado que activa la creación del asiento
            created_by=user
        )
        
        print(f"✅ Factura de prueba creada: ID {invoice.id}")
        
        # Buscar un producto existente
        from apps.inventory.models import Product
        from apps.invoicing.models import InvoiceLine
        
        product = Product.objects.filter(company=company).first()
        if not product:
            print("❌ No se encontró ningún producto para la empresa")
            invoice.delete()
            return False
        
        # Crear línea de factura (necesario para que tenga total > 0)
        line = InvoiceLine.objects.create(
            invoice=invoice,
            product=product,
            description="Producto de prueba",
            quantity=Decimal('1.00'),
            unit_price=Decimal('100.00'),
            discount=Decimal('0.00'),
            iva_rate=Decimal('15.00'),
            line_total=Decimal('115.00')
        )
        
        # Recalcular totales de la factura
        invoice.calculate_totals()
        invoice.refresh_from_db()
        
        print(f"✅ Línea de factura creada")
        print(f"   💰 Total recalculado: ${invoice.total}")
        
        # Probar creación de asiento
        journal_entry, created = AutomaticJournalEntryService.create_journal_entry_from_invoice(invoice)
        
        if created and journal_entry:
            print(f"✅ ¡Asiento contable creado exitosamente!")
            print(f"   📊 Número de asiento: {journal_entry.number}")
            print(f"   📅 Fecha: {journal_entry.date}")
            print(f"   📝 Referencia: {journal_entry.reference}")
            print(f"   💰 Total Débito: ${journal_entry.total_debit}")
            print(f"   💰 Total Crédito: ${journal_entry.total_credit}")
            print(f"   ⚖️ Balanceado: {'✅ Sí' if journal_entry.is_balanced else '❌ No'}")
            
            # Mostrar líneas del asiento
            print(f"   📋 Líneas del asiento:")
            for line in journal_entry.lines.all():
                tipo = "DEBE" if line.debit > 0 else "HABER"
                monto = line.debit if line.debit > 0 else line.credit
                print(f"      {tipo}: {line.account.code} - ${monto} - {line.description}")
            
            # Limpiar - eliminar factura de prueba
            invoice.delete()
            journal_entry.delete()
            print(f"🧹 Datos de prueba limpiados")
            
            return True
            
        elif journal_entry and not created:
            print(f"⚠️ El asiento ya existía: {journal_entry.number}")
            invoice.delete()
            return True
        else:
            print(f"❌ No se pudo crear el asiento contable")
            invoice.delete()
            return False
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_journal_entry_service()
    
    if success:
        print(f"\n🎉 ¡Prueba completada exitosamente!")
        print(f"📋 El servicio de asientos contables está funcionando correctamente")
    else:
        print(f"\n❌ La prueba falló")
        
    sys.exit(0 if success else 1)