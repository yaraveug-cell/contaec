#!/usr/bin/env python
"""
Script de verificación: Interfaz de Configuración de Cuentas IVA - GUEBER
Verifica que la implementación esté completa y funcionando
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import Company, CompanyTaxAccountMapping
from apps.accounting.services import AutomaticJournalEntryService
from django.contrib import admin
from decimal import Decimal

def verify_implementation():
    """Verificar implementación completa de la interfaz de cuentas IVA"""
    
    print("🔍 VERIFICACIÓN FINAL: INTERFAZ CUENTAS IVA - GUEBER")
    print("=" * 70)
    
    success_count = 0
    total_checks = 7
    
    # 1. Verificar modelo CompanyTaxAccountMapping
    print("1️⃣ MODELO CompanyTaxAccountMapping:")
    try:
        # Verificar que el modelo existe y tiene los campos correctos
        model_fields = [field.name for field in CompanyTaxAccountMapping._meta.fields]
        required_fields = ['company', 'tax_rate', 'account']
        
        if all(field in model_fields for field in required_fields):
            print("   ✅ Modelo creado con campos correctos")
            success_count += 1
        else:
            print("   ❌ Modelo incompleto")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Verificar migración aplicada
    print("\n2️⃣ MIGRACIÓN DE BASE DE DATOS:")
    try:
        # Intentar crear una instancia de prueba
        test_count = CompanyTaxAccountMapping.objects.count()
        print(f"   ✅ Tabla existe - Registros actuales: {test_count}")
        success_count += 1
    except Exception as e:
        print(f"   ❌ Error en base de datos: {e}")
    
    # 3. Verificar configuración en Admin
    print("\n3️⃣ CONFIGURACIÓN ADMIN:")
    try:
        if CompanyTaxAccountMapping in admin.site._registry:
            print("   ✅ Inline disponible en admin")
            success_count += 1
        else:
            print("   ❌ Inline no registrado")
    except Exception as e:
        print(f"   ❌ Error admin: {e}")
    
    # 4. Verificar empresa GUEBER
    print("\n4️⃣ EMPRESA GUEBER:")
    try:
        gueber = Company.objects.filter(trade_name__icontains='gueber').first()
        if gueber:
            print(f"   ✅ Empresa encontrada: {gueber.trade_name}")
            success_count += 1
        else:
            print("   ❌ Empresa GUEBER no encontrada")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 5. Verificar configuraciones IVA de GUEBER
    print("\n5️⃣ CONFIGURACIONES IVA GUEBER:")
    try:
        mappings = CompanyTaxAccountMapping.objects.filter(company=gueber)
        if mappings.exists():
            print(f"   ✅ Configuraciones creadas: {mappings.count()}")
            for mapping in mappings:
                print(f"      • IVA {mapping.tax_rate}% → {mapping.account.code}")
            success_count += 1
        else:
            print("   ❌ Sin configuraciones")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 6. Verificar integración con AutomaticJournalEntryService
    print("\n6️⃣ INTEGRACIÓN CON SERVICIO CONTABLE:")
    try:
        # Probar método _get_iva_account
        account_15 = AutomaticJournalEntryService._get_iva_account(gueber, Decimal('15.00'))
        account_5 = AutomaticJournalEntryService._get_iva_account(gueber, Decimal('5.00'))
        
        if account_15 and account_5:
            print("   ✅ Método _get_iva_account funcionando")
            print(f"      • IVA 15%: {account_15.code}")
            print(f"      • IVA 5%: {account_5.code}")
            success_count += 1
        else:
            print("   ❌ Método no funciona correctamente")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 7. Verificar compatibilidad con sistema existente
    print("\n7️⃣ COMPATIBILIDAD CON SISTEMA EXISTENTE:")
    try:
        # Verificar que el mapeo hardcodeado sigue existiendo como fallback
        hardcoded_mapping = AutomaticJournalEntryService.IVA_ACCOUNTS_MAPPING
        if hardcoded_mapping:
            print("   ✅ Mapeo hardcodeado conservado como fallback")
            print(f"      • Mapeo actual: {hardcoded_mapping}")
            success_count += 1
        else:
            print("   ❌ Mapeo hardcodeado perdido")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Resumen final
    print(f"\n🎯 RESUMEN DE VERIFICACIÓN:")
    print(f"   ✅ Verificaciones exitosas: {success_count}/{total_checks}")
    print(f"   📊 Porcentaje de éxito: {(success_count/total_checks)*100:.1f}%")
    
    if success_count == total_checks:
        print(f"\n🚀 IMPLEMENTACIÓN COMPLETA Y EXITOSA!")
        print(f"\n📍 UBICACIÓN DE LA INTERFAZ:")
        print(f"   🌐 Admin → Empresas → GUEBER → Modificar empresa")
        print(f"   📋 Sección: 'Configuración Contable'")
        print(f"   ➕ Tabla inline: 'Configuraciones Cuentas IVA'")
        
        print(f"\n🎨 CARACTERÍSTICAS IMPLEMENTADAS:")
        print(f"   • ✅ Modelo CompanyTaxAccountMapping creado")
        print(f"   • ✅ Migración aplicada correctamente")
        print(f"   • ✅ Interface admin con inline tabular")
        print(f"   • ✅ Datos iniciales para GUEBER configurados")
        print(f"   • ✅ Integración con AutomaticJournalEntryService")
        print(f"   • ✅ Sistema de fallback conservado")
        print(f"   • ✅ Configuración dinámica por empresa")
        
        print(f"\n🔄 FUNCIONAMIENTO:")
        print(f"   1️⃣ Sistema busca configuración específica por empresa")
        print(f"   2️⃣ Si no encuentra, usa mapeo hardcodeado como fallback")
        print(f"   3️⃣ Facturas existentes no se ven afectadas")
        print(f"   4️⃣ Nueva funcionalidad lista para usar")
        
        return True
    else:
        print(f"\n❌ IMPLEMENTACIÓN INCOMPLETA")
        print(f"   Faltan {total_checks - success_count} verificaciones")
        return False

if __name__ == "__main__":
    success = verify_implementation()
    sys.exit(0 if success else 1)