#!/usr/bin/env python3
"""
Test: Verificar cálculo automático de totales al crear factura nueva
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append('.')
django.setup()

def test_invoice_totals_calculation():
    """Test de cálculo automático de totales en nueva factura"""
    
    from apps.invoicing.models import Invoice, InvoiceLine, Customer
    from apps.companies.models import Company, PaymentMethod
    from apps.inventory.models import Product
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from decimal import Decimal
    
    User = get_user_model()
    
    print("🧪 TEST: CÁLCULO AUTOMÁTICO DE TOTALES")
    print("=" * 50)
    
    try:
        # 1. Obtener datos necesarios
        print("📋 OBTENIENDO DATOS NECESARIOS:")
        
        user = User.objects.first()
        company = Company.objects.first()
        customer = Customer.objects.filter(company=company).first()
        payment_method = PaymentMethod.objects.filter(name__icontains='efectivo').first()
        
        # Obtener o crear un producto
        product = Product.objects.filter(company=company, is_active=True).first()
        if not product:
            product = Product.objects.create(
                company=company,
                code='TEST001',
                name='Producto de Prueba',
                description='Producto para test de totales',
                product_type='product',
                sale_price=Decimal('100.00'),
                cost_price=Decimal('50.00'),
                iva_rate=Decimal('15.00'),
                is_active=True,
                manages_inventory=False
            )
            print(f"   ✅ Producto creado: {product.name}")
        else:
            print(f"   ✅ Producto: {product.name}")
        
        print(f"   ✅ Usuario: {user.username}")
        print(f"   ✅ Empresa: {company.trade_name}")
        print(f"   ✅ Cliente: {customer.trade_name}")
        print(f"   ✅ Método de pago: {payment_method.name}")
        
        # 2. Crear nueva factura (SIN líneas aún)
        print(f"\n💾 CREANDO NUEVA FACTURA:")
        
        invoice = Invoice.objects.create(
            company=company,
            customer=customer,
            date=timezone.now().date(),
            payment_form=payment_method,
            status='draft',
            created_by=user
        )
        
        print(f"   ✅ Factura creada: {invoice.number}")
        print(f"   📊 Totales iniciales:")
        print(f"      Subtotal: {invoice.subtotal}")
        print(f"      Impuestos: {invoice.tax_amount}")
        print(f"      Total: {invoice.total}")
        
        # 3. Agregar líneas a la factura
        print(f"\n📝 AGREGANDO LÍNEAS A LA FACTURA:")
        
        # Línea 1: 2 unidades a $100 c/u, 15% IVA
        line1 = InvoiceLine.objects.create(
            invoice=invoice,
            product=product,
            description=product.name,
            quantity=Decimal('2.00'),
            unit_price=Decimal('100.00'),
            discount=Decimal('0.00'),
            iva_rate=Decimal('15.00')
        )
        
        print(f"   ✅ Línea 1: 2 x $100.00 (15% IVA)")
        print(f"      Total línea: ${line1.line_total}")
        
        # Recargar factura para ver totales actualizados
        invoice.refresh_from_db()
        print(f"\n   📊 Totales después de línea 1:")
        print(f"      Subtotal: ${invoice.subtotal}")
        print(f"      Impuestos: ${invoice.tax_amount}")
        print(f"      Total: ${invoice.total}")
        
        # Línea 2: 1 unidad a $50, 10% descuento, 15% IVA
        line2 = InvoiceLine.objects.create(
            invoice=invoice,
            product=product,
            description=f"{product.name} - Línea 2",
            quantity=Decimal('1.00'),
            unit_price=Decimal('50.00'),
            discount=Decimal('10.00'),  # 10% descuento
            iva_rate=Decimal('15.00')
        )
        
        print(f"   ✅ Línea 2: 1 x $50.00 (10% desc, 15% IVA)")
        print(f"      Total línea: ${line2.line_total}")
        
        # Recargar factura para ver totales finales
        invoice.refresh_from_db()
        print(f"\n   📊 Totales finales:")
        print(f"      Subtotal: ${invoice.subtotal}")
        print(f"      Impuestos: ${invoice.tax_amount}")
        print(f"      Total: ${invoice.total}")
        
        # 4. Verificar cálculos manuales
        print(f"\n🧮 VERIFICACIÓN MANUAL:")
        
        # Línea 1: 2 x $100 = $200 (sin desc) + 15% IVA = $230
        line1_subtotal = Decimal('2.00') * Decimal('100.00')
        line1_iva = line1_subtotal * (Decimal('15.00') / 100)
        line1_expected = line1_subtotal + line1_iva
        
        print(f"   Línea 1: ${line1_subtotal} + ${line1_iva} = ${line1_expected}")
        
        # Línea 2: 1 x $50 - 10% desc = $45 + 15% IVA = $51.75
        line2_base = Decimal('1.00') * Decimal('50.00')
        line2_discount = line2_base * (Decimal('10.00') / 100)
        line2_subtotal = line2_base - line2_discount
        line2_iva = line2_subtotal * (Decimal('15.00') / 100)
        line2_expected = line2_subtotal + line2_iva
        
        print(f"   Línea 2: ${line2_base} - ${line2_discount} + ${line2_iva} = ${line2_expected}")
        
        # Totales esperados
        expected_subtotal = line1_subtotal + line2_subtotal
        expected_tax = line1_iva + line2_iva
        expected_total = expected_subtotal + expected_tax
        
        print(f"   📊 Esperado:")
        print(f"      Subtotal: ${expected_subtotal}")
        print(f"      Impuestos: ${expected_tax}")
        print(f"      Total: ${expected_total}")
        
        # 5. Comparar resultados
        print(f"\n🎯 COMPARACIÓN:")
        
        subtotal_ok = abs(invoice.subtotal - expected_subtotal) < Decimal('0.01')
        tax_ok = abs(invoice.tax_amount - expected_tax) < Decimal('0.01')
        total_ok = abs(invoice.total - expected_total) < Decimal('0.01')
        
        print(f"   Subtotal: {'✅' if subtotal_ok else '❌'} (BD: ${invoice.subtotal}, Esperado: ${expected_subtotal})")
        print(f"   Impuestos: {'✅' if tax_ok else '❌'} (BD: ${invoice.tax_amount}, Esperado: ${expected_tax})")
        print(f"   Total: {'✅' if total_ok else '❌'} (BD: ${invoice.total}, Esperado: ${expected_total})")
        
        # 6. Resultado final
        print(f"\n🏆 RESULTADO:")
        if subtotal_ok and tax_ok and total_ok:
            print(f"   ✅ CÁLCULOS CORRECTOS")
            print(f"   ✅ Los totales se actualizan automáticamente al crear factura")
            print(f"   ✅ Los totales se recalculan al agregar líneas")
            return True
        else:
            print(f"   ❌ PROBLEMA EN LOS CÁLCULOS")
            print(f"   ❌ Los totales no se están calculando correctamente")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE EL TEST:")
        print(f"   Error: {str(e)}")
        
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_invoice_totals_calculation()
    if success:
        print(f"\n🎉 TEST EXITOSO - Los totales se calculan automáticamente")
    else:
        print(f"\n💥 TEST FALLIDO - Revisar cálculos de totales")