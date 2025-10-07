"""
Script para configurar empresa GUEBER y usuario Yolanda con seguridad apropiada
"""

import os
import django
from decimal import Decimal
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import Company, CompanyUser
from apps.suppliers.models import Supplier, PurchaseInvoice, PurchaseInvoiceLine
from apps.inventory.models import Product
from apps.accounting.models import ChartOfAccounts, AccountType
from django.contrib.auth import get_user_model

User = get_user_model()

def setup_gueber_company_and_user():
    """Configurar empresa GUEBER y usuario Yolanda"""
    
    print("🏢 CONFIGURACIÓN DE EMPRESA GUEBER Y USUARIO YOLANDA")
    print("=" * 55)
    
    # Buscar o crear empresa GUEBER
    gueber_company, created = Company.objects.get_or_create(
        trade_name='GUEBER',
        defaults={
            'legal_name': 'GUEBER SOCIEDAD ANONIMA',
            'ruc': '1792146740001',
            'establishment_code': '001',
            'emission_point': '001',
            'address': 'Av. Amazonas 123, Quito, Ecuador',
            'phone': '022345678',
            'email': 'info@gueber.com.ec'
        }
    )
    
    if created:
        print(f"✅ Empresa GUEBER creada: {gueber_company.trade_name}")
        
        # Configurar campos adicionales requeridos
        from apps.core.models import City, Currency
        from apps.companies.models import CompanyType, EconomicActivity
        
        # Obtener o crear datos necesarios
        city = City.objects.first()
        currency = Currency.objects.filter(code='USD').first()
        company_type = CompanyType.objects.first()
        activity = EconomicActivity.objects.first()
        
        if city and currency and company_type and activity:
            gueber_company.city = city
            gueber_company.base_currency = currency
            gueber_company.company_type = company_type
            gueber_company.primary_activity = activity
            gueber_company.save()
            print(f"   Configuración completada para {gueber_company.trade_name}")
        
    else:
        print(f"✅ Empresa GUEBER ya existe: {gueber_company.trade_name}")
    
    # Buscar o crear usuario Yolanda
    yolanda_user, created = User.objects.get_or_create(
        email='yolanda@gueber.com.ec',
        defaults={
            'first_name': 'Yolanda',
            'last_name': 'González',
            'is_staff': True,
            'is_active': True
        }
    )
    
    if created:
        yolanda_user.set_password('yolanda123')
        yolanda_user.save()
        print(f"✅ Usuario Yolanda creado: {yolanda_user.full_name}")
    else:
        print(f"✅ Usuario Yolanda ya existe: {yolanda_user.full_name}")
    
    # Asignar usuario a empresa GUEBER
    company_user, created = CompanyUser.objects.get_or_create(
        user=yolanda_user,
        company=gueber_company,
        defaults={
            'role': 'admin'  # Rol de administradora
        }
    )
    
    if created:
        print(f"✅ Yolanda asignada como admin de GUEBER")
    else:
        print(f"✅ Yolanda ya está asignada a GUEBER como {company_user.get_role_display()}")
    
    return gueber_company, yolanda_user

def create_gueber_chart_of_accounts(company):
    """Crear plan de cuentas para GUEBER"""
    
    print("\n📊 CREANDO PLAN DE CUENTAS PARA GUEBER")
    print("=" * 45)
    
    # Obtener tipos de cuenta
    asset_type = AccountType.objects.get(code='ASSET')
    liability_type = AccountType.objects.get(code='LIABILITY')
    expense_type = AccountType.objects.get(code='EXPENSE')
    
    accounts_to_create = [
        {
            'code': '2105',
            'name': 'Cuentas por Pagar Proveedores',
            'account_type': liability_type,
            'level': 4
        },
        {
            'code': '5101',
            'name': 'Gastos de Operación',
            'account_type': expense_type,
            'level': 4
        },
        {
            'code': '1125',
            'name': 'IVA por Recuperar',
            'account_type': asset_type,
            'level': 4
        },
        {
            'code': '5201',
            'name': 'Gastos Administrativos',
            'account_type': expense_type,
            'level': 4
        },
        {
            'code': '5301',
            'name': 'Gastos de Ventas',
            'account_type': expense_type,
            'level': 4
        }
    ]
    
    created_accounts = []
    
    for account_data in accounts_to_create:
        account, created = ChartOfAccounts.objects.get_or_create(
            company=company,
            code=account_data['code'],
            defaults={
                'name': account_data['name'],
                'account_type': account_data['account_type'],
                'level': account_data['level'],
                'is_active': True
            }
        )
        
        if created:
            print(f"   ✅ Cuenta creada: {account.code} - {account.name}")
        else:
            print(f"   📋 Cuenta existe: {account.code} - {account.name}")
        
        created_accounts.append(account)
    
    return created_accounts

def create_gueber_suppliers(company, user):
    """Crear proveedores para GUEBER"""
    
    print("\n👥 CREANDO PROVEEDORES PARA GUEBER")
    print("=" * 40)
    
    # Obtener cuentas contables
    payable_account = ChartOfAccounts.objects.filter(
        company=company,
        name__icontains='por pagar'
    ).first()
    
    expense_account = ChartOfAccounts.objects.filter(
        company=company,
        name__icontains='operación'
    ).first()
    
    suppliers_data = [
        {
            'identification': '1792146741001',
            'trade_name': 'DISTRIBUIDORA ANDINA S.A.',
            'legal_name': 'DISTRIBUIDORA ANDINA SOCIEDAD ANONIMA',
            'supplier_type': 'juridical',
            'email': 'ventas@andina.com.ec',
            'phone': '023456789',
            'address': 'Av. 6 de Diciembre 456, Quito',
            'credit_limit': Decimal('75000.00'),
            'payment_terms': 30,
        },
        {
            'identification': '0992737124001',
            'trade_name': 'COMERCIAL DEL PACIFICO CIA. LTDA.',
            'legal_name': 'COMERCIAL DEL PACIFICO COMPAÑIA LIMITADA',
            'supplier_type': 'juridical',
            'email': 'compras@pacifico.com.ec',
            'phone': '042567891',
            'address': 'Av. 9 de Octubre 789, Guayaquil',
            'credit_limit': Decimal('50000.00'),
            'payment_terms': 15,
        },
        {
            'identification': '1001234568001',
            'trade_name': 'SUMINISTROS EMPRESARIALES DEL NORTE',
            'legal_name': 'SUMINISTROS EMPRESARIALES DEL NORTE S.A.',
            'supplier_type': 'juridical',
            'email': 'ventas@sumnorte.ec',
            'phone': '062345679',
            'address': 'Calle Sucre 321, Ibarra',
            'credit_limit': Decimal('30000.00'),
            'payment_terms': 30,
        },
        {
            'identification': '1717171718',
            'trade_name': 'MARIA FERNANDEZ SERVICIOS',
            'legal_name': '',
            'supplier_type': 'natural',
            'email': 'maria.fernandez@gmail.com',
            'phone': '0987654322',
            'address': 'Calle Mejía 654, Quito',
            'credit_limit': Decimal('8000.00'),
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
            print(f"   ✅ Proveedor creado: {supplier.trade_name}")
        else:
            print(f"   📋 Proveedor existe: {supplier.trade_name}")
        
        created_suppliers.append(supplier)
    
    return created_suppliers

def create_gueber_purchase_invoices(company, user, suppliers):
    """Crear facturas de compra de prueba para GUEBER"""
    
    print("\n🧾 CREANDO FACTURAS DE COMPRA PARA GUEBER")
    print("=" * 47)
    
    # Obtener cuenta de gastos para líneas
    expense_account = ChartOfAccounts.objects.filter(
        company=company,
        name__icontains='operación'
    ).first()
    
    # Datos de facturas de compra
    invoices_data = [
        {
            'supplier': suppliers[0],  # DISTRIBUIDORA ANDINA
            'supplier_invoice_number': 'AND-2024-001234',
            'date': date.today() - timedelta(days=7),
            'reference': 'Suministros de oficina mensuales',
            'status': 'validated',
            'lines': [
                {
                    'description': 'Papel bond A4 - 20 resmas',
                    'quantity': Decimal('20.00'),
                    'unit_cost': Decimal('4.25'),
                    'iva_rate': Decimal('12.00'),
                },
                {
                    'description': 'Carpetas archivadoras',
                    'quantity': Decimal('50.00'),
                    'unit_cost': Decimal('2.80'),
                    'iva_rate': Decimal('12.00'),
                },
            ]
        },
        {
            'supplier': suppliers[1],  # COMERCIAL DEL PACIFICO
            'supplier_invoice_number': 'PAC-456789',
            'date': date.today() - timedelta(days=4),
            'reference': 'Equipos y suministros tecnológicos',
            'status': 'received',
            'lines': [
                {
                    'description': 'Tóner para impresoras HP',
                    'quantity': Decimal('8.00'),
                    'unit_cost': Decimal('45.50'),
                    'iva_rate': Decimal('12.00'),
                },
                {
                    'description': 'Cables de red CAT6',
                    'quantity': Decimal('15.00'),
                    'unit_cost': Decimal('12.75'),
                    'iva_rate': Decimal('12.00'),
                },
            ]
        },
        {
            'supplier': suppliers[2],  # SUMINISTROS DEL NORTE
            'supplier_invoice_number': 'SN-2024-789',
            'date': date.today() - timedelta(days=2),
            'reference': 'Material de limpieza y mantenimiento',
            'status': 'draft',
            'lines': [
                {
                    'description': 'Productos de limpieza varios',
                    'quantity': Decimal('1.00'),
                    'unit_cost': Decimal('150.00'),
                    'iva_rate': Decimal('12.00'),
                },
            ]
        },
        {
            'supplier': suppliers[3],  # MARIA FERNANDEZ
            'supplier_invoice_number': 'MF-001',
            'date': date.today(),
            'reference': 'Servicio de limpieza semanal',
            'status': 'paid',
            'lines': [
                {
                    'description': 'Servicio de limpieza oficinas',
                    'quantity': Decimal('1.00'),
                    'unit_cost': Decimal('120.00'),
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
            print(f"   📋 Factura existe: {invoice.internal_number}")
            continue
        
        # Crear las líneas
        for line_data in invoice_data['lines']:
            PurchaseInvoiceLine.objects.create(
                purchase_invoice=invoice,
                account=expense_account,
                description=line_data['description'],
                quantity=line_data['quantity'],
                unit_cost=line_data['unit_cost'],
                iva_rate=line_data['iva_rate']
            )
        
        print(f"   ✅ Factura creada: {invoice.internal_number} - {invoice.supplier.trade_name} - ${invoice.total}")
        created_invoices.append(invoice)
    
    return created_invoices

if __name__ == '__main__':
    print("🚀 CONFIGURACIÓN COMPLETA PARA GUEBER Y YOLANDA")
    print("=" * 55)
    
    # Configurar empresa y usuario
    company, user = setup_gueber_company_and_user()
    
    # Crear plan de cuentas
    accounts = create_gueber_chart_of_accounts(company)
    
    # Crear proveedores
    suppliers = create_gueber_suppliers(company, user)
    
    # Crear facturas de compra
    invoices = create_gueber_purchase_invoices(company, user, suppliers)
    
    print(f"\n✅ CONFIGURACIÓN COMPLETADA PARA GUEBER")
    print(f"   👤 Usuario: {user.full_name} ({user.email})")
    print(f"   🏢 Empresa: {company.trade_name}")
    print(f"   📊 Cuentas creadas: {len(accounts)}")
    print(f"   👥 Proveedores: {len(suppliers)}")
    print(f"   🧾 Facturas: {len(invoices)}")
    
    print(f"\n🔐 ACCESO AL SISTEMA:")
    print(f"   Email: yolanda@gueber.com.ec")
    print(f"   Password: yolanda123")
    print(f"   URL Admin: http://127.0.0.1:8000/admin/")
    print(f"   URL Dashboard: http://127.0.0.1:8000/dashboard/")