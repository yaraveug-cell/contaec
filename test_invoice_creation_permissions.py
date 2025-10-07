#!/usr/bin/env python
"""
Script para verificar que los permisos de creación de facturas funcionan correctamente
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from apps.invoicing.models import Invoice
from apps.companies.models import Company, CompanyUser

User = get_user_model()

def test_invoice_creation_permissions():
    """Verificar permisos de creación de facturas con estados"""
    
    print("🔐 VERIFICACIÓN: PERMISOS DE CREACIÓN DE FACTURAS")
    print("=" * 60)
    
    # 1. Verificar permisos disponibles
    print("📋 PERMISOS DISPONIBLES:")
    content_type = ContentType.objects.get_for_model(Invoice)
    perms = Permission.objects.filter(content_type=content_type)
    
    for perm in perms:
        print(f"   • {perm.codename}: {perm.name}")
    
    # 2. Buscar usuarios de prueba
    print(f"\n👥 USUARIOS DISPONIBLES:")
    users = User.objects.all()[:5]
    
    for user in users:
        print(f"\n   Usuario: {user.username}")
        print(f"   Es superusuario: {user.is_superuser}")
        
        # Verificar permisos específicos
        has_add = user.has_perm('invoicing.add_invoice')
        has_change = user.has_perm('invoicing.change_invoice')
        has_change_status = user.has_perm('invoicing.change_invoice_status')
        has_mark_sent = user.has_perm('invoicing.mark_invoice_sent')
        has_mark_paid = user.has_perm('invoicing.mark_invoice_paid')
        has_mark_cancelled = user.has_perm('invoicing.mark_invoice_cancelled')
        
        print(f"   Permisos:")
        print(f"     - add_invoice: {'✅' if has_add else '❌'}")
        print(f"     - change_invoice: {'✅' if has_change else '❌'}")  
        print(f"     - change_invoice_status: {'✅' if has_change_status else '❌'}")
        print(f"     - mark_invoice_sent: {'✅' if has_mark_sent else '❌'}")
        print(f"     - mark_invoice_paid: {'✅' if has_mark_paid else '❌'}")
        print(f"     - mark_invoice_cancelled: {'✅' if has_mark_cancelled else '❌'}")
        
        # Verificar empresas asignadas
        try:
            company_users = CompanyUser.objects.filter(user=user, is_active=True)
            if company_users.exists():
                print(f"   Empresas asignadas: {company_users.count()}")
                for cu in company_users:
                    print(f"     - {cu.company.trade_name} ({cu.get_role_display()})")
            else:
                print(f"   Empresas asignadas: Ninguna")
        except Exception as e:
            print(f"   Error verificando empresas: {e}")
    
    # 3. Verificar configuración del modelo
    print(f"\n📊 CONFIGURACIÓN DEL MODELO INVOICE:")
    print(f"   Estados disponibles:")
    for status_code, status_name in Invoice.STATUS_CHOICES:
        print(f"     - {status_code}: {status_name}")
    
    print(f"   Estado por defecto: {Invoice.DRAFT}")
    
    # 4. Instrucciones de prueba
    print(f"\n🧪 INSTRUCCIONES PARA PROBAR:")
    print(f"1. Crear usuario sin permisos de cambio de estado")
    print(f"2. Ir a Admin → Invoices → Add Invoice")
    print(f"3. Verificar que campo 'Estado' está readonly")
    print(f"4. Intentar crear factura con estado diferente a 'Borrador'")
    print(f"5. Verificar que se fuerza a estado 'Borrador'")
    
    print(f"\n✅ VERIFICACIÓN COMPLETADA")
    print(f"📋 Permisos implementados: {perms.count()}")
    print(f"👥 Usuarios revisados: {users.count()}")
    
    return True

if __name__ == "__main__":
    success = test_invoice_creation_permissions()
    sys.exit(0 if success else 1)