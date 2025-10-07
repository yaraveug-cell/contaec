#!/usr/bin/env python
"""
Verificacion detallada de las acciones en lote
"""

import os
import sys
import django
import inspect

# Configurar Django
sys.path.append('c:/contaec')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.suppliers.admin import PurchaseInvoiceAdmin
from apps.suppliers.models import PurchaseInvoice

def check_action_security():
    print("=== VERIFICACION DETALLADA DE ACCIONES ===")
    
    admin_instance = PurchaseInvoiceAdmin(PurchaseInvoice, None)
    actions = ['mark_as_received', 'mark_as_validated', 'mark_as_paid', 'mark_as_cancelled', 'create_journal_entries']
    
    for action_name in actions:
        if hasattr(admin_instance, action_name):
            action_method = getattr(admin_instance, action_name)
            source_code = inspect.getsource(action_method)
            
            print(f"\n--- {action_name} ---")
            
            # Verificar si filtra por empresa del usuario
            if 'user_companies' in source_code and 'CompanyUser.objects.filter' in source_code:
                print("✅ SEGURO: Filtra por empresa del usuario")
            elif 'request.user.is_superuser' in source_code:
                print("✅ SEGURO: Verifica si es superuser")
            else:
                print("❌ INSEGURO: No filtra por empresa")
                
            # Mostrar fragmento relevante
            lines = source_code.split('\n')
            for i, line in enumerate(lines):
                if 'user_companies' in line or 'is_superuser' in line:
                    print(f"Linea {i+1}: {line.strip()}")

if __name__ == "__main__":
    check_action_security()