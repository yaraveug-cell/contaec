#!/usr/bin/env python3
"""
Script para verificar si existe la URL del dashboard
"""

import requests
import sys

def check_dashboard_url():
    """Verificar acceso a la URL del dashboard"""
    
    url = "http://localhost:8000/dashboard/"
    
    print("🔍 VERIFICANDO URL DEL DASHBOARD")
    print(f"📍 URL: {url}")
    print("=" * 50)
    
    try:
        # Hacer request con timeout corto
        response = requests.get(url, timeout=5)
        
        print(f"📊 Código de estado: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ DASHBOARD ACCESIBLE")
            print("📄 La URL existe y responde correctamente")
            
            # Verificar contenido básico
            content_length = len(response.text)
            print(f"📏 Tamaño del contenido: {content_length} caracteres")
            
            # Mostrar preview del contenido
            preview = response.text[:200].replace('\n', ' ').replace('  ', ' ').strip()
            print(f"📄 Preview del contenido: {preview}...")
            
            # Buscar palabras clave de dashboard
            content_lower = response.text.lower()
            keywords = ['dashboard', 'kpi', 'chart', 'gráfico', 'métrica', 'indicador', 'balance', 'resultado']
            found_keywords = [kw for kw in keywords if kw in content_lower]
            
            if found_keywords:
                print(f"🔍 Palabras clave encontradas: {', '.join(found_keywords)}")
            else:
                print("⚠️  No se encontraron palabras clave típicas de dashboard")
                
            # Verificar si contiene elementos HTML típicos de dashboard
            html_elements = ['<div', '<canvas', '<chart', '<script', '<style']
            found_elements = [elem for elem in html_elements if elem in content_lower]
            
            if found_elements:
                print(f"🏗️  Elementos HTML encontrados: {', '.join(found_elements)}")
            else:
                print("⚠️  No se encontraron elementos HTML típicos")
                
        elif response.status_code == 404:
            print("❌ DASHBOARD NO EXISTE")
            print("📄 La URL devuelve 404 Not Found")
            
        elif response.status_code == 500:
            print("⚠️  DASHBOARD CON ERRORES")
            print("📄 La URL existe pero tiene errores internos (500)")
            
        elif response.status_code == 302 or response.status_code == 301:
            print("🔄 REDIRECCIÓN DETECTADA")
            location = response.headers.get('Location', 'No especificada')
            print(f"📍 Redirige a: {location}")
            
        elif response.status_code == 403:
            print("🚫 ACCESO DENEGADO")
            print("📄 Requiere autenticación o permisos")
            
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
    check_dashboard_url()