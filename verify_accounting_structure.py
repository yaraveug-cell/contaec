#!/usr/bin/env python
import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.apps import apps

print("🔍 REVISANDO ESTRUCTURA CONTABLE")
print("=" * 40)

# 1. Buscar modelos relacionados con contabilidad
accounting_models = []
for app in apps.get_app_configs():
    for model in app.get_models():
        model_name = model._meta.model_name.lower()
        if any(keyword in model_name for keyword in ['entry', 'asiento', 'journal', 'contable', 'accounting']):
            accounting_models.append(f"{app.label}.{model._meta.model_name}")
            print(f"📋 Modelo encontrado: {app.label}.{model._meta.model_name}")

# 2. Revisar modelo Invoice
try:
    from apps.invoicing.models import Invoice
    print(f"\n💼 MODELO INVOICE:")
    fields = [f.name for f in Invoice._meta.fields]
    print(f"   Campos: {fields}")
    
    # Buscar relaciones con contabilidad
    contable_fields = []
    for field in Invoice._meta.fields:
        if any(keyword in field.name.lower() for keyword in ['entry', 'asiento', 'journal', 'contable']):
            contable_fields.append(f"{field.name} ({field.__class__.__name__})")
            print(f"   🔗 Campo contable: {field.name} ({field.__class__.__name__})")
    
    if not contable_fields:
        print("   ❌ No se encontraron campos contables directos")
            
except ImportError as e:
    print(f"❌ Error importando Invoice: {e}")

# 3. Buscar archivos de señales o admin que manejen asientos
print(f"\n📄 REVISANDO ARCHIVOS:")
signal_files = [
    "apps/invoicing/signals.py",
    "apps/invoicing/admin.py", 
    "apps/accounting/signals.py",
    "apps/accounting/admin.py"
]

for file_path in signal_files:
    if Path(file_path).exists():
        print(f"✅ Encontrado: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                keywords = ['asiento', 'entry', 'journal', 'contable']
                found_keywords = [kw for kw in keywords if kw.lower() in content.lower()]
                if found_keywords:
                    print(f"   📋 Contiene: {', '.join(found_keywords)}")
                else:
                    print(f"   ⚪ Sin lógica contable evidente")
        except Exception as e:
            print(f"   ❌ Error leyendo archivo: {e}")
    else:
        print(f"❌ No encontrado: {file_path}")

# 4. Revisar modelos de accounting específicamente
print(f"\n🏦 MODELOS DE ACCOUNTING:")
try:
    accounting_app = apps.get_app_config('accounting')
    for model in accounting_app.get_models():
        print(f"   📋 {model.__name__}: {[f.name for f in model._meta.fields]}")
        
        # Buscar campos de descripción
        desc_fields = []
        for field in model._meta.fields:
            if any(keyword in field.name.lower() for keyword in ['desc', 'detail', 'concept', 'note']):
                desc_fields.append(field.name)
        
        if desc_fields:
            print(f"      💬 Campos descripción: {desc_fields}")
            
except Exception as e:
    print(f"❌ Error revisando app accounting: {e}")

# 5. Buscar en admin.py de Invoice contenido sobre asientos
print(f"\n🔍 REVISANDO INVOICE ADMIN:")
try:
    with open("apps/invoicing/admin.py", 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        
        # Buscar métodos relacionados con asientos
        accounting_methods = []
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['asiento', 'entry', 'journal']):
                accounting_methods.append(f"Línea {i+1}: {line.strip()}")
        
        if accounting_methods:
            print("   📋 Líneas con lógica contable:")
            for method in accounting_methods[:5]:  # Mostrar solo las primeras 5
                print(f"      {method}")
        else:
            print("   ❌ No se encontró lógica contable en Invoice admin")
            
except Exception as e:
    print(f"❌ Error revisando Invoice admin: {e}")

print("\n🏁 Revisión completada")