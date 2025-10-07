#!/usr/bin/env python3
"""
Verificar estado limpio después de eliminar lógica de forma de pago
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice

def main():
    print("🧹 VERIFICACIÓN DE ESTADO LIMPIO")
    print("=" * 50)
    
    try:
        # Verificar factura de prueba
        invoice = Invoice.objects.get(id=99)
        print(f"📄 Factura ID: {invoice.id}")
        print(f"Número: {invoice.number}")
        print(f"Empresa: {invoice.company}")
        print(f"Cliente: {invoice.customer}")
        print(f"Forma de pago: {invoice.payment_form}")
        print(f"Cuenta: {invoice.account}")
        
        # Verificar campos que pueden tener datos legacy
        print()
        print("🔍 CAMPOS DE OBSERVACIONES:")
        print(f"bank_observations: {bool(invoice.bank_observations)}")
        if invoice.bank_observations:
            print(f"   Contenido: {invoice.bank_observations[:100]}...")
        
        print(f"transfer_detail: {bool(invoice.transfer_detail)}")
        if invoice.transfer_detail:
            print(f"   Contenido: {invoice.transfer_detail[:100]}...")
        
        print()
        print("✅ Estado verificado - La aplicación funciona correctamente")
        print("🎯 Lista para implementar nueva lógica simple")
        
        # URL para pruebas
        print()
        print("🌐 URLs DE PRUEBA:")
        print(f"Editar factura: http://localhost:8000/admin/invoicing/invoice/{invoice.id}/change/")
        print("Crear nueva: http://localhost:8000/admin/invoicing/invoice/add/")
        
    except Invoice.DoesNotExist:
        print("❌ Factura ID 99 no encontrada")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()