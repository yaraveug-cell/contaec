"""
Comparar extractos de PICHINCHA vs PACIFICO para encontrar diferencias
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.banking.models import BankAccount, ExtractoBancario, ExtractoBancarioDetalle

def comparar_extractos():
    """Comparar extractos para encontrar diferencias"""
    
    print("🔍 COMPARACIÓN DE EXTRACTOS")
    print("="*60)
    
    # Obtener cuentas
    try:
        cuenta_pacifico = BankAccount.objects.get(account_number='2100123456')  # Funciona
        cuenta_pichincha = BankAccount.objects.get(account_number='2201109377')  # No funciona
        
        print(f"📊 CUENTAS BANCARIAS:")
        print(f"   ✅ Pacífico: {cuenta_pacifico} (ID: {cuenta_pacifico.id})")
        print(f"   ❓ Pichincha: {cuenta_pichincha} (ID: {cuenta_pichincha.id})")
        
        # Obtener extractos
        extracto_pacifico = ExtractoBancario.objects.filter(bank_account=cuenta_pacifico).first()
        extracto_pichincha = ExtractoBancario.objects.filter(bank_account=cuenta_pichincha).first()
        
        print(f"\n📄 EXTRACTOS:")
        if extracto_pacifico:
            print(f"   ✅ Pacífico: {extracto_pacifico} (ID: {extracto_pacifico.id})")
            print(f"      📅 Período: {extracto_pacifico.period_start} - {extracto_pacifico.period_end}")
            print(f"      💰 Saldos: ${extracto_pacifico.initial_balance} → ${extracto_pacifico.final_balance}")
            print(f"      📊 Status: {extracto_pacifico.status}")
        else:
            print(f"   ❌ Pacífico: No tiene extracto")
        
        if extracto_pichincha:
            print(f"   ❓ Pichincha: {extracto_pichincha} (ID: {extracto_pichincha.id})")
            print(f"      📅 Período: {extracto_pichincha.period_start} - {extracto_pichincha.period_end}")
            print(f"      💰 Saldos: ${extracto_pichincha.initial_balance} → ${extracto_pichincha.final_balance}")
            print(f"      📊 Status: {extracto_pichincha.status}")
        else:
            print(f"   ❌ Pichincha: No tiene extracto")
        
        # Comparar detalles
        if extracto_pacifico and extracto_pichincha:
            print(f"\n📋 DETALLES DE EXTRACTOS:")
            
            items_pacifico = ExtractoBancarioDetalle.objects.filter(extracto=extracto_pacifico)
            items_pichincha = ExtractoBancarioDetalle.objects.filter(extracto=extracto_pichincha)
            
            print(f"   ✅ Pacífico: {items_pacifico.count()} items")
            print(f"   ❓ Pichincha: {items_pichincha.count()} items")
            
            # Analizar items de Pichincha en detalle
            print(f"\n🔍 ANÁLISIS DETALLADO - PICHINCHA:")
            if items_pichincha.exists():
                for i, item in enumerate(items_pichincha, 1):
                    print(f"   {i}. ID: {item.id}")
                    print(f"      📅 Fecha: {item.fecha} (tipo: {type(item.fecha)})")
                    print(f"      📝 Descripción: '{item.descripcion}' (len: {len(item.descripcion)})")
                    print(f"      🔢 Referencia: '{item.referencia}'")
                    print(f"      💰 Débito: {item.debito}, Crédito: {item.credito}")
                    print(f"      💳 Saldo: {item.saldo}")
                    print(f"      ✅ Conciliado: {item.is_reconciled}")
                    
                    # Verificar si hay caracteres especiales o problemas
                    if item.descripcion:
                        try:
                            item.descripcion.encode('utf-8')
                            print(f"      ✅ Descripción OK (UTF-8)")
                        except UnicodeEncodeError:
                            print(f"      ❌ Descripción tiene problemas de encoding")
                    
                    # Verificar campos None
                    campos_none = []
                    if item.debito is None and item.credito is None:
                        campos_none.append('ambos_montos_none')
                    if item.descripcion is None:
                        campos_none.append('descripcion_none')
                    if item.fecha is None:
                        campos_none.append('fecha_none')
                    
                    if campos_none:
                        print(f"      ⚠️  Campos None: {campos_none}")
                    
                    print()
            else:
                print(f"   ❌ No hay items en el extracto de Pichincha")
        
        # Probar query específica que usa la vista
        print(f"\n🧪 TEST QUERY ESPECÍFICA (como en la vista):")
        if extracto_pichincha:
            query_result = ExtractoBancarioDetalle.objects.filter(
                extracto=extracto_pichincha
            ).filter(is_reconciled=False).order_by('fecha')
            
            print(f"   📊 Query result count: {query_result.count()}")
            
            if query_result.exists():
                print(f"   ✅ Query exitosa")
                for item in query_result[:3]:  # Solo primeros 3
                    print(f"      - {item.fecha}: {item.descripcion}")
            else:
                print(f"   ⚠️  Query retorna vacío")
                
                # Probar sin filtro de conciliado
                all_items = ExtractoBancarioDetalle.objects.filter(extracto=extracto_pichincha)
                print(f"   📊 Sin filtro conciliado: {all_items.count()} items")
                
                if all_items.exists():
                    all_reconciled = all(item.is_reconciled for item in all_items)
                    print(f"   📊 ¿Todos conciliados?: {all_reconciled}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    comparar_extractos()