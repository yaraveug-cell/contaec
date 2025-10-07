"""
Configuración de la aplicación Banking
"""

from django.apps import AppConfig


class BankingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.banking'
    verbose_name = 'Gestión Bancaria'