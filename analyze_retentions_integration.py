#!/usr/bin/env python

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def analyze_retentions_and_journal_integration():
    """Análisis completo del estado de retenciones y asientos contables"""
    
    print("🔍 ANÁLISIS: RETENCIONES Y ASIENTOS CONTABLES")
    print("=" * 60)
    
    try:
        from apps.suppliers.models import Supplier, PurchaseInvoice, PurchaseInvoiceLine
        from apps.accounting.models import JournalEntry, JournalEntryLine, ChartOfAccounts
        from apps.companies.models import Company
        from decimal import Decimal
        
        # ===============================
        # 1. VERIFICAR ESTRUCTURA DE RETENCIONES
        # ===============================
        print("\n🧮 1. ESTRUCTURA DE RETENCIONES:")
        
        # Campos de retenciones en PurchaseInvoice
        invoice_fields = [f.name for f in PurchaseInvoice._meta.fields]
        retention_fields = [f for f in invoice_fields if 'retention' in f.lower()]
        
        print(f"   ✅ Campos de retención en PurchaseInvoice:")
        for field in retention_fields:
            print(f"      • {field}")
        
        # Verificar métodos de cálculo
        supplier_methods = dir(Supplier)
        retention_methods = [m for m in supplier_methods if 'retention' in m.lower()]
        
        print(f"\n   ✅ Métodos de retención en Supplier:")
        for method in retention_methods:
            print(f"      • {method}")
        
        # ===============================
        # 2. VERIFICAR INTEGRACIÓN CONTABLE
        # ===============================
        print(f"\n🏦 2. INTEGRACIÓN CONTABLE:")
        
        # Verificar método create_journal_entry
        invoice_methods = dir(PurchaseInvoice)
        journal_methods = [m for m in invoice_methods if 'journal' in m.lower() or 'entry' in m.lower()]
        
        print(f"   ✅ Métodos contables en PurchaseInvoice:")
        for method in journal_methods:
            print(f"      • {method}")
        
        # Verificar métodos de cuentas
        account_methods = [m for m in invoice_methods if '_get_' in m and 'account' in m.lower()]
        print(f"\n   ✅ Métodos de cuentas automáticas:")
        for method in account_methods:
            print(f"      • {method}")
        
        # ===============================
        # 3. PROBAR CON DATOS REALES
        # ===============================
        print(f"\n📊 3. PRUEBAS CON DATOS REALES:")
        
        # Contar registros
        total_suppliers = Supplier.objects.count()
        total_invoices = PurchaseInvoice.objects.count()
        invoices_with_retentions = PurchaseInvoice.objects.filter(total_retentions__gt=0).count()
        total_journal_entries = JournalEntry.objects.count()
        
        print(f"   📈 Estadísticas generales:")
        print(f"      • Proveedores: {total_suppliers}")
        print(f"      • Facturas de compra: {total_invoices}")
        print(f"      • Facturas con retenciones: {invoices_with_retentions}")
        print(f"      • Asientos contables: {total_journal_entries}")
        
        # Probar proveedor con retenciones
        if total_suppliers > 0:
            sample_supplier = Supplier.objects.filter(retention_agent=True).first()
            if sample_supplier:
                print(f"\n   🧪 Prueba con proveedor: {sample_supplier.trade_name}")
                
                # Probar cálculo automático
                test_subtotal = Decimal('1000.00')
                test_iva = Decimal('150.00')
                
                retentions = sample_supplier.calculate_retentions(test_subtotal, test_iva)
                
                print(f"      📋 Cálculo automático (Base: $1000 + IVA $150):")
                print(f"         • IVA Retención: {retentions['iva_retention_rate']}% = ${retentions['iva_retention_amount']}")
                print(f"         • IR Retención: {retentions['ir_retention_rate']}% = ${retentions['ir_retention_amount']}")
                print(f"         • Total Retenciones: ${retentions['total_retentions']}")
                print(f"         • Neto a Pagar: ${retentions['net_payable']}")
        
        # ===============================
        # 4. VERIFICAR ASIENTOS GENERADOS
        # ===============================
        print(f"\n📝 4. ASIENTOS CONTABLES GENERADOS:")
        
        if invoices_with_retentions > 0:
            sample_invoice = PurchaseInvoice.objects.filter(total_retentions__gt=0).first()
            
            print(f"   🧪 Factura de prueba: {sample_invoice.internal_number}")
            print(f"      • Proveedor: {sample_invoice.supplier.trade_name}")
            print(f"      • Total: ${sample_invoice.total}")
            print(f"      • Retenciones: ${sample_invoice.total_retentions}")
            print(f"      • Neto a pagar: ${sample_invoice.net_payable}")
            
            # Buscar asiento relacionado
            related_entries = JournalEntry.objects.filter(
                reference__icontains=sample_invoice.internal_number
            )
            
            if related_entries.exists():
                entry = related_entries.first()
                print(f"\n   ✅ Asiento contable encontrado: {entry.number}")
                print(f"      • Fecha: {entry.date}")
                print(f"      • Estado: {entry.get_state_display()}")
                print(f"      • Líneas: {entry.lines.count()}")
                print(f"      • Débitos: ${entry.total_debit}")
                print(f"      • Créditos: ${entry.total_credit}")
                print(f"      • Balanceado: {'✅' if entry.is_balanced else '❌'}")
                
                print(f"\n   📋 Detalle de líneas:")
                for line in entry.lines.all():
                    tipo = "DÉBITO" if line.debit > 0 else "CRÉDITO"
                    monto = line.debit if line.debit > 0 else line.credit
                    print(f"      • {tipo}: {line.account.code} - {line.account.name} = ${monto}")
                    print(f"         Descripción: {line.description}")
            else:
                print(f"   ❌ No se encontró asiento contable para esta factura")
                
                # Intentar crear asiento
                print(f"   🔧 Intentando crear asiento...")
                try:
                    new_entry = sample_invoice.create_journal_entry()
                    if new_entry:
                        print(f"   ✅ Asiento creado: {new_entry.number} con {new_entry.lines.count()} líneas")
                    else:
                        print(f"   ❌ No se pudo crear el asiento")
                except Exception as e:
                    print(f"   ❌ Error creando asiento: {e}")
        else:
            print(f"   ⚠️ No hay facturas con retenciones para probar")
        
        # ===============================
        # 5. VERIFICAR CUENTAS CONTABLES
        # ===============================
        print(f"\n🗂️ 5. CUENTAS CONTABLES REQUERIDAS:")
        
        company = Company.objects.first()
        if company:
            print(f"   🏢 Empresa: {company.trade_name}")
            
            # Buscar cuentas típicas
            required_accounts = [
                ('Gastos/Inventario', ['5', '1.3']),
                ('IVA por recuperar', ['1.1.05', 'iva recuperable']),
                ('Cuentas por pagar', ['2.1.02', 'por pagar']),
                ('Retención IVA', ['1.1.07', 'retencion iva']),
                ('Retención IR', ['1.1.08', 'retencion renta'])
            ]
            
            for account_name, search_terms in required_accounts:
                found_accounts = ChartOfAccounts.objects.filter(company=company)
                
                for term in search_terms:
                    matches = found_accounts.filter(
                        models.Q(code__icontains=term) | 
                        models.Q(name__icontains=term)
                    )[:3]
                    
                    if matches:
                        print(f"   ✅ {account_name}:")
                        for account in matches:
                            print(f"      • {account.code} - {account.name}")
                        break
                else:
                    print(f"   ❌ {account_name}: No encontrada")
        
        # ===============================
        # 6. ESTADO DE INTEGRACIÓN
        # ===============================
        print(f"\n🎯 6. RESUMEN DE INTEGRACIÓN:")
        
        integration_status = []
        
        # Verificar funcionalidades
        if hasattr(PurchaseInvoice, 'create_journal_entry'):
            integration_status.append("✅ Método create_journal_entry() implementado")
        else:
            integration_status.append("❌ Método create_journal_entry() faltante")
        
        if hasattr(Supplier, 'calculate_retentions'):
            integration_status.append("✅ Cálculo automático de retenciones")
        else:
            integration_status.append("❌ Cálculo de retenciones faltante")
        
        if invoices_with_retentions > 0:
            integration_status.append(f"✅ {invoices_with_retentions} facturas con retenciones aplicadas")
        else:
            integration_status.append("⚠️ No hay facturas con retenciones para verificar")
        
        # Verificar si hay asientos relacionados con retenciones
        retention_entries = JournalEntryLine.objects.filter(
            description__icontains='retención'
        ).count()
        
        if retention_entries > 0:
            integration_status.append(f"✅ {retention_entries} líneas contables con retenciones")
        else:
            integration_status.append("❌ No se encontraron asientos con retenciones")
        
        for status in integration_status:
            print(f"   {status}")
        
        # ===============================
        # 7. CONCLUSIONES
        # ===============================
        print(f"\n📋 7. CONCLUSIONES:")
        
        total_checks = len(integration_status)
        passed_checks = len([s for s in integration_status if s.startswith('✅')])
        
        if passed_checks == total_checks:
            print(f"   🎉 COMPLETAMENTE INTEGRADO ({passed_checks}/{total_checks} ✅)")
            print(f"      Las retenciones y asientos están funcionando correctamente.")
        elif passed_checks >= total_checks * 0.7:
            print(f"   🔧 MAYORMENTE INTEGRADO ({passed_checks}/{total_checks} ✅)")
            print(f"      La base está implementada, falta ajustar algunos detalles.")
        else:
            print(f"   ⚠️ INTEGRACIÓN PARCIAL ({passed_checks}/{total_checks} ✅)")
            print(f"      Faltan componentes importantes por implementar.")
        
        print(f"\n💡 RECOMENDACIONES:")
        if retention_entries == 0:
            print(f"   1. Generar asientos para facturas existentes con retenciones")
        if invoices_with_retentions == 0:
            print(f"   1. Crear facturas de prueba con retenciones")
        if passed_checks < total_checks:
            print(f"   2. Completar implementación de componentes faltantes")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
    except Exception as e:
        print(f"❌ Error durante análisis: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "=" * 60)
    print(f"🔍 ANÁLISIS COMPLETADO")
    print(f"=" * 60)

if __name__ == "__main__":
    # Importar Q aquí para evitar problemas
    from django.db import models
    analyze_retentions_and_journal_integration()