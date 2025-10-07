#!/usr/bin/env python

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.companies.models import Company, CompanySettings
from apps.suppliers.models import Supplier, PurchaseInvoice, PurchaseInvoiceLine

User = get_user_model()

def test_purchase_invoice_iva():
    """Probar que las nuevas facturas de compra usen el IVA de la empresa"""
    
    print("=== PRUEBA DE IVA EN FACTURAS DE COMPRA ===")
    
    # Tomar la primera empresa
    company = Company.objects.first()
    if not company:
        print("No hay empresas")
        return
    
    print(f"Empresa: {company.trade_name}")
    
    # Verificar configuracion de IVA
    settings, _ = CompanySettings.objects.get_or_create(company=company)
    original_iva = settings.default_iva_rate
    print(f"IVA actual: {settings.default_iva_rate}%")
    
    # Cambiar temporalmente a 17% para la prueba
    settings.default_iva_rate = Decimal('17.00')
    settings.save()
    print(f"IVA cambiado temporalmente a: {settings.default_iva_rate}%")
    
    # Obtener proveedor
    supplier = Supplier.objects.filter(company=company).first()
    if not supplier:
        print("No hay proveedores")
        return
    
    # Obtener usuario
    user = User.objects.first()
    if not user:
        print("No hay usuarios")
        return
    
    # Crear factura de compra
    invoice = PurchaseInvoice.objects.create(
        company=company,
        supplier=supplier,
        supplier_invoice_number="TEST-IVA-001",
        invoice_date="2025-01-01",
        created_by=user
    )
    
    print(f"Factura creada: {invoice.supplier_invoice_number}")
    
    # Crear linea de factura SIN producto
    invoice_line = PurchaseInvoiceLine.objects.create(
        invoice=invoice,
        description="Servicio de prueba IVA",
        quantity=Decimal('1.00'),
        unit_cost=Decimal('100.00')
    )
    
    print(f"Linea de factura creada")
    print(f"IVA de la linea: {invoice_line.iva_rate}%")
    print(f"Total de la linea: {invoice_line.line_total}")
    
    # Verificar resultado
    if invoice_line.iva_rate == settings.default_iva_rate:
        print("SUCCESS: La linea usa el IVA de la empresa")
    else:
        print(f"ERROR: Esperado {settings.default_iva_rate}%, obtenido {invoice_line.iva_rate}%")
    
    # Restaurar y limpiar
    settings.default_iva_rate = original_iva
    settings.save()
    invoice.delete()
    
    print(f"IVA restaurado a: {original_iva}%")
    print("Factura de prueba eliminada")
    print("=== PRUEBA COMPLETADA ===")

if __name__ == "__main__":
    test_purchase_invoice_iva()