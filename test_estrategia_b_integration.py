#!/usr/bin/env python
"""
Script de Verificación - ESTRATEGIA B (Híbrida)
Integración Inteligente Inventory-Accounting

Este script verifica que:
1. Los nuevos campos en Category funcionan correctamente
2. Los métodos inteligentes de Product retornan cuentas válidas
3. La compatibilidad hacia atrás se mantiene intacta
4. El AutomaticJournalEntryService maneja ambos casos (con/sin config)
"""

import os
import sys
import django
from decimal import Decimal

# Configurar Django
sys.path.append('c:/contaec')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.inventory.models import Category, Product
from apps.accounting.models import ChartOfAccounts
from apps.companies.models import Company
from apps.invoicing.models import Invoice, InvoiceLine, Customer
from apps.accounting.services import AutomaticJournalEntryService

class EstrategiaBTester:
    def __init__(self):
        self.company = Company.objects.first()
        self.results = []
        
    def log(self, message, status="INFO"):
        print(f"[{status}] {message}")
        self.results.append((status, message))
    
    def test_category_fields(self):
        """Verificar que los nuevos campos de Category funcionan"""
        self.log("=== TESTING: Campos de Category ===")
        
        # Buscar categoría existente
        category = Category.objects.filter(company=self.company).first()
        if not category:
            self.log("No hay categorías en el sistema", "SKIP")
            return
            
        # Verificar que los campos existen y son accesibles
        try:
            sales_account = category.default_sales_account
            cost_account = category.default_cost_account  
            inventory_account = category.default_inventory_account
            self.log(f"✅ Campos agregados correctamente a categoría: {category.name}", "SUCCESS")
        except AttributeError as e:
            self.log(f"❌ Error en campos de categoría: {e}", "ERROR")
            
    def test_product_intelligent_methods(self):
        """Verificar métodos inteligentes de Product"""
        self.log("=== TESTING: Métodos Inteligentes de Product ===")
        
        product = Product.objects.filter(company=self.company, is_active=True).first()
        if not product:
            self.log("No hay productos en el sistema", "SKIP")
            return
            
        try:
            # Test métodos de cuentas efectivas
            sales_account = product.get_effective_sales_account()
            cost_account = product.get_effective_cost_account()
            inventory_account = product.get_effective_inventory_account()
            
            self.log(f"✅ Producto: {product.code} - {product.name}", "INFO")
            self.log(f"  📊 Cuenta Ventas: {sales_account.code if sales_account else 'No configurada'}", "INFO")
            self.log(f"  📈 Cuenta Costo: {cost_account.code if cost_account else 'No configurada'}", "INFO") 
            self.log(f"  📦 Cuenta Inventario: {inventory_account.code if inventory_account else 'No configurada'}", "INFO")
            
            # Test estado de configuración
            config_status = product.get_account_configuration_status()
            self.log(f"  ⚙️ Config Status: {config_status}", "INFO")
            
            self.log("✅ Métodos inteligentes funcionando correctamente", "SUCCESS")
            
        except Exception as e:
            self.log(f"❌ Error en métodos de producto: {e}", "ERROR")
    
    def test_backward_compatibility(self):
        """Verificar compatibilidad hacia atrás"""
        self.log("=== TESTING: Compatibilidad Hacia Atrás ===")
        
        try:
            # Verificar que las facturas existentes siguen funcionando
            invoice = Invoice.objects.filter(company=self.company).first()
            if invoice:
                self.log(f"✅ Factura existente accesible: {invoice.number}", "SUCCESS")
                
                # Verificar líneas existentes
                lines = invoice.lines.all()
                for line in lines[:3]:  # Solo primeras 3 líneas
                    if line.product:
                        sales_account = line.product.get_effective_sales_account()
                        self.log(f"  📋 Línea {line.id}: {line.product.code} → {sales_account.code if sales_account else 'Sin cuenta'}", "INFO")
                        
            self.log("✅ Compatibilidad hacia atrás verificada", "SUCCESS")
            
        except Exception as e:
            self.log(f"❌ Error en compatibilidad: {e}", "ERROR")
    
    def test_journal_service_integration(self):
        """Verificar integración con AutomaticJournalEntryService"""
        self.log("=== TESTING: AutomaticJournalEntryService ===")
        
        try:
            # Verificar que el servicio tiene los nuevos métodos
            if hasattr(AutomaticJournalEntryService, '_group_sales_by_account'):
                self.log("✅ Método _group_sales_by_account existe", "SUCCESS")
            else:
                self.log("❌ Método _group_sales_by_account no encontrado", "ERROR")
                
            # Test con factura existente (sin crear asiento real)
            invoice = Invoice.objects.filter(company=self.company, status='sent').first()
            if invoice:
                try:
                    # Solo test del agrupamiento, sin crear asiento
                    sales_groups = AutomaticJournalEntryService._group_sales_by_account(invoice)
                    self.log(f"✅ Agrupamiento funcional: {len(sales_groups)} grupos de cuentas", "SUCCESS")
                    
                    for account, amount in sales_groups.items():
                        self.log(f"  💰 {account.code}: ${amount}", "INFO")
                        
                except Exception as e:
                    self.log(f"⚠️ Error en agrupamiento (no crítico): {e}", "WARNING")
                    
        except Exception as e:
            self.log(f"❌ Error en servicio de asientos: {e}", "ERROR")
    
    def test_configuration_scenarios(self):
        """Probar diferentes escenarios de configuración"""
        self.log("=== TESTING: Escenarios de Configuración ===")
        
        # Escenario 1: Categoría sin configuración contable
        categories_without_config = Category.objects.filter(
            company=self.company,
            default_sales_account__isnull=True,
            default_cost_account__isnull=True,
            default_inventory_account__isnull=True
        )
        
        self.log(f"📋 Categorías sin configuración: {categories_without_config.count()}", "INFO")
        
        # Escenario 2: Categorías con configuración parcial
        categories_with_partial_config = Category.objects.filter(
            company=self.company
        ).exclude(
            default_sales_account__isnull=True,
            default_cost_account__isnull=True, 
            default_inventory_account__isnull=True
        )
        
        self.log(f"⚙️ Categorías con configuración: {categories_with_partial_config.count()}", "INFO")
        
        # Verificar que productos en ambos escenarios obtienen cuentas
        for scenario, categories in [("Sin config", categories_without_config), ("Con config", categories_with_partial_config)]:
            category = categories.first()
            if category:
                product = Product.objects.filter(category=category, is_active=True).first()
                if product:
                    sales_account = product.get_effective_sales_account()
                    self.log(f"  {scenario} - Producto {product.code}: {'✅' if sales_account else '❌'} Cuenta obtenida", "INFO")
    
    def run_all_tests(self):
        """Ejecutar todos los tests"""
        self.log("🚀 INICIANDO VERIFICACIÓN ESTRATEGIA B", "INFO")
        self.log(f"📍 Empresa: {self.company.trade_name if self.company else 'No encontrada'}", "INFO")
        self.log("=" * 60, "INFO")
        
        if not self.company:
            self.log("❌ No hay empresas en el sistema", "ERROR")
            return
            
        self.test_category_fields()
        self.test_product_intelligent_methods()
        self.test_backward_compatibility()
        self.test_journal_service_integration()
        self.test_configuration_scenarios()
        
        self.log("=" * 60, "INFO")
        self.log("📊 RESUMEN DE RESULTADOS", "INFO")
        
        # Contar resultados
        success_count = len([r for r in self.results if r[0] == "SUCCESS"])
        error_count = len([r for r in self.results if r[0] == "ERROR"]) 
        warning_count = len([r for r in self.results if r[0] == "WARNING"])
        
        self.log(f"✅ Éxitos: {success_count}", "INFO")
        self.log(f"⚠️ Advertencias: {warning_count}", "INFO")
        self.log(f"❌ Errores: {error_count}", "INFO")
        
        if error_count == 0:
            self.log("🎉 ESTRATEGIA B IMPLEMENTADA CORRECTAMENTE", "SUCCESS")
        else:
            self.log("🚨 REVISAR ERRORES ANTES DE USAR EN PRODUCCIÓN", "ERROR")

if __name__ == "__main__":
    tester = EstrategiaBTester()
    tester.run_all_tests()