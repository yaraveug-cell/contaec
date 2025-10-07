"""
Análisis revisado del sistema de inventario considerando la cuenta 4.2.01 - COSTO DE VENTAS
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
import django.db.models as models

def analyze_inventory_accounting_revised():
    """Análisis revisado considerando la cuenta 4.2.01 - COSTO DE VENTAS"""
    print("🔍 ANÁLISIS REVISADO: Sistema de Inventario con cuenta 4.2.01 - COSTO DE VENTAS")
    print("=" * 80)
    
    # Obtener empresa GUEBER
    gueber = Company.objects.filter(trade_name__icontains='GUEBER').first()
    if not gueber:
        print("❌ Empresa GUEBER no encontrada")
        return False
    
    print(f"🏢 Empresa: {gueber.trade_name}")
    
    # ==========================================
    # 1. VERIFICAR CUENTA 4.2.01 - COSTO DE VENTAS
    # ==========================================
    print(f"\\n1️⃣ VERIFICACIÓN DE CUENTA DE COSTO DE VENTAS")
    print("-" * 60)
    
    cost_account = ChartOfAccounts.objects.filter(
        company=gueber,
        code='4.2.01'
    ).first()
    
    if cost_account:
        print(f"✅ CUENTA ENCONTRADA:")
        print(f"   Código: {cost_account.code}")
        print(f"   Nombre: {cost_account.name}")
        print(f"   Acepta movimientos: {'✅ Sí' if cost_account.accepts_movement else '❌ No'}")
        print(f"   Activa: {'✅ Sí' if cost_account.is_active else '❌ No'}")
        print(f"   Nivel: {cost_account.level}")
        print(f"   Categoría: {cost_account.account_type.name if cost_account.account_type else 'Sin tipo'}")
    else:
        print(f"❌ CUENTA 4.2.01 NO ENCONTRADA")
        return False
    
    # ==========================================
    # 2. BUSCAR TODAS LAS CUENTAS RELACIONADAS CON COSTO
    # ==========================================
    print(f"\\n2️⃣ TODAS LAS CUENTAS RELACIONADAS CON COSTO")
    print("-" * 60)
    
    # Buscar por código 4.2.x (cuentas de costo dentro de ingresos)
    cost_accounts_4_2 = ChartOfAccounts.objects.filter(
        company=gueber,
        code__startswith='4.2',
        is_active=True
    ).order_by('code')
    
    print(f"\\n📊 CUENTAS 4.2.x - COSTOS DENTRO DE INGRESOS ({cost_accounts_4_2.count()}):")
    for account in cost_accounts_4_2:
        movement_status = "✅" if account.accepts_movement else "❌"
        print(f"   {account.code} - {account.name} {movement_status}")
    
    # Buscar por código 5.x (cuentas de gastos/costos tradicionales)
    cost_accounts_5 = ChartOfAccounts.objects.filter(
        company=gueber,
        code__startswith='5',
        is_active=True
    ).filter(
        models.Q(name__icontains='costo') |
        models.Q(name__icontains='inventario') |
        models.Q(name__icontains='mercader')
    ).order_by('code')
    
    print(f"\\n📊 CUENTAS 5.x - GASTOS/COSTOS TRADICIONALES ({cost_accounts_5.count()}):")
    for account in cost_accounts_5:
        movement_status = "✅" if account.accepts_movement else "❌"
        print(f"   {account.code} - {account.name} {movement_status}")
    
    # ==========================================
    # 3. VERIFICAR CONFIGURACIÓN ACTUAL DE CATEGORÍAS
    # ==========================================
    print(f"\\n3️⃣ CONFIGURACIÓN ACTUAL DE CATEGORÍAS")
    print("-" * 60)
    
    categories = Category.objects.filter(company=gueber)
    
    print(f"\\n📦 ANÁLISIS DE CONFIGURACIÓN POR CATEGORÍA:")
    for category in categories:
        print(f"\\n   📂 {category.name}:")
        
        # Verificar cuentas configuradas
        sales_account = category.default_sales_account
        cost_account_cat = category.default_cost_account
        inventory_account = category.default_inventory_account
        
        print(f"      🏪 Ventas: {sales_account.code} - {sales_account.name}" if sales_account else "      ❌ Ventas: No configurada")
        print(f"      💸 Costo: {cost_account_cat.code} - {cost_account_cat.name}" if cost_account_cat else "      ❌ Costo: No configurada")
        print(f"      📦 Inventario: {inventory_account.code} - {inventory_account.name}" if inventory_account else "      ❌ Inventario: No configurada")
        
        # Verificar si usa la cuenta correcta de costo
        if cost_account_cat:
            if cost_account_cat.code == '4.2.01':
                print(f"      ✅ Usa cuenta de costo correcta (4.2.01)")
            else:
                print(f"      ⚠️ Usa cuenta diferente: {cost_account_cat.code} (recomendado: 4.2.01)")
    
    # ==========================================
    # 4. PROPUESTA DE ASIENTO CONTABLE CORRECTO
    # ==========================================
    print(f"\\n4️⃣ PROPUESTA DE ASIENTO CONTABLE CORRECTO")
    print("-" * 60)
    
    # Buscar una factura con productos para usar como ejemplo
    invoice_sample = Invoice.objects.filter(
        company=gueber,
        status='sent',
        lines__product__manages_inventory=True
    ).first()
    
    if invoice_sample:
        print(f"\\n📄 EJEMPLO CON FACTURA #{invoice_sample.id}:")
        print(f"   📅 Fecha: {invoice_sample.date}")
        print(f"   🧾 Total: ${invoice_sample.total}")
        
        # Calcular datos para el asiento
        inventory_lines = invoice_sample.lines.filter(product__manages_inventory=True)
        
        total_cost = Decimal('0.00')
        for line in inventory_lines:
            cost = line.quantity * line.product.cost_price
            total_cost += cost
            print(f"   📦 {line.product.code}: {line.quantity} x ${line.product.cost_price} = ${cost}")
        
        print(f"\\n💰 TOTALES:")
        print(f"   Subtotal venta: ${invoice_sample.subtotal}")
        print(f"   IVA: ${invoice_sample.tax_amount}")
        print(f"   Total facturado: ${invoice_sample.total}")
        print(f"   Costo total: ${total_cost}")
        print(f"   Utilidad bruta: ${invoice_sample.subtotal - total_cost}")
        
        print(f"\\n📋 ASIENTO CONTABLE PROPUESTO:")
        print(f"   ")
        print(f"   🟢 DEBE:")
        print(f"   {invoice_sample.account.code} - {invoice_sample.account.name}")
        print(f"   └─ ${invoice_sample.total:>10} (Total cobrado)")
        
        if total_cost > 0:
            print(f"   4.2.01 - COSTO DE VENTAS")
            print(f"   └─ ${total_cost:>10} (Costo de mercadería)")
        
        # Retenciones si aplica
        if invoice_sample.customer.retention_agent:
            retention_amounts = invoice_sample.customer.calculate_retention_amounts(
                invoice_sample.subtotal, 
                invoice_sample.tax_amount
            )
            if retention_amounts['iva_retention'] > 0:
                print(f"   1.1.05.04 - RETENCION IVA VENTAS")
                print(f"   └─ ${retention_amounts['iva_retention']:>10} (Retención IVA)")
            if retention_amounts['ir_retention'] > 0:
                print(f"   1.1.05.03 - RETENCION IR VENTAS") 
                print(f"   └─ ${retention_amounts['ir_retention']:>10} (Retención IR)")
        
        print(f"   ")
        print(f"   🔴 HABER:")
        print(f"   4.1.01 - VENTAS")
        print(f"   └─ ${invoice_sample.subtotal:>10} (Ventas netas)")
        
        # IVA por pagar
        if invoice_sample.tax_amount > 0:
            # Buscar cuentas IVA (simplificado)
            iva_15_account = ChartOfAccounts.objects.filter(
                company=gueber, 
                code='2.1.01.01.03.01'
            ).first()
            if iva_15_account:
                print(f"   {iva_15_account.code} - {iva_15_account.name}")
                print(f"   └─ ${invoice_sample.tax_amount:>10} (IVA por pagar)")
        
        if total_cost > 0:
            print(f"   1.1.06.01.01 - INVENTARIOS ALMACEN")
            print(f"   └─ ${total_cost:>10} (Reducción inventario)")
    
    # ==========================================
    # 5. VERIFICAR SI YA EXISTEN ASIENTOS CON ESTA LÓGICA
    # ==========================================
    print(f"\\n5️⃣ VERIFICAR ASIENTOS EXISTENTES")
    print("-" * 60)
    
    # Buscar asientos que ya usen la cuenta 4.2.01
    existing_cost_lines = JournalEntryLine.objects.filter(
        journal_entry__company=gueber,
        account__code='4.2.01'
    )
    
    print(f"\\n📊 LÍNEAS DE ASIENTO CON CUENTA 4.2.01:")
    print(f"   Total líneas: {existing_cost_lines.count()}")
    
    if existing_cost_lines.exists():
        print(f"\\n   📋 ÚLTIMAS 5 LÍNEAS:")
        for line in existing_cost_lines[:5]:
            entry_ref = line.journal_entry.reference or f"#{line.journal_entry.number}"
            print(f"      {entry_ref}: ${line.debit} DEBE / ${line.credit} HABER - {line.description[:50]}")
    else:
        print(f"   ❌ No se encontraron asientos con cuenta de costo 4.2.01")
    
    # Buscar asientos con cuentas de inventario
    inventory_lines = JournalEntryLine.objects.filter(
        journal_entry__company=gueber,
        account__code='1.1.06.01.01'
    )
    
    print(f"\\n📊 LÍNEAS DE ASIENTO CON INVENTARIO (1.1.06.01.01):")
    print(f"   Total líneas: {inventory_lines.count()}")
    
    # ==========================================
    # 6. ANÁLISIS DE FACTIBILIDAD
    # ==========================================
    print(f"\\n6️⃣ ANÁLISIS DE FACTIBILIDAD")
    print("-" * 60)
    
    # Verificar elementos necesarios
    checks = {
        'cuenta_costo_existe': cost_account and cost_account.is_active and cost_account.accepts_movement,
        'cuenta_inventario_existe': ChartOfAccounts.objects.filter(
            company=gueber, 
            code='1.1.06.01.01',
            is_active=True,
            accepts_movement=True
        ).exists(),
        'productos_con_costo': Product.objects.filter(
            company=gueber,
            manages_inventory=True,
            cost_price__gt=0
        ).exists(),
        'facturas_con_productos': Invoice.objects.filter(
            company=gueber,
            lines__product__manages_inventory=True
        ).exists()
    }
    
    print(f"\\n✅ ELEMENTOS NECESARIOS:")
    for check_name, result in checks.items():
        status = "✅ Sí" if result else "❌ No"
        description = {
            'cuenta_costo_existe': 'Cuenta 4.2.01 operativa',
            'cuenta_inventario_existe': 'Cuenta inventario operativa',
            'productos_con_costo': 'Productos con precio de costo',
            'facturas_con_productos': 'Facturas con productos'
        }.get(check_name, check_name)
        print(f"   {description}: {status}")
    
    # ==========================================
    # 7. RECOMENDACIONES FINALES
    # ==========================================
    print(f"\\n7️⃣ RECOMENDACIONES FINALES")
    print("-" * 60)
    
    all_ready = all(checks.values())
    
    if all_ready:
        print(f"\\n🟢 SISTEMA LISTO PARA IMPLEMENTACIÓN:")
        print(f"   ✅ Cuenta 4.2.01 - COSTO DE VENTAS disponible")
        print(f"   ✅ Cuenta 1.1.06.01.01 - INVENTARIOS ALMACEN disponible")
        print(f"   ✅ Productos con costos configurados")
        print(f"   ✅ Facturas existentes para procesar")
        
        print(f"\\n🛠️ PASOS DE IMPLEMENTACIÓN:")
        print(f"   1. Actualizar categorías para usar cuenta 4.2.01")
        print(f"   2. Modificar AutomaticJournalEntryService")
        print(f"   3. Agregar método _create_inventory_cost_lines()")
        print(f"   4. Probar con factura nueva")
        print(f"   5. Regenerar asientos existentes (opcional)")
        
        return True
    else:
        missing = [desc for check, desc in [
            (checks['cuenta_costo_existe'], 'Cuenta de costo'),
            (checks['cuenta_inventario_existe'], 'Cuenta de inventario'),
            (checks['productos_con_costo'], 'Productos con costo'),
            (checks['facturas_con_productos'], 'Facturas con productos')
        ] if not check]
        
        print(f"\\n🔴 SISTEMA NO LISTO - Faltan elementos:")
        for item in missing:
            print(f"   ❌ {item}")
        
        return False

if __name__ == "__main__":
    success = analyze_inventory_accounting_revised()
    if success:
        print(f"\\n✅ Conclusión: Sistema listo para implementar inventario en asientos")
    else:
        print(f"\\n❌ Conclusión: Se requiere configuración adicional")
    
    sys.exit(0 if success else 1)