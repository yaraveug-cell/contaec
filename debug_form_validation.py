"""
Script para diagnosticar errores del formulario de filtros
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.companies.models import Company
from apps.banking.forms import ReconciliationFilterForm

User = get_user_model()

def debug_form_validation():
    """Diagnosticar errores en el formulario de filtros"""
    
    print("🔍 DIAGNÓSTICO FORMULARIO DE FILTROS")
    print("="*50)
    
    yolanda = User.objects.get(email='yolismarlen@gmail.com')
    gueber = Company.objects.get(trade_name='GUEBER')
    
    test_data_sets = [
        {
            'name': 'Solo bank_account',
            'data': {'bank_account': '3'}
        },
        {
            'name': 'bank_account + extracto',
            'data': {'bank_account': '3', 'extracto': '1'}
        },
        {
            'name': 'Completo con fechas',
            'data': {
                'bank_account': '3',
                'extracto': '1',
                'fecha_desde': '2025-09-01',
                'fecha_hasta': '2025-10-10'
            }
        }
    ]
    
    for test in test_data_sets:
        print(f"\n📋 Test: {test['name']}")
        print(f"   Datos: {test['data']}")
        
        # Crear formulario
        form = ReconciliationFilterForm(
            data=test['data'],
            company=gueber
        )
        
        print(f"   ✅ Formulario creado")
        print(f"   📊 Es válido: {form.is_valid()}")
        
        if not form.is_valid():
            print(f"   ❌ Errores: {form.errors}")
            print(f"   ❌ Errores no de campo: {form.non_field_errors()}")
        else:
            cleaned_data = form.cleaned_data
            print(f"   ✅ Datos limpiados:")
            for key, value in cleaned_data.items():
                print(f"     - {key}: {value} ({type(value).__name__})")
        
        # Verificar queryset específicamente
        print(f"   📂 Bank account queryset: {form.fields['bank_account'].queryset.count()} items")
        print(f"   📂 Extracto queryset: {form.fields['extracto'].queryset.count()} items")

if __name__ == "__main__":
    debug_form_validation()