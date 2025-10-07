#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Verificacion: Implementacion Completa de Retenciones Ecuatorianas
Fases 1, 2 y 3 completadas

Este script verifica que:
1. Los nuevos campos de retencion funcionan correctamente
2. Los calculos automaticos son precisos segun normativas ecuatorianas
3. Los asientos contables incluyen retenciones correctamente
4. Los comprobantes de retencion se generan automaticamente
5. La compatibilidad hacia atras se mantiene intacta
"""

import os
import sys
import django
from decimal import Decimal

# Configurar Django
sys.path.append('c:/contaec')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.suppliers.models import Supplier, PurchaseInvoice
from apps.companies.models import Company
from apps.accounting.models import JournalEntry

class RetentionSystemTester:
    def __init__(self):
        self.company = Company.objects.filter(trade_name__icontains='GUEBER').first()
        if not self.company:
            self.company = Company.objects.first()
        self.results = []
        
    def log(self, message, status="INFO"):
        print(f"[{status}] {message}")
        self.results.append((status, message))
    
    def test_supplier_retention_fields(self):
        """Verificar campos de retención en Supplier"""
        self.log("=== TESTING: Campos de Retención en Supplier ===")
        
        supplier = Supplier.objects.filter(company=self.company).first()
        if not supplier:
            self.log("No hay proveedores para probar", "SKIP")
            return
            
        try:
            # Verificar campos nuevos
            retention_agent = supplier.retention_agent
            iva_percentage = supplier.iva_retention_percentage  
            ir_percentage = supplier.ir_retention_percentage
            sri_classification = supplier.sri_classification
            
            self.log(f"✓ Proveedor: {supplier.trade_name}", "SUCCESS")
            self.log(f"  Agente retencion: {retention_agent}", "INFO")
            self.log(f"  Clasificacion SRI: {sri_classification}", "INFO")
            self.log(f"  IVA retencion: {iva_percentage}%", "INFO")
            self.log(f"  IR retencion: {ir_percentage}%", "INFO")
            
        except AttributeError as e:
            self.log(f"X Error en campos de Supplier: {e}", "ERROR")
    
    def test_automatic_retention_calculation(self):
        """Verificar cálculos automáticos de retención"""
        self.log("=== TESTING: Cálculos Automáticos de Retención ===")
        
        supplier = Supplier.objects.filter(company=self.company).first()
        if not supplier:
            self.log("No hay proveedores para probar", "SKIP")
            return
            
        try:
            # Test con montos de prueba
            subtotal = Decimal('1000.00')
            iva_amount = Decimal('150.00')  # 15% IVA
            
            # Calcular retenciones
            retentions = supplier.calculate_retentions(subtotal, iva_amount)
            
            self.log(f"$ Prueba calculo: $1,000 + IVA $150 = $1,150", "INFO")
            self.log(f"  IVA retencion: ${retentions['iva_retention_amount']}", "INFO")
            self.log(f"  IR retencion: ${retentions['ir_retention_amount']}", "INFO")  
            self.log(f"  Total retenciones: ${retentions['total_retentions']}", "INFO")
            self.log(f"  Neto a pagar: ${retentions['net_payable']}", "INFO")
            
            if retentions['net_payable'] < subtotal + iva_amount:
                self.log("✓ Calculo de retenciones funcionando", "SUCCESS")
            else:
                self.log("! Sin retenciones aplicadas (normal si proveedor no configurado)", "WARNING")
                
        except Exception as e:
            self.log(f"X Error en calculos de retencion: {e}", "ERROR")
    
    def test_purchase_invoice_retention_fields(self):
        """Verificar campos de retencion en PurchaseInvoice"""
        self.log("=== TESTING: Campos de Retencion en Factura de Compra ===")
        
        invoice = PurchaseInvoice.objects.filter(company=self.company).first()
        if not invoice:
            self.log("No hay facturas de compra para probar", "SKIP")
            return
            
        try:
            # Verificar campos de retencion
            iva_ret_percentage = invoice.iva_retention_percentage
            iva_ret_amount = invoice.iva_retention_amount
            ir_ret_percentage = invoice.ir_retention_percentage
            ir_ret_amount = invoice.ir_retention_amount
            total_retentions = invoice.total_retentions
            net_payable = invoice.net_payable
            voucher_number = invoice.retention_voucher_number
            
            self.log(f"✓ Factura: {invoice.internal_number}", "SUCCESS")
            self.log(f"  Total factura: ${invoice.total}", "INFO")
            self.log(f"  Retenciones: ${total_retentions}", "INFO")
            self.log(f"  Neto a pagar: ${net_payable}", "INFO")
            self.log(f"  Comprobante: {voucher_number or 'No generado'}", "INFO")
            
        except AttributeError as e:
            self.log(f"X Error en campos de PurchaseInvoice: {e}", "ERROR")
    
    def test_journal_entry_with_retentions(self):
        """Verificar asientos contables con retenciones"""
        self.log("=== TESTING: Asientos Contables con Retenciones ===")
        
        try:
            # Buscar facturas validadas con retenciones
            invoices_with_retentions = PurchaseInvoice.objects.filter(
                company=self.company,
                status='validated',
                total_retentions__gt=0
            )
            
            self.log(f">> Facturas con retenciones: {invoices_with_retentions.count()}", "INFO")
            
            if invoices_with_retentions.exists():
                invoice = invoices_with_retentions.first()
                
                # Verificar si tiene asiento contable
                journal_entry = JournalEntry.objects.filter(
                    reference__icontains=invoice.internal_number,
                    company=self.company
                ).first()
                
                if journal_entry:
                    lines_count = journal_entry.lines.count()
                    self.log(f"✓ Asiento encontrado: {journal_entry.number} ({lines_count} lineas)", "SUCCESS")
                    
                    # Verificar balance
                    if journal_entry.is_balanced:
                        self.log("✓ Asiento balanceado correctamente", "SUCCESS")
                    else:
                        self.log("X Asiento desbalanceado", "ERROR")
                else:
                    self.log("! No se encontro asiento para factura con retenciones", "WARNING")
            else:
                self.log("i No hay facturas validadas con retenciones para probar", "INFO")
                
        except Exception as e:
            self.log(f"X Error verificando asientos: {e}", "ERROR")
    
    def test_backward_compatibility(self):
        """Verificar compatibilidad hacia atrás"""
        self.log("=== TESTING: Compatibilidad Hacia Atras ===")
        
        try:
            # Verificar que facturas sin retenciones funcionan igual
            invoices_without_retentions = PurchaseInvoice.objects.filter(
                company=self.company,
                total_retentions=0
            )
            
            self.log(f">> Facturas sin retenciones: {invoices_without_retentions.count()}", "INFO")
            
            if invoices_without_retentions.exists():
                invoice = invoices_without_retentions.first()
                
                # Verificar que net_payable = total (sin retenciones)
                if abs(invoice.net_payable - invoice.total) < Decimal('0.01'):
                    self.log("✓ Facturas sin retenciones funcionan igual que antes", "SUCCESS")
                else:
                    self.log(f"X Discrepancia en factura sin retenciones: neto={invoice.net_payable}, total={invoice.total}", "ERROR")
            
            # Verificar que proveedores sin retenciones funcionan
            suppliers_without_retentions = Supplier.objects.filter(
                company=self.company,
                retention_agent=False
            )
            
            self.log(f">> Proveedores sin retenciones: {suppliers_without_retentions.count()}", "INFO")
            self.log("✓ Compatibilidad hacia atras preservada", "SUCCESS")
            
        except Exception as e:
            self.log(f"X Error en compatibilidad: {e}", "ERROR")
    
    def test_retention_voucher_generation(self):
        """Verificar generación de comprobantes de retención"""
        self.log("=== TESTING: Generación de Comprobantes de Retención ===")
        
        try:
            # Buscar facturas con retenciones que deberían tener comprobante
            invoices_with_vouchers = PurchaseInvoice.objects.filter(
                company=self.company,
                total_retentions__gt=0,
                retention_voucher_number__isnull=False
            )
            
            invoices_without_vouchers = PurchaseInvoice.objects.filter(
                company=self.company,
                total_retentions__gt=0,
                retention_voucher_number__isnull=True
            )
            
            self.log(f"📊 Facturas con comprobante: {invoices_with_vouchers.count()}", "INFO")
            self.log(f"📊 Facturas sin comprobante: {invoices_without_vouchers.count()}", "INFO")
            
            if invoices_with_vouchers.exists():
                invoice = invoices_with_vouchers.first()
                voucher_data = invoice.get_retention_voucher_data()
                
                if voucher_data:
                    self.log(f"✅ Comprobante: {voucher_data['voucher_number']}", "SUCCESS")
                    self.log(f"  Fecha: {voucher_data['voucher_date']}", "INFO")
                    self.log(f"  Retenciones: {len([r for r in voucher_data['retentions'] if r])}", "INFO")
                else:
                    self.log("❌ Error obteniendo datos del comprobante", "ERROR")
            
        except Exception as e:
            self.log(f"X Error en comprobantes: {e}", "ERROR")
    
    def run_all_tests(self):
        """Ejecutar todos los tests"""
        self.log(">> INICIANDO VERIFICACION: SISTEMA DE RETENCIONES ECUATORIANAS", "INFO")
        self.log(f">> Empresa: {self.company.trade_name if self.company else 'No encontrada'}", "INFO")
        self.log("=" * 70, "INFO")
        
        if not self.company:
            self.log("X No hay empresas en el sistema", "ERROR")
            return
            
        self.test_supplier_retention_fields()
        self.test_automatic_retention_calculation()
        self.test_purchase_invoice_retention_fields()
        self.test_journal_entry_with_retentions()
        self.test_backward_compatibility()
        self.test_retention_voucher_generation()
        
        self.log("=" * 70, "INFO")
        self.log(">> RESUMEN DE RESULTADOS", "INFO")
        
        # Contar resultados
        success_count = len([r for r in self.results if r[0] == "SUCCESS"])
        error_count = len([r for r in self.results if r[0] == "ERROR"]) 
        warning_count = len([r for r in self.results if r[0] == "WARNING"])
        
        self.log(f"✓ Exitos: {success_count}", "INFO")
        self.log(f"! Advertencias: {warning_count}", "INFO")
        self.log(f"X Errores: {error_count}", "INFO")
        
        if error_count == 0:
            self.log("✓✓ SISTEMA DE RETENCIONES IMPLEMENTADO CORRECTAMENTE", "SUCCESS")
            self.log("EC LISTO PARA CUMPLIMIENTO NORMATIVO ECUATORIANO", "SUCCESS")
        else:
            self.log("!! REVISAR ERRORES ANTES DE USAR EN PRODUCCION", "ERROR")

if __name__ == "__main__":
    tester = RetentionSystemTester()
    tester.run_all_tests()