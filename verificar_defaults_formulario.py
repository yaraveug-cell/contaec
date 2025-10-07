#!/usr/bin/env python3
"""
Verificar configuración de valores por defecto en formulario de factura
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append('.')
django.setup()

def verificar_configuracion():
    """Verificar configuración de valores por defecto"""
    
    from apps.companies.models import Company, CompanyUser, PaymentMethod
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    print("🔍 VERIFICACIÓN DE VALORES POR DEFECTO EN FORMULARIO")
    print("=" * 60)
    
    # 1. Verificar empresas disponibles
    empresas = Company.objects.all()
    print(f"📋 Empresas totales: {empresas.count()}")
    for empresa in empresas:
        print(f"   - {empresa.trade_name} (ID: {empresa.id})")
    
    # 2. Verificar usuarios y sus empresas asignadas
    print(f"\n👥 Usuarios del sistema:")
    usuarios = User.objects.all()
    for usuario in usuarios:
        user_companies = CompanyUser.objects.filter(
            user=usuario,
            is_active=True
        )
        print(f"   - {usuario.username} ({'Superusuario' if usuario.is_superuser else 'Usuario normal'})")
        if user_companies.exists():
            for uc in user_companies:
                print(f"     → Empresa: {uc.company.trade_name}")
        else:
            print(f"     → Sin empresas asignadas")
    
    # 3. Verificar método de pago "Efectivo"
    print(f"\n💳 Verificación método 'Efectivo':")
    efectivo = PaymentMethod.objects.filter(
        is_active=True,
        name__icontains='efectivo'
    ).first()
    
    if efectivo:
        print(f"   ✅ Encontrado: {efectivo.name} (ID: {efectivo.id})")
        if efectivo.parent_account:
            print(f"   📊 Cuenta padre: {efectivo.parent_account.code} - {efectivo.parent_account.name}")
    else:
        print("   ❌ Método 'Efectivo' no encontrado")
    
    # 4. Simulación de configuración por tipo de usuario
    print(f"\n🎯 CONFIGURACIÓN ESPERADA:")
    
    for usuario in usuarios:
        print(f"\n   👤 Usuario: {usuario.username}")
        
        if usuario.is_superuser:
            print("   🔧 Configuración (Superusuario):")
            primera_empresa = empresas.first()
            if primera_empresa:
                print(f"      📍 Empresa por defecto: {primera_empresa.trade_name}")
            if efectivo:
                print(f"      💳 Forma de pago por defecto: {efectivo.name}")
        else:
            print("   🔧 Configuración (Usuario normal):")
            user_companies = CompanyUser.objects.filter(
                user=usuario,
                is_active=True
            )
            
            if user_companies.count() == 1:
                empresa = user_companies.first().company
                print(f"      📍 Empresa por defecto: {empresa.trade_name} (único, readonly)")
            elif user_companies.count() > 1:
                primera = user_companies.first().company
                print(f"      📍 Empresa por defecto: {primera.trade_name} (primera de {user_companies.count()})")
            else:
                print("      ⚠️ Sin empresas asignadas")
            
            if efectivo:
                print(f"      💳 Forma de pago por defecto: {efectivo.name}")

if __name__ == '__main__':
    try:
        verificar_configuracion()
        print(f"\n🎉 VERIFICACIÓN COMPLETADA")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()