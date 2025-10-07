"""
Prueba de las acciones de admin para extractos bancarios
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.banking.models import ExtractoBancario, ExtractoBancarioDetalle
from apps.banking.processors import ExtractoBancarioProcessor

def probar_procesador_admin():
    """Probar el procesador automático"""
    
    print("🧪 PRUEBA DEL PROCESADOR AUTOMÁTICO")
    print("="*50)
    
    # Encontrar extracto PICHINCHA no procesado
    extracto_pichincha = ExtractoBancario.objects.filter(
        bank_account__account_number='2201109377',
        status='uploaded'
    ).first()
    
    if not extracto_pichincha:
        # Si ya está procesado, resetear para prueba
        extracto_pichincha = ExtractoBancario.objects.filter(
            bank_account__account_number='2201109377'
        ).first()
        
        if extracto_pichincha:
            print(f"📄 Reseteando extracto para prueba: {extracto_pichincha}")
            # Limpiar detalles
            ExtractoBancarioDetalle.objects.filter(extracto=extracto_pichincha).delete()
            # Resetear status
            extracto_pichincha.status = 'uploaded'
            extracto_pichincha.processed_at = None
            extracto_pichincha.notes = ''
            extracto_pichincha.save()
        else:
            print("❌ No se encontró extracto PICHINCHA")
            return
    
    print(f"📊 Estado inicial:")
    print(f"   - Status: {extracto_pichincha.status}")
    print(f"   - Detalles: {ExtractoBancarioDetalle.objects.filter(extracto=extracto_pichincha).count()}")
    print(f"   - Archivo: {extracto_pichincha.file}")
    
    # Detectar formato
    print(f"\n🔍 DETECCIÓN DE FORMATO:")
    formato = ExtractoBancarioProcessor.detect_bank_format(extracto_pichincha.file.path)
    print(f"   - Formato detectado: {formato}")
    
    # Procesar extracto
    print(f"\n🚀 PROCESANDO EXTRACTO:")
    extracto_pichincha.status = 'processing'
    extracto_pichincha.save()
    
    success, message = ExtractoBancarioProcessor.process_extracto(extracto_pichincha)
    
    print(f"   - Resultado: {'✅ Exitoso' if success else '❌ Error'}")
    print(f"   - Mensaje: {message}")
    
    # Verificar resultado
    extracto_pichincha.refresh_from_db()
    detalles = ExtractoBancarioDetalle.objects.filter(extracto=extracto_pichincha)
    
    print(f"\n📊 RESULTADO FINAL:")
    print(f"   - Status: {extracto_pichincha.status}")
    print(f"   - Detalles creados: {detalles.count()}")
    print(f"   - Procesado el: {extracto_pichincha.processed_at}")
    print(f"   - Notas: {extracto_pichincha.notes}")
    
    if detalles.exists():
        print(f"\n📋 PRIMEROS 5 DETALLES:")
        for i, detalle in enumerate(detalles[:5], 1):
            print(f"   {i}. {detalle.fecha} - {detalle.descripcion[:30]} - D:{detalle.debito} C:{detalle.credito}")
        
        # Verificar totales
        total_debitos = sum(d.debito or 0 for d in detalles)
        total_creditos = sum(d.credito or 0 for d in detalles)
        
        print(f"\n💰 TOTALES:")
        print(f"   - Total débitos: ${total_debitos}")
        print(f"   - Total créditos: ${total_creditos}")
        print(f"   - Diferencia: ${total_creditos - total_debitos}")
    
    # Probar conciliación
    if success:
        print(f"\n🔗 PROBANDO CONCILIACIÓN:")
        from django.test import Client
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = User.objects.filter(is_superuser=True).first()
        
        if user:
            client = Client()
            client.force_login(user)
            
            url = f"/banking/conciliacion/?bank_account={extracto_pichincha.bank_account.id}&extracto={extracto_pichincha.id}"
            print(f"   - URL: {url}")
            
            response = client.get(url)
            print(f"   - Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Conciliación accesible")
                
                # Verificar extractos en dropdown
                content = response.content.decode('utf-8')
                if f'value="{extracto_pichincha.id}"' in content:
                    print(f"   ✅ Extracto disponible en dropdown")
                else:
                    print(f"   ❌ Extracto NO disponible en dropdown")
            else:
                print(f"   ❌ Error accediendo a conciliación")
        else:
            print(f"   ⚠️  No se encontró usuario superuser para prueba")

if __name__ == "__main__":
    probar_procesador_admin()