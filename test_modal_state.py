#!/usr/bin/env python3
"""
Script para verificar el estado de la ventana modal del resumen de factura
"""

import os
import django
from django.test import RequestFactory, TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.loader import render_to_string

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice, InvoiceLine, Customer
from apps.accounting.models import Account, Company

def test_modal_javascript():
    """Verifica que el JavaScript de la modal esté correctamente configurado"""
    
    js_file_path = 'static/admin/js/tax_breakdown_calculator.js'
    
    if not os.path.exists(js_file_path):
        print("❌ Archivo JavaScript no encontrado")
        return False
    
    with open(js_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar que el código tiene la configuración correcta
    checks = [
        ("Estado inicial desplegado", "let isMinimized = false;" in content),
        ("Display block inicial", "contentContainer.style.display = 'block';" in content),
        ("Botón minimizar inicial", "minimizeBtn.innerHTML = '▲';" in content),
        ("Título inicial correcto", "titleText.textContent = 'Resumen de Factura';" in content),
        ("Tooltip minimizar inicial", "minimizeBtn.title = 'Minimizar';" in content),
    ]
    
    print("🔍 Verificando configuración del JavaScript:")
    print("-" * 50)
    
    all_passed = True
    for check_name, condition in checks:
        if condition:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
            all_passed = False
    
    # Buscar posibles problemas
    print("\n🔍 Análisis adicional:")
    print("-" * 30)
    
    if "isMinimized = true" in content:
        print("⚠️ PROBLEMA: Encontrado 'isMinized = true' en el código")
        
    if "display: 'none'" in content and "contentContainer.style.display = 'none'" not in content:
        print("⚠️ PROBLEMA: Posible conflicto con display 'none'")
        
    if "'Resumen (minimizado)'" in content:
        print("⚠️ PROBLEMA: Texto 'minimizado' encontrado en el código")
    
    # Mostrar líneas relevantes
    lines = content.split('\n')
    print("\n📋 Líneas relevantes del código:")
    print("-" * 40)
    
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        if any(keyword in line_stripped for keyword in [
            'isMinimized = ', 
            'contentContainer.style.display = ',
            'minimizeBtn.innerHTML = ',
            "titleText.textContent = 'Resumen",
            "minimizeBtn.title = '"
        ]):
            print(f"Línea {i:3}: {line_stripped}")
    
    return all_passed

def create_test_invoice_page():
    """Crea una página de prueba para verificar la modal"""
    
    try:
        # Obtener o crear empresa
        company = Company.objects.first()
        if not company:
            print("❌ No hay empresas configuradas")
            return None
            
        # Obtener o crear cliente
        customer = Customer.objects.first()
        if not customer:
            print("❌ No hay clientes configurados")
            return None
            
        # Crear factura de prueba
        invoice = Invoice.objects.create(
            company=company,
            customer=customer,
            invoice_number="TEST-MODAL-001",
            subtotal=0,
            tax_amount=0,
            total=0
        )
        
        print(f"✅ Factura de prueba creada: {invoice}")
        print(f"🔗 URL de edición: /admin/invoicing/invoice/{invoice.id}/change/")
        
        return invoice
        
    except Exception as e:
        print(f"❌ Error creando factura de prueba: {e}")
        return None

def main():
    print("🧪 Test del Estado de la Ventana Modal del Resumen")
    print("=" * 60)
    
    # Test 1: Verificar JavaScript
    print("\n1️⃣ VERIFICACIÓN DEL JAVASCRIPT")
    js_ok = test_modal_javascript()
    
    # Test 2: Crear factura de prueba
    print("\n2️⃣ CREACIÓN DE FACTURA DE PRUEBA")
    invoice = create_test_invoice_page()
    
    # Resumen
    print("\n📊 RESUMEN")
    print("=" * 30)
    
    if js_ok:
        print("✅ JavaScript configurado correctamente")
    else:
        print("❌ Problemas en la configuración JavaScript")
    
    if invoice:
        print("✅ Factura de prueba disponible")
        print(f"   ID: {invoice.id}")
    else:
        print("❌ No se pudo crear factura de prueba")
    
    # Instrucciones para el usuario
    print("\n🔧 INSTRUCCIONES PARA RESOLVER EL PROBLEMA:")
    print("-" * 50)
    print("1. Abre la factura de prueba en el admin")
    print("2. Presiona F12 para abrir DevTools")
    print("3. Ve a la pestaña 'Console'")
    print("4. Busca errores JavaScript")
    print("5. Ve a la pestaña 'Network' y recarga (F5)")
    print("6. Verifica que tax_breakdown_calculator.js se cargue sin caché")
    print("7. Si persiste el problema, presiona Ctrl+Shift+R para forzar recarga")

if __name__ == "__main__":
    main()