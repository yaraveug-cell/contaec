"""
Script para diagnosticar específicamente los items del extracto
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.companies.models import Company
from apps.banking.models import ExtractoBancario, ExtractoBancarioDetalle

User = get_user_model()

def debug_extracto_items():
    """Diagnosticar los items del extracto específicamente"""
    
    print("🔍 DIAGNÓSTICO ITEMS DEL EXTRACTO")
    print("="*50)
    
    yolanda = User.objects.get(email='yolismarlen@gmail.com')
    gueber = Company.objects.get(trade_name='GUEBER')
    
    # Verificar extracto 1
    print("📄 EXTRACTO ID 1:")
    try:
        extracto = ExtractoBancario.objects.get(id=1)
        print(f"   ✅ Extracto encontrado: {extracto}")
        print(f"   🏢 Empresa: {extracto.bank_account.company.trade_name}")
        print(f"   🏦 Cuenta: {extracto.bank_account}")
        print(f"   📅 Período: {extracto.period_start} - {extracto.period_end}")
        print(f"   💰 Saldos: ${extracto.initial_balance} → ${extracto.final_balance}")
        
        # Verificar items del extracto
        print(f"\n📋 ITEMS DEL EXTRACTO:")
        items = ExtractoBancarioDetalle.objects.filter(extracto=extracto)
        print(f"   📊 Total items: {items.count()}")
        
        if items.exists():
            for i, item in enumerate(items, 1):
                conciliado = "✅ Conciliado" if item.is_reconciled else "⏳ Pendiente"
                tipo = "💰 Crédito" if item.credito else "💸 Débito"
                monto = item.credito if item.credito else item.debito
                print(f"   {i}. {item.fecha} | {tipo} ${monto} | {item.descripcion[:40]} | {conciliado}")
        
        # Simular filtro con show_all=False (comportamiento normal)
        print(f"\n🔍 FILTRO NORMAL (solo no conciliados):")
        items_pendientes = items.filter(is_reconciled=False)
        print(f"   📊 Items pendientes: {items_pendientes.count()}")
        
        # Simular filtro con show_all=True
        print(f"\n🔍 FILTRO SHOW_ALL (todos):")
        items_todos = items
        print(f"   📊 Todos los items: {items_todos.count()}")
        
        # Verificar si hay items conciliados
        items_conciliados = items.filter(is_reconciled=True)
        print(f"\n📈 ESTADO DE CONCILIACIÓN:")
        print(f"   ✅ Conciliados: {items_conciliados.count()}")
        print(f"   ⏳ Pendientes: {items_pendientes.count()}")
        
    except ExtractoBancario.DoesNotExist:
        print("   ❌ Extracto ID 1 no encontrado")

if __name__ == "__main__":
    debug_extracto_items()