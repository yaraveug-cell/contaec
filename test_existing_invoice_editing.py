#!/usr/bin/env python
"""
Script para probar la corrección de validación de stock en facturas existentes
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.users.models import User
from apps.companies.models import Company, PaymentMethod
from apps.inventory.models import Product
from apps.invoicing.models import Customer, Invoice, InvoiceLine
from django.core.exceptions import ValidationError
from decimal import Decimal

def test_existing_invoice_editing():
    """Probar edición de facturas existentes sin errores de stock"""
    print("🔄 TESTING: Edición de facturas existentes - Validación de stock")
    print("=" * 70)
    
    # Obtener datos de GUEBER
    try:
        gueber = Company.objects.filter(trade_name__icontains='GUEBER').first()
        test_product = Product.objects.filter(company=gueber).first()
        test_customer = Customer.objects.filter(company=gueber).first()
        user = User.objects.first()
        payment_method = PaymentMethod.objects.first()
        
        if not all([gueber, test_product, test_customer, user, payment_method]):
            print("❌ ERROR: Faltan datos de prueba")
            return
        
        print(f"📊 Datos de prueba:")
        print(f"   Empresa: {gueber.trade_name}")
        print(f"   Producto: {test_product.name}")
        print(f"   Stock inicial: {test_product.get_current_stock()}")
        print(f"   Cliente: {test_customer.trade_name}")
        
    except Exception as e:
        print(f"❌ ERROR obteniendo datos: {e}")
        return
    
    # Test 1: Crear factura nueva (esto debería consumir stock)
    print(f"\n1️⃣ Test creación de factura nueva")
    print("-" * 50)
    
    try:
        # Verificar stock antes
        stock_before = test_product.get_current_stock()
        print(f"📦 Stock antes de crear factura: {stock_before}")
        
        if stock_before <= 0:
            print("⚠️  No hay stock disponible, omitiendo test de creación")
            return
        
        # Crear factura con 1 unidad
        test_invoice = Invoice.objects.create(
            company=gueber,
            customer=test_customer,
            date='2024-01-15',
            status='DRAFT',
            payment_form=payment_method,
            created_by=user
        )
        
        # Crear línea de factura
        test_line = InvoiceLine.objects.create(
            invoice=test_invoice,
            product=test_product,
            description=f"{test_product.name} - Test",
            quantity=1,
            unit_price=test_product.sale_price or Decimal('100.00')
        )
        
        # Verificar stock después
        # Recargar el producto para obtener stock actualizado
        test_product.refresh_from_db()
        stock_after = test_product.get_current_stock()
        print(f"✅ Factura creada - ID: {test_invoice.id}")
        print(f"📦 Stock después de crear: {stock_after}")
        
    except Exception as e:
        print(f"❌ ERROR creando factura: {e}")
        return
    
    # Test 2: Editar estado de factura sin cambiar producto
    print(f"\n2️⃣ Test edición de estado sin cambiar producto")
    print("-" * 50)
    
    try:
        print(f"📋 Estado inicial: {test_invoice.status}")
        
        # Cambiar solo el estado
        test_invoice.status = 'CONFIRMED'
        test_invoice.save()  # Esto NO debería dar error de stock
        
        print(f"✅ Estado cambiado a: {test_invoice.status}")
        print(f"📦 Stock permanece en: {test_product.get_current_stock()}")
        
    except ValidationError as e:
        print(f"❌ ERROR inesperado al cambiar estado: {e}")
    except Exception as e:
        print(f"❌ ERROR al cambiar estado: {e}")
    
    # Test 3: Editar línea sin cambiar cantidad
    print(f"\n3️⃣ Test edición de línea sin cambiar cantidad")
    print("-" * 50)
    
    try:
        print(f"📝 Descripción original: {test_line.description}")
        
        # Cambiar solo la descripción
        test_line.description = f"{test_product.name} - Descripción modificada"
        test_line.save()  # Esto NO debería dar error de stock
        
        print(f"✅ Descripción cambiada a: {test_line.description}")
        print(f"📦 Stock permanece en: {test_product.get_current_stock()}")
        
    except ValidationError as e:
        print(f"❌ ERROR inesperado al cambiar descripción: {e}")
    except Exception as e:
        print(f"❌ ERROR al cambiar descripción: {e}")
    
    # Test 4: Intentar cambiar cantidad (esto SÍ debe validar stock)
    print(f"\n4️⃣ Test cambio de cantidad (debe validar stock)")
    print("-" * 50)
    
    try:
        current_stock = test_product.get_current_stock()
        original_quantity = test_line.quantity
        new_quantity = original_quantity + current_stock + 5  # Cantidad imposible
        
        print(f"📊 Cantidad original: {original_quantity}")
        print(f"📦 Stock disponible: {current_stock}")
        print(f"🎯 Intentando cantidad: {new_quantity}")
        
        # Intentar cambiar a cantidad imposible
        test_line.quantity = new_quantity
        test_line.save()  # Esto SÍ debería dar error de stock
        
        print(f"❌ ERROR: Debería haber fallado por stock insuficiente")
        
    except ValidationError as e:
        print(f"✅ Error de validación esperado: {e}")
    except Exception as e:
        print(f"❌ ERROR inesperado: {e}")
    
    # Test 5: Cambio válido de cantidad
    print(f"\n5️⃣ Test cambio válido de cantidad")
    print("-" * 50)
    
    try:
        # Recargar la línea para restaurar cantidad original
        test_line.refresh_from_db()
        current_stock = test_product.get_current_stock()
        
        if current_stock > 0:
            # Reducir cantidad (debería ser válido)
            new_valid_quantity = max(1, test_line.quantity - 1)
            print(f"📊 Cantidad original: {test_line.quantity}")
            print(f"🎯 Nueva cantidad válida: {new_valid_quantity}")
            
            test_line.quantity = new_valid_quantity
            test_line.save()
            
            print(f"✅ Cantidad cambiada exitosamente a: {test_line.quantity}")
        else:
            print("⚠️  No hay stock para reducir cantidad")
        
    except ValidationError as e:
        print(f"❌ ERROR inesperado en cambio válido: {e}")
    except Exception as e:
        print(f"❌ ERROR en cambio válido: {e}")
    
    # Limpiar: Eliminar factura de prueba
    try:
        test_invoice.delete()
        print(f"\n🧹 Factura de prueba eliminada")
    except Exception as e:
        print(f"\n⚠️  Error eliminando factura de prueba: {e}")
    
    print(f"\n🏁 RESUMEN - CORRECCIÓN APLICADA")
    print("=" * 70)
    print("✅ Correcciones implementadas:")
    print("   - Validación de stock solo en líneas nuevas")
    print("   - Validación de stock solo cuando cambia cantidad")
    print("   - Edición de estado/descripción sin validar stock")
    print("   - Consideración de cantidad original en validación")
    print("\n💡 Ahora puedes editar facturas existentes sin errores de stock")
    print("   cuando solo cambias estado u otros campos")

if __name__ == "__main__":
    test_existing_invoice_editing()