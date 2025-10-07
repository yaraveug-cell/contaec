"""
Vista del módulo de Conciliación Bancaria con submódulos
"""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import CompanyContextMixin


class ConciliacionModuleView(LoginRequiredMixin, CompanyContextMixin, TemplateView):
    """
    Vista principal del módulo de Conciliación Bancaria
    Muestra los submódulos disponibles de conciliación
    """
    template_name = 'banking/conciliacion/module_index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Submódulos del módulo de Conciliación Bancaria
        conciliacion_modules = [
            {
                'name': 'Conciliación Manual',
                'description': 'Herramienta interactiva para conciliar movimientos manualmente',
                'icon': '🔄',
                'url': '/banking/conciliacion/',
                'color': 'text-primary',
            },
            {
                'name': 'Estado de Conciliación',
                'description': 'Resumen del estado actual por cuenta bancaria',
                'icon': '📊',
                'url': '/banking/reportes/estado-conciliacion/',
                'color': 'text-success',
            },
            {
                'name': 'Diferencias No Conciliadas',
                'description': 'Listado de movimientos pendientes de conciliar',
                'icon': '⚠️',
                'url': '/banking/reportes/diferencias/',
                'color': 'text-warning',
            },
            {
                'name': 'Extracto Mensual',
                'description': 'Reporte detallado de conciliación por período',
                'icon': '📅',
                'url': '/banking/reportes/extracto-conciliacion/',
                'color': 'text-info',
            },
        ]
        
        context['conciliacion_modules'] = conciliacion_modules
        context['title'] = 'Módulo de Conciliación Bancaria'
        
        return context