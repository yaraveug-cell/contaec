"""
Análisis de parametrización de cuentas contables en ContaEC
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import Company, CompanyAccountDefaults, CompanyTaxAccountMapping
from apps.accounting.models import ChartOfAccounts
from apps.accounting.services import AutomaticJournalEntryService

def analyze_account_parameterization():
    """Analizar la parametrización completa del sistema contable"""
    print("🔍 ANÁLISIS DE PARAMETRIZACIÓN DE CUENTAS CONTABLES")
    print("=" * 70)
    
    errors = []
    warnings = []
    recommendations = []
    
    # 1. Verificar configuración GUEBER
    gueber = Company.objects.filter(trade_name__icontains='GUEBER').first()
    
    print(f"\\n1️⃣ CONFIGURACIÓN EMPRESA: {gueber.trade_name}")
    print("-" * 50)
    
    # 1.1 CompanyAccountDefaults
    defaults = CompanyAccountDefaults.objects.filter(company=gueber).first()
    if defaults:
        print("✅ CompanyAccountDefaults configurado:")
        print(f"   Ventas: {defaults.default_sales_account.code if defaults.default_sales_account else '❌ NO CONFIGURADO'}")
        print(f"   IVA Ret: {defaults.iva_retention_receivable_account.code if defaults.iva_retention_receivable_account else '❌ NO CONFIGURADO'}")
        print(f"   IR Ret: {defaults.ir_retention_receivable_account.code if defaults.ir_retention_receivable_account else '❌ NO CONFIGURADO'}")
        
        if not defaults.default_sales_account:
            errors.append("Cuenta de ventas por defecto no configurada")
        if not defaults.iva_retention_receivable_account:
            errors.append("Cuenta retención IVA por cobrar no configurada")
        if not defaults.ir_retention_receivable_account:
            errors.append("Cuenta retención IR por cobrar no configurada")
    else:
        errors.append("CompanyAccountDefaults no existe para GUEBER")
    
    # 1.2 CompanyTaxAccountMapping
    mappings = CompanyTaxAccountMapping.objects.filter(company=gueber)
    print(f"\\n✅ CompanyTaxAccountMapping: {mappings.count()} mapeos")
    
    expected_rates = [5.00, 12.00, 15.00]  # Tarifas IVA Ecuador
    configured_rates = [float(m.tax_rate) for m in mappings]
    
    for rate in expected_rates:
        mapping = mappings.filter(tax_rate=rate).first()
        if mapping:
            ret_status = f"Ret: {mapping.retention_account.code}" if mapping.retention_account else "⚠️ Sin ret"
            print(f"   IVA {rate:4.0f}%: {mapping.account.code} | {ret_status}")
        else:
            warnings.append(f"Mapeo IVA {rate}% no configurado")
    
    # 2. Verificar consistencia de cuentas de retención
    print(f"\\n2️⃣ CONSISTENCIA CUENTAS DE RETENCIÓN")
    print("-" * 50)
    
    # 2.1 Verificar que todas las retenciones apunten a la misma cuenta
    retention_accounts = [m.retention_account.code for m in mappings if m.retention_account]
    unique_retention_accounts = set(retention_accounts)
    
    if len(unique_retention_accounts) > 1:
        errors.append(f"Inconsistencia: Múltiples cuentas de retención IVA: {unique_retention_accounts}")
    elif len(unique_retention_accounts) == 1:
        main_retention_account = list(unique_retention_accounts)[0]
        print(f"✅ Cuenta retención IVA consistente: {main_retention_account}")
        
        # Verificar que coincida con CompanyAccountDefaults
        if defaults and defaults.iva_retention_receivable_account:
            if defaults.iva_retention_receivable_account.code != main_retention_account:
                warnings.append(f"Inconsistencia: CompanyAccountDefaults IVA ret ({defaults.iva_retention_receivable_account.code}) != CompanyTaxAccountMapping ({main_retention_account})")
        else:
            print("⚠️ No hay CompanyAccountDefaults para comparar")
    
    # 3. Verificar mapeo hardcodeado vs configuración
    print(f"\\n3️⃣ MAPEO HARDCODEADO vs CONFIGURACIÓN")
    print("-" * 50)
    
    hardcoded_mapping = AutomaticJournalEntryService.IVA_ACCOUNTS_MAPPING
    print("Mapeo hardcodeado:")
    for rate, code in hardcoded_mapping.items():
        if code:
            print(f"   IVA {rate:4.0f}%: {code}")
    
    print("\\nComparación configuración vs hardcoded:")
    for mapping in mappings:
        rate = float(mapping.tax_rate)
        hardcoded_code = hardcoded_mapping.get(rate)
        configured_code = mapping.account.code
        
        if hardcoded_code and hardcoded_code != configured_code:
            warnings.append(f"Diferencia IVA {rate}%: Hardcoded={hardcoded_code} vs Configurado={configured_code}")
        elif hardcoded_code == configured_code:
            print(f"   ✅ IVA {rate:4.0f}%: Consistente ({configured_code})")
        else:
            print(f"   ℹ️ IVA {rate:4.0f}%: Solo configurado ({configured_code})")
    
    # 4. Verificar existencia de cuentas
    print(f"\\n4️⃣ VERIFICACIÓN EXISTENCIA DE CUENTAS")
    print("-" * 50)
    
    all_accounts = set()
    if defaults:
        if defaults.default_sales_account:
            all_accounts.add(defaults.default_sales_account.code)
        if defaults.iva_retention_receivable_account:
            all_accounts.add(defaults.iva_retention_receivable_account.code)
        if defaults.ir_retention_receivable_account:
            all_accounts.add(defaults.ir_retention_receivable_account.code)
    
    for mapping in mappings:
        all_accounts.add(mapping.account.code)
        if mapping.retention_account:
            all_accounts.add(mapping.retention_account.code)
    
    for code in sorted(all_accounts):
        account = ChartOfAccounts.objects.filter(company=gueber, code=code).first()
        if account:
            movement_status = "✅ Acepta mov" if account.accepts_movement else "❌ No acepta mov"
            active_status = "✅ Activa" if account.is_active else "❌ Inactiva"
            print(f"   {code}: {movement_status} | {active_status}")
            
            if not account.accepts_movement:
                errors.append(f"Cuenta {code} no acepta movimientos")
            if not account.is_active:
                errors.append(f"Cuenta {code} está inactiva")
        else:
            errors.append(f"Cuenta {code} no existe")
    
    # 5. Verificar lógica de prioridades en el servicio
    print(f"\\n5️⃣ LÓGICA DE PRIORIDADES DEL SERVICIO")
    print("-" * 50)
    
    # Simular búsqueda de cuentas
    test_rate = 15.0
    print(f"Simulación para IVA {test_rate}%:")
    
    # Prioridad 1: CompanyTaxAccountMapping
    mapping = CompanyTaxAccountMapping.objects.filter(company=gueber, tax_rate=test_rate).first()
    if mapping:
        print(f"   1️⃣ CompanyTaxAccountMapping: {mapping.account.code} ✅")
    else:
        print(f"   1️⃣ CompanyTaxAccountMapping: No encontrado ❌")
        
    # Prioridad 2: Hardcoded
    hardcoded = hardcoded_mapping.get(test_rate)
    if hardcoded:
        print(f"   2️⃣ Mapeo hardcodeado: {hardcoded} ✅")
    else:
        print(f"   2️⃣ Mapeo hardcodeado: No encontrado ❌")
    
    # 6. Generar recomendaciones
    print(f"\\n6️⃣ RECOMENDACIONES")
    print("-" * 50)
    
    if not errors and not warnings:
        recommendations.append("Configuración óptima - considerar eliminar mapeo hardcodeado")
    
    if len(unique_retention_accounts) > 1:
        recommendations.append("Unificar todas las retenciones IVA a una sola cuenta")
    
    if mappings.filter(retention_account__isnull=True).exists():
        recommendations.append("Configurar cuentas de retención para todos los mapeos IVA")
    
    missing_rates = [rate for rate in expected_rates if rate not in configured_rates]
    if missing_rates:
        recommendations.append(f"Agregar mapeos para tarifas IVA: {missing_rates}")
    
    # RESUMEN FINAL
    print(f"\\n🎯 RESUMEN DEL ANÁLISIS")
    print("=" * 70)
    
    print(f"\\n❌ ERRORES ENCONTRADOS ({len(errors)}):")
    for i, error in enumerate(errors, 1):
        print(f"   {i}. {error}")
    
    print(f"\\n⚠️ ADVERTENCIAS ({len(warnings)}):")
    for i, warning in enumerate(warnings, 1):
        print(f"   {i}. {warning}")
    
    print(f"\\n💡 RECOMENDACIONES ({len(recommendations)}):")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    # Puntuación final
    total_issues = len(errors) + len(warnings)
    if total_issues == 0:
        score = "🟢 EXCELENTE"
    elif total_issues <= 2:
        score = "🟡 BUENO"
    elif total_issues <= 5:
        score = "🟠 REGULAR"
    else:
        score = "🔴 CRÍTICO"
    
    print(f"\\n📊 PUNTUACIÓN GENERAL: {score}")
    
    return len(errors) == 0

if __name__ == "__main__":
    success = analyze_account_parameterization()
    sys.exit(0 if success else 1)