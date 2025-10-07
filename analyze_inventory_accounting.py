"""
Análisis del sistema de inventario y cuentas contables en facturas de venta
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import Company, CompanyAccountDefaults
from apps.accounting.models import ChartOfAccounts, JournalEntry, JournalEntryLine
from apps.accounting.services import AutomaticJournalEntryService
from apps.inventory.models import Product, Category
from apps.invoicing.models import Invoice, InvoiceLine
from decimal import Decimal

def analyze_inventory_accounting_system():
    """Analizar si el sistema maneja cuentas de inventario en asientos de venta"""
    print("🔍 ANÁLISIS: Sistema de Inventario y Cuentas Contables en Facturas")
    print("=" * 80)
    
    # Obtener empresa GUEBER
    gueber = Company.objects.filter(trade_name__icontains='GUEBER').first()
    if not gueber:
        print("❌ Empresa GUEBER no encontrada")
        return False
    
    print(f"🏢 Empresa: {gueber.trade_name}")
    
    # ==========================================
    # 1. ANÁLISIS DEL SISTEMA ACTUAL DE ASIENTOS
    # ==========================================
    print(f"\\n1️⃣ ANÁLISIS DEL SISTEMA ACTUAL DE ASIENTOS")
    print("-" * 60)
    
    print(f"\\n📋 ESTRUCTURA ACTUAL DE ASIENTOS DE VENTA:")
    print(f"   DEBE:")
    print(f"   • Cuenta seleccionada en factura (Caja/Banco/Por Cobrar)")
    print(f"   • Retenciones IVA por cobrar (si cliente es agente)")
    print(f"   • Retenciones IR por cobrar (si cliente es agente)")
    print(f"   ")
    print(f"   HABER:")
    print(f"   • Cuenta de ventas (configurada por empresa/categoría)")
    print(f"   • IVA por pagar (por cada tarifa)")
    
    print(f"\\n❌ LO QUE FALTA:")
    print(f"   DEBE: Costo de mercadería vendida (CMV/COGS)")
    print(f"   HABER: Inventario/Mercaderías")
    
    # ==========================================
    # 2. VERIFICAR CONFIGURACIÓN DE CUENTAS DE INVENTARIO
    # ==========================================
    print(f"\\n2️⃣ CONFIGURACIÓN DE CUENTAS DE INVENTARIO")
    print("-" * 60)
    
    # Verificar CompanyAccountDefaults
    defaults = CompanyAccountDefaults.objects.filter(company=gueber).first()
    if defaults:
        print(f"\\n✅ CompanyAccountDefaults configurado:")
        
        # Verificar si tiene cuentas de inventario/costo
        inventory_fields = [
            ('default_inventory_account', 'Cuenta de Inventario'),
            ('default_cost_account', 'Cuenta de Costo de Ventas')
        ]
        
        for field_name, description in inventory_fields:
            if hasattr(defaults, field_name):
                account = getattr(defaults, field_name, None)
                if account:
                    print(f"   ✅ {description}: {account.code} - {account.name}")
                else:
                    print(f"   ❌ {description}: No configurada")
            else:
                print(f"   ❌ {description}: Campo no existe en modelo")
    else:
        print(f"\\n❌ CompanyAccountDefaults no configurado")
    
    # Verificar categorías con cuentas de inventario
    categories = Category.objects.filter(company=gueber)
    print(f"\\n📦 CATEGORÍAS DE PRODUCTOS ({categories.count()}):")
    
    for category in categories:
        print(f"\\n   📂 {category.name}:")
        
        accounts_config = [
            ('default_sales_account', 'Ventas'),
            ('default_cost_account', 'Costo'),  
            ('default_inventory_account', 'Inventario')
        ]
        
        for field_name, account_type in accounts_config:
            account = getattr(category, field_name, None)
            if account:
                print(f"      ✅ {account_type}: {account.code} - {account.name}")
            else:
                print(f"      ❌ {account_type}: No configurada")
    
    # ==========================================
    # 3. VERIFICAR PRODUCTOS CON GESTIÓN DE INVENTARIO
    # ==========================================
    print(f"\\n3️⃣ PRODUCTOS CON GESTIÓN DE INVENTARIO")
    print("-" * 60)
    
    inventory_products = Product.objects.filter(
        company=gueber,
        manages_inventory=True,
        is_active=True
    )
    
    print(f"\\n📊 Productos que manejan inventario: {inventory_products.count()}")
    
    if inventory_products.exists():
        print(f"\\n📋 MUESTRA DE PRODUCTOS CON INVENTARIO:")
        for product in inventory_products[:5]:
            print(f"\\n   📦 {product.code} - {product.name}")
            print(f"      💰 Precio costo: ${product.cost_price}")
            print(f"      💵 Precio venta: ${product.sale_price}")
            print(f"      📊 Stock actual: {product.get_current_stock()}")
            
            # Verificar configuración de cuentas
            config = product.get_account_configuration_status()
            print(f"      🏦 Cuentas efectivas:")
            print(f"         Ventas: {config['effective_sales_account'].code if config['effective_sales_account'] else 'No configurada'}")
            print(f"         Costo: {config['effective_cost_account'].code if config['effective_cost_account'] else 'No configurada'}")
            print(f"         Inventario: {config['effective_inventory_account'].code if config['effective_inventory_account'] else 'No configurada'}")
    
    # ==========================================
    # 4. ANÁLIZAR FACTURAS CON PRODUCTOS DE INVENTARIO
    # ==========================================
    print(f"\\n4️⃣ FACTURAS CON PRODUCTOS DE INVENTARIO")
    print("-" * 60)
    
    # Buscar facturas enviadas con productos
    invoices_with_products = Invoice.objects.filter(
        company=gueber,
        status='sent',
        lines__product__manages_inventory=True
    ).distinct()
    
    print(f"\\n📊 Facturas enviadas con productos de inventario: {invoices_with_products.count()}")
    
    if invoices_with_products.exists():
        sample_invoice = invoices_with_products.first()
        print(f"\\n📄 ANÁLISIS DE FACTURA MUESTRA: #{sample_invoice.id}")
        print(f"   📅 Fecha: {sample_invoice.date}")
        print(f"   💰 Total: ${sample_invoice.total}")
        
        # Verificar líneas con productos de inventario
        inventory_lines = sample_invoice.lines.filter(product__manages_inventory=True)
        print(f"\\n   📦 LÍNEAS CON PRODUCTOS DE INVENTARIO:")
        
        total_cost = Decimal('0.00')
        for line in inventory_lines:
            line_cost = line.quantity * line.product.cost_price
            total_cost += line_cost
            
            print(f"      • {line.product.code}: {line.quantity} x ${line.product.cost_price} = ${line_cost}")
        
        print(f"\\n   💸 COSTO TOTAL DE MERCADERÍA VENDIDA: ${total_cost}")
        
        # Verificar si existe asiento contable
        journal_entry = JournalEntry.objects.filter(
            company=gueber,
            reference=f'FAC-{sample_invoice.id}'
        ).first()
        
        if journal_entry:
            print(f"\\n   📝 ASIENTO CONTABLE #{journal_entry.number}:")
            lines = journal_entry.lines.all()
            
            inventory_related_lines = []
            cost_related_lines = []
            
            for line in lines:
                if ('inventario' in line.account.name.lower() or 
                    'mercader' in line.account.name.lower() or
                    line.account.code.startswith('1.1.04')):
                    inventory_related_lines.append(line)
                
                if ('costo' in line.account.name.lower() or 
                    'cmv' in line.account.name.lower() or
                    line.account.code.startswith('5.1')):
                    cost_related_lines.append(line)
            
            print(f"\\n      📊 LÍNEAS RELACIONADAS CON INVENTARIO:")
            if inventory_related_lines:
                for line in inventory_related_lines:
                    print(f"         ✅ {line.account.code} - {line.account.name}: ${line.credit} HABER")
            else:
                print(f"         ❌ No se encontraron líneas de inventario")
            
            print(f"\\n      📊 LÍNEAS RELACIONADAS CON COSTO:")
            if cost_related_lines:
                for line in cost_related_lines:
                    print(f"         ✅ {line.account.code} - {line.account.name}: ${line.debit} DEBE")
            else:
                print(f"         ❌ No se encontraron líneas de costo de ventas")
    
    # ==========================================
    # 5. VERIFICAR CÓDIGO DEL SERVICIO DE ASIENTOS
    # ==========================================
    print(f"\\n5️⃣ ANÁLISIS DEL CÓDIGO DEL SERVICIO DE ASIENTOS")
    print("-" * 60)
    
    print(f"\\n🔍 VERIFICANDO AutomaticJournalEntryService...")
    
    # Inspeccionar métodos del servicio
    service_methods = [method for method in dir(AutomaticJournalEntryService) if not method.startswith('_')]
    print(f"\\n📋 MÉTODOS PÚBLICOS DEL SERVICIO:")
    for method in service_methods:
        print(f"   • {method}")
    
    # Buscar métodos relacionados con inventario/costo
    inventory_methods = [method for method in dir(AutomaticJournalEntryService) 
                        if any(keyword in method.lower() for keyword in ['inventory', 'cost', 'cogs', 'stock'])]
    
    if inventory_methods:
        print(f"\\n✅ MÉTODOS RELACIONADOS CON INVENTARIO:")
        for method in inventory_methods:
            print(f"   • {method}")
    else:
        print(f"\\n❌ NO SE ENCONTRARON MÉTODOS RELACIONADOS CON INVENTARIO")
    
    # ==========================================
    # 6. RECOMENDACIONES PARA IMPLEMENTAR INVENTARIO
    # ==========================================
    print(f"\\n6️⃣ RECOMENDACIONES PARA IMPLEMENTAR CUENTAS DE INVENTARIO")
    print("-" * 60)
    
    print(f"\\n📋 ASIENTO COMPLETO RECOMENDADO PARA VENTA:")
    print(f"   ")
    print(f"   🟢 DEBE (lo que tenemos):")
    print(f"   • Caja/Banco/Por Cobrar............ $XXX.XX")
    print(f"   • Retención IVA por Cobrar......... $XX.XX")
    print(f"   • Retención IR por Cobrar.......... $X.XX")
    print(f"   ")
    print(f"   🔴 DEBE (lo que falta):")
    print(f"   • Costo de Mercadería Vendida...... $XX.XX")
    print(f"   ")
    print(f"   🟢 HABER (lo que tenemos):")
    print(f"   • Ventas........................... $XXX.XX")
    print(f"   • IVA por Pagar.................... $XX.XX")
    print(f"   ")
    print(f"   🔴 HABER (lo que falta):")
    print(f"   • Inventario/Mercaderías........... $XX.XX")
    
    print(f"\\n💡 PASOS PARA IMPLEMENTAR:")
    print(f"   1. ✅ Configurar cuentas de inventario en CompanyAccountDefaults")
    print(f"   2. ✅ Configurar cuentas de costo en CompanyAccountDefaults") 
    print(f"   3. ✅ Configurar cuentas por categoría de productos")
    print(f"   4. ❌ Modificar AutomaticJournalEntryService para incluir:")
    print(f"      • _create_inventory_cost_lines()")
    print(f"      • Cálculo automático del CMV")
    print(f"      • Reducción de inventario")
    
    # ==========================================
    # 7. VERIFICAR CUENTAS DISPONIBLES
    # ==========================================
    print(f"\\n7️⃣ CUENTAS DISPONIBLES PARA INVENTARIO")
    print("-" * 60)
    
    # Buscar cuentas de inventario
    inventory_accounts = ChartOfAccounts.objects.filter(
        company=gueber,
        is_active=True,
        accepts_movement=True
    ).filter(
        models.Q(name__icontains='inventario') |
        models.Q(name__icontains='mercader') |
        models.Q(code__startswith='1.1.04')
    )
    
    print(f"\\n📦 CUENTAS DE INVENTARIO DISPONIBLES ({inventory_accounts.count()}):")
    for account in inventory_accounts:
        print(f"   {account.code} - {account.name}")
    
    # Buscar cuentas de costo
    cost_accounts = ChartOfAccounts.objects.filter(
        company=gueber,
        is_active=True,
        accepts_movement=True
    ).filter(
        models.Q(name__icontains='costo') |
        models.Q(name__icontains='cmv') |
        models.Q(code__startswith='5.1')
    )
    
    print(f"\\n💸 CUENTAS DE COSTO DISPONIBLES ({cost_accounts.count()}):")
    for account in cost_accounts:
        print(f"   {account.code} - {account.name}")
    
    # ==========================================
    # 8. CONCLUSIÓN TÉCNICA
    # ==========================================
    print(f"\\n8️⃣ CONCLUSIÓN TÉCNICA")
    print("-" * 60)
    
    has_inventory_products = inventory_products.exists()
    has_inventory_accounts = inventory_accounts.exists()
    has_cost_accounts = cost_accounts.exists()
    has_invoices_with_inventory = invoices_with_products.exists()
    
    print(f"\\n🎯 ESTADO ACTUAL DEL SISTEMA:")
    print(f"   ✅ Productos con inventario: {'Sí' if has_inventory_products else 'No'}")
    print(f"   ✅ Cuentas de inventario: {'Sí' if has_inventory_accounts else 'No'}")
    print(f"   ✅ Cuentas de costo: {'Sí' if has_cost_accounts else 'No'}")
    print(f"   ✅ Facturas con inventario: {'Sí' if has_invoices_with_inventory else 'No'}")
    print(f"   ❌ Asientos con inventario: No implementado")
    
    if all([has_inventory_products, has_inventory_accounts, has_cost_accounts]):
        print(f"\\n🟡 VEREDICTO: SISTEMA PREPARADO PERO INCOMPLETO")
        print(f"   • Toda la infraestructura está disponible")
        print(f"   • Solo falta implementar la lógica en AutomaticJournalEntryService")
        print(f"   • Los asientos actuales son CORRECTOS pero INCOMPLETOS")
        return 'ready_for_implementation'
    else:
        print(f"\\n🔴 VEREDICTO: SISTEMA NO PREPARADO")
        print(f"   • Faltan elementos básicos de configuración")
        print(f"   • Se requiere configuración previa")
        return 'needs_configuration'

if __name__ == "__main__":
    import django.db.models as models
    result = analyze_inventory_accounting_system()
    print(f"\\n📊 Resultado: {result}")
    sys.exit(0 if result == 'ready_for_implementation' else 1)