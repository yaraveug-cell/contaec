"""
Vista principal del módulo Bancos
Contiene los submódulos de gestión bancaria
"""
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from apps.core.mixins import CompanyContextMixin


class BankingModuleView(LoginRequiredMixin, CompanyContextMixin, TemplateView):
    """
    Vista principal del módulo Bancos
    Muestra los submódulos disponibles para gestión bancaria
    """
    template_name = 'banking/module_index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Definir submódulos del módulo Bancos
        context['banking_modules'] = [
            {
                'name': 'Conciliación Bancaria',
                'description': 'Módulo completo de conciliación y reportes',
                'url': '/banking/conciliacion-module/',
                'icon': '🔄',
                'color': 'bg-blue-500',
                'features': [
                    'Conciliación manual e inteligente',
                    'Reportes de estado y diferencias',
                    'Extractos de conciliación mensual',
                    'Control total de movimientos'
                ]
            },
            {
                'name': 'Bancos',
                'description': 'Gestionar entidades bancarias y configuraciones',
                'url': '/admin/banking/bank/',
                'icon': '🏦',
                'color': 'bg-orange-500',
                'features': [
                    'Crear y gestionar bancos',
                    'Códigos SWIFT y configuraciones',
                    'Información de contacto bancario',
                    'Estados de bancos'
                ]
            },
            {
                'name': 'Cuentas Bancarias',
                'description': 'Administrar cuentas bancarias de la empresa',
                'url': '/admin/banking/bankaccount/',
                'icon': '💳',
                'color': 'bg-green-500',
                'features': [
                    'Cuentas corrientes y ahorros',
                    'Saldos y movimientos',
                    'Configuración por empresa',
                    'Estados de cuenta'
                ]
            },
            {
                'name': 'Extracto Bancario',
                'description': 'Procesar y gestionar extractos bancarios',
                'url': '/admin/banking/extractobancario/',
                'icon': '📄',
                'color': 'bg-purple-500',
                'features': [
                    'Importar extractos CSV/Excel',
                    'Procesamiento automático',
                    'Validación de datos',
                    'Historial de extractos'
                ]
            },
            {
                'name': 'Movimientos Bancarios',
                'description': 'Registrar y controlar transacciones bancarias',
                'url': '/admin/banking/banktransaction/',
                'icon': '💰',
                'color': 'bg-orange-500',
                'features': [
                    'Débitos y créditos',
                    'Transferencias bancarias',
                    'Conciliación automática',
                    'Reportes de movimientos'
                ]
            }
        ]
        
        return context