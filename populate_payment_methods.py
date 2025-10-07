#!/usr/bin/env python
"""
Script para crear datos iniciales de formas de pago
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import PaymentMethod
from apps.accounting.models import ChartOfAccounts

def create_initial_payment_methods():
    """Crear métodos de pago iniciales"""
    
    print("💳 CREANDO DATOS INICIALES: FORMAS DE PAGO")
    print("=" * 60)
    
    # Buscar cuentas padre en el plan de cuentas
    try:
        # Buscar cuenta padre para EFECTIVO (CAJA)
        caja_account = ChartOfAccounts.objects.filter(
            name__icontains='CAJA'
        ).first()
        
        # Buscar cuenta padre para CREDITO (CLIENTES RELACIONADOS)
        credito_account = ChartOfAccounts.objects.filter(
            name__icontains='CLIENTES RELACIONADOS'
        ).first()
        
        # Buscar cuenta padre para TRANSFERENCIA (BANCOS)
        banco_account = ChartOfAccounts.objects.filter(
            name__icontains='BANCO'
        ).first()
        
        print(f"🔍 Cuentas encontradas:")
        print(f"   💰 CAJA: {caja_account}")
        print(f"   💳 CLIENTES RELACIONADOS: {credito_account}")  
        print(f"   🏦 BANCOS: {banco_account}")
        
    except Exception as e:
        print(f"⚠️  Error buscando cuentas: {e}")
        caja_account = None
        credito_account = None
        banco_account = None
    
    # Crear métodos de pago
    payment_methods_data = [
        {
            'name': 'Efectivo',
            'description': 'Pago en efectivo inmediato',
            'parent_account': caja_account
        },
        {
            'name': 'Crédito',
            'description': 'Pago a crédito según términos acordados',
            'parent_account': credito_account
        },
        {
            'name': 'Transferencia',
            'description': 'Transferencia bancaria electrónica',
            'parent_account': banco_account
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for method_data in payment_methods_data:
        payment_method, created = PaymentMethod.objects.get_or_create(
            name=method_data['name'],
            defaults={
                'description': method_data['description'],
                'parent_account': method_data['parent_account']
            }
        )
        
        if created:
            created_count += 1
            status = "✅ CREADO"
        else:
            # Actualizar campos si ya existe
            payment_method.description = method_data['description']
            payment_method.parent_account = method_data['parent_account']
            payment_method.save()
            updated_count += 1
            status = "🔄 ACTUALIZADO"
        
        account_name = payment_method.parent_account.name if payment_method.parent_account else "Sin cuenta padre"
        
        print(f"   {status}: {payment_method.name}")
        print(f"      Descripción: {payment_method.description}")
        print(f"      Cuenta Padre: {account_name}")
        print()
    
    print("=" * 60)
    print("📊 RESUMEN:")
    print(f"   ✅ Creados: {created_count}")
    print(f"   🔄 Actualizados: {updated_count}")
    print(f"   📋 Total: {PaymentMethod.objects.count()}")
    
    print("\n🎯 CONFIGURACIÓN COMPLETADA:")
    print("   • Modelos creados y migrados")
    print("   • Datos iniciales cargados")
    print("   • Admin configurado con modal")
    print("   • Campo agregado a Company")
    
    print(f"\n🚀 El campo 'Forma de Pago' está listo en:")
    print(f"   📝 Admin → Empresas → Añadir Empresa → Configuración Contable")
    print(f"   ➕ Botón '+' disponible para agregar nuevas formas de pago")
    print(f"   🔗 Vinculado al plan de cuentas")
    
    return True

if __name__ == "__main__":
    success = create_initial_payment_methods()
    sys.exit(0 if success else 1)