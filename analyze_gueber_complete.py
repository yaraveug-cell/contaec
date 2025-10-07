"""
Análisis completo de parametrización del plan de cuentas para GUEBER
Validación exhaustiva de toda la configuración contable
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import Company, CompanyAccountDefaults, CompanyTaxAccountMapping, PaymentMethod
from apps.accounting.models import ChartOfAccounts, JournalEntry, JournalEntryLine
from apps.accounting.services import AutomaticJournalEntryService
from apps.invoicing.models import Customer
from decimal import Decimal

def analyze_gueber_chart_of_accounts():
    """Análisis completo del plan de cuentas de GUEBER"""
    print("🏢 ANÁLISIS COMPLETO DEL PLAN DE CUENTAS - GUEBER")
    print("=" * 80)
    
    # Obtener empresa GUEBER
    gueber = Company.objects.filter(trade_name__icontains='GUEBER').first()
    if not gueber:
        print("❌ Empresa GUEBER no encontrada")
        return False
    
    print(f"📋 Empresa: {gueber.trade_name} (ID: {gueber.id})")
    print(f"📧 Email: {gueber.email}")
    print(f"🆔 RUC: {getattr(gueber, 'ruc', 'No disponible')}")
    
    errors = []
    warnings = []
    recommendations = []
    
    # ==========================================
    # 1. ESTRUCTURA DEL PLAN DE CUENTAS
    # ==========================================
    print(f"\\n1️⃣ ESTRUCTURA DEL PLAN DE CUENTAS")
    print("-" * 60)
    
    total_accounts = ChartOfAccounts.objects.filter(company=gueber).count()
    active_accounts = ChartOfAccounts.objects.filter(company=gueber, is_active=True).count()
    movement_accounts = ChartOfAccounts.objects.filter(company=gueber, accepts_movement=True).count()
    
    print(f"📊 Total cuentas: {total_accounts}")
    print(f"📊 Cuentas activas: {active_accounts}")
    print(f"📊 Cuentas que aceptan movimiento: {movement_accounts}")
    
    if total_accounts == 0:
        errors.append("No hay cuentas en el plan de cuentas")
    elif total_accounts < 20:
        warnings.append(f"Plan de cuentas muy básico ({total_accounts} cuentas)")
    
    # Verificar estructura por niveles
    print(f"\\n📈 Estructura por niveles:")
    for level in range(1, 6):
        level_accounts = ChartOfAccounts.objects.filter(
            company=gueber, 
            level=level
        ).count()
        print(f"   Nivel {level}: {level_accounts} cuentas")
    
    # ==========================================
    # 2. CONFIGURACIÓN DE DEFAULTS
    # ==========================================
    print(f"\\n2️⃣ CONFIGURACIÓN DE CUENTAS POR DEFECTO")
    print("-" * 60)
    
    defaults = CompanyAccountDefaults.objects.filter(company=gueber).first()
    if defaults:
        print("✅ CompanyAccountDefaults configurado")
        
        # Verificar cuenta de ventas
        if defaults.default_sales_account:
            sales_account = defaults.default_sales_account
            print(f"   💰 Ventas: {sales_account.code} - {sales_account.name}")
            if not sales_account.is_active:
                errors.append(f"Cuenta de ventas {sales_account.code} está inactiva")
            if not sales_account.accepts_movement:
                errors.append(f"Cuenta de ventas {sales_account.code} no acepta movimientos")
            if not sales_account.code.startswith('4'):
                warnings.append(f"Cuenta de ventas {sales_account.code} no sigue patrón típico de ingresos (4.x)")
        else:
            errors.append("Cuenta de ventas por defecto no configurada")
        
        # Verificar cuenta retención IVA
        if defaults.iva_retention_receivable_account:
            iva_ret_account = defaults.iva_retention_receivable_account
            print(f"   🧾 Retención IVA: {iva_ret_account.code} - {iva_ret_account.name}")
            if not iva_ret_account.is_active:
                errors.append(f"Cuenta retención IVA {iva_ret_account.code} está inactiva")
            if not iva_ret_account.accepts_movement:
                errors.append(f"Cuenta retención IVA {iva_ret_account.code} no acepta movimientos")
            if not iva_ret_account.code.startswith('1.1'):
                warnings.append(f"Cuenta retención IVA {iva_ret_account.code} no sigue patrón típico (1.1.x)")
        else:
            errors.append("Cuenta retención IVA por defecto no configurada")
        
        # Verificar cuenta retención IR
        if defaults.ir_retention_receivable_account:
            ir_ret_account = defaults.ir_retention_receivable_account
            print(f"   📄 Retención IR: {ir_ret_account.code} - {ir_ret_account.name}")
            if not ir_ret_account.is_active:
                errors.append(f"Cuenta retención IR {ir_ret_account.code} está inactiva")
            if not ir_ret_account.accepts_movement:
                errors.append(f"Cuenta retención IR {ir_ret_account.code} no acepta movimientos")
            if not ir_ret_account.code.startswith('1.1'):
                warnings.append(f"Cuenta retención IR {ir_ret_account.code} no sigue patrón típico (1.1.x)")
        else:
            errors.append("Cuenta retención IR por defecto no configurada")
    else:
        errors.append("CompanyAccountDefaults no configurado")
    
    # ==========================================
    # 3. MAPEO DE CUENTAS IVA
    # ==========================================
    print(f"\\n3️⃣ MAPEO DE CUENTAS IVA")
    print("-" * 60)
    
    iva_mappings = CompanyTaxAccountMapping.objects.filter(company=gueber).order_by('tax_rate')
    
    expected_rates = [Decimal('0.00'), Decimal('5.00'), Decimal('12.00'), Decimal('15.00')]
    print(f"📋 Mapeos configurados: {iva_mappings.count()}")
    
    for rate in expected_rates:
        mapping = iva_mappings.filter(tax_rate=rate).first()
        if mapping:
            account = mapping.account
            ret_account = mapping.retention_account
            
            status_account = "✅" if account.is_active and account.accepts_movement else "❌"
            status_ret = "✅" if ret_account and ret_account.is_active and ret_account.accepts_movement else "❌"
            
            print(f"   IVA {rate:5.1f}%: {account.code} {status_account}")
            if ret_account:
                print(f"              Ret: {ret_account.code} {status_ret}")
            else:
                print(f"              Ret: No configurada ⚠️")
            
            # Validaciones
            if not account.is_active:
                errors.append(f"Cuenta IVA {rate}% ({account.code}) está inactiva")
            if not account.accepts_movement:
                errors.append(f"Cuenta IVA {rate}% ({account.code}) no acepta movimientos")
            if rate > 0 and not account.code.startswith('2.1'):
                warnings.append(f"Cuenta IVA {rate}% ({account.code}) no sigue patrón típico (2.1.x)")
            
            if rate > 0 and not ret_account:
                warnings.append(f"Cuenta retención IVA {rate}% no configurada")
            elif ret_account:
                if not ret_account.is_active:
                    errors.append(f"Cuenta retención IVA {rate}% ({ret_account.code}) está inactiva")
                if not ret_account.accepts_movement:
                    errors.append(f"Cuenta retención IVA {rate}% ({ret_account.code}) no acepta movimientos")
        else:
            if rate == Decimal('0.00'):
                warnings.append(f"Mapeo IVA {rate}% no configurado (opcional)")
            else:
                errors.append(f"Mapeo IVA {rate}% no configurado")
    
    # ==========================================
    # 4. CONSISTENCIA ENTRE CONFIGURACIONES
    # ==========================================
    print(f"\\n4️⃣ CONSISTENCIA ENTRE CONFIGURACIONES")
    print("-" * 60)
    
    if defaults and defaults.iva_retention_receivable_account:
        default_iva_ret = defaults.iva_retention_receivable_account.code
        
        # Verificar que todas las retenciones IVA apunten a la misma cuenta
        retention_accounts = set()
        for mapping in iva_mappings:
            if mapping.retention_account:
                retention_accounts.add(mapping.retention_account.code)
        
        if len(retention_accounts) == 0:
            warnings.append("No hay cuentas de retención IVA configuradas en mapeos")
        elif len(retention_accounts) == 1:
            mapping_iva_ret = list(retention_accounts)[0]
            if default_iva_ret == mapping_iva_ret:
                print(f"✅ Consistencia retención IVA: {default_iva_ret}")
            else:
                errors.append(f"Inconsistencia retención IVA: Default={default_iva_ret} vs Mapeo={mapping_iva_ret}")
        else:
            errors.append(f"Múltiples cuentas de retención IVA: {retention_accounts}")
    
    # ==========================================
    # 5. VERIFICACIÓN DE CUENTAS CRÍTICAS
    # ==========================================
    print(f"\\n5️⃣ VERIFICACIÓN DE CUENTAS CRÍTICAS")
    print("-" * 60)
    
    critical_patterns = [
        ('1.1', 'Activo Corriente'),
        ('1.2', 'Activo No Corriente'),
        ('2.1', 'Pasivo Corriente'),
        ('2.2', 'Pasivo No Corriente'),
        ('3.', 'Patrimonio'),
        ('4.', 'Ingresos'),
        ('5.', 'Gastos'),
        ('6.', 'Costos')
    ]
    
    for pattern, description in critical_patterns:
        count = ChartOfAccounts.objects.filter(
            company=gueber,
            code__startswith=pattern,
            is_active=True
        ).count()
        
        status = "✅" if count > 0 else "⚠️"
        print(f"   {description} ({pattern}*): {count} cuentas {status}")
        
        if count == 0:
            warnings.append(f"No hay cuentas de {description}")
    
    # ==========================================
    # 6. MÉTODO DE PAGO CONFIGURADO
    # ==========================================
    print(f"\\n6️⃣ MÉTODO DE PAGO CONFIGURADO")
    print("-" * 60)
    
    if gueber.payment_method:
        payment_method = gueber.payment_method
        print(f"✅ Método de pago: {payment_method.name}")
        
        if payment_method.parent_account:
            account = payment_method.parent_account
            print(f"   💳 Cuenta asociada: {account.code} - {account.name}")
            
            if not account.is_active:
                errors.append(f"Cuenta método de pago {account.code} está inactiva")
            if not account.accepts_movement:
                errors.append(f"Cuenta método de pago {account.code} no acepta movimientos")
        else:
            warnings.append("Método de pago sin cuenta asociada")
    else:
        errors.append("Método de pago no configurado")
    
    # ==========================================
    # 7. PRUEBAS DE INTEGRACIÓN
    # ==========================================
    print(f"\\n7️⃣ PRUEBAS DE INTEGRACIÓN CON SERVICIOS")
    print("-" * 60)
    
    # Probar servicio de cuentas de ventas
    sales_account_service = AutomaticJournalEntryService._get_sales_account(gueber)
    if sales_account_service:
        print(f"✅ Servicio ventas: {sales_account_service.code}")
    else:
        errors.append("Servicio de cuentas de ventas falla")
    
    # Probar servicio de cuentas IVA
    test_rates = [5.0, 12.0, 15.0]
    for rate in test_rates:
        iva_account_service = AutomaticJournalEntryService._get_iva_account(gueber, rate)
        if iva_account_service:
            print(f"✅ Servicio IVA {rate:4.1f}%: {iva_account_service.code}")
        else:
            errors.append(f"Servicio de cuentas IVA {rate}% falla")
    
    # Probar servicio de retenciones
    iva_ret_service = AutomaticJournalEntryService._get_iva_retention_receivable_account(gueber, 15.0)
    if iva_ret_service:
        print(f"✅ Servicio retención IVA: {iva_ret_service.code}")
    else:
        errors.append("Servicio de retención IVA falla")
    
    ir_ret_service = AutomaticJournalEntryService._get_ir_retention_receivable_account(gueber)
    if ir_ret_service:
        print(f"✅ Servicio retención IR: {ir_ret_service.code}")
    else:
        errors.append("Servicio de retención IR falla")
    
    # ==========================================
    # 8. ANÁLISIS DE MOVIMIENTOS EXISTENTES
    # ==========================================
    print(f"\\n8️⃣ ANÁLISIS DE MOVIMIENTOS CONTABLES")
    print("-" * 60)
    
    journal_entries = JournalEntry.objects.filter(company=gueber).count()
    journal_lines = JournalEntryLine.objects.filter(
        journal_entry__company=gueber
    ).count()
    
    print(f"📊 Asientos contables: {journal_entries}")
    print(f"📊 Líneas de asiento: {journal_lines}")
    
    if journal_entries > 0:
        # Verificar balance
        total_debits = JournalEntryLine.objects.filter(
            journal_entry__company=gueber
        ).aggregate(total=django.db.models.Sum('debit'))['total'] or Decimal('0')
        
        total_credits = JournalEntryLine.objects.filter(
            journal_entry__company=gueber
        ).aggregate(total=django.db.models.Sum('credit'))['total'] or Decimal('0')
        
        balance_diff = abs(total_debits - total_credits)
        
        print(f"💰 Total débitos: ${total_debits:,.2f}")
        print(f"💰 Total créditos: ${total_credits:,.2f}")
        print(f"⚖️ Diferencia: ${balance_diff:,.2f}")
        
        if balance_diff > Decimal('0.01'):
            errors.append(f"Asientos desbalanceados: diferencia ${balance_diff}")
        else:
            print("✅ Asientos balanceados correctamente")
    
    # ==========================================
    # 9. CLIENTES CON RETENCIÓN
    # ==========================================
    print(f"\\n9️⃣ CLIENTES CON CONFIGURACIÓN DE RETENCIÓN")
    print("-" * 60)
    
    total_customers = Customer.objects.filter(company=gueber).count()
    retention_customers = Customer.objects.filter(
        company=gueber, 
        retention_agent=True
    ).count()
    
    print(f"👥 Total clientes: {total_customers}")
    print(f"🏛️ Clientes agentes de retención: {retention_customers}")
    
    if retention_customers > 0:
        print("   📋 Clientes configurados para retención:")
        for customer in Customer.objects.filter(company=gueber, retention_agent=True)[:5]:
            rates = customer.get_retention_rates()
            print(f"      • {customer.trade_name or customer.legal_name}")
            print(f"        IVA: {rates['iva_retention']}% | IR: {rates['ir_retention']}%")
    
    # ==========================================
    # 10. RESUMEN Y RECOMENDACIONES
    # ==========================================
    print(f"\\n🎯 RESUMEN DEL ANÁLISIS")
    print("=" * 80)
    
    print(f"\\n❌ ERRORES CRÍTICOS ({len(errors)}):")
    for i, error in enumerate(errors, 1):
        print(f"   {i}. {error}")
    
    print(f"\\n⚠️ ADVERTENCIAS ({len(warnings)}):")
    for i, warning in enumerate(warnings, 1):
        print(f"   {i}. {warning}")
    
    # Generar recomendaciones automáticas
    if len(errors) == 0 and len(warnings) <= 2:
        recommendations.append("Configuración óptima para operaciones contables")
        recommendations.append("Sistema listo para generar asientos automáticos")
    
    if len(errors) > 0:
        recommendations.append("Corregir errores críticos antes de usar sistema")
        recommendations.append("Revisar configuración de cuentas inactivas")
    
    if retention_customers == 0:
        recommendations.append("Configurar clientes como agentes de retención según SRI")
    
    if journal_entries == 0:
        recommendations.append("Generar facturas de prueba para validar configuración")
    
    print(f"\\n💡 RECOMENDACIONES ({len(recommendations)}):")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    # Puntuación final
    total_issues = len(errors) + len(warnings)
    if len(errors) == 0 and len(warnings) == 0:
        score = "🟢 EXCELENTE"
        score_text = "Configuración perfecta"
    elif len(errors) == 0 and len(warnings) <= 3:
        score = "🟡 MUY BUENO"
        score_text = "Configuración funcional con mejoras menores"
    elif len(errors) <= 2:
        score = "🟠 BUENO"
        score_text = "Configuración funcional con correcciones necesarias"
    else:
        score = "🔴 REQUIERE ATENCIÓN"
        score_text = "Configuración con problemas críticos"
    
    print(f"\\n📊 PUNTUACIÓN GENERAL: {score}")
    print(f"📝 {score_text}")
    
    return len(errors) == 0

if __name__ == "__main__":
    import django.db.models
    success = analyze_gueber_chart_of_accounts()
    sys.exit(0 if success else 1)