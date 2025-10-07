#!/usr/bin/env python
"""
Script de prueba para verificar que las vistas de comprobantes de retención funcionen correctamente
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.suppliers.models import PurchaseInvoice
from apps.companies.models import Company

def test_retention_voucher_data():
    """Prueba básica de los datos necesarios para comprobantes de retención"""
    
    print("🔍 Verificando datos para comprobantes de retención...")
    
    # Verificar que hay empresas
    companies = Company.objects.all()
    print(f"📊 Empresas en el sistema: {companies.count()}")
    
    if companies.exists():
        company = companies.first()
        print(f"✅ Empresa de prueba: {company.trade_name} (RUC: {company.ruc})")
    
    # Verificar facturas con retenciones
    invoices_with_retentions = PurchaseInvoice.objects.filter(
        total_retentions__gt=0
    ).select_related('company', 'supplier')
    
    print(f"📋 Facturas con retenciones: {invoices_with_retentions.count()}")
    
    if invoices_with_retentions.exists():
        for invoice in invoices_with_retentions[:3]:  # Mostrar máximo 3
            print(f"✅ Factura #{invoice.internal_number}:")
            print(f"   - Empresa: {invoice.company.trade_name}")
            print(f"   - Proveedor: {invoice.supplier.trade_name}")
            print(f"   - Total: ${invoice.total}")
            print(f"   - Retenciones: ${invoice.total_retentions}")
            print(f"   - IVA Ret.: {invoice.iva_retention_percentage}% = ${invoice.iva_retention_amount}")
            print(f"   - IR Ret.: {invoice.ir_retention_percentage}% = ${invoice.ir_retention_amount}")
            print("   ---")
    else:
        print("⚠️  No se encontraron facturas con retenciones para probar")
        print("💡 Sugerencia: Crear algunas facturas de prueba con retenciones aplicadas")
    
    print("\n🔗 URLs de prueba disponibles:")
    if invoices_with_retentions.exists():
        invoice = invoices_with_retentions.first()
        print(f"📄 Comprobante individual: http://127.0.0.1:8000/suppliers/retention-voucher/{invoice.pk}/")
        
        ids = list(invoices_with_retentions.values_list('pk', flat=True)[:3])
        print(f"📄 Múltiples comprobantes: http://127.0.0.1:8000/suppliers/retention-vouchers/multiple/?invoice_ids={','.join(map(str, ids))}")
    
    print("\n✅ Verificación completada")

if __name__ == "__main__":
    test_retention_voucher_data()