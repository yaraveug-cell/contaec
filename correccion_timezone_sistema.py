#!/usr/bin/env python
"""
Script para corregir timestamps de timezone en todo el sistema
Convierte timezone.now() y datetime.now() a hora local de Ecuador
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.utils import timezone

def identificar_archivos_problematicos():
    """Identifica archivos que necesitan corrección de timezone"""
    
    archivos_identificados = [
        {
            'archivo': 'apps/accounting/journal_book_views.py',
            'linea': 398,
            'problema': 'datetime.now().strftime()',
            'tipo': 'PDF Report Generator'
        },
        {
            'archivo': 'apps/accounting/cash_flow_views.py', 
            'linea': 521,
            'problema': 'datetime.now().strftime()',
            'tipo': 'PDF Report Generator'
        },
        {
            'archivo': 'apps/accounting/journal_pdf.py',
            'linea': 116,
            'problema': 'created_at.strftime() - campo DateTimeField',
            'tipo': 'PDF Model Data Display'
        },
        {
            'archivo': 'apps/accounting/journal_pdf.py',
            'linea': 123,
            'problema': 'posted_at.strftime() - campo DateTimeField',
            'tipo': 'PDF Model Data Display'
        },
        {
            'archivo': 'apps/accounting/admin.py',
            'linea': 357,
            'problema': 'posted_at = timezone.now()',
            'tipo': 'Model Field Assignment'
        }
    ]
    
    print("🔍 ARCHIVOS IDENTIFICADOS PARA CORRECCIÓN:")
    print("="*60)
    
    for i, archivo in enumerate(archivos_identificados, 1):
        print(f"{i}. {archivo['archivo']}")
        print(f"   📍 Línea: {archivo['linea']}")
        print(f"   ❌ Problema: {archivo['problema']}")
        print(f"   📂 Tipo: {archivo['tipo']}")
        print()
    
    return archivos_identificados

def mostrar_correcciones():
    """Muestra las correcciones que se van a aplicar"""
    
    correcciones = {
        'PDF Generators': {
            'antes': 'datetime.now().strftime("format")',
            'despues': 'timezone.localtime(timezone.now()).strftime("format")',
            'explicacion': 'Para timestamps de generación de documentos PDF'
        },
        'Model DateTime Fields': {
            'antes': 'model.created_at.strftime("format")',
            'despues': 'timezone.localtime(model.created_at).strftime("format")',
            'explicacion': 'Para mostrar campos DateTimeField en hora local'
        },
        'Model Field Assignment': {
            'antes': 'model.posted_at = timezone.now()',
            'despues': 'model.posted_at = timezone.now()  # Mantener UTC en DB',
            'explicacion': 'En base de datos mantener UTC, solo convertir para display'
        }
    }
    
    print("🔧 ESTRATEGIA DE CORRECCIÓN:")
    print("="*50)
    
    for tipo, info in correcciones.items():
        print(f"\n📋 {tipo}:")
        print(f"   ❌ ANTES: {info['antes']}")
        print(f"   ✅ DESPUÉS: {info['despues']}")
        print(f"   📝 Razón: {info['explicacion']}")

def mostrar_impacto():
    """Muestra el impacto de las correcciones"""
    
    print("\n📊 IMPACTO DE LAS CORRECCIONES:")
    print("="*40)
    
    impactos = [
        "✅ PDFs de Asientos Contables: Hora local Ecuador",
        "✅ PDFs de Libro Diario: Hora local Ecuador", 
        "✅ PDFs de Flujo de Caja: Hora local Ecuador",
        "✅ Fechas de creación en reportes: Hora local",
        "✅ Fechas de contabilización: Hora local",
        "📋 Base de datos: Mantiene UTC (recomendado)",
        "🌍 Zona horaria: America/Guayaquil (UTC-5)"
    ]
    
    for impacto in impactos:
        print(f"  {impacto}")

def verificar_timezone_actual():
    """Verifica el timezone actual del sistema"""
    
    print(f"\n🕐 VERIFICACIÓN TIMEZONE ACTUAL:")
    print("="*35)
    
    now_utc = timezone.now()
    now_local = timezone.localtime(now_utc)
    
    print(f"UTC: {now_utc.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Local (Ecuador): {now_local.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Diferencia: {(now_utc.hour - now_local.hour) % 24} horas")

if __name__ == "__main__":
    print("🛠️  CORRECCIÓN MASIVA DE TIMEZONE - SISTEMA CONTABLE")
    print("="*55)
    
    # Identificar archivos
    archivos = identificar_archivos_problematicos()
    
    # Mostrar estrategia
    mostrar_correcciones()
    
    # Mostrar impacto
    mostrar_impacto()
    
    # Verificar timezone actual
    verificar_timezone_actual()
    
    print(f"\n⚡ PRÓXIMO PASO: Aplicar correcciones automáticamente")
    print(f"   Los cambios se aplicarán de forma segura y sistemática")