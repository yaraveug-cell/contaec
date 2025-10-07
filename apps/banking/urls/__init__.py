"""
URLs principales del módulo banking
"""

from django.urls import path, include
from ..views import reportes, conciliacion, conciliacion_module, module

app_name = 'banking'

urlpatterns = [
    # Módulo Principal Bancos
    path('', module.BankingModuleView.as_view(), name='module_index'),
    
    # Módulo de Conciliación Bancaria con submódulos
    path('conciliacion-module/', conciliacion_module.ConciliacionModuleView.as_view(), name='conciliacion_module'),
    
    # Conciliación Bancaria (importar directamente para evitar namespace conflicts)
    path('conciliacion/', conciliacion.ReconciliationView.as_view(), name='conciliacion'),
    path('conciliacion/ajax/', conciliacion.ReconciliationAjaxView.as_view(), name='conciliacion_ajax'),
    
    # Reportes de Conciliación - FASE 1 (Esenciales)
    path('reportes/', reportes.ReportesIndexView.as_view(), name='reportes_index'),
    path('reportes/estado-conciliacion/', 
         reportes.EstadoConciliacionPorCuentaView.as_view(), 
         name='estado_conciliacion'),
    path('reportes/diferencias/', 
         reportes.DiferenciasNoConciliadasView.as_view(), 
         name='diferencias_no_conciliadas'),
    path('reportes/extracto-conciliacion/', 
         reportes.ExtractoConciliacionMensualView.as_view(), 
         name='extracto_conciliacion_mensual'),
    path('reportes/exportar/', 
         reportes.ExportarReporteView.as_view(), 
         name='exportar_reporte'),
]