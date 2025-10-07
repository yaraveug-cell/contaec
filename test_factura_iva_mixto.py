#!/usr/bin/env python3
"""
Script de prueba para factura con productos de diferentes tasas de IVA
Objetivo: Verificar qué cuentas contables se afectan con IVA 15%, 5% y 0%
Fecha: 3 de octubre, 2025
"""
import os
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.companies.models import Company, PaymentMethod
from apps.invoicing.models import Customer, Invoice, InvoiceLine
from apps.inventory.models import Product, Category
from apps.accounting.models import ChartOfAccounts, JournalEntry, JournalEntryLine
from apps.accounting.services import AutomaticJournalEntryService

User = get_user_model()

def test_factura_iva_mixto():
    """
    Crear factura con productos de diferentes tasas de IVA y verificar asientos
    """
    print("🧪 PRUEBA: FACTURA CON IVA MIXTO (15%, 5%, 0%)")
    print("=" * 60)
    
    try:
        # 1. Obtener datos base
        print("\n📋 1. PREPARANDO DATOS DE PRUEBA:")
        print("-" * 50)
        
        user = User.objects.filter(is_active=True).first()
        company = Company.objects.first()
        payment_method = PaymentMethod.objects.filter(is_active=True).first()
        
        if not all([user, company, payment_method]):
            print("❌ Error: Faltan datos básicos (user, company, payment_method)")
            return
        
        print(f"   ✅ Usuario: {user.username}")
        print(f"   ✅ Empresa: {company.trade_name}")
        print(f"   ✅ Método de pago: {payment_method.name}")
        
        # 2. Obtener/crear cliente
        customer, created = Customer.objects.get_or_create(
            company=company,
            identification='1234567890123',
            defaults={
                'customer_type': 'juridical',
                'trade_name': 'Cliente Prueba IVA Mixto S.A.',
                'legal_name': 'Cliente Prueba IVA Mixto S.A.',
                'address': 'Dirección de prueba',
                'email': 'prueba@ejemplo.com',
                'phone': '0999999999'
            }
        )
        print(f"   ✅ Cliente: {customer.trade_name} ({'creado' if created else 'existente'})")
        
        # 3. Obtener cuenta de caja
        caja_account = ChartOfAccounts.objects.filter(
            company=company,
            code__icontains='caja'
        ).first()
        
        if not caja_account:
            # Buscar cualquier cuenta que acepte movimiento para usar como cuenta de cobro
            caja_account = ChartOfAccounts.objects.filter(
                company=company,
                accepts_movement=True
            ).first()
        
        print(f"   ✅ Cuenta de cobro: {caja_account.code if caja_account else 'N/A'} - {caja_account.name if caja_account else 'N/A'}")
        
        # 4. Crear/obtener productos con diferentes tasas de IVA
        print(f"\n📦 2. CREANDO PRODUCTOS CON DIFERENTES TASAS DE IVA:")
        print("-" * 50)
        
        categoria, _ = Category.objects.get_or_create(
            company=company,
            name='Productos Prueba IVA',
            defaults={'description': 'Categoría para prueba de IVA'}
        )
        
        productos_iva = []
        
        # Producto con IVA 15%
        producto_15, created = Product.objects.get_or_create(
            company=company,
            code='TEST-IVA-15',
            defaults={
                'name': 'Producto IVA 15%',
                'description': 'Producto con IVA del 15%',
                'category': categoria,
                'unit_of_measure': 'UND',
                'sale_price': Decimal('100.00'),
                'cost_price': Decimal('70.00'),
                'has_iva': True,
                'iva_rate': Decimal('15.00'),
                'is_active': True
            }
        )
        productos_iva.append((producto_15, Decimal('2.00'), '15%'))
        print(f"   ✅ {producto_15.code} - {producto_15.name} (IVA: {producto_15.iva_rate}%)")
        
        # Producto con IVA 5%
        producto_5, created = Product.objects.get_or_create(
            company=company,
            code='TEST-IVA-5',
            defaults={
                'name': 'Producto IVA 5%',
                'description': 'Producto con IVA del 5%',
                'category': categoria,
                'unit_of_measure': 'UND',
                'sale_price': Decimal('50.00'),
                'cost_price': Decimal('35.00'),
                'has_iva': True,
                'iva_rate': Decimal('5.00'),
                'is_active': True
            }
        )
        productos_iva.append((producto_5, Decimal('3.00'), '5%'))
        print(f"   ✅ {producto_5.code} - {producto_5.name} (IVA: {producto_5.iva_rate}%)")
        
        # Producto sin IVA (0%)
        producto_0, created = Product.objects.get_or_create(
            company=company,
            code='TEST-IVA-0',
            defaults={
                'name': 'Producto Sin IVA',
                'description': 'Producto exento de IVA',
                'category': categoria,
                'unit_of_measure': 'UND',
                'sale_price': Decimal('80.00'),
                'cost_price': Decimal('60.00'),
                'has_iva': False,
                'iva_rate': Decimal('0.00'),
                'is_active': True
            }
        )
        productos_iva.append((producto_0, Decimal('1.00'), '0%'))
        print(f"   ✅ {producto_0.code} - {producto_0.name} (IVA: {producto_0.iva_rate}%)")
        
        # 5. Crear factura
        print(f"\n🧾 3. CREANDO FACTURA CON PRODUCTOS MIXTOS:")
        print("-" * 50)
        
        invoice = Invoice.objects.create(
            company=company,
            customer=customer,
            account=caja_account,
            payment_form=payment_method,
            date='2025-10-03',
            status='draft',  # Empezamos en borrador
            created_by=user
        )
        
        print(f"   ✅ Factura #{invoice.id} creada")
        
        # 6. Agregar líneas de factura
        print(f"\n📝 4. AGREGANDO LÍNEAS DE FACTURA:")
        print("-" * 50)
        
        total_subtotal = Decimal('0.00')
        total_iva = Decimal('0.00')
        
        for producto, cantidad, tipo_iva in productos_iva:
            subtotal_linea = cantidad * producto.sale_price
            iva_linea = subtotal_linea * (producto.iva_rate / Decimal('100'))
            total_linea = subtotal_linea + iva_linea
            
            line = InvoiceLine.objects.create(
                invoice=invoice,
                product=producto,
                description=producto.description,
                quantity=cantidad,
                unit_price=producto.sale_price,
                discount=Decimal('0.00'),
                iva_rate=producto.iva_rate,
                stock=Decimal('100.00')  # Stock disponible para la línea
            )
            
            total_subtotal += subtotal_linea
            total_iva += iva_linea
            
            print(f"   📦 Línea: {producto.name}")
            print(f"      Cantidad: {cantidad}")
            print(f"      Precio unitario: ${producto.sale_price}")
            print(f"      Subtotal: ${subtotal_linea}")
            print(f"      IVA {producto.iva_rate}%: ${iva_linea}")
            print(f"      Total línea: ${total_linea}")
            print()
        
        # Actualizar totales de la factura
        invoice.subtotal = total_subtotal
        invoice.tax_amount = total_iva
        invoice.total = total_subtotal + total_iva
        invoice.save()
        
        print(f"   💰 TOTALES DE LA FACTURA:")
        print(f"      Subtotal: ${invoice.subtotal}")
        print(f"      IVA Total: ${invoice.tax_amount}")
        print(f"      TOTAL: ${invoice.total}")
        
        # 7. Cambiar estado a 'sent' para generar asiento
        print(f"\n📋 5. CAMBIANDO ESTADO A 'SENT' PARA GENERAR ASIENTO:")
        print("-" * 50)
        
        invoice.status = 'sent'
        invoice.save()
        
        # 8. Crear asiento contable manualmente para verificación
        journal_entry, created = AutomaticJournalEntryService.create_journal_entry_from_invoice(invoice)
        
        if created and journal_entry:
            print(f"   ✅ Asiento contable #{journal_entry.number} creado exitosamente")
            
            # 9. Analizar cuentas afectadas
            print(f"\n📊 6. ANÁLISIS DE CUENTAS AFECTADAS:")
            print("-" * 50)
            
            print(f"   📋 Asiento #{journal_entry.number}")
            print(f"   📅 Fecha: {journal_entry.date}")
            print(f"   📝 Referencia: {journal_entry.reference}")
            print(f"   📄 Descripción: {journal_entry.description}")
            print(f"   💰 Total Débito: ${journal_entry.total_debit}")
            print(f"   💰 Total Crédito: ${journal_entry.total_credit}")
            print(f"   ⚖️ Balanceado: {'✅ Sí' if journal_entry.total_debit == journal_entry.total_credit else '❌ No'}")
            print()
            
            lines = journal_entry.lines.all().order_by('-debit', '-credit')
            print(f"   📝 LÍNEAS DEL ASIENTO ({lines.count()}):")
            
            total_debe = Decimal('0.00')
            total_haber = Decimal('0.00')
            
            for i, line in enumerate(lines, 1):
                tipo = 'DEBE' if line.debit > 0 else 'HABER'
                monto = line.debit if line.debit > 0 else line.credit
                
                print(f"      {i}. {tipo}: {line.account.code} - {line.account.name}")
                print(f"         Monto: ${monto}")
                print(f"         Descripción: {line.description}")
                print(f"         Documento: {line.document_type} {line.document_number}")
                print(f"         Auxiliar: {line.auxiliary_code} - {line.auxiliary_name}")
                
                if line.debit > 0:
                    total_debe += line.debit
                else:
                    total_haber += line.credit
                print()
            
            # 10. Desglose de IVA
            print(f"\n🧮 7. DESGLOSE DE IVA POR TARIFAS:")
            print("-" * 50)
            
            iva_breakdown = AutomaticJournalEntryService._calculate_iva_breakdown(invoice)
            for tasa, monto in iva_breakdown.items():
                cuenta_iva = AutomaticJournalEntryService._get_iva_account(company, tasa)
                cuenta_codigo = cuenta_iva.code if cuenta_iva else 'N/A'
                cuenta_nombre = cuenta_iva.name if cuenta_iva else 'No encontrada'
                print(f"   IVA {tasa}%: ${monto}")
                print(f"   Cuenta: {cuenta_codigo} - {cuenta_nombre}")
                print()
            
            # 11. Verificación final
            print(f"\n✅ 8. VERIFICACIÓN FINAL:")
            print("-" * 50)
            print(f"   📋 Factura #{invoice.id} procesada correctamente")
            print(f"   📊 Asiento #{journal_entry.number} balanceado")
            print(f"   💰 Total factura: ${invoice.total}")
            print(f"   ⚖️ Debe = Haber: ${total_debe} = ${total_haber}")
            print(f"   🎯 Diferencia: ${abs(total_debe - total_haber)}")
            
        else:
            print(f"   ❌ Error al crear asiento contable")
            if journal_entry and not created:
                print(f"   ⚠️ Ya existe asiento para esta factura: #{journal_entry.number}")
        
        return invoice, journal_entry
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

def mostrar_mapeo_cuentas():
    """Mostrar el mapeo de cuentas IVA configurado"""
    print(f"\n🗺️ MAPEO DE CUENTAS IVA CONFIGURADO:")
    print("-" * 50)
    
    for tasa, codigo in AutomaticJournalEntryService.IVA_ACCOUNTS_MAPPING.items():
        print(f"   IVA {tasa}%: {codigo if codigo else 'Sin cuenta asignada'}")

def mostrar_cuentas_disponibles():
    """Mostrar cuentas contables disponibles"""
    print(f"\n📋 CUENTAS CONTABLES DISPONIBLES:")
    print("-" * 50)
    
    company = Company.objects.first()
    if company:
        cuentas = ChartOfAccounts.objects.filter(company=company).order_by('code')
        print(f"   Total cuentas: {cuentas.count()}")
        print()
        
        for cuenta in cuentas:
            print(f"   {cuenta.code} - {cuenta.name}")
            print(f"   Tipo: {cuenta.account_type} | Acepta mov: {cuenta.accepts_movement}")
            print()
    else:
        print("   ❌ No hay empresas registradas")

if __name__ == "__main__":
    print("🚀 INICIANDO SCRIPT DE PRUEBA")
    print("=" * 60)
    
    # Mostrar configuración actual
    mostrar_mapeo_cuentas()
    mostrar_cuentas_disponibles()
    
    # Ejecutar prueba principal
    invoice, journal_entry = test_factura_iva_mixto()
    
    if invoice and journal_entry:
        print(f"\n🎉 PRUEBA COMPLETADA EXITOSAMENTE")
        print(f"   📋 Factura ID: {invoice.id}")
        print(f"   📊 Asiento ID: {journal_entry.id}")
    else:
        print(f"\n❌ La prueba no se completó correctamente")
    
    print(f"\n" + "=" * 60)
    print("🏁 FIN DEL SCRIPT")