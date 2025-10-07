#!/usr/bin/env python
"""
Script simple para probar IVA por empresa
"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from decimal import Decimal
from apps.companies.models import Company, CompanySettings

# Obtener empresas y mostrar su configuracion de IVA
companies = Company.objects.all()
print(f"Total empresas: {companies.count()}")

for company in companies:
    settings, created = CompanySettings.objects.get_or_create(company=company)
    print(f"Empresa: {company.trade_name}")
    print(f"IVA por defecto: {settings.default_iva_rate}%")
    print(f"Status: {'Nueva configuracion' if created else 'Configuracion existente'}")
    print("---")

print("Configuracion de IVA completada")