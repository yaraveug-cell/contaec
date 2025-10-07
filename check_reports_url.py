#!/usr/bin/env python3
"""
Script simple para verificar si existe la URL de reportes
"""

import requests
import sys

def check_reports_url():
    """Verificar acceso a la URL de reportes"""
    
    url = "http://localhost:8000/modulos/reportes/"
    
    print("🔍 VERIFICANDO URL DE REPORTES")
    print(f"📍 URL: {url}")
    print("=" * 50)
    
    try:
        # Hacer request con timeout corto
        response = requests.get(url, timeout=5)
        
        print(f"📊 Código de estado: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ REPORTES ACCESIBLES")
            print("📄 La URL existe y responde correctamente")
            
            # Verificar contenido básico
            content_length = len(response.text)
            print(f"📏 Tamaño del contenido: {content_length} caracteres")
            
            # Buscar palabras clave
            content_lower = response.text.lower()
            keywords = ['reporte', 'balance', 'estado', 'resultado', 'dashboard']
            found_keywords = [kw for kw in keywords if kw in content_lower]
            
            if found_keywords:
                print(f"🔍 Palabras clave encontradas: {', '.join(found_keywords)}")
            else:
                print("⚠️  No se encontraron palabras clave de reportes")
                
        elif response.status_code == 404:
            print("❌ REPORTES NO EXISTEN")
            print("📄 La URL devuelve 404 Not Found")
            
        elif response.status_code == 500:
            print("⚠️  REPORTES CON ERRORES")
            print("📄 La URL existe pero tiene errores internos (500)")
            
        elif response.status_code == 302 or response.status_code == 301:
            print("🔄 REDIRECCIÓN DETECTADA")
            location = response.headers.get('Location', 'No especificada')
            print(f"📍 Redirige a: {location}")
            
        else:
            print(f"⚠️  RESPUESTA INESPERADA: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ SERVIDOR NO DISPONIBLE")
        print("📄 No se puede conectar a localhost:8000")
        print("💡 Asegúrate de que el servidor Django esté corriendo")
        
    except requests.exceptions.Timeout:
        print("⏱️  TIMEOUT")
        print("📄 El servidor tardó más de 5 segundos en responder")
        
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")
        
    print("\n🏁 VERIFICACIÓN COMPLETADA")

if __name__ == "__main__":
    check_reports_url()