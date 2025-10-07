#!/usr/bin/env python
"""
Verificar empresas disponibles en el sistema
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
sys.path.append('c:\\contaec')
django.setup()

from apps.companies.models import Company

def check_companies():
    """Verificar empresas disponibles"""
    companies = Company.objects.all()
    
    print(f"📊 Total empresas en el sistema: {companies.count()}")
    print("\n🏢 EMPRESAS DISPONIBLES:")
    
    for company in companies:
        print(f"   ID: {company.id}")
        print(f"   Legal Name: {company.legal_name}")
        print(f"   Trade Name: {company.trade_name}")
        print(f"   RUC: {company.ruc}")
        print(f"   Activa: {company.is_active}")
        print("   " + "-" * 40)
    
    # Buscar GUEBER específicamente
    gueber_companies = Company.objects.filter(
        legal_name__icontains="GUEBER"
    )
    
    if gueber_companies.exists():
        print(f"\n🎯 EMPRESAS CON 'GUEBER': {gueber_companies.count()}")
        for company in gueber_companies:
            print(f"   ✅ {company.legal_name} (ID: {company.id})")
    else:
        print(f"\n❌ No se encontraron empresas con 'GUEBER' en el nombre")
        
        # Buscar por trade_name también
        gueber_trade = Company.objects.filter(
            trade_name__icontains="GUEBER"
        )
        
        if gueber_trade.exists():
            print(f"\n🎯 EMPRESAS CON 'GUEBER' EN TRADE NAME: {gueber_trade.count()}")
            for company in gueber_trade:
                print(f"   ✅ {company.trade_name} (ID: {company.id})")

if __name__ == "__main__":
    check_companies()