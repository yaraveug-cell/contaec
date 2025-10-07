from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from rest_framework.response import Response


def home_view(request):
    """Vista principal del sistema"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    context = {
        'title': 'ContaEC - Sistema de Contabilidad para Empresas Ecuatorianas',
        'description': 'Sistema integral de contabilidad diseñado específicamente para pequeñas y medianas empresas en Ecuador.',
        'version': '1.0.0',
        'features': [
            'Contabilidad General',
            'Facturación Electrónica SRI',
            'Inventarios',
            'Reportes Financieros',
            'Gestión Multiempresa',
            'API REST Completa'
        ]
    }
    return render(request, 'home.html', context)


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido {user.full_name}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Credenciales inválidas. Verifica tu email y contraseña.')
        else:
            messages.error(request, 'Por favor ingresa email y contraseña.')
    
    context = {
        'title': 'Iniciar Sesión - ContaEC'
    }
    return render(request, 'registration/login.html', context)


@login_required
def profile_view(request):
    """Vista del perfil personal del usuario"""
    from django.shortcuts import redirect
    
    # Redirigir al admin del usuario con los permisos correctos
    return redirect(f'/admin/users/user/{request.user.id}/change/')


@login_required
def dashboard_view(request):
    """Dashboard principal después del login"""
    from apps.companies.models import Company, CompanyUser
    from apps.core.permissions import get_available_modules
    
    # Obtener SOLO las empresas asignadas al usuario
    if request.user.is_superuser:
        # Superuser ve todas las empresas
        user_companies = CompanyUser.objects.all().select_related('company')
        all_companies = Company.objects.all()
    else:
        # Usuario normal solo ve sus empresas asignadas
        user_companies = CompanyUser.objects.filter(user=request.user).select_related('company')
        all_companies = Company.objects.filter(
            id__in=user_companies.values_list('company_id', flat=True)
        )
    
    # Obtener módulos disponibles usando la función centralizada de permisos
    modules = get_available_modules(request.user)
    
    # Obtener roles del usuario en las empresas
    user_roles = set()
    has_companies = user_companies.exists()
    
    for company_user in user_companies:
        user_roles.add(company_user.role)
    
    # Los módulos ya están determinados por la función get_available_modules
    # que maneja todas las reglas de acceso según roles y permisos


            modules.extend([
                {
                    'name': 'Contabilidad',
                    'description': 'Plan de cuentas, asientos contables',
                    'url': '/modulos/contabilidad/',
                    'icon': '📊',
                    'color': 'bg-green-500'
                },
                {
                    'name': 'Reportes',
                    'description': 'Estados financieros y reportes',
                    'url': '/modulos/reportes/',
                    'icon': '📈',
                    'color': 'bg-purple-500'
                },
                {
                    'name': 'Nómina',
                    'description': 'Gestión de empleados y pagos',
                    'url': '/admin/payroll/employee/',
                    'icon': '💰',
                    'color': 'bg-pink-500'
                },
                {
                    'name': 'Activos Fijos',
                    'description': 'Control de bienes y depreciaciones',
                    'url': '/admin/fixed_assets/fixedasset/',
                    'icon': '�️',
                    'color': 'bg-teal-500'
                }
            ])
        
        # Módulos para administradores y propietarios
        if ('admin' in user_roles or 'owner' in user_roles) or request.user.is_staff:
            modules.extend([
                {
                    'name': 'Usuarios de mi Empresa',
                    'description': 'Gestionar usuarios de mis empresas',
                    'url': '/admin/companies/companyuser/',
                    'icon': '👥',
                    'color': 'bg-indigo-400'
                },
                {
                    'name': 'Facturación',
                    'description': 'Facturas y documentos tributarios',
                    'url': '/modulos/facturacion/',
                    'icon': '🧾',
                    'color': 'bg-red-500'
                },
                {
                    'name': 'Inventarios',
                    'description': 'Control de stock y productos',
                    'url': '/modulos/inventarios/',
                    'icon': '📦',
                    'color': 'bg-yellow-500'
                }
            ])
        
        # Módulos para empleados (acceso limitado)
        if 'employee' in user_roles and not any(role in ['accountant', 'admin', 'owner'] for role in user_roles):
            modules.extend([
                {
                    'name': 'Mi Nómina',
                    'description': 'Ver mis datos de empleado',
                    'url': '/admin/payroll/employee/',
                    'icon': '💰',
                    'color': 'bg-pink-500'
                }
            ])
        
        # Solo viewers pueden ver información básica
        if 'viewer' in user_roles and not any(role in ['employee', 'accountant', 'admin', 'owner'] for role in user_roles):
            modules.extend([
                {
                    'name': 'Reportes (Solo Lectura)',
                    'description': 'Ver reportes financieros',
                    'url': '/modulos/reportes/',
                    'icon': '�',
                    'color': 'bg-gray-400'
                }
            ])
    
    # Módulos administrativos solo para superuser
    if request.user.is_superuser:
        modules.extend([
            {
                'name': 'Usuarios',
                'description': 'Gestión de usuarios del sistema',
                'url': '/admin/users/user/',
                'icon': '👥',
                'color': 'bg-indigo-500'
            },
            {
                'name': 'SRI Integración',
                'description': 'Configuración SRI y facturación electrónica',
                'url': '/admin/sri_integration/',
                'icon': '🏛️',
                'color': 'bg-gray-500'
            }
        ])
    
    # Módulos del sistema para super usuarios
    if request.user.is_superuser:
        modules.extend([
            {
                'name': 'Administración',
                'description': 'Panel completo de administración',
                'url': '/modulos/administracion/',
                'icon': '⚙️',
                'color': 'bg-black'
            },
            {
                'name': 'API Docs',
                'description': 'Documentación de la API REST',
                'url': '/api/docs/',
                'icon': '📚',
                'color': 'bg-cyan-500'
            }
        ])
    
    # Determinar el rol principal del usuario (el más alto)
    role_hierarchy = ['owner', 'admin', 'accountant', 'employee', 'viewer']
    primary_role = 'USER'
    for role in role_hierarchy:
        if role in user_roles:
            primary_role = role.upper()
            break
    
    context = {
        'title': 'Dashboard - ContaEC',
        'user_companies': user_companies,
        'available_companies': all_companies,  # Para el filtro dropdown - solo empresas asignadas
        'all_companies': all_companies,        # Alias para compatibilidad
        'total_companies': user_companies.count(),
        'modules': modules,
        'user_role': primary_role,
        'all_roles': list(user_roles),
        'has_companies': has_companies,
        'show_access_message': not has_companies and not request.user.is_superuser and not request.user.is_staff
    }
    return render(request, 'dashboard.html', context)


def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('home')


def api_docs_view(request):
    """Vista de documentación de API"""
    return render(request, 'api_docs.html')


@api_view(['GET'])
def api_info(request):
    """Información de la API"""
    return Response({
        'message': 'Bienvenido a ContaEC API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/v1/auth/',
            'companies': '/api/v1/companies/',
            'accounting': '/api/v1/accounting/',
            'invoicing': '/api/v1/invoicing/',
            'inventory': '/api/v1/inventory/',
            'reports': '/api/v1/reports/',
            'sri': '/api/v1/sri/',
            'documentation': '/api/docs/',
            'schema': '/api/schema/'
        },
        'support': {
            'email': 'soporte@contaec.com',
            'docs': 'https://docs.contaec.com'
        }
    })