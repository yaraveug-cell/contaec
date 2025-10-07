"""
URLs para los módulos del sistema
"""
from django.urls import path
from apps.core.module_views import (
    accounting_module,
    invoicing_module,
    inventory_module,
    reports_module,
    companies_module,
    admin_module
)

app_name = 'modules'

urlpatterns = [
    path('contabilidad/', accounting_module, name='accounting'),
    path('facturacion/', invoicing_module, name='invoicing'),
    path('inventarios/', inventory_module, name='inventory'),
    path('reportes/', reports_module, name='reports'),
    path('empresas/', companies_module, name='companies'),
    path('administracion/', admin_module, name='admin'),
]