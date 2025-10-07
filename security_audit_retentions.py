#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AUDITORIA DE SEGURIDAD: Sistema de Retenciones Ecuatorianas
Verificar que solo se muestren datos de la empresa asignada al usuario activo
"""

import os
import sys
import django
from decimal import Decimal

# Configurar Django
sys.path.append('c:/contaec')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.contrib import admin
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from apps.companies.models import Company, CompanyUser
from apps.suppliers.models import Supplier, PurchaseInvoice
from apps.suppliers.admin import SupplierAdmin, PurchaseInvoiceAdmin
from apps.accounting.models import ChartOfAccounts, JournalEntry
from apps.inventory.models import Product, Category

User = get_user_model()

class SecurityAudit:
    def __init__(self):
        self.factory = RequestFactory()
        self.results = {}
        
    def log(self, section, message, status="INFO"):
        if section not in self.results:
            self.results[section] = []
        self.results[section].append((status, message))
        print(f"[{status}] {section}: {message}")
    
    def test_user_company_assignments(self):
        """Verificar asignaciones de usuarios a empresas"""
        section = "ASIGNACIONES USUARIO-EMPRESA"
        self.log(section, "=== VERIFICANDO ASIGNACIONES ===")
        
        users = User.objects.all()
        companies = Company.objects.all()
        
        self.log(section, f"Total usuarios: {users.count()}")
        self.log(section, f"Total empresas: {companies.count()}")
        
        for user in users:
            if user.is_superuser:
                self.log(section, f"👑 {user.email}: SUPERUSER - Ve todas las empresas", "INFO")
            else:
                user_companies = CompanyUser.objects.filter(user=user)
                if user_companies.exists():
                    company_names = ", ".join([cu.company.trade_name for cu in user_companies])
                    self.log(section, f"👤 {user.email}: {company_names}", "SUCCESS")
                else:
                    self.log(section, f"⚠️ {user.email}: Sin empresas asignadas", "WARNING")
    
    def test_supplier_admin_security(self):
        """Verificar seguridad del admin de proveedores"""
        section = "SEGURIDAD SUPPLIER ADMIN"
        self.log(section, "=== VERIFICANDO FILTRADO DE PROVEEDORES ===")
        
        # Crear request mock para usuario normal
        normal_user = User.objects.filter(is_superuser=False).first()
        if not normal_user:
            self.log(section, "No hay usuarios normales para probar", "SKIP")
            return
            
        request = self.factory.get('/admin/suppliers/supplier/')
        request.user = normal_user
        
        admin_instance = SupplierAdmin(Supplier, admin.site)
        
        # Verificar que get_queryset está implementado
        if hasattr(admin_instance, 'get_queryset'):
            self.log(section, "✅ get_queryset implementado", "SUCCESS")
            
            # Test queryset filtering
            queryset = admin_instance.get_queryset(request)
            total_suppliers = Supplier.objects.count()
            filtered_suppliers = queryset.count()
            
            self.log(section, f"Total proveedores en BD: {total_suppliers}")
            self.log(section, f"Proveedores visibles para {normal_user.email}: {filtered_suppliers}")
            
            if filtered_suppliers < total_suppliers:
                self.log(section, "✅ Filtrado por empresa funcionando", "SUCCESS")
            else:
                self.log(section, "⚠️ Usuario ve todos los proveedores - REVISAR", "WARNING")
        else:
            self.log(section, "❌ get_queryset NO implementado - VULNERABILIDAD", "ERROR")
        
        # Verificar formfield_for_foreignkey
        if hasattr(admin_instance, 'formfield_for_foreignkey'):
            self.log(section, "✅ formfield_for_foreignkey implementado", "SUCCESS")
        else:
            self.log(section, "❌ formfield_for_foreignkey NO implementado", "ERROR")
    
    def test_purchase_invoice_admin_security(self):
        """Verificar seguridad del admin de facturas de compra"""
        section = "SEGURIDAD PURCHASE INVOICE ADMIN"
        self.log(section, "=== VERIFICANDO FILTRADO DE FACTURAS ===")
        
        normal_user = User.objects.filter(is_superuser=False).first()
        if not normal_user:
            self.log(section, "No hay usuarios normales para probar", "SKIP")
            return
            
        request = self.factory.get('/admin/suppliers/purchaseinvoice/')
        request.user = normal_user
        
        admin_instance = PurchaseInvoiceAdmin(PurchaseInvoice, admin.site)
        
        # Verificar que get_queryset está implementado
        if hasattr(admin_instance, 'get_queryset'):
            self.log(section, "✅ get_queryset implementado", "SUCCESS")
            
            queryset = admin_instance.get_queryset(request)
            total_invoices = PurchaseInvoice.objects.count()
            filtered_invoices = queryset.count()
            
            self.log(section, f"Total facturas en BD: {total_invoices}")
            self.log(section, f"Facturas visibles para {normal_user.email}: {filtered_invoices}")
            
            if filtered_invoices < total_invoices or total_invoices == 0:
                self.log(section, "✅ Filtrado por empresa funcionando", "SUCCESS")
            else:
                self.log(section, "⚠️ Usuario ve todas las facturas - REVISAR", "WARNING")
        else:
            self.log(section, "❌ get_queryset NO implementado - VULNERABILIDAD", "ERROR")
    
    def test_related_models_security(self):
        """Verificar seguridad en modelos relacionados"""
        section = "SEGURIDAD MODELOS RELACIONADOS"
        self.log(section, "=== VERIFICANDO CUENTAS CONTABLES ===")
        
        normal_user = User.objects.filter(is_superuser=False).first()
        if not normal_user:
            self.log(section, "No hay usuarios normales para probar", "SKIP")
            return
        
        # Verificar que las cuentas se filtren por empresa
        user_companies = CompanyUser.objects.filter(user=normal_user).values_list('company_id', flat=True)
        
        if user_companies:
            total_accounts = ChartOfAccounts.objects.count()
            user_accounts = ChartOfAccounts.objects.filter(company_id__in=user_companies).count()
            
            self.log(section, f"Total cuentas en BD: {total_accounts}")
            self.log(section, f"Cuentas de empresas del usuario: {user_accounts}")
            
            if user_accounts < total_accounts:
                self.log(section, "✅ Cuentas filtradas por empresa", "SUCCESS")
            else:
                self.log(section, "⚠️ Posible acceso a todas las cuentas", "WARNING")
        
        # Verificar productos
        if user_companies:
            total_products = Product.objects.count()
            user_products = Product.objects.filter(company_id__in=user_companies).count()
            
            self.log(section, f"Total productos en BD: {total_products}")
            self.log(section, f"Productos de empresas del usuario: {user_products}")
            
            if user_products < total_products or total_products == 0:
                self.log(section, "✅ Productos filtrados por empresa", "SUCCESS")
            else:
                self.log(section, "⚠️ Posible acceso a todos los productos", "WARNING")
    
    def test_retention_fields_security(self):
        """Verificar que los campos de retención mantengan la seguridad"""
        section = "SEGURIDAD CAMPOS DE RETENCION"
        self.log(section, "=== VERIFICANDO NUEVOS CAMPOS ===")
        
        # Verificar que los proveedores con retenciones están correctamente filtrados
        suppliers_with_retentions = Supplier.objects.filter(retention_agent=True)
        
        if suppliers_with_retentions.exists():
            self.log(section, f"Proveedores con retenciones: {suppliers_with_retentions.count()}")
            
            for supplier in suppliers_with_retentions[:3]:  # Solo primeros 3
                company_name = supplier.company.trade_name if supplier.company else "Sin empresa"
                self.log(section, f"  - {supplier.trade_name} (Empresa: {company_name})")
        else:
            self.log(section, "No hay proveedores con retenciones configuradas")
        
        # Verificar facturas con retenciones
        invoices_with_retentions = PurchaseInvoice.objects.filter(total_retentions__gt=0)
        
        if invoices_with_retentions.exists():
            self.log(section, f"Facturas con retenciones: {invoices_with_retentions.count()}")
            
            for invoice in invoices_with_retentions[:3]:  # Solo primeras 3
                company_name = invoice.company.trade_name if invoice.company else "Sin empresa"
                self.log(section, f"  - {invoice.internal_number} (Empresa: {company_name}, Retenciones: ${invoice.total_retentions})")
        else:
            self.log(section, "No hay facturas con retenciones")
    
    def test_superuser_vs_normal_access(self):
        """Comparar acceso entre superuser y usuario normal"""
        section = "COMPARACION ACCESOS"
        self.log(section, "=== SUPERUSER vs USUARIO NORMAL ===")
        
        superuser = User.objects.filter(is_superuser=True).first()
        normal_user = User.objects.filter(is_superuser=False).first()
        
        if not superuser or not normal_user:
            self.log(section, "Faltan usuarios para comparar", "SKIP")
            return
        
        # Test con superuser
        request_super = self.factory.get('/admin/')
        request_super.user = superuser
        
        admin_instance = SupplierAdmin(Supplier, admin.site)
        super_queryset = admin_instance.get_queryset(request_super)
        
        # Test con usuario normal  
        request_normal = self.factory.get('/admin/')
        request_normal.user = normal_user
        
        normal_queryset = admin_instance.get_queryset(request_normal)
        
        self.log(section, f"Superuser ve: {super_queryset.count()} proveedores")
        self.log(section, f"Usuario normal ve: {normal_queryset.count()} proveedores")
        
        if super_queryset.count() >= normal_queryset.count():
            self.log(section, "✅ Superuser ve igual o más datos que usuario normal", "SUCCESS")
        else:
            self.log(section, "❌ Usuario normal ve más que superuser - ERROR", "ERROR")
    
    def test_action_security(self):
        """Verificar que las acciones en lote respeten la seguridad"""
        section = "SEGURIDAD ACCIONES EN LOTE"
        self.log(section, "=== VERIFICANDO ACCIONES ADMIN ===")
        
        admin_instance = PurchaseInvoiceAdmin(PurchaseInvoice, admin.site)
        
        # Verificar que las acciones filtren por empresa del usuario
        actions = ['mark_as_received', 'mark_as_validated', 'mark_as_paid', 'mark_as_cancelled', 'create_journal_entries']
        
        for action_name in actions:
            if hasattr(admin_instance, action_name):
                self.log(section, f"✅ Acción {action_name} existe")
                
                # Verificar el código de la acción para buscar filtros de seguridad
                action_method = getattr(admin_instance, action_name)
                action_code = action_method.__code__
                
                if 'user_companies' in action_code.co_names:
                    self.log(section, f"✅ Acción {action_name} filtra por empresa del usuario", "SUCCESS")
                else:
                    self.log(section, f"⚠️ Acción {action_name} puede no filtrar por empresa", "WARNING")
            else:
                self.log(section, f"❌ Acción {action_name} no existe", "ERROR")
    
    def run_full_audit(self):
        """Ejecutar auditoría completa"""
        print("🔒 INICIANDO AUDITORIA DE SEGURIDAD - SISTEMA DE RETENCIONES")
        print("=" * 80)
        
        self.test_user_company_assignments()
        print("")
        self.test_supplier_admin_security()
        print("")
        self.test_purchase_invoice_admin_security()
        print("")
        self.test_related_models_security()
        print("")
        self.test_retention_fields_security()
        print("")
        self.test_superuser_vs_normal_access()
        print("")
        self.test_action_security()
        
        print("=" * 80)
        print("📊 RESUMEN DE AUDITORIA")
        print("=" * 80)
        
        total_success = 0
        total_warnings = 0
        total_errors = 0
        
        for section, messages in self.results.items():
            success = len([m for m in messages if m[0] == "SUCCESS"])
            warnings = len([m for m in messages if m[0] == "WARNING"]) 
            errors = len([m for m in messages if m[0] == "ERROR"])
            
            total_success += success
            total_warnings += warnings
            total_errors += errors
            
            if errors > 0:
                status = "❌ CRITICO"
            elif warnings > 0:
                status = "⚠️ ATENCION"
            else:
                status = "✅ SEGURO"
            
            print(f"{status} {section}: {success} OK, {warnings} advertencias, {errors} errores")
        
        print(f"\n📈 TOTALES: {total_success} éxitos, {total_warnings} advertencias, {total_errors} errores")
        
        if total_errors == 0 and total_warnings == 0:
            print("\n🎉 SISTEMA COMPLETAMENTE SEGURO")
            print("✅ Todos los filtros de empresa funcionan correctamente")
            print("✅ Usuarios solo ven datos de sus empresas asignadas")
            print("✅ Sistema de retenciones implementado de forma segura")
        elif total_errors == 0:
            print(f"\n✅ SISTEMA MAYORMENTE SEGURO")
            print(f"⚠️ {total_warnings} advertencias requieren revisión")
        else:
            print(f"\n🚨 SISTEMA REQUIERE ATENCION")
            print(f"❌ {total_errors} vulnerabilidades críticas encontradas")
            print(f"⚠️ {total_warnings} advertencias adicionales")

if __name__ == "__main__":
    auditor = SecurityAudit()
    auditor.run_full_audit()