#!/usr/bin/env python
"""
Script para monitorear y probar el guardado de campos en tiempo real
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from django.db import connection

def monitor_invoice_changes():
    """Monitorear cambios en facturas en tiempo real"""
    print("👀 MONITOR: Cambios en facturas (Ctrl+C para salir)")
    print("=" * 60)
    
    # Obtener la última factura actual
    try:
        last_invoice = Invoice.objects.latest('id')
        last_id = last_invoice.id
        print(f"📊 Última factura actual: ID {last_id}")
    except Invoice.DoesNotExist:
        last_id = 0
        print("📊 No hay facturas previas")
    
    print(f"🔍 Monitoreando nuevas facturas y cambios...")
    print(f"💡 Crear una factura en el admin: http://127.0.0.1:8000/admin/invoicing/invoice/add/")
    print("-" * 60)
    
    import time
    try:
        while True:
            # Buscar facturas nuevas o modificadas
            new_invoices = Invoice.objects.filter(id__gt=last_id).order_by('id')
            
            for invoice in new_invoices:
                print(f"\n🆕 NUEVA FACTURA DETECTADA!")
                print(f"   ID: {invoice.id}")
                print(f"   Número: {invoice.number}")
                print(f"   Cliente: {invoice.customer.trade_name}")
                print(f"   📝 Forma de Pago: {invoice.payment_form}")
                print(f"   🏦 Cuenta: {invoice.account}")
                print(f"   📋 Transfer Detail: '{invoice.transfer_detail}'")
                print(f"   📊 Estado: {invoice.status}")
                print(f"   💰 Total: ${invoice.total}")
                print(f"   ⏰ Creada: {invoice.created_at}")
                
                # Verificar si los campos están correctamente poblados
                issues = []
                if not invoice.payment_form:
                    issues.append("❌ payment_form está vacío")
                if not invoice.account:
                    issues.append("❌ account está vacío")
                    
                if issues:
                    print(f"   🚨 PROBLEMAS DETECTADOS:")
                    for issue in issues:
                        print(f"      {issue}")
                else:
                    print(f"   ✅ Todos los campos principales están poblados")
                
                last_id = invoice.id
            
            # Verificar cambios en facturas existentes
            if last_id > 0:
                recent_updated = Invoice.objects.filter(
                    id__lte=last_id,
                    updated_at__gt=django.utils.timezone.now() - django.utils.timezone.timedelta(seconds=5)
                ).exclude(id__gt=last_id)
                
                for invoice in recent_updated:
                    print(f"\n🔄 FACTURA ACTUALIZADA!")
                    print(f"   ID: {invoice.id} - {invoice.number}")
                    print(f"   📝 Forma de Pago: {invoice.payment_form}")
                    print(f"   🏦 Cuenta: {invoice.account}")
                    print(f"   📋 Transfer Detail: '{invoice.transfer_detail}'")
                    print(f"   📊 Estado: {invoice.status}")
                    print(f"   ⏰ Actualizada: {invoice.updated_at}")
            
            time.sleep(2)  # Verificar cada 2 segundos
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Monitoreo detenido por el usuario")
        
        # Mostrar resumen final
        final_invoices = Invoice.objects.filter(id__gt=last_id).order_by('-id')
        if final_invoices.exists():
            print(f"\n📋 RESUMEN - Facturas creadas durante el monitoreo:")
            for invoice in final_invoices[:3]:
                print(f"   • ID {invoice.id}: {invoice.number}")
                print(f"     Forma de Pago: {invoice.payment_form}")
                print(f"     Cuenta: {invoice.account}")
                print(f"     Transfer Detail: '{invoice.transfer_detail}'")
        else:
            print(f"\n📋 No se crearon facturas nuevas durante el monitoreo")

if __name__ == "__main__":
    monitor_invoice_changes()