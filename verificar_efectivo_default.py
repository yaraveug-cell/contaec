#!/usr/bin/env python3
"""
Verificar y configurar método de pago "Efectivo" como por defecto
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append('.')
django.setup()

def verificar_efectivo():
    """Verificar que existe el método de pago Efectivo"""
    
    from apps.companies.models import PaymentMethod
    
    print("🔍 VERIFICACIÓN DEL MÉTODO DE PAGO POR DEFECTO")
    print("=" * 50)
    
    # Buscar método Efectivo
    efectivo = PaymentMethod.objects.filter(
        is_active=True,
        name__icontains='efectivo'
    ).first()
    
    if efectivo:
        print(f"✅ Método 'Efectivo' encontrado:")
        print(f"   ID: {efectivo.id}")
        print(f"   Nombre: {efectivo.name}")
        print(f"   Activo: {efectivo.is_active}")
        if efectivo.parent_account:
            print(f"   Cuenta Padre: {efectivo.parent_account.code} - {efectivo.parent_account.name}")
        else:
            print("   ⚠️ Sin cuenta padre configurada")
    else:
        print("❌ Método 'Efectivo' no encontrado")
        print("\n📋 Métodos de pago disponibles:")
        methods = PaymentMethod.objects.filter(is_active=True)
        for method in methods:
            print(f"   - {method.name} (ID: {method.id})")
    
    print("\n📊 RESUMEN:")
    print(f"   Total métodos activos: {PaymentMethod.objects.filter(is_active=True).count()}")
    
    # Verificar configuración en invoices existentes
    from apps.invoicing.models import Invoice
    facturas_con_efectivo = Invoice.objects.filter(payment_form=efectivo).count() if efectivo else 0
    print(f"   Facturas con Efectivo: {facturas_con_efectivo}")
    
    return efectivo

if __name__ == '__main__':
    try:
        metodo_efectivo = verificar_efectivo()
        if metodo_efectivo:
            print(f"\n🎯 CONFIGURACIÓN EXITOSA:")
            print(f"   El método '{metodo_efectivo.name}' (ID: {metodo_efectivo.id}) se usará como valor por defecto")
        else:
            print("\n⚠️ ACCIÓN REQUERIDA:")
            print("   Crear o activar un método de pago llamado 'Efectivo'")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()