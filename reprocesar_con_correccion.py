"""
Reprocesar extracto PICHINCHA con corrección de decimales
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

def reprocesar_con_correccion():
    """Reprocesar extracto PICHINCHA con corrección de decimales"""
    
    print("🔄 REPROCESAMIENTO CON CORRECCIÓN DECIMALES")
    print("="*60)
    
    # Buscar extracto PICHINCHA
    extracto = ExtractoBancario.objects.filter(
        bank_account__account_number='2201109377',
        status='processed'
    ).first()
    
    if not extracto:
        print("❌ No se encontró extracto PICHINCHA procesado")
        return
    
    print(f"📄 Extracto: {extracto}")
    
    # Mostrar totales ANTES
    detalles_antes = ExtractoBancarioDetalle.objects.filter(extracto=extracto)
    total_debitos_antes = sum(d.debito or 0 for d in detalles_antes)
    total_creditos_antes = sum(d.credito or 0 for d in detalles_antes)
    
    print(f"\n📊 ANTES DE LA CORRECCIÓN:")
    print(f"   - Detalles: {detalles_antes.count()}")
    print(f"   - Total débitos: ${total_debitos_antes:,.2f}")
    print(f"   - Total créditos: ${total_creditos_antes:,.2f}")
    
    # Ejemplo de primeros 3 antes
    print(f"\n   📋 Primeros 3 ANTES:")
    for i, detalle in enumerate(detalles_antes[:3], 1):
        debito = detalle.debito or 0
        credito = detalle.credito or 0
        print(f"      {i}. D:${debito} C:${credito} - {detalle.descripcion[:30]}")
    
    # Resetear para reprocesar
    print(f"\n🔄 REPROCESANDO...")
    extracto.status = 'uploaded'
    extracto.processed_at = None
    extracto.save()
    
    # Limpiar detalles
    ExtractoBancarioDetalle.objects.filter(extracto=extracto).delete()
    
    # Reprocesar con corrección
    success, message = ExtractoBancarioProcessor.process_extracto(extracto)
    
    print(f"   - Resultado: {'✅ Exitoso' if success else '❌ Error'}")
    print(f"   - Mensaje: {message}")
    
    # Mostrar totales DESPUÉS
    if success:
        extracto.refresh_from_db()
        detalles_despues = ExtractoBancarioDetalle.objects.filter(extracto=extracto)
        total_debitos_despues = sum(d.debito or 0 for d in detalles_despues)
        total_creditos_despues = sum(d.credito or 0 for d in detalles_despues)
        
        print(f"\n📊 DESPUÉS DE LA CORRECCIÓN:")
        print(f"   - Detalles: {detalles_despues.count()}")
        print(f"   - Total débitos: ${total_debitos_despues:,.2f}")
        print(f"   - Total créditos: ${total_creditos_despues:,.2f}")
        
        # Ejemplo de primeros 3 después
        print(f"\n   📋 Primeros 3 DESPUÉS:")
        for i, detalle in enumerate(detalles_despues[:3], 1):
            debito = detalle.debito or 0
            credito = detalle.credito or 0
            print(f"      {i}. D:${debito} C:${credito} - {detalle.descripcion[:30]}")
        
        # Comparar diferencia
        print(f"\n🔍 COMPARACIÓN:")
        factor_debitos = total_debitos_antes / total_debitos_despues if total_debitos_despues > 0 else 0
        factor_creditos = total_creditos_antes / total_creditos_despues if total_creditos_despues > 0 else 0
        
        print(f"   - Factor débitos: {factor_debitos:.1f}x")
        print(f"   - Factor créditos: {factor_creditos:.1f}x")
        
        if abs(factor_debitos - 100) < 5:  # Aproximadamente 100x
            print(f"   ✅ Corrección exitosa: los valores se dividieron por 100")
        else:
            print(f"   ⚠️  Factor inesperado")
        
        # Verificar archivo original nuevamente
        print(f"\n🔍 VERIFICACIÓN CON ARCHIVO:")
        try:
            with open(extracto.file.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar primer monto en archivo
            import re
            montos_archivo = re.findall(r'\$(\d+,\d+)', content)
            
            if montos_archivo:
                primer_monto_archivo = montos_archivo[0]
                primer_monto_bd = detalles_despues.first()
                
                print(f"   - Primer monto archivo: ${primer_monto_archivo}")
                if primer_monto_bd:
                    monto_bd = primer_monto_bd.debito or primer_monto_bd.credito or 0
                    print(f"   - Primer monto BD: ${monto_bd}")
                    
                    # Convertir archivo a decimal para comparar
                    archivo_decimal = float(primer_monto_archivo.replace(',', '.'))
                    if abs(float(monto_bd) - archivo_decimal) < 0.01:
                        print(f"   ✅ Montos coinciden perfectamente")
                    else:
                        print(f"   ⚠️  Diferencia: BD=${monto_bd} vs Archivo=${archivo_decimal}")
        
        except Exception as e:
            print(f"   ❌ Error verificando archivo: {e}")

if __name__ == "__main__":
    reprocesar_con_correccion()