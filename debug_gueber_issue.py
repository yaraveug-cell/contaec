#!/usr/bin/env python3
"""
Debug: Verificar configuración actual de empresa GUEBER
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append('.')
django.setup()

def debug_gueber_config():
    """Verificar configuración específica de GUEBER"""
    
    from apps.companies.models import Company, PaymentMethod
    from apps.invoicing.models import Invoice
    
    print("🔍 DEBUG: CONFIGURACIÓN DE GUEBER")
    print("=" * 50)
    
    # 1. Verificar empresa GUEBER
    try:
        gueber = Company.objects.get(trade_name__icontains='GUEBER')
        print(f"✅ Empresa GUEBER encontrada:")
        print(f"   ID: {gueber.id}")
        print(f"   Trade Name: {gueber.trade_name}")
        
        # Verificar si GUEBER tiene una forma de pago por defecto configurada
        if hasattr(gueber, 'payment_method') and gueber.payment_method:
            print(f"   💳 Forma de pago configurada: {gueber.payment_method.name} (ID: {gueber.payment_method.id})")
            if gueber.payment_method.parent_account:
                print(f"   📊 Cuenta padre: {gueber.payment_method.parent_account.code} - {gueber.payment_method.parent_account.name}")
        else:
            print(f"   ⚠️ No tiene forma de pago configurada")
            
    except Company.DoesNotExist:
        print("❌ Empresa GUEBER no encontrada")
        return
    
    # 2. Verificar método "Efectivo"
    print(f"\n💰 VERIFICACIÓN MÉTODO EFECTIVO:")
    efectivo = PaymentMethod.objects.filter(
        is_active=True,
        name__icontains='efectivo'
    ).first()
    
    if efectivo:
        print(f"   ✅ Método Efectivo: {efectivo.name} (ID: {efectivo.id})")
        if efectivo.parent_account:
            print(f"   📊 Cuenta padre: {efectivo.parent_account.code} - {efectivo.parent_account.name}")
    else:
        print("   ❌ Método Efectivo no encontrado")
    
    # 3. Verificar método "Crédito"  
    print(f"\n💳 VERIFICACIÓN MÉTODO CRÉDITO:")
    credito = PaymentMethod.objects.filter(
        is_active=True,
        name__icontains='credito'
    ).first()
    
    if credito:
        print(f"   ✅ Método Crédito: {credito.name} (ID: {credito.id})")
        if credito.parent_account:
            print(f"   📊 Cuenta padre: {credito.parent_account.code} - {credito.parent_account.name}")
    else:
        print("   ❌ Método Crédito no encontrado")
    
    # 4. Verificar por qué GUEBER aparece con Crédito
    print(f"\n🔍 ANÁLISIS DEL PROBLEMA:")
    
    if hasattr(gueber, 'payment_method') and gueber.payment_method:
        if gueber.payment_method.name.upper().find('CREDITO') >= 0:
            print(f"   ❌ PROBLEMA IDENTIFICADO:")
            print(f"   La empresa GUEBER está configurada con '{gueber.payment_method.name}'")
            print(f"   Esto sobrescribe el valor por defecto 'Efectivo'")
            
            # Verificar configuración en JavaScript
            print(f"\n📱 CONFIGURACIÓN JAVASCRIPT:")
            print(f"   El sistema JavaScript carga esta configuración:")
            print(f"   Empresa {gueber.id} → Método {gueber.payment_method.id} ({gueber.payment_method.name})")
            print(f"   Método {gueber.payment_method.id} → Cuenta padre {gueber.payment_method.parent_account.code if gueber.payment_method.parent_account else 'Sin cuenta'}")
            
    # 5. Mostrar todos los métodos de pago
    print(f"\n📋 TODOS LOS MÉTODOS DE PAGO:")
    methods = PaymentMethod.objects.filter(is_active=True).order_by('id')
    for method in methods:
        parent_info = f" → {method.parent_account.code}" if method.parent_account else " → Sin cuenta padre"
        print(f"   {method.id}: {method.name}{parent_info}")

if __name__ == '__main__':
    try:
        debug_gueber_config()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()