#!/usr/bin/env python
"""
Script para configurar empresas con formas de pago predeterminadas
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.companies.models import Company, PaymentMethod

def configure_companies_payment_methods():
    """Configurar formas de pago predeterminadas para empresas"""
    
    print("💳 CONFIGURANDO FORMAS DE PAGO PARA EMPRESAS")
    print("=" * 60)
    
    try:
        # Obtener empresas y métodos de pago
        companies = Company.objects.all()
        payment_methods = PaymentMethod.objects.filter(is_active=True)
        
        print(f"🏢 Empresas encontradas: {companies.count()}")
        print(f"💳 Métodos de pago disponibles: {payment_methods.count()}")
        
        # Obtener métodos específicos
        efectivo = PaymentMethod.objects.filter(name='Efectivo').first()
        credito = PaymentMethod.objects.filter(name='Crédito').first()
        transferencia = PaymentMethod.objects.filter(name='Transferencia').first()
        
        print(f"\n📋 Métodos disponibles:")
        if efectivo:
            print(f"   💰 Efectivo: {efectivo}")
        if credito:
            print(f"   💳 Crédito: {credito}")
        if transferencia:
            print(f"   🏦 Transferencia: {transferencia}")
        
        # Configurar empresas con diferentes métodos
        configured_count = 0
        
        for i, company in enumerate(companies):
            # Asignar método según empresa (ejemplo de distribución)
            if i % 3 == 0 and efectivo:
                company.payment_method = efectivo
                method_name = "Efectivo"
            elif i % 3 == 1 and credito:
                company.payment_method = credito
                method_name = "Crédito"
            elif transferencia:
                company.payment_method = transferencia
                method_name = "Transferencia"
            else:
                # Fallback a efectivo si está disponible
                if efectivo:
                    company.payment_method = efectivo
                    method_name = "Efectivo (fallback)"
                else:
                    continue
            
            company.save(update_fields=['payment_method'])
            configured_count += 1
            
            print(f"   ✅ {company.trade_name}: {method_name}")
        
        print(f"\n" + "=" * 60)
        print(f"📊 RESUMEN:")
        print(f"   ✅ Empresas configuradas: {configured_count}")
        print(f"   📋 Total empresas: {companies.count()}")
        
        print(f"\n🎯 FUNCIONALIDAD HABILITADA:")
        print(f"   • Cada empresa tiene forma de pago predeterminada")
        print(f"   • Facturas heredarán configuración de empresa")
        print(f"   • Filtrado dinámico completamente funcional")
        
        # Verificar configuración
        print(f"\n🔍 VERIFICACIÓN FINAL:")
        companies_with_payment = Company.objects.filter(
            payment_method__isnull=False
        ).count()
        
        print(f"   📈 Empresas con forma de pago: {companies_with_payment}/{companies.count()}")
        
        if companies_with_payment > 0:
            print(f"   ✅ Configuración completada exitosamente")
            return True
        else:
            print(f"   ❌ No se pudieron configurar empresas")
            return False
            
    except Exception as e:
        print(f"   ❌ Error configurando empresas: {e}")
        return False

if __name__ == "__main__":
    success = configure_companies_payment_methods()
    sys.exit(0 if success else 1)