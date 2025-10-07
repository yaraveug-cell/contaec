from functools import wraps
from django.http import Http404
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.companies.models import CompanyUser


def require_company_access(allowed_roles=None):
    """
    Decorador que requiere que el usuario tenga acceso a al menos una empresa
    con uno de los roles especificados.
    
    Args:
        allowed_roles (list): Lista de roles permitidos ['owner', 'admin', 'accountant', 'employee', 'viewer']
                            Si es None, cualquier rol con empresa asignada es válido.
    """
    if allowed_roles is None:
        allowed_roles = ['owner', 'admin', 'accountant', 'employee', 'viewer']
    
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            # Superusers y staff tienen acceso completo
            if request.user.is_superuser or request.user.is_staff:
                return view_func(request, *args, **kwargs)
            
            # Verificar si el usuario tiene empresas asignadas con roles permitidos
            user_companies = CompanyUser.objects.filter(
                user=request.user,
                role__in=allowed_roles
            )
            
            if not user_companies.exists():
                messages.error(
                    request, 
                    'No tienes permisos para acceder a este módulo. '
                    'Contacta al administrador si crees que esto es un error.'
                )
                return redirect('dashboard')
            
            # Agregar las empresas del usuario al contexto de la request
            request.user_companies = user_companies
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_accounting_access(view_func):
    """
    Decorador específico para módulos de contabilidad.
    Requiere rol de contador, administrador o propietario.
    """
    return require_company_access(['accountant', 'admin', 'owner'])(view_func)


def require_admin_access(view_func):
    """
    Decorador específico para módulos administrativos.
    Requiere rol de administrador o propietario.
    """
    return require_company_access(['admin', 'owner'])(view_func)


def require_owner_access(view_func):
    """
    Decorador específico para funciones de propietario.
    Requiere rol de propietario únicamente.
    """
    return require_company_access(['owner'])(view_func)


def get_user_companies_with_roles(user, required_roles=None):
    """
    Obtiene las empresas del usuario con los roles especificados.
    
    Args:
        user: Usuario de Django
        required_roles (list): Lista de roles requeridos. Si es None, obtiene todas.
    
    Returns:
        QuerySet de CompanyUser
    """
    if user.is_superuser or user.is_staff:
        # Superusers ven todas las empresas
        return CompanyUser.objects.all()
    
    if required_roles is None:
        required_roles = ['owner', 'admin', 'accountant', 'employee', 'viewer']
    
    return CompanyUser.objects.filter(
        user=user,
        role__in=required_roles
    ).select_related('company')


def user_has_module_access(user, module_name):
    """
    Verifica si un usuario tiene acceso a un módulo específico.
    
    Args:
        user: Usuario de Django
        module_name (str): Nombre del módulo ('accounting', 'invoicing', 'inventory', etc.)
    
    Returns:
        bool: True si tiene acceso, False en caso contrario
    """
    if user.is_superuser or user.is_staff:
        return True
    
    user_companies = CompanyUser.objects.filter(user=user)
    if not user_companies.exists():
        return False
    
    user_roles = set(user_companies.values_list('role', flat=True))
    
    # Definir módulos por rol
    module_access = {
        'profile': ['owner', 'admin', 'accountant', 'employee', 'viewer'],
        'companies': ['owner', 'admin', 'accountant', 'employee', 'viewer'],
        'accounting': ['owner', 'admin', 'accountant'],
        'reports': ['owner', 'admin', 'accountant'],
        'invoicing': ['owner', 'admin'],
        'inventory': ['owner', 'admin'],
        'payroll': ['owner', 'admin', 'accountant'],
        'fixed_assets': ['owner', 'admin', 'accountant'],
        'company_users': ['owner', 'admin'],
        'banking': ['owner', 'admin', 'accountant'],
        # Enlaces Rápidos - Permisos
        'journal_entries': ['owner', 'admin', 'accountant'],
        'sales_invoices': ['owner', 'admin', 'accountant'],
        'purchase_invoices': ['owner', 'admin', 'accountant'],
        'suppliers_management': ['owner', 'admin', 'accountant'],
        'chart_accounts': ['owner', 'admin', 'accountant'],
        'bank_reconciliation': ['owner', 'admin', 'accountant'],
        'bank_statements': ['owner', 'admin', 'accountant'],
    }
    
    required_roles = module_access.get(module_name, [])
    return bool(user_roles.intersection(required_roles))


def get_available_modules(user):
    """
    Obtiene la lista de módulos disponibles para un usuario específico.
    
    Args:
        user: Usuario de Django
    
    Returns:
        list: Lista de diccionarios con información de los módulos disponibles
    """
    modules = []
    
    # Módulo de perfil para todos los usuarios autenticados
    if user.is_authenticated:
        modules.append({
            'name': 'Mi Perfil',
            'description': 'Gestionar información personal',
            'url': '/perfil/',
            'icon': '👤',
            'color': 'bg-blue-500',
            'key': 'profile'
        })
    
    # Si el usuario no tiene empresas asignadas, solo mostrar perfil
    # (excepto superusers y staff)
    if not user.is_superuser and not user.is_staff:
        user_companies = CompanyUser.objects.filter(user=user)
        if not user_companies.exists():
            return modules
    
    # Agregar módulos según acceso
    module_definitions = [
        {
            'key': 'companies',
            'name': 'Empresas',
            'description': 'Ver información de mis empresas',
            'url': '/modulos/empresas/',
            'icon': '🏢',
            'color': 'bg-orange-500'
        },
        {
            'key': 'accounting',
            'name': 'Contabilidad',
            'description': 'Plan de cuentas, asientos contables',
            'url': '/modulos/contabilidad/',
            'icon': '📊',
            'color': 'bg-green-500'
        },
        {
            'key': 'reports',
            'name': 'Reportes',
            'description': 'Estados financieros y reportes',
            'url': '/modulos/reportes/',
            'icon': '📈',
            'color': 'bg-purple-500'
        },
        {
            'key': 'invoicing',
            'name': 'Facturación',
            'description': 'Facturas y documentos tributarios',
            'url': '/modulos/facturacion/',
            'icon': '🧾',
            'color': 'bg-red-500'
        },
        {
            'key': 'inventory',
            'name': 'Inventarios',
            'description': 'Control de stock y productos',
            'url': '/modulos/inventarios/',
            'icon': '📦',
            'color': 'bg-yellow-500'
        },
        {
            'key': 'payroll',
            'name': 'Nómina',
            'description': 'Gestión de empleados y pagos',
            'url': '/admin/payroll/employee/',
            'icon': '💰',
            'color': 'bg-pink-500'
        },
        {
            'key': 'fixed_assets',
            'name': 'Activos Fijos',
            'description': 'Control de bienes y depreciaciones',
            'url': '/admin/fixed_assets/fixedasset/',
            'icon': '🏗️',
            'color': 'bg-teal-500'
        },
        {
            'key': 'company_users',
            'name': 'Usuarios de mi Empresa',
            'description': 'Gestionar usuarios de mis empresas',
            'url': '/admin/companies/companyuser/',
            'icon': '👥',
            'color': 'bg-indigo-400'
        },
        {
            'key': 'banking',
            'name': 'Bancos',
            'description': 'Módulo integral de gestión bancaria',
            'url': '/banking/',
            'icon': '🏦',
            'color': 'bg-emerald-500'
        },
        # Enlaces Rápidos - Convertidos de estáticos a dinámicos
        {
            'key': 'journal_entries',
            'name': 'Asientos Contables',
            'description': 'Ver y gestionar asientos contables',
            'url': '/admin/accounting/journalentry/',
            'icon': '📝',
            'color': 'bg-blue-600'
        },
        {
            'key': 'sales_invoices',
            'name': 'Facturas de Venta',
            'description': 'Gestionar facturas de venta',
            'url': '/admin/invoicing/invoice/',
            'icon': '💰',
            'color': 'bg-green-600'
        },
        {
            'key': 'purchase_invoices', 
            'name': 'Facturas de Compra',
            'description': 'Gestionar facturas de proveedores',
            'url': '/admin/suppliers/purchaseinvoice/',
            'icon': '🛒',
            'color': 'bg-orange-600'
        },
        {
            'key': 'suppliers_management',
            'name': 'Proveedores',
            'description': 'Gestión de proveedores',
            'url': '/admin/suppliers/supplier/',
            'icon': '🏪',
            'color': 'bg-purple-600'
        },
        {
            'key': 'chart_accounts',
            'name': 'Plan de Cuentas',
            'description': 'Gestionar plan contable',
            'url': '/admin/accounting/chartofaccounts/',
            'icon': '🗂️',
            'color': 'bg-amber-600'
        },
        {
            'key': 'bank_reconciliation',
            'name': 'Conciliación Bancaria',
            'description': 'Conciliar movimientos bancarios',
            'url': '/banking/conciliacion/',
            'icon': '🔄',
            'color': 'bg-blue-500'
        },
        {
            'key': 'bank_statements',
            'name': 'Extractos Bancarios',
            'description': 'Administrar extractos bancarios',
            'url': '/admin/banking/extractobancario/',
            'icon': '📄',
            'color': 'bg-cyan-600'
        }
    ]
    
    for module_def in module_definitions:
        if user_has_module_access(user, module_def['key']):
            modules.append(module_def)
    
    # Módulos para superusers
    if user.is_superuser:
        modules.extend([
            {
                'name': 'Usuarios',
                'description': 'Gestión de usuarios del sistema',
                'url': '/admin/users/user/',
                'icon': '👥',
                'color': 'bg-indigo-500',
                'key': 'system_users'
            },
            {
                'name': 'Administración',
                'description': 'Panel completo de administración',
                'url': '/modulos/administracion/',
                'icon': '⚙️',
                'color': 'bg-black',
                'key': 'admin_panel'
            },
            {
                'name': 'API Docs',
                'description': 'Documentación de la API REST',
                'url': '/api/docs/',
                'icon': '📚',
                'color': 'bg-cyan-500',
                'key': 'api_docs'
            }
        ])
    
    return modules
