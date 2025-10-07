"""
Script para crear proveedores y facturas de compra de prueba
"""

import os
import django
from decimal import Decimal
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import Company
from apps.suppliers.models import Supplier, PurchaseInvoice, PurchaseInvoiceLine
from apps.inventory.models import Product
from apps.accounting.models import ChartOfAccounts, AccountType
from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_suppliers():
    """Crear proveedores de prueba"""
    
    # Obtener la primera empresa
    company = Company.objects.first()
    if not company:
        print("No hay empresas creadas")
        return
    
    # Obtener cuentas contables
    payable_account = ChartOfAccounts.objects.filter(
        company=company,
        name__icontains='por pagar'
    ).first()
    
    expense_account = ChartOfAccounts.objects.filter(
        company=company,
        name__icontains='gasto'
    ).first()
    
    if not payable_account:
        print("Creando cuenta por pagar...")
        liability_type = AccountType.objects.get(code='LIABILITY')
        payable_account = ChartOfAccounts.objects.create(
            company=company,
            code='2105',
            name='Cuentas por Pagar Proveedores',
            account_type=liability_type,
            level=4,
            is_active=True
        )
    
    if not expense_account:
        print("Creando cuenta de gastos...")
        expense_type = AccountType.objects.get(code='EXPENSE')
        expense_account = ChartOfAccounts.objects.create(
            company=company,
            code='5101',
            name='Gastos de Operación',
            account_type=expense_type,
            level=4,
            is_active=True
        )
    
    # Crear proveedores de prueba
    suppliers_data = [
        {
            'identification': '1792146739001',
            'trade_name': 'IMPORTADORA TOMEBAMBA S.A.',
            'legal_name': 'IMPORTADORA TOMEBAMBA SOCIEDAD ANONIMA',
            'supplier_type': 'juridical',
            'email': 'ventas@tomebamba.com',
            'phone': '023456789',
            'address': 'Av. 10 de Agosto 123, Quito',
            'credit_limit': Decimal('50000.00'),
            'payment_terms': 30,
        },
        {
            'identification': '0992737123001',
            'trade_name': 'DISTRIBUIDORA EL ROSADO CIA. LTDA.',
            'legal_name': 'DISTRIBUIDORA EL ROSADO COMPAÑIA LIMITADA',
            'supplier_type': 'juridical',
            'email': 'compras@elrosado.com.ec',
            'phone': '042567890',
            'address': 'Av. Francisco de Orellana, Guayaquil',
            'credit_limit': Decimal('75000.00'),
            'payment_terms': 15,
        },
        {
            'identification': '1001234567001',
            'trade_name': 'PAPELERIA Y SUMINISTROS ANDINA',
            'legal_name': 'PAPELERIA Y SUMINISTROS ANDINA S.A.',
            'supplier_type': 'juridical',
            'email': 'ventas@andina.ec',
            'phone': '062345678',
            'address': 'Calle Bolivar 456, Cuenca',
            'credit_limit': Decimal('25000.00'),
            'payment_terms': 30,
        },
        {
            'identification': '1717171717',
            'trade_name': 'JUAN PEREZ COMERCIANTE',
            'legal_name': '',
            'supplier_type': 'natural',
            'email': 'juanperez@gmail.com',
            'phone': '0987654321',
            'address': 'Calle Rocafuerte 789, Quito',
            'credit_limit': Decimal('5000.00'),
            'payment_terms': 0,  # Contado
        },
    ]
    
    created_suppliers = []
    
    for supplier_data in suppliers_data:
        supplier, created = Supplier.objects.get_or_create(
            company=company,
            identification=supplier_data['identification'],
            defaults={
                **supplier_data,
                'payable_account': payable_account,
                'expense_account': expense_account,
            }
        )
        
        if created:
            print(f"Proveedor creado: {supplier.trade_name}")
        else:
            print(f"Proveedor ya existe: {supplier.trade_name}")
        
        created_suppliers.append(supplier)
    
    return created_suppliers

def create_test_purchase_invoices():
    """Crear facturas de compra de prueba"""
    
    company = Company.objects.first()
    if not company:
        print("No hay empresas creadas")
        return
    
    user = User.objects.first()
    if not user:
        print("No hay usuarios creados")
        return
    
    suppliers = Supplier.objects.filter(company=company)
    if not suppliers.exists():
        print("No hay proveedores. Creando...")
        suppliers = create_test_suppliers()
    
    # Obtener algunos productos para las facturas
    products = Product.objects.filter(company=company)[:3]
    
    # Obtener cuenta de gastos para líneas sin producto
    expense_account = ChartOfAccounts.objects.filter(
        company=company,
        name__icontains='gasto'
    ).first()
    
    # Datos de facturas de compra
    invoices_data = [
        {
            'supplier': suppliers[0],  # TOMEBAMBA
            'supplier_invoice_number': 'TOM-001-000245',
            'date': date.today() - timedelta(days=5),
            'reference': 'Compra de inventario mensual',
            'status': 'validated',
            'lines': [
                {
                    'product': products[0] if products else None,
                    'description': 'Producto A - Lote 001',
                    'quantity': Decimal('50.00'),
                    'unit_cost': Decimal('125.50'),
                    'iva_rate': Decimal('12.00'),
                },
                {
                    'product': products[1] if len(products) > 1 else None,
                    'description': 'Producto B - Lote 002',
                    'quantity': Decimal('25.00'),
                    'unit_cost': Decimal('89.75'),
                    'iva_rate': Decimal('12.00'),
                },
            ]
        },
        {
            'supplier': suppliers[1],  # EL ROSADO
            'supplier_invoice_number': 'ER-2024-001567',
            'date': date.today() - timedelta(days=3),
            'reference': 'Suministros de oficina',
            'status': 'received',
            'lines': [
                {
                    'product': None,
                    'account': 'expense_account',
                    'description': 'Papel bond A4 - 10 resmas',
                    'quantity': Decimal('10.00'),
                    'unit_cost': Decimal('4.50'),
                    'iva_rate': Decimal('12.00'),
                },
                {
                    'product': None,
                    'account': 'expense_account',
                    'description': 'Tinta para impresora',
                    'quantity': Decimal('5.00'),
                    'unit_cost': Decimal('35.00'),
                    'iva_rate': Decimal('12.00'),
                },
            ]
        },
        {
            'supplier': suppliers[2],  # ANDINA
            'supplier_invoice_number': 'AND-456789',
            'date': date.today() - timedelta(days=1),
            'reference': 'Material de oficina',
            'status': 'draft',
            'lines': [
                {
                    'product': None,
                    'account': 'expense_account',
                    'description': 'Útiles de escritorio varios',
                    'quantity': Decimal('1.00'),
                    'unit_cost': Decimal('125.00'),
                    'iva_rate': Decimal('12.00'),
                },
            ]
        },
        {
            'supplier': suppliers[3],  # JUAN PEREZ
            'supplier_invoice_number': 'JP-001',
            'date': date.today(),
            'reference': 'Servicio de limpieza',
            'status': 'paid',
            'lines': [
                {
                    'product': None,
                    'account': 'expense_account',
                    'description': 'Servicio de limpieza oficina',
                    'quantity': Decimal('1.00'),
                    'unit_cost': Decimal('80.00'),
                    'iva_rate': Decimal('12.00'),
                },
            ]
        },
    ]
    
    created_invoices = []
    
    for invoice_data in invoices_data:
        # Crear o obtener la factura
        invoice, created = PurchaseInvoice.objects.get_or_create(
            company=company,
            supplier=invoice_data['supplier'],
            supplier_invoice_number=invoice_data['supplier_invoice_number'],
            defaults={
                'date': invoice_data['date'],
                'reference': invoice_data['reference'],
                'status': invoice_data['status'],
                'received_by': user
            }
        )
        
        if not created:
            print(f"Factura ya existe: {invoice.internal_number}")
            continue
        
        # Crear las líneas
        for line_data in invoice_data['lines']:
            line_account = None
            if line_data.get('account') == 'expense_account':
                line_account = expense_account
            
            PurchaseInvoiceLine.objects.create(
                purchase_invoice=invoice,
                product=line_data['product'],
                account=line_account,
                description=line_data['description'],
                quantity=line_data['quantity'],
                unit_cost=line_data['unit_cost'],
                iva_rate=line_data['iva_rate']
            )
        
        print(f"Factura de compra creada: {invoice.internal_number} - {invoice.supplier.trade_name}")
        created_invoices.append(invoice)
    
    return created_invoices

if __name__ == '__main__':
    print("Creando datos de prueba para el sistema de proveedores...")
    
    suppliers = create_test_suppliers()
    print(f"\n{len(suppliers)} proveedores procesados")
    
    invoices = create_test_purchase_invoices()
    print(f"{len(invoices)} facturas de compra creadas")
    
    print("\n✅ Datos de prueba creados exitosamente!")
    print("\nPuedes acceder al admin en:")
    print("- Proveedores: /admin/suppliers/supplier/")
    print("- Facturas de Compra: /admin/suppliers/purchaseinvoice/")