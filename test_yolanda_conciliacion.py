"""
Prueba de conciliación bancaria con usuario Yolanda
"""
import os
import django
import sys
import json

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from apps.companies.models import Company
from apps.banking.models import ExtractoBancario
from apps.banking.views.conciliacion import ReconciliationAjaxView

User = get_user_model()

def test_yolanda_ajax():
    """Probar el AJAX con el contexto de Yolanda"""
    
    print("🧪 PRUEBA AJAX - Usuario Yolanda")
    print("="*50)
    
    # 1. Obtener usuario Yolanda
    yolanda = User.objects.get(email='yolismarlen@gmail.com')
    gueber = Company.objects.get(trade_name='GUEBER')
    
    print(f"👤 Usuario: {yolanda.email}")
    print(f"🏢 Empresa: {gueber.trade_name}")
    
    # 2. Crear request factory
    factory = RequestFactory()
    
    # 3. Simular petición AJAX
    request = factory.get('/banking/conciliacion/ajax/?action=get_extractos&bank_account_id=3')
    request.user = yolanda
    
    # 4. Crear vista y probar
    view = ReconciliationAjaxView()
    view.request = request
    
    # 5. Probar get_current_company
    try:
        current_company = view.get_current_company()
        print(f"✅ Empresa actual obtenida: {current_company}")
        
        if current_company != gueber:
            print(f"⚠️  ADVERTENCIA: Empresa esperada {gueber.trade_name}, obtenida {current_company}")
            
    except Exception as e:
        print(f"❌ Error obteniendo empresa: {e}")
        return
    
    # 6. Probar la lógica del AJAX manualmente
    bank_account_id = request.GET.get('bank_account_id')
    action = request.GET.get('action')
    
    print(f"\n📋 Parámetros AJAX:")
    print(f"   - action: {action}")
    print(f"   - bank_account_id: {bank_account_id}")
    
    # 7. Ejecutar la misma lógica que la vista
    extractos = ExtractoBancario.objects.filter(
        bank_account_id=bank_account_id,
        bank_account__company=current_company
    ).order_by('-period_end')
    
    print(f"\n📊 Consulta de Extractos:")
    print(f"   - Extractos encontrados: {extractos.count()}")
    
    data = [
        {
            'id': extracto.id,
            'text': f"{extracto.period_start} - {extracto.period_end}"
        }
        for extracto in extractos
    ]
    
    print(f"\n📤 Respuesta JSON:")
    print(json.dumps(data, indent=2, default=str))
    
    # 8. Probar la vista completa
    print(f"\n🔧 Probando vista completa...")
    try:
        response = view.get(request)
        print(f"✅ Vista ejecutada exitosamente")
        print(f"   - Status code: {response.status_code}")
        print(f"   - Content: {response.content.decode()}")
    except Exception as e:
        print(f"❌ Error en la vista: {e}")

if __name__ == "__main__":
    test_yolanda_ajax()