"""
URLs para conciliación bancaria
"""

from django.urls import path
from ..views import ReconciliationView, ReconciliationAjaxView

app_name = 'conciliacion'

urlpatterns = [
    path('', ReconciliationView.as_view(), name='index'),
    path('ajax/', ReconciliationAjaxView.as_view(), name='ajax'),
]