#!/usr/bin/env python3
"""
Script para probar las acciones grupales de asientos contables
Versión: 1.0
Fecha: 2025-10-01
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib import admin
from apps.accounting.models import JournalEntry
from apps.accounting.admin import JournalEntryAdmin
from django.test import RequestFactory

User = get_user_model()

def test_bulk_actions():
    """Probar las acciones grupales de asientos contables"""
    
    print("=== PRUEBA DE ACCIONES GRUPALES DE ASIENTOS CONTABLES ===\n")
    
    # Obtener datos iniciales
    total_entries = JournalEntry.objects.count()
    draft_entries = JournalEntry.objects.filter(state='draft').count()
    posted_entries = JournalEntry.objects.filter(state='posted').count()
    cancelled_entries = JournalEntry.objects.filter(state='cancelled').count()
    
    print(f"📊 ESTADO INICIAL:")
    print(f"   Total de asientos: {total_entries}")
    print(f"   Borradores: {draft_entries}")
    print(f"   Contabilizados: {posted_entries}")
    print(f"   Anulados: {cancelled_entries}")
    print()
    
    # Verificar asientos balanceados vs desbalanceados
    balanced_count = 0
    unbalanced_count = 0
    
    for entry in JournalEntry.objects.all():
        if entry.is_balanced:
            balanced_count += 1
        else:
            unbalanced_count += 1
    
    print(f"⚖️ ESTADO DE BALANCE:")
    print(f"   Asientos balanceados: {balanced_count}")
    print(f"   Asientos desbalanceados: {unbalanced_count}")
    print()
    
    # Mostrar detalles de asientos
    print("📝 DETALLES DE ASIENTOS:")
    for entry in JournalEntry.objects.all()[:10]:  # Mostrar primeros 10
        balance_status = "✅ Balanceado" if entry.is_balanced else f"❌ Desbalanceado (diff: {abs(entry.total_debit - entry.total_credit):.2f})"
        print(f"   {entry.number} | {entry.state.upper()} | {balance_status}")
    
    if total_entries > 10:
        print(f"   ... y {total_entries - 10} asientos más")
    print()
    
    # Simular request para pruebas
    factory = RequestFactory()
    request = factory.get('/admin/accounting/journalentry/')
    
    # Obtener usuario admin para las pruebas
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.filter(is_staff=True).first()
        
        if admin_user:
            request.user = admin_user
            print(f"👤 Usuario para pruebas: {admin_user.username}")
        else:
            print("⚠️ No se encontró usuario admin/staff para pruebas")
            return
    except Exception as e:
        print(f"❌ Error obteniendo usuario: {e}")
        return
    
    # Crear instancia del admin
    admin_instance = JournalEntryAdmin(JournalEntry, admin.site)
    
    print("\n🔧 ACCIONES DISPONIBLES:")
    for action_name in admin_instance.actions:
        action_func = getattr(admin_instance, action_name)
        print(f"   - {action_name}: {action_func.short_description}")
    
    print("\n✅ CONFIGURACIÓN COMPLETADA")
    print("Las acciones grupales están disponibles en el admin de Django:")
    print("1. 🟢 Contabilizar asientos seleccionados - Valida balance y cambia estado a 'posted'")
    print("2. 🔴 Anular asientos seleccionados - Cambia estado a 'cancelled'") 
    print("3. 🟡 Regresar asientos a borrador - Cambia estado a 'draft'")
    
    print(f"\n📍 Accede al admin: http://localhost:8000/admin/accounting/journalentry/")
    print("Selecciona uno o más asientos y elige la acción desde el dropdown 'Acción'")

if __name__ == "__main__":
    try:
        test_bulk_actions()
    except Exception as e:
        print(f"❌ Error ejecutando pruebas: {e}")
        import traceback
        traceback.print_exc()