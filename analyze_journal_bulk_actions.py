#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import JournalEntry, JournalEntryLine
from django.contrib.admin import ModelAdmin
from django.apps import apps

print('🔍 ANÁLISIS: Acciones Grupales para Asientos Contables')
print('=' * 60)

# 1. Revisar estructura actual de JournalEntry
print('📊 MODELO JOURNALENTRY:')
journal_fields = [f.name for f in JournalEntry._meta.fields]
print(f'   Campos: {journal_fields}')

# Buscar campo de estado
state_field = None
for field in JournalEntry._meta.fields:
    if 'state' in field.name.lower() or 'status' in field.name.lower():
        state_field = field
        break

if state_field:
    print(f'✅ Campo de estado encontrado: {state_field.name}')
    if hasattr(state_field, 'choices') and state_field.choices:
        print(f'   Estados disponibles: {state_field.choices}')
    else:
        print('   Sin choices definidas - campo libre')
else:
    print('❌ No se encontró campo de estado específico')

# 2. Contar asientos por estado actual
total_entries = JournalEntry.objects.count()
print(f'\n📋 DISTRIBUCIÓN ACTUAL:')
print(f'   Total asientos: {total_entries}')

if state_field and hasattr(state_field, 'choices') and state_field.choices:
    for state_code, state_name in state_field.choices:
        count = JournalEntry.objects.filter(**{state_field.name: state_code}).count()
        print(f'   {state_name}: {count} asientos')

# 3. Revisar admin actual
try:
    from apps.accounting.admin import JournalEntryAdmin
    admin_class = JournalEntryAdmin
    print(f'\n✅ ADMIN ACTUAL ENCONTRADO: {admin_class.__name__}')
    
    # Verificar si ya tiene acciones
    existing_actions = getattr(admin_class, 'actions', [])
    print(f'   Acciones existentes: {existing_actions}')
    
    # Revisar list_display
    list_display = getattr(admin_class, 'list_display', [])
    print(f'   Campos mostrados: {list_display}')
    
except ImportError:
    print('❌ Admin de JournalEntry no encontrado o no importado')

# 4. Analizar relaciones con facturas
print(f'\n🔗 RELACIÓN CON FACTURAS:')
entries_with_invoice_ref = JournalEntry.objects.filter(
    reference__startswith='FAC-'
).count()
print(f'   Asientos relacionados con facturas: {entries_with_invoice_ref}')

# Buscar patrones en referencias
sample_entries = JournalEntry.objects.filter(
    reference__startswith='FAC-'
)[:5]

print(f'   Ejemplos de referencias:')
for entry in sample_entries:
    print(f'     - {entry.reference}: {entry.description[:50]}...')

# 5. Analizar casos de uso potenciales
print(f'\n🎯 CASOS DE USO IDENTIFICADOS:')
print(f'   1. APROBAR asientos en borrador → Definitivo')
print(f'   2. ANULAR asientos erróneos → Anulado/Cancelado') 
print(f'   3. REABRIR asientos para corrección → Borrador')
print(f'   4. CERRAR período contable → Cerrado/Bloqueado')

# 6. Identificar estados comunes en contabilidad
print(f'\n📋 ESTADOS TÍPICOS EN SISTEMAS CONTABLES:')
common_states = [
    ('draft', 'Borrador'),
    ('posted', 'Registrado'), 
    ('approved', 'Aprobado'),
    ('closed', 'Cerrado'),
    ('cancelled', 'Anulado'),
    ('reversed', 'Revertido')
]

for code, name in common_states:
    print(f'   - {code}: {name}')

# 7. Analizar impacto en balances
print(f'\n⚖️ IMPACTO EN BALANCES:')
print(f'   - Estados ACTIVOS (afectan balance): posted, approved, closed')
print(f'   - Estados INACTIVOS (no afectan): draft, cancelled, reversed')
print(f'   - Transiciones críticas que requieren recálculo de balances')

# 8. Consideraciones de seguridad
print(f'\n🔒 CONSIDERACIONES DE SEGURIDAD:')
print(f'   - Cambios masivos pueden afectar reportes financieros')
print(f'   - Necesidad de validar períodos contables abiertos')
print(f'   - Auditoría de cambios grupales')
print(f'   - Permisos específicos para operaciones masivas')

# 9. Complejidad técnica estimada
print(f'\n⚡ ANÁLISIS DE COMPLEJIDAD:')
print(f'   BAJA COMPLEJIDAD:')
print(f'     - Cambio simple de estado sin validaciones')
print(f'     - Mensajes de confirmación básicos')
print(f'   ')
print(f'   MEDIA COMPLEJIDAD:')
print(f'     - Validación de períodos contables')
print(f'     - Recálculo de balances automático')
print(f'   ')
print(f'   ALTA COMPLEJIDAD:')
print(f'     - Sistema de aprobaciones por niveles')
print(f'     - Integración con auditoría completa')

print(f'\n🎯 RECOMENDACIÓN: Implementación por FASES')
print(f'   FASE 1: Acciones básicas de estado (MÍNIMA COMPLEJIDAD)')
print(f'   FASE 2: Validaciones contables (según necesidad)')
print(f'   FASE 3: Funciones avanzadas (si se requiere)')

print(f'\n🏁 Análisis completado')