#!/usr/bin/env python3
"""
Análisis de implementación de autocompletado para cuentas contables

Autor: Sistema ContaEC
Fecha: 2 de octubre, 2025
Objetivo: Analizar y diseñar autocompletado eficiente para selección de cuentas
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import ChartOfAccounts, JournalEntry
from apps.companies.models import Company
from django.contrib.auth import get_user_model

User = get_user_model()

def analyze_current_account_selection():
    """
    Analizar el sistema actual de selección de cuentas
    """
    print("📊 ANÁLISIS DEL SISTEMA ACTUAL DE SELECCIÓN DE CUENTAS")
    print("=" * 65)
    
    total_accounts = ChartOfAccounts.objects.filter(is_active=True).count()
    companies = Company.objects.count()
    
    print(f"\n📈 ESTADÍSTICAS GENERALES:")
    print("-" * 50)
    print(f"✅ Total de cuentas activas: {total_accounts}")
    print(f"✅ Total de empresas: {companies}")
    
    if total_accounts > 0:
        # Analizar distribución por empresa
        print(f"\n🏢 DISTRIBUCIÓN POR EMPRESA:")
        print("-" * 50)
        
        for company in Company.objects.all():
            company_accounts = ChartOfAccounts.objects.filter(
                company=company, 
                is_active=True
            ).count()
            percentage = (company_accounts / total_accounts) * 100 if total_accounts > 0 else 0
            print(f"   • {company.trade_name}: {company_accounts} cuentas ({percentage:.1f}%)")
        
        # Analizar niveles de jerarquía
        print(f"\n📊 ANÁLISIS DE JERARQUÍA:")
        print("-" * 50)
        
        levels_distribution = {}
        for account in ChartOfAccounts.objects.filter(is_active=True):
            level = account.level
            if level in levels_distribution:
                levels_distribution[level] += 1
            else:
                levels_distribution[level] = 1
        
        for level, count in sorted(levels_distribution.items()):
            percentage = (count / total_accounts) * 100
            print(f"   • Nivel {level}: {count} cuentas ({percentage:.1f}%)")
        
        # Mostrar ejemplos de cuentas largas
        print(f"\n📝 EJEMPLOS DE CUENTAS (LONGITUD):")
        print("-" * 50)
        
        sample_accounts = ChartOfAccounts.objects.filter(is_active=True)[:10]
        for account in sample_accounts:
            full_name = str(account)  # Usa el __str__ que incluye código + nombre
            length = len(full_name)
            print(f"   • {full_name[:60]}{'...' if length > 60 else ''} ({length} chars)")

def analyze_performance_needs():
    """
    Analizar necesidades de rendimiento para autocompletado
    """
    print(f"\n⚡ ANÁLISIS DE RENDIMIENTO PARA AUTOCOMPLETADO")
    print("=" * 65)
    
    print(f"🎯 ESCENARIOS DE USO:")
    print("-" * 50)
    print("   • Usuario escribe código de cuenta (ej: '1.1.01')")
    print("   • Usuario escribe nombre de cuenta (ej: 'caja')")
    print("   • Usuario necesita ver jerarquía completa")
    print("   • Usuario trabaja con múltiples empresas")
    
    total_accounts = ChartOfAccounts.objects.filter(is_active=True).count()
    
    print(f"\n📊 MÉTRICAS DE RENDIMIENTO:")
    print("-" * 50)
    
    if total_accounts <= 100:
        performance_level = "EXCELENTE"
        recommendation = "Select estándar funciona bien"
    elif total_accounts <= 500:
        performance_level = "BUENO"  
        recommendation = "Autocompletado recomendado"
    elif total_accounts <= 1000:
        performance_level = "MODERADO"
        recommendation = "Autocompletado necesario"
    else:
        performance_level = "CRÍTICO"
        recommendation = "Autocompletado + paginación obligatorios"
    
    print(f"   • Total cuentas: {total_accounts}")
    print(f"   • Nivel de rendimiento: {performance_level}")
    print(f"   • Recomendación: {recommendation}")
    
    print(f"\n🔍 ANÁLISIS POR EMPRESA:")
    print("-" * 50)
    
    for company in Company.objects.all():
        company_accounts = ChartOfAccounts.objects.filter(
            company=company,
            is_active=True
        ).count()
        
        if company_accounts <= 50:
            company_performance = "Excelente"
        elif company_accounts <= 200:
            company_performance = "Bueno"
        elif company_accounts <= 500:
            company_performance = "Moderado"
        else:
            company_performance = "Lento"
        
        print(f"   • {company.trade_name}: {company_accounts} cuentas - {company_performance}")

def evaluate_autocomplete_options():
    """
    Evaluar opciones de autocompletado disponibles
    """
    print(f"\n🛠️ OPCIONES DE IMPLEMENTACIÓN DE AUTOCOMPLETADO")
    print("=" * 65)
    
    print("✅ OPCIÓN 1 - DJANGO ADMIN AUTOCOMPLETE (RECOMENDADA)")
    print("-" * 50)
    print("   🎯 Características:")
    print("      • Widget nativo de Django Admin")
    print("      • Integración perfecta con admin")
    print("      • Búsqueda AJAX automática")
    print("      • Paginación incluida")
    print("      • Filtrado por empresa automático")
    print("")
    print("   ✅ Ventajas:")
    print("      • Sin JavaScript adicional")
    print("      • Mantenimiento mínimo") 
    print("      • Rendimiento óptimo")
    print("      • Integración con seguridad")
    print("      • Soporte móvil")
    print("")
    print("   ❌ Limitaciones:")
    print("      • Estilo limitado a Django Admin")
    print("      • Menos personalización visual")
    
    print("\n⚠️ OPCIÓN 2 - SELECT2 PERSONALIZADO")
    print("-" * 50)
    print("   🎯 Características:")
    print("      • Widget Select2 con AJAX")
    print("      • Mayor personalización visual")
    print("      • Búsqueda avanzada")
    print("")
    print("   ✅ Ventajas:")
    print("      • Interfaz más atractiva")
    print("      • Búsqueda multi-campo")
    print("      • Mayor control del comportamiento")
    print("")
    print("   ❌ Limitaciones:")
    print("      • Más código JavaScript")
    print("      • Mayor complejidad de mantenimiento")
    print("      • Posible conflicto con Django Admin")

def analyze_search_patterns():
    """
    Analizar patrones de búsqueda esperados
    """
    print(f"\n🔍 ANÁLISIS DE PATRONES DE BÚSQUEDA")
    print("=" * 65)
    
    print("📝 PATRONES COMUNES DE BÚSQUEDA:")
    print("-" * 50)
    
    # Analizar cuentas para extraer patrones
    sample_accounts = ChartOfAccounts.objects.filter(is_active=True)[:20]
    
    print("   🔢 POR CÓDIGO:")
    for account in sample_accounts[:5]:
        code = account.code
        print(f"      • '{code[:3]}' → '{account.code} - {account.name}'")
    
    print("\n   📝 POR NOMBRE:")  
    for account in sample_accounts[5:10]:
        name = account.name
        words = name.split()
        first_word = words[0] if words else name
        print(f"      • '{first_word.lower()[:4]}' → '{account.code} - {account.name}'")
    
    print(f"\n🎯 REQUERIMIENTOS DE BÚSQUEDA:")
    print("-" * 50)
    print("   ✅ Búsqueda por código (parcial)")
    print("   ✅ Búsqueda por nombre (parcial)")
    print("   ✅ Búsqueda insensible a mayúsculas")
    print("   ✅ Filtrado automático por empresa")
    print("   ✅ Ordenamiento por código")
    print("   ✅ Mostrar jerarquía visual")
    print("   ✅ Paginación para conjuntos grandes")

def recommend_implementation():
    """
    Recomendar implementación específica
    """
    print(f"\n🎯 RECOMENDACIÓN DE IMPLEMENTACIÓN")
    print("=" * 65)
    
    print("✅ IMPLEMENTACIÓN RECOMENDADA: DJANGO ADMIN AUTOCOMPLETE")
    print("-" * 50)
    
    print("📋 JUSTIFICACIÓN:")
    print("   • Sistema ya funciona bien con filtrado actual")
    print("   • Django Admin Autocomplete es nativo y eficiente") 
    print("   • Integración perfecta con seguridad multiempresa")
    print("   • Mantenimiento mínimo")
    print("   • Excelente rendimiento con AJAX")
    
    print(f"\n🛠️ PASOS DE IMPLEMENTACIÓN:")
    print("-" * 50)
    print("   1. Agregar autocomplete_fields a JournalEntryLineInline")
    print("   2. Configurar search_fields en ChartOfAccountsAdmin")  
    print("   3. Personalizar get_search_results para mejor búsqueda")
    print("   4. Probar filtrado por empresa")
    print("   5. Verificar rendimiento")
    
    print(f"\n💻 CÓDIGO SUGERIDO:")
    print("-" * 50)
    
    print("🔧 EN JournalEntryLineInline:")
    print("""
    class JournalEntryLineInline(admin.TabularInline):
        model = JournalEntryLine
        fields = ['account', 'description', 'debit', 'credit', 'auxiliary_code']
        autocomplete_fields = ['account']  # ← Habilitar autocompletado
    """)
    
    print("🔧 EN ChartOfAccountsAdmin:")
    print("""
    @admin.register(ChartOfAccounts) 
    class ChartOfAccountsAdmin(CompanyFilterMixin, admin.ModelAdmin):
        search_fields = ['code', 'name']  # ← Campos de búsqueda
        
        def get_search_results(self, request, queryset, search_term):
            '''Búsqueda mejorada por código y nombre'''
            queryset, may_have_duplicates = super().get_search_results(
                request, queryset, search_term
            )
            
            # Búsqueda adicional por términos parciales
            if search_term:
                queryset = queryset.filter(
                    Q(code__icontains=search_term) | 
                    Q(name__icontains=search_term)
                ).distinct()
            
            return queryset, may_have_duplicates
    """)
    
    print(f"\n⚡ BENEFICIOS ESPERADOS:")
    print("-" * 50)
    print("   • 🚀 Búsqueda instantánea mientras escribes")
    print("   • 🎯 Filtrado automático por empresa")  
    print("   • 📱 Funciona perfectamente en móviles")
    print("   • ⚡ Carga solo resultados necesarios (paginado)")
    print("   • 🔒 Respeta permisos de seguridad")
    print("   • 🎨 Integración visual perfecta con admin")

def main():
    """
    Función principal del análisis
    """
    try:
        analyze_current_account_selection()
        analyze_performance_needs()
        evaluate_autocomplete_options()
        analyze_search_patterns()
        recommend_implementation()
        
        print("\n" + "=" * 65)
        print("🎉 ANÁLISIS COMPLETADO")
        print("=" * 65)
        print("✅ Django Admin Autocomplete es la mejor opción")
        print("✅ Implementación simple y eficiente") 
        print("✅ Mejora significativa en UX")
        print("✅ Compatible con sistema actual")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()