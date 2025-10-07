#!/usr/bin/env python3
"""
Corrección: Establecer Efectivo como forma de pago por defecto para todas las empresas
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append('.')
django.setup()

def fix_companies_payment_method():
    """Corregir configuración de formas de pago en empresas"""
    
    from apps.companies.models import Company, PaymentMethod
    
    print("🔧 CORRECCIÓN: CONFIGURACIÓN FORMAS DE PAGO")
    print("=" * 50)
    
    # 1. Obtener método "Efectivo"
    try:
        efectivo = PaymentMethod.objects.get(name__icontains='efectivo', is_active=True)
        print(f"✅ Método Efectivo encontrado: {efectivo.name} (ID: {efectivo.id})")
    except PaymentMethod.DoesNotExist:
        print("❌ Método Efectivo no encontrado")
        return
    
    # 2. Actualizar todas las empresas
    print(f"\n🏢 ACTUALIZANDO EMPRESAS:")
    
    companies = Company.objects.all()
    updated_count = 0
    
    for company in companies:
        old_method = company.payment_method.name if company.payment_method else "Sin configurar"
        
        # Actualizar a Efectivo
        company.payment_method = efectivo
        company.save()
        
        print(f"   {company.trade_name}:")
        print(f"      Anterior: {old_method}")
        print(f"      Nuevo: {efectivo.name} ✅")
        
        updated_count += 1
    
    print(f"\n🎯 RESULTADO:")
    print(f"   ✅ {updated_count} empresas actualizadas")
    print(f"   💳 Todas configuradas con: {efectivo.name}")
    print(f"   📊 Cuenta padre: {efectivo.parent_account.code} - {efectivo.parent_account.name}")
    
    # 3. Verificar resultado
    print(f"\n✅ VERIFICACIÓN:")
    for company in Company.objects.all():
        method_name = company.payment_method.name if company.payment_method else "Sin configurar"
        print(f"   {company.trade_name} → {method_name}")

if __name__ == '__main__':
    try:
        fix_companies_payment_method()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()