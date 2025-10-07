#!/usr/bin/env python
"""
Test de contabilidad de inventario
Verifica que las nuevas líneas de costo e inventario se generen correctamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append('c:\\contaec')
django.setup()

from decimal import Decimal
from apps.invoicing.models import Invoice, InvoiceLine, Customer
from apps.inventory.models import Product
from apps.companies.models import Company
from apps.accounting.models import JournalEntry
from apps.accounting.services import AutomaticJournalEntryService
from django.contrib.auth import get_user_model

User = get_user_model()

def test_inventory_accounting():
    """Prueba completa de contabilidad de inventario"""
    
    # Obtener datos de GUEBER
    try:
        company = Company.objects.get(trade_name="GUEBER")
        print(f"🏢 Empresa: {company.trade_name} (Legal: {company.legal_name})")
        
        # Obtener cliente de prueba
        customer = Customer.objects.filter(company=company).first()
        if not customer:
            print("❌ No hay clientes disponibles")
            return
        
        print(f"👤 Cliente: {customer.legal_name}")
        
        # Obtener productos con inventario Y stock disponible
        all_products = Product.objects.filter(
            company=company,
            manages_inventory=True,
            cost_price__gt=0
        )
        
        # Filtrar solo los que tienen stock
        products_with_inventory = []
        for product in all_products:
            if product.get_current_stock() > 0:
                products_with_inventory.append(product)
                if len(products_with_inventory) >= 3:  # Solo necesitamos 3
                    break
        
        if not products_with_inventory:
            print("❌ No hay productos con inventario, costo y stock disponible")
            return
        
        print(f"📦 Productos con inventario: {len(products_with_inventory)}")
        for p in products_with_inventory:
            print(f"   - {p.code}: Costo ${p.cost_price}, Stock: {p.get_current_stock()}")
            print(f"     Cuenta Costo: {p.get_effective_cost_account()}")
            print(f"     Cuenta Inventario: {p.get_effective_inventory_account()}")
        
        # Crear factura de prueba
        user = User.objects.filter(is_superuser=True).first()
        
        # Obtener método de pago EFECTIVO
        from apps.companies.models import PaymentMethod
        payment_form = PaymentMethod.objects.filter(
            company=company,
            name__icontains='efectivo'
        ).first()
        
        if not payment_form:
            print("❌ No se encontró método de pago EFECTIVO")
            return
        
        print(f"💳 Método de pago: {payment_form.name}")
        print(f"💰 Cuenta asociada: {payment_form.parent_account}")
        
        # Crear nueva factura con número único
        import time
        unique_number = f'TEST-INV-{int(time.time())}'
        
        invoice = Invoice.objects.create(
            company=company,
            customer=customer,
            account=payment_form.parent_account,
            payment_form=payment_form,
            date='2024-12-29',
            number=unique_number,
            subtotal=Decimal('0.00'),
            tax_amount=Decimal('0.00'), 
            total=Decimal('0.00'),
            status='draft',
            created_by=user
        )
        
        print(f"🧾 Factura creada: {invoice.number}")
        
        # Agregar líneas de productos con inventario (cantidades pequeñas)
        total_subtotal = Decimal('0.00')
        for i, product in enumerate(products_with_inventory, 1):
            # Usar cantidad 1 para todos para evitar problemas de stock
            quantity = 1
            unit_price = product.sale_price or Decimal('10.00')
            
            line_subtotal = quantity * unit_price
            line_tax = line_subtotal * Decimal('0.15')  # IVA 15%
            
            InvoiceLine.objects.create(
                invoice=invoice,
                product=product,
                description=f"Venta {product.name}",
                quantity=quantity,
                unit_price=unit_price,
                discount=Decimal('0.00'),
                iva_rate=Decimal('15.00')
            )
            
            total_subtotal += line_subtotal
            
            print(f"📋 Línea {i}: {product.code} x {quantity} = ${line_subtotal}")
        
        # Calcular totales de factura
        total_tax = total_subtotal * Decimal('0.15')
        total_amount = total_subtotal + total_tax
        
        invoice.subtotal = total_subtotal
        invoice.tax_amount = total_tax
        invoice.total = total_amount
        invoice.save()
        
        print(f"💰 Totales - Subtotal: ${total_subtotal}, IVA: ${total_tax}, Total: ${total_amount}")
        
        # Cambiar estado para generar asiento automático
        print("\n🔄 Generando asiento contable...")
        print(f"Estado actual: {invoice.status}")
        
        # Llamar al servicio directamente para ver errores
        from apps.accounting.services import AutomaticJournalEntryService
        
        print("📞 Llamando al servicio de asientos directamente...")
        journal_entry, created = AutomaticJournalEntryService.create_journal_entry_from_invoice(invoice)
        
        if journal_entry and created:
            print(f"✅ Asiento creado directamente: {journal_entry.number}")
        elif journal_entry and not created:
            print(f"ℹ️ Asiento ya existía: {journal_entry.number}")
        else:
            print("❌ Error creando asiento - ver logs arriba")
            
        # También cambiar estado de factura
        invoice.status = 'sent'
        invoice.save()
        print(f"Estado cambiado a: {invoice.status}")
        
        # Verificar que se creó el asiento
        journal_entry = JournalEntry.objects.filter(
            reference=f"FAC-{invoice.id}",
            company=company
        ).first()
        
        if journal_entry:
            print(f"✅ Asiento generado: {journal_entry.number}")
            print(f"📝 Descripción: {journal_entry.description}")
            
            # Mostrar todas las líneas del asiento
            print("\n📊 LÍNEAS DEL ASIENTO:")
            debe_total = Decimal('0.00')
            haber_total = Decimal('0.00')
            
            # Agrupar líneas por tipo
            lines_efectivo = []
            lines_ventas = []
            lines_iva = []
            lines_costo = []
            lines_inventario = []
            
            for line in journal_entry.lines.all():
                if line.debit > 0:
                    debe_total += line.debit
                if line.credit > 0:
                    haber_total += line.credit
                
                # Clasificar líneas
                if 'caja' in line.account.name.lower() or 'efectivo' in line.description.lower():
                    lines_efectivo.append(line)
                elif 'venta' in line.account.name.lower():
                    lines_ventas.append(line)
                elif 'iva' in line.account.name.lower():
                    lines_iva.append(line)
                elif 'costo' in line.account.name.lower():
                    lines_costo.append(line)
                elif 'inventario' in line.account.name.lower():
                    lines_inventario.append(line)
            
            # Mostrar líneas organizadas
            print("\n🟢 DÉBITOS:")
            for line in lines_efectivo:
                print(f"   {line.account.code} - {line.account.name}: ${line.debit}")
            for line in lines_costo:
                print(f"   {line.account.code} - {line.account.name}: ${line.debit}")
            
            print("\n🔴 CRÉDITOS:")
            for line in lines_ventas:
                print(f"   {line.account.code} - {line.account.name}: ${line.credit}")
            for line in lines_iva:
                print(f"   {line.account.code} - {line.account.name}: ${line.credit}")
            for line in lines_inventario:
                print(f"   {line.account.code} - {line.account.name}: ${line.credit}")
            
            print(f"\n⚖️ Balance: DEBE ${debe_total} = HABER ${haber_total}")
            
            # Verificar que las líneas de inventario están presentes
            inventory_lines_count = sum(1 for line in journal_entry.lines.all() 
                                      if 'costo' in line.account.name.lower() or 'inventario' in line.account.name.lower())
            
            if inventory_lines_count > 0:
                print(f"✅ INVENTARIO IMPLEMENTADO: {inventory_lines_count} líneas de inventario/costo encontradas")
            else:
                print("❌ PROBLEMA: No se encontraron líneas de inventario/costo")
            
            if debe_total == haber_total:
                print("✅ Asiento balanceado correctamente")
            else:
                print(f"❌ Asiento desbalanceado: diferencia ${abs(debe_total - haber_total)}")
        
        else:
            print("❌ No se generó el asiento contable")
        
        return invoice, journal_entry
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    print("🧪 PRUEBA DE CONTABILIDAD DE INVENTARIO")
    print("=" * 50)
    
    invoice, journal_entry = test_inventory_accounting()
    
    if invoice and journal_entry:
        print(f"\n🎉 PRUEBA EXITOSA")
        print(f"Factura ID: {invoice.id}")
        print(f"Asiento ID: {journal_entry.id}")
    else:
        print(f"\n💥 PRUEBA FALLIDA")