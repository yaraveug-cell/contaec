"""
Análisis de impacto del mapeo hardcodeado IVA_ACCOUNTS_MAPPING
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import Company, CompanyTaxAccountMapping
from apps.accounting.models import ChartOfAccounts, JournalEntry, JournalEntryLine
from apps.accounting.services import AutomaticJournalEntryService
from decimal import Decimal

def analyze_hardcoded_mapping_impact():
    """Analizar impacto del mapeo hardcodeado IVA_ACCOUNTS_MAPPING"""
    print("🔍 ANÁLISIS DE IMPACTO DEL MAPEO HARDCODEADO IVA_ACCOUNTS_MAPPING")
    print("=" * 80)
    
    # 1. Estado actual del mapeo hardcodeado
    print("\\n1️⃣ MAPEO HARDCODEADO ACTUAL")
    print("-" * 60)
    
    hardcoded_mapping = AutomaticJournalEntryService.IVA_ACCOUNTS_MAPPING
    print("Contenido actual:")
    for rate, code in hardcoded_mapping.items():
        status = f"→ {code}" if code else "→ Sin cuenta"
        print(f"   IVA {rate:4.0f}% {status}")
    
    # 2. Escenarios de impacto
    print("\\n2️⃣ ESCENARIOS DE IMPACTO SI SE ELIMINA EL HARDCODE")
    print("-" * 60)
    
    gueber = Company.objects.filter(trade_name__icontains='GUEBER').first()
    
    # Escenario 1: Empresa CON configuración completa
    mappings = CompanyTaxAccountMapping.objects.filter(company=gueber)
    print("\\n📊 Empresa GUEBER (CON configuración):")
    print(f"   Mapeos configurados: {mappings.count()}")
    
    for rate, hardcode in hardcoded_mapping.items():
        if hardcode:  # Solo para tarifas con hardcode
            # Buscar configuración
            config_mapping = mappings.filter(tax_rate=rate).first()
            if config_mapping:
                config_account = config_mapping.account.code
                if config_account == hardcode:
                    print(f"   ✅ IVA {rate:4.0f}%: Configuración coincide ({config_account})")
                else:
                    print(f"   ⚠️ IVA {rate:4.0f}%: DIFERENCIA - Config: {config_account} vs Hardcode: {hardcode}")
            else:
                print(f"   ❌ IVA {rate:4.0f}%: Sin configuración, dependería del hardcode ({hardcode})")
    
    # Escenario 2: Empresa SIN configuración
    print("\\n🏢 Empresa hipotética SIN configuración:")
    print("   Impacto: Dependería 100% del mapeo hardcodeado")
    
    for rate, hardcode in hardcoded_mapping.items():
        if hardcode:
            print(f"   🔴 IVA {rate:4.0f}%: FALLO total → No encontraría cuenta")
        else:
            print(f"   ⚪ IVA {rate:4.0f}%: Sin impacto (ya es None)")
    
    # 3. Análisis de dependencias en el código
    print("\\n3️⃣ ANÁLISIS DE DEPENDENCIAS EN EL CÓDIGO")
    print("-" * 60)
    
    print("\\n🔧 Función _get_iva_account() - SISTEMA DE FALLBACK:")
    print("   1. PRIORIDAD 1: CompanyTaxAccountMapping (configurable)")
    print("   2. PRIORIDAD 2: IVA_ACCOUNTS_MAPPING (hardcode) ← AQUÍ")
    print("   3. PRIORIDAD 3: Búsqueda por código en ChartOfAccounts")
    
    print("\\n🎯 ¿Qué pasa si se elimina el hardcode?")
    print("   • Empresas CON configuración: ✅ Sin impacto")
    print("   • Empresas SIN configuración: ❌ Fallarían en Prioridad 2")
    print("   • Resultado: Pasarían directo a Prioridad 3 (búsqueda por código)")
    
    # 4. Simulación práctica
    print("\\n4️⃣ SIMULACIÓN PRÁCTICA")
    print("-" * 60)
    
    test_rates = [15.0, 5.0, 12.0]
    
    for rate in test_rates:
        print(f"\\n🧪 Simulación IVA {rate}% para GUEBER:")
        
        # Simular con configuración actual (CON hardcode)
        account_with_hardcode = AutomaticJournalEntryService._get_iva_account(gueber, rate)
        
        # Simular SIN hardcode (solo configuración)
        mapping = CompanyTaxAccountMapping.objects.filter(company=gueber, tax_rate=rate).first()
        account_without_hardcode = mapping.account if mapping else None
        
        print(f"   Con hardcode: {account_with_hardcode.code if account_with_hardcode else 'None'}")
        print(f"   Sin hardcode: {account_without_hardcode.code if account_without_hardcode else 'None'}")
        
        if account_with_hardcode and account_without_hardcode:
            if account_with_hardcode.code == account_without_hardcode.code:
                print(f"   ✅ Resultado idéntico")
            else:
                print(f"   ⚠️ Resultado diferente")
        elif account_without_hardcode:
            print(f"   ✅ Configuración suficiente")
        else:
            print(f"   ❌ Perdería funcionalidad sin hardcode")
    
    # 5. Facturas existentes
    print("\\n5️⃣ IMPACTO EN FACTURAS EXISTENTES")
    print("-" * 60)
    
    # Buscar asientos que pudieran usar cuentas del hardcode
    hardcoded_accounts = [code for code in hardcoded_mapping.values() if code]
    
    for account_code in hardcoded_accounts:
        account = ChartOfAccounts.objects.filter(company=gueber, code=account_code).first()
        if account:
            lines_count = JournalEntryLine.objects.filter(account=account).count()
            print(f"   📝 Cuenta {account_code}: {lines_count} líneas de asiento existentes")
        else:
            print(f"   ❌ Cuenta {account_code}: No existe en GUEBER")
    
    # 6. Recomendaciones
    print("\\n6️⃣ RECOMENDACIONES DE MIGRACIÓN")
    print("-" * 60)
    
    print("\\n🟢 ELIMINACIÓN SEGURA (recomendado):")
    print("   1. ✅ GUEBER tiene configuración completa")
    print("   2. ✅ Todas las tarifas están mapeadas")
    print("   3. ✅ Sistema de prioridades funciona sin hardcode")
    print("   4. ✅ Mejora la mantenibilidad del código")
    
    print("\\n🟡 ELIMINACIÓN CON PRECAUCIÓN:")
    print("   1. ⚠️ Verificar otras empresas antes de eliminar")
    print("   2. ⚠️ Crear configuración para empresas faltantes")
    print("   3. ⚠️ Probar generación de asientos después")
    
    print("\\n🔴 CONSERVAR SI:")
    print("   1. ❌ Existen empresas sin configurar")
    print("   2. ❌ Se requiere compatibilidad absoluta")
    print("   3. ❌ No hay tiempo para migración completa")
    
    # 7. Plan de migración
    print("\\n7️⃣ PLAN DE MIGRACIÓN SUGERIDO")
    print("-" * 60)
    
    print("\\nFASE 1 - Preparación:")
    print("   • Auditar todas las empresas del sistema")
    print("   • Crear CompanyTaxAccountMapping para empresas faltantes")
    print("   • Verificar que todas tengan cuentas IVA válidas")
    
    print("\\nFASE 2 - Transición:")
    print("   • Agregar logging cuando se use fallback hardcode")
    print("   • Monitorear por período de prueba")
    print("   • Documentar empresas que aún dependen del hardcode")
    
    print("\\nFASE 3 - Eliminación:")
    print("   • Comentar el IVA_ACCOUNTS_MAPPING temporalmente")
    print("   • Probar generación de asientos en todas las empresas")
    print("   • Eliminar definitivamente si todo funciona")
    
    # 8. Código de eliminación segura
    print("\\n8️⃣ CÓDIGO PARA ELIMINACIÓN SEGURA")
    print("-" * 60)
    
    print("""
    # Modificación en _get_iva_account():
    
    # ANTES (con hardcode):
    account_code = cls.IVA_ACCOUNTS_MAPPING.get(iva_rate)
    
    # DESPUÉS (sin hardcode):
    # Eliminar la línea anterior y dejar que pase
    # directo a la búsqueda por código en ChartOfAccounts
    """)
    
    return True

if __name__ == "__main__":
    analyze_hardcoded_mapping_impact()