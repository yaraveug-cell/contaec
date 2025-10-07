#!/usr/bin/env python3
"""
Verificar clientes existentes para probar autocompletado
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append('.')
django.setup()

def check_customers_for_autocomplete():
    """Verificar clientes disponibles para autocompletado"""
    
    from apps.invoicing.models import Customer
    from apps.companies.models import Company
    
    print("👤 VERIFICACIÓN DE CLIENTES PARA AUTOCOMPLETADO")
    print("=" * 55)
    
    # Obtener todas las empresas
    companies = Company.objects.all()
    print(f"🏢 Empresas totales: {companies.count()}")
    
    total_customers = 0
    
    for company in companies:
        customers = Customer.objects.filter(company=company)
        customer_count = customers.count()
        total_customers += customer_count
        
        print(f"\n🏢 {company.trade_name}:")
        print(f"   👤 Clientes: {customer_count}")
        
        if customer_count > 0:
            print(f"   📋 Ejemplos de búsqueda:")
            
            # Mostrar algunos clientes para ejemplos de búsqueda
            sample_customers = customers[:5]
            for i, customer in enumerate(sample_customers, 1):
                # Crear ejemplos de términos de búsqueda
                search_terms = []
                
                # Por nombre comercial
                if len(customer.trade_name) >= 3:
                    search_terms.append(customer.trade_name[:3].lower())
                
                # Por identificación
                if len(customer.identification) >= 3:
                    search_terms.append(customer.identification[:3])
                
                # Por razón social si existe
                if customer.legal_name and len(customer.legal_name) >= 3:
                    search_terms.append(customer.legal_name[:3].lower())
                
                terms_text = " / ".join(search_terms[:2])  # Mostrar max 2 términos
                
                print(f"      {i}. {customer.trade_name} ({customer.identification})")
                print(f"         💡 Buscar con: '{terms_text}'")
        else:
            print(f"   ⚠️ No hay clientes para esta empresa")
    
    print(f"\n📊 RESUMEN TOTAL:")
    print(f"   👤 Clientes totales: {total_customers}")
    
    if total_customers > 0:
        print(f"\n✅ AUTOCOMPLETADO LISTO:")
        print(f"   🔍 El campo Cliente tendrá {total_customers} registros para buscar")
        print(f"   📝 Podrás buscar por:")
        print(f"      • Nombre comercial")
        print(f"      • Identificación (cédula/RUC)")
        print(f"      • Razón social")
        print(f"      • Email")
        print(f"      • Teléfono")
        
        print(f"\n🧪 PARA PROBAR:")
        print(f"   1. Ve a: http://127.0.0.1:8000/admin/invoicing/invoice/add/")
        print(f"   2. Haz clic en el campo Cliente")
        print(f"   3. Escribe algunas letras del nombre o identificación")
        print(f"   4. Deberían aparecer sugerencias filtradas")
        
        # Mostrar algunos términos de búsqueda sugeridos
        print(f"\n💡 TÉRMINOS DE PRUEBA SUGERIDOS:")
        all_customers = Customer.objects.all()[:10]
        
        suggested_terms = set()
        for customer in all_customers:
            # Agregar primeras 3 letras del nombre
            if len(customer.trade_name) >= 3:
                suggested_terms.add(f"'{customer.trade_name[:3].lower()}'")
            
            # Agregar primeros números de identificación
            if len(customer.identification) >= 3 and customer.identification[:3].isdigit():
                suggested_terms.add(f"'{customer.identification[:3]}'")
        
        terms_list = list(suggested_terms)[:5]  # Mostrar máximo 5
        print(f"   {' • '.join(terms_list)}")
        
    else:
        print(f"\n❌ NO HAY CLIENTES:")
        print(f"   📝 Necesitas crear clientes para probar el autocompletado")
        print(f"   ➕ Ve a: http://127.0.0.1:8000/admin/invoicing/customer/add/")
        print(f"   💡 Crea algunos clientes con nombres variados")

if __name__ == '__main__':
    try:
        check_customers_for_autocomplete()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()