#!/usr/bin/env python
import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.users.models import User
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# Obtener el usuario contador
try:
    contador_user = User.objects.get(username='contador')
    print(f"Usuario contador encontrado: {contador_user.email}")
    
    # Lista de modelos para los cuales el contador debe tener permisos
    models_for_contador = [
        'companies.company',
        'companies.companyuser',
        'companies.companysettings', 
        'companies.companytype',
        'companies.economicactivity',
        'accounting.account',
        'accounting.accounttype',
        'accounting.fiscalyear',
        'accounting.journalentry',
        'accounting.journalentryline',
        'accounting.accountbalance',
        'invoicing.customer',
        'invoicing.supplier',
        'invoicing.invoice',
        'invoicing.invoiceline',
        'invoicing.product',
        'inventory.product',
        'inventory.warehouse',
        'inventory.stockmovement',
        'reports.report',
        'payroll.employee',
        'payroll.payroll',
        'fixed_assets.fixedasset',
        'fixed_assets.depreciationschedule',
    ]
    
    permissions_granted = 0
    
    for model in models_for_contador:
        app_label, model_name = model.split('.')
        try:
            content_type = ContentType.objects.get(app_label=app_label, model=model_name)
            
            # Obtener todos los permisos para este modelo
            permisos = Permission.objects.filter(content_type=content_type)
            
            for permiso in permisos:
                if not contador_user.user_permissions.filter(id=permiso.id).exists():
                    contador_user.user_permissions.add(permiso)
                    permissions_granted += 1
                    print(f"Agregado: {permiso}")
        
        except ContentType.DoesNotExist:
            print(f"Modelo no encontrado: {model}")
    
    print(f"\nTotal de permisos agregados: {permissions_granted}")
    print("Permisos del contador actualizados correctamente.")
    
except User.DoesNotExist:
    print("Usuario contador no encontrado")