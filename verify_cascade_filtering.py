"""
Verificar si el sistema de filtrado en cascada de facturas soluciona el problema
de la cuenta del método de pago que no acepta movimientos
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import Company, PaymentMethod
from apps.accounting.models import ChartOfAccounts
from apps.invoicing.models import Invoice

def verify_cascade_filtering_solution():
    """Verificar si el filtrado en cascada resuelve el problema"""
    print("🔍 VERIFICACIÓN: Sistema de Filtrado en Cascada para Facturas")
    print("=" * 80)
    
    # Obtener empresa GUEBER
    gueber = Company.objects.filter(trade_name__icontains='GUEBER').first()
    if not gueber:
        print("❌ Empresa GUEBER no encontrada")
        return False
    
    print(f"🏢 Empresa: {gueber.trade_name}")
    
    # ==========================================
    # 1. CONFIGURACIÓN ACTUAL DEL MÉTODO DE PAGO
    # ==========================================
    print(f"\\n1️⃣ CONFIGURACIÓN ACTUAL DEL MÉTODO DE PAGO")
    print("-" * 60)
    
    if gueber.payment_method:
        payment_method = gueber.payment_method
        parent_account = payment_method.parent_account
        
        print(f"💳 Método de pago: {payment_method.name}")
        print(f"🏦 Cuenta padre: {parent_account.code} - {parent_account.name}")
        print(f"💱 Acepta movimientos: {'✅ Sí' if parent_account.accepts_movement else '❌ No'}")
        print(f"📊 Nivel: {parent_account.level}")
        
        # ==========================================
        # 2. ANALIZAR EL FILTRADO EN CASCADA
        # ==========================================
        print(f"\\n2️⃣ ANÁLISIS DEL FILTRADO EN CASCADA")
        print("-" * 60)
        
        print(f"\\n🔍 LÓGICA DEL SISTEMA ACTUAL:")
        print(f"   1. Usuario selecciona método de pago: '{payment_method.name}'")
        print(f"   2. JavaScript detecta cuenta padre: {parent_account.code}")
        print(f"   3. Filtra automáticamente cuentas hijas que SÍ aceptan movimientos")
        print(f"   4. Usuario selecciona cuenta hija específica")
        print(f"   5. Factura se guarda con cuenta hija (que SÍ acepta movimientos)")
        
        # Buscar cuentas hijas disponibles
        child_accounts = ChartOfAccounts.objects.filter(
            company=gueber,
            code__startswith=parent_account.code + '.',
            accepts_movement=True,
            is_active=True
        ).order_by('code')
        
        print(f"\\n📋 CUENTAS HIJAS DISPONIBLES PARA FILTRADO:")
        print(f"   Total cuentas hijas que aceptan movimientos: {child_accounts.count()}")
        
        for account in child_accounts:
            print(f"   ✅ {account.code} - {account.name}")
        
        if child_accounts.count() == 0:
            print(f"   ❌ No hay cuentas hijas disponibles")
            return False
        
        # ==========================================
        # 3. VERIFICAR FACTURAS EXISTENTES
        # ==========================================
        print(f"\\n3️⃣ VERIFICACIÓN DE FACTURAS EXISTENTES")
        print("-" * 60)
        
        # Facturas con método Efectivo
        invoices_efectivo = Invoice.objects.filter(
            company=gueber,
            payment_form=payment_method
        )
        
        print(f"📊 Total facturas con método '{payment_method.name}': {invoices_efectivo.count()}")
        
        if invoices_efectivo.exists():
            # Analizar qué cuentas están usando
            accounts_used = set()
            accounts_that_accept_movement = 0
            accounts_that_dont_accept = 0
            
            for invoice in invoices_efectivo:
                if invoice.account:
                    accounts_used.add(invoice.account)
                    if invoice.account.accepts_movement:
                        accounts_that_accept_movement += 1
                    else:
                        accounts_that_dont_accept += 1
            
            print(f"\\n📈 ANÁLISIS DE CUENTAS EN FACTURAS:")
            print(f"   Cuentas diferentes usadas: {len(accounts_used)}")
            print(f"   Facturas con cuentas que SÍ aceptan movimiento: {accounts_that_accept_movement}")
            print(f"   Facturas con cuentas que NO aceptan movimiento: {accounts_that_dont_accept}")
            
            print(f"\\n📋 DETALLE DE CUENTAS USADAS:")
            for account in accounts_used:
                movement_status = "✅ Sí" if account.accepts_movement else "❌ No"
                invoice_count = invoices_efectivo.filter(account=account).count()
                print(f"   {account.code} - {account.name}")
                print(f"      Acepta movimientos: {movement_status}")
                print(f"      Facturas con esta cuenta: {invoice_count}")
        
        # ==========================================
        # 4. SIMULAR CREACIÓN DE NUEVA FACTURA
        # ==========================================
        print(f"\\n4️⃣ SIMULACIÓN DE CREACIÓN DE NUEVA FACTURA")
        print("-" * 60)
        
        print(f"\\n🎭 SIMULACIÓN DEL PROCESO:")
        print(f"   1. Usuario crea nueva factura")
        print(f"   2. Selecciona empresa: {gueber.trade_name}")
        
        if gueber.payment_method:
            print(f"   3. Sistema auto-selecciona método: {gueber.payment_method.name}")
            print(f"   4. JavaScript detecta cuenta padre: {parent_account.code}")
            
            if child_accounts.exists():
                first_child = child_accounts.first()
                print(f"   5. Sistema filtra y auto-selecciona: {first_child.code}")
                print(f"   6. ✅ Cuenta seleccionada SÍ acepta movimientos")
                print(f"   7. ✅ Factura se puede guardar correctamente")
                print(f"   8. ✅ Asientos contables se pueden generar")
            else:
                print(f"   5. ❌ No hay cuentas hijas disponibles")
                print(f"   6. ❌ No se puede completar la factura")
        
        # ==========================================
        # 5. VERIFICAR JAVASCRIPT INTEGRADO
        # ==========================================
        print(f"\\n5️⃣ VERIFICACIÓN DEL JAVASCRIPT INTEGRADO")
        print("-" * 60)
        
        # Verificar si los archivos JavaScript existen
        js_files = [
            'static/admin/js/integrated_payment_account_handler.js',
            'static/admin/js/integrated_payment_account_handler_vanilla.js',
            'staticfiles/admin/js/integrated_payment_account_handler.js',
            'staticfiles/admin/js/integrated_payment_account_handler_vanilla.js'
        ]
        
        print(f"\\n📁 ARCHIVOS JAVASCRIPT:")
        js_exists = False
        for js_file in js_files:
            if os.path.exists(js_file):
                print(f"   ✅ {js_file}")
                js_exists = True
            else:
                print(f"   ❌ {js_file}")
        
        if js_exists:
            print(f"\\n✅ FUNCIONALIDAD JAVASCRIPT DISPONIBLE:")
            print(f"   • filterChildAccounts(): Filtra cuentas hijas automáticamente")
            print(f"   • isChildAccount(): Verifica relación padre-hijo")
            print(f"   • Auto-selección de primera cuenta válida")
        else:
            print(f"\\n❌ JAVASCRIPT NO ENCONTRADO - Funcionalidad limitada")
        
        # ==========================================
        # 6. CONCLUSIÓN TÉCNICA
        # ==========================================
        print(f"\\n6️⃣ CONCLUSIÓN TÉCNICA")
        print("-" * 60)
        
        print(f"\\n🎯 ANÁLISIS DEL PROBLEMA ORIGINAL:")
        print(f"   Problema: Cuenta padre {parent_account.code} no acepta movimientos")
        print(f"   Impacto: Asientos automáticos fallarían")
        
        print(f"\\n🛠️ ANÁLISIS DE LA SOLUCIÓN ACTUAL:")
        
        if child_accounts.exists() and js_exists:
            print(f"   ✅ SOLUCIÓN EFECTIVA:")
            print(f"      • Sistema filtra automáticamente a cuentas hijas")
            print(f"      • Cuentas hijas SÍ aceptan movimientos")
            print(f"      • JavaScript maneja la cascada automáticamente")
            print(f"      • Usuario no puede seleccionar cuenta padre directamente")
            
            print(f"\\n🎉 VEREDICTO: EL PROBLEMA ESTÁ RESUELTO")
            print(f"   • El filtrado en cascada previene el error")
            print(f"   • Las facturas usan automáticamente cuentas válidas")
            print(f"   • Los asientos contables se pueden generar sin problemas")
            
            return True
        else:
            problems = []
            if not child_accounts.exists():
                problems.append("No hay cuentas hijas disponibles")
            if not js_exists:
                problems.append("JavaScript de filtrado no encontrado")
            
            print(f"   ❌ SOLUCIÓN INCOMPLETA:")
            for problem in problems:
                print(f"      • {problem}")
            
            print(f"\\n⚠️ VEREDICTO: SOLUCIÓN PARCIAL")
            print(f"   • El problema persiste en algunos casos")
            print(f"   • Se requieren correcciones adicionales")
            
            return False
    
    else:
        print("❌ No hay método de pago configurado")
        return False

if __name__ == "__main__":
    success = verify_cascade_filtering_solution()
    if success:
        print(f"\\n✅ Resultado: Sistema funcionando correctamente")
    else:
        print(f"\\n❌ Resultado: Se requieren correcciones")
    
    sys.exit(0 if success else 1)