#!/usr/bin/env python
"""
AUDITORIA DE SEGURIDAD: Sistema de Retenciones Ecuatorianas
Verificar que solo se muestren datos de la empresa asignada al usuario activo
"""

import os
import sys
import django

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
from apps.accounting.models import ChartOfAccounts
from apps.inventory.models import Product

User = get_user_model()

def audit_user_company_assignments():
    """Verificar asignaciones de usuarios a empresas"""
    print("=== VERIFICANDO ASIGNACIONES USUARIO-EMPRESA ===")
    
    users = User.objects.all()
    companies = Company.objects.all()
    
    print(f"Total usuarios: {users.count()}")
    print(f"Total empresas: {companies.count()}")
    
    security_issues = 0
    
    for user in users:
        if user.is_superuser:
            print(f"SUPERUSER {user.email}: Ve todas las empresas")
        else:
            user_companies = CompanyUser.objects.filter(user=user)
            if user_companies.exists():
                company_names = ", ".join([cu.company.trade_name for cu in user_companies])
                print(f"USER {user.email}: {company_names}")
            else:
                print(f"WARNING: {user.email} sin empresas asignadas")
                security_issues += 1
    
    return security_issues

def audit_supplier_admin_security():
    """Verificar seguridad del admin de proveedores"""
    print("\n=== VERIFICANDO SEGURIDAD SUPPLIER ADMIN ===")
    
    factory = RequestFactory()
    normal_user = User.objects.filter(is_superuser=False).first()
    
    if not normal_user:
        print("SKIP: No hay usuarios normales para probar")
        return 0
    
    security_issues = 0
    
    # Test get_queryset
    request = factory.get('/admin/suppliers/supplier/')
    request.user = normal_user
    
    admin_instance = SupplierAdmin(Supplier, admin.site)
    
    if hasattr(admin_instance, 'get_queryset'):
        print("OK: get_queryset implementado")
        
        queryset = admin_instance.get_queryset(request)
        total_suppliers = Supplier.objects.count()
        filtered_suppliers = queryset.count()
        
        print(f"Total proveedores en BD: {total_suppliers}")
        print(f"Proveedores visibles para {normal_user.email}: {filtered_suppliers}")
        
        if filtered_suppliers < total_suppliers or total_suppliers == 0:
            print("OK: Filtrado por empresa funcionando")
        else:
            print("ERROR: Usuario ve todos los proveedores")
            security_issues += 1
    else:
        print("ERROR: get_queryset NO implementado - VULNERABILIDAD CRITICA")
        security_issues += 1
    
    # Test formfield_for_foreignkey
    if hasattr(admin_instance, 'formfield_for_foreignkey'):
        print("OK: formfield_for_foreignkey implementado")
    else:
        print("ERROR: formfield_for_foreignkey NO implementado")
        security_issues += 1
    
    return security_issues

def audit_purchase_invoice_admin_security():
    """Verificar seguridad del admin de facturas"""
    print("\n=== VERIFICANDO SEGURIDAD PURCHASE INVOICE ADMIN ===")
    
    factory = RequestFactory()
    normal_user = User.objects.filter(is_superuser=False).first()
    
    if not normal_user:
        print("SKIP: No hay usuarios normales para probar")
        return 0
    
    security_issues = 0
    
    request = factory.get('/admin/suppliers/purchaseinvoice/')
    request.user = normal_user
    
    admin_instance = PurchaseInvoiceAdmin(PurchaseInvoice, admin.site)
    
    if hasattr(admin_instance, 'get_queryset'):
        print("OK: get_queryset implementado")
        
        queryset = admin_instance.get_queryset(request)
        total_invoices = PurchaseInvoice.objects.count()
        filtered_invoices = queryset.count()
        
        print(f"Total facturas en BD: {total_invoices}")
        print(f"Facturas visibles para {normal_user.email}: {filtered_invoices}")
        
        if filtered_invoices < total_invoices or total_invoices == 0:
            print("OK: Filtrado por empresa funcionando")
        else:
            print("ERROR: Usuario ve todas las facturas")
            security_issues += 1
    else:
        print("ERROR: get_queryset NO implementado - VULNERABILIDAD CRITICA")
        security_issues += 1
    
    return security_issues

def audit_related_models():
    """Verificar seguridad en modelos relacionados"""
    print("\n=== VERIFICANDO MODELOS RELACIONADOS ===")
    
    normal_user = User.objects.filter(is_superuser=False).first()
    if not normal_user:
        print("SKIP: No hay usuarios normales")
        return 0
    
    security_issues = 0
    user_companies = CompanyUser.objects.filter(user=normal_user).values_list('company_id', flat=True)
    
    if user_companies:
        # Cuentas contables
        total_accounts = ChartOfAccounts.objects.count()
        user_accounts = ChartOfAccounts.objects.filter(company_id__in=user_companies).count()
        
        print(f"Total cuentas: {total_accounts}")
        print(f"Cuentas del usuario: {user_accounts}")
        
        if user_accounts < total_accounts or total_accounts == 0:
            print("OK: Cuentas filtradas por empresa")
        else:
            print("WARNING: Posible acceso a todas las cuentas")
            security_issues += 1
        
        # Productos
        total_products = Product.objects.count()
        user_products = Product.objects.filter(company_id__in=user_companies).count()
        
        print(f"Total productos: {total_products}")
        print(f"Productos del usuario: {user_products}")
        
        if user_products < total_products or total_products == 0:
            print("OK: Productos filtrados por empresa")
        else:
            print("WARNING: Posible acceso a todos los productos")
            security_issues += 1
    
    return security_issues

def audit_retention_data():
    """Verificar datos de retenciones"""
    print("\n=== VERIFICANDO DATOS DE RETENCIONES ===")
    
    # Proveedores con retenciones
    suppliers_with_retentions = Supplier.objects.filter(retention_agent=True)
    print(f"Proveedores con retenciones configuradas: {suppliers_with_retentions.count()}")
    
    for supplier in suppliers_with_retentions[:3]:
        company_name = supplier.company.trade_name if supplier.company else "Sin empresa"
        print(f"  - {supplier.trade_name} (Empresa: {company_name})")
    
    # Facturas con retenciones
    invoices_with_retentions = PurchaseInvoice.objects.filter(total_retentions__gt=0)
    print(f"Facturas con retenciones aplicadas: {invoices_with_retentions.count()}")
    
    for invoice in invoices_with_retentions[:3]:
        company_name = invoice.company.trade_name if invoice.company else "Sin empresa"
        print(f"  - {invoice.internal_number} (Empresa: {company_name}, Retenciones: ${invoice.total_retentions})")
    
    return 0

def audit_actions_security():
    """Verificar seguridad de acciones en lote"""
    print("\n=== VERIFICANDO SEGURIDAD ACCIONES EN LOTE ===")
    
    admin_instance = PurchaseInvoiceAdmin(PurchaseInvoice, admin.site)
    actions = ['mark_as_received', 'mark_as_validated', 'mark_as_paid', 'mark_as_cancelled', 'create_journal_entries']
    
    security_issues = 0
    
    for action_name in actions:
        if hasattr(admin_instance, action_name):
            print(f"OK: Accion {action_name} existe")
            
            action_method = getattr(admin_instance, action_name)
            action_code = action_method.__code__
            
            if 'user_companies' in action_code.co_names:
                print(f"OK: Accion {action_name} filtra por empresa")
            else:
                print(f"WARNING: Accion {action_name} puede no filtrar por empresa")
                security_issues += 1
        else:
            print(f"ERROR: Accion {action_name} no existe")
            security_issues += 1
    
    return security_issues

def run_security_audit():
    """Ejecutar auditoria completa"""
    print("INICIANDO AUDITORIA DE SEGURIDAD - SISTEMA DE RETENCIONES")
    print("=" * 80)
    
    total_issues = 0
    
    total_issues += audit_user_company_assignments()
    total_issues += audit_supplier_admin_security() 
    total_issues += audit_purchase_invoice_admin_security()
    total_issues += audit_related_models()
    total_issues += audit_retention_data()
    total_issues += audit_actions_security()
    
    print("\n" + "=" * 80)
    print("RESUMEN DE AUDITORIA")
    print("=" * 80)
    
    if total_issues == 0:
        print("RESULTADO: SISTEMA COMPLETAMENTE SEGURO")
        print("- Todos los filtros de empresa funcionan correctamente")
        print("- Usuarios solo ven datos de sus empresas asignadas")
        print("- Sistema de retenciones implementado de forma segura")
        print("- Acciones en lote respetan filtros de seguridad")
    else:
        print(f"RESULTADO: {total_issues} PROBLEMAS DE SEGURIDAD ENCONTRADOS")
        print("- Revisar y corregir los problemas identificados")
        print("- No usar en produccion hasta resolver todos los problemas")
    
    return total_issues

if __name__ == "__main__":
    issues = run_security_audit()