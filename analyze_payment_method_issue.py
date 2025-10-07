"""
Análisis detallado del problema: Cuenta método de pago no acepta movimientos
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import Company, PaymentMethod
from apps.accounting.models import ChartOfAccounts, JournalEntry, JournalEntryLine
from apps.invoicing.models import Invoice

def analyze_payment_method_account_issue():
    """Análizar el problema específico de la cuenta del método de pago"""
    print("🔍 ANÁLISIS DETALLADO: Problema Cuenta Método de Pago")
    print("=" * 80)
    
    # Obtener empresa GUEBER
    gueber = Company.objects.filter(trade_name__icontains='GUEBER').first()
    if not gueber:
        print("❌ Empresa GUEBER no encontrada")
        return False
    
    print(f"🏢 Empresa: {gueber.trade_name}")
    
    # ==========================================
    # 1. IDENTIFICAR EL MÉTODO DE PAGO
    # ==========================================
    print(f"\\n1️⃣ MÉTODO DE PAGO CONFIGURADO")
    print("-" * 60)
    
    if gueber.payment_method:
        payment_method = gueber.payment_method
        print(f"💳 Método de pago: {payment_method.name}")
        print(f"📝 ID: {payment_method.id}")
        
        if payment_method.parent_account:
            account = payment_method.parent_account
            print(f"🏦 Cuenta asociada: {account.code} - {account.name}")
            print(f"🆔 ID cuenta: {account.id}")
            print(f"🏢 Empresa: {account.company.trade_name}")
            print(f"✅ Activa: {'Sí' if account.is_active else 'No'}")
            print(f"💱 Acepta movimientos: {'Sí' if account.accepts_movement else 'No'}")
            print(f"📊 Nivel: {account.level}")
            print(f"👨‍👩‍👧‍👦 Cuenta padre: {account.parent.code if account.parent else 'Sin padre'}")
        else:
            print("❌ Método de pago sin cuenta asociada")
            return False
    else:
        print("❌ No hay método de pago configurado")
        return False
    
    # ==========================================
    # 2. ANALIZAR POR QUÉ NO ACEPTA MOVIMIENTOS
    # ==========================================
    print(f"\\n2️⃣ ANÁLISIS DEL PROBLEMA")
    print("-" * 60)
    
    problem_account = payment_method.parent_account
    
    print(f"\\n🚨 PROBLEMA IDENTIFICADO:")
    print(f"   Cuenta: {problem_account.code} - {problem_account.name}")
    print(f"   accepts_movement = {problem_account.accepts_movement}")
    
    if not problem_account.accepts_movement:
        print(f"\\n❌ IMPACTO DEL PROBLEMA:")
        print(f"   • La cuenta NO puede recibir movimientos contables")
        print(f"   • Los asientos automáticos FALLARÁN al intentar usar esta cuenta")
        print(f"   • Las facturas no podrán generar líneas contables correctamente")
    
    # Verificar si es cuenta padre o hija
    children_count = ChartOfAccounts.objects.filter(
        company=gueber,
        parent=problem_account
    ).count()
    
    print(f"\\n🔍 ANÁLISIS ESTRUCTURAL:")
    print(f"   • Código: {problem_account.code}")
    print(f"   • Nivel: {problem_account.level}")
    print(f"   • Cuentas hijas: {children_count}")
    
    if children_count > 0:
        print(f"   📋 EXPLICACIÓN: Cuenta PADRE con {children_count} cuentas hijas")
        print(f"   📚 En contabilidad, las cuentas padre generalmente NO aceptan movimientos")
        print(f"   🎯 Solo las cuentas HIJAS (de último nivel) deben aceptar movimientos")
        
        # Mostrar cuentas hijas
        children = ChartOfAccounts.objects.filter(
            company=gueber,
            parent=problem_account
        )
        print(f"\\n   👶 CUENTAS HIJAS DISPONIBLES:")
        for child in children:
            movement_status = "✅" if child.accepts_movement else "❌"
            print(f"      {child.code} - {child.name} {movement_status}")
    else:
        print(f"   📋 EXPLICACIÓN: Cuenta HIJA sin subcuentas")
        print(f"   ⚠️ Esta cuenta DEBERÍA aceptar movimientos")
    
    # ==========================================
    # 3. VERIFICAR IMPACTO EN FACTURAS
    # ==========================================
    print(f"\\n3️⃣ VERIFICAR IMPACTO EN FACTURAS")
    print("-" * 60)
    
    # Buscar facturas que usen el método de pago (campo correcto: payment_form)
    invoices_count = Invoice.objects.filter(
        company=gueber,
        payment_form=payment_method
    ).count()
    
    print(f"📊 Facturas con método '{payment_method.name}': {invoices_count}")
    
    if invoices_count > 0:
        # Verificar si hay asientos que usan esta cuenta
        journal_lines = JournalEntryLine.objects.filter(
            journal_entry__company=gueber,
            account=problem_account
        )
        
        print(f"📝 Líneas de asiento en cuenta {problem_account.code}: {journal_lines.count()}")
        
        if journal_lines.exists():
            print(f"\\n⚠️ INCONSISTENCIA DETECTADA:")
            print(f"   • La cuenta {problem_account.code} NO acepta movimientos")
            print(f"   • Pero YA TIENE {journal_lines.count()} líneas de asiento")
            print(f"   • Esto indica que antes SÍ aceptaba movimientos")
            
            # Mostrar algunas líneas para análisis
            for line in journal_lines[:3]:
                print(f"      💰 ${line.debit} DEBE / ${line.credit} HABER - {line.description[:50]}")
    
    # ==========================================
    # 4. SOLUCIONES PROPUESTAS
    # ==========================================
    print(f"\\n4️⃣ SOLUCIONES PROPUESTAS")
    print("-" * 60)
    
    print(f"\\n🟢 SOLUCIÓN 1: HABILITAR MOVIMIENTOS EN CUENTA ACTUAL")
    print(f"   Pros: Rápido, mantiene configuración actual")
    print(f"   Contras: Rompe principios contables si es cuenta padre")
    print(f"   SQL: UPDATE accounting_chartofaccounts SET accepts_movement=true WHERE id={problem_account.id}")
    
    if children_count > 0:
        # Buscar cuenta hija más apropiada
        best_child = children.filter(accepts_movement=True).first()
        if best_child:
            print(f"\\n🟡 SOLUCIÓN 2: CAMBIAR A CUENTA HIJA APROPIADA")
            print(f"   Cuenta sugerida: {best_child.code} - {best_child.name}")
            print(f"   Pros: Sigue principios contables correctos")
            print(f"   Contras: Requiere actualizar configuración")
            print(f"   SQL: UPDATE companies_paymentmethod SET parent_account_id={best_child.id} WHERE id={payment_method.id}")
    
    print(f"\\n🔵 SOLUCIÓN 3: CREAR NUEVA CUENTA ESPECÍFICA")
    print(f"   Crear: 1.1.01.01 - Efectivo en Caja")
    print(f"   Pros: Cuenta dedicada, sigue mejores prácticas")
    print(f"   Contras: Requiere más trabajo de configuración")
    
    # ==========================================
    # 5. VERIFICAR OTRAS EMPRESAS
    # ==========================================
    print(f"\\n5️⃣ VERIFICAR OTRAS EMPRESAS")
    print("-" * 60)
    
    all_companies = Company.objects.all()
    
    for company in all_companies:
        if company.payment_method and company.payment_method.parent_account:
            pm_account = company.payment_method.parent_account
            status = "✅" if pm_account.accepts_movement else "❌"
            print(f"   {company.trade_name}: {pm_account.code} {status}")
    
    # ==========================================
    # 6. RECOMENDACIÓN TÉCNICA
    # ==========================================
    print(f"\\n6️⃣ RECOMENDACIÓN TÉCNICA")
    print("-" * 60)
    
    print(f"\\n🎯 ANÁLISIS FINAL:")
    
    if children_count > 0:
        print(f"   • La cuenta {problem_account.code} ES CUENTA PADRE")
        print(f"   • Tiene {children_count} cuentas hijas")
        print(f"   • NO debería aceptar movimientos (correcto)")
        print(f"   • PROBLEMA: El método de pago apunta a cuenta padre")
        
        if children.filter(accepts_movement=True).exists():
            best_child = children.filter(accepts_movement=True).first()
            print(f"\\n✅ RECOMENDACIÓN: Cambiar a cuenta hija")
            print(f"   Usar: {best_child.code} - {best_child.name}")
            return "change_to_child"
        else:
            print(f"\\n✅ RECOMENDACIÓN: Habilitar una cuenta hija")
            first_child = children.first()
            print(f"   Habilitar: {first_child.code} - {first_child.name}")
            return "enable_child"
    else:
        print(f"   • La cuenta {problem_account.code} ES CUENTA HIJA")
        print(f"   • NO tiene subcuentas")
        print(f"   • DEBERÍA aceptar movimientos")
        print(f"   • PROBLEMA: Configuración incorrecta")
        
        print(f"\\n✅ RECOMENDACIÓN: Habilitar movimientos")
        print(f"   Es seguro habilitar accepts_movement=True")
        return "enable_current"

if __name__ == "__main__":
    recommendation = analyze_payment_method_account_issue()
    print(f"\\n🔧 Recomendación: {recommendation}")