#!/usr/bin/env python3
"""
Script para crear asientos de capital inicial y balancear el sistema
Versión: 1.0
Fecha: 2025-10-02
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.accounting.models import JournalEntry, JournalEntryLine, ChartOfAccounts
from apps.companies.models import Company
from django.contrib.auth import get_user_model
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

User = get_user_model()

def create_balance_entries():
    """Crear asientos de capital inicial para balancear el sistema"""
    
    print("🔧 CREACIÓN DE ASIENTOS DE BALANCE")
    print("=" * 45)
    
    # Obtener empresas
    companies = Company.objects.all()
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if not admin_user:
        admin_user = User.objects.filter(is_staff=True).first()
        
    if not admin_user:
        print("❌ No se encontró usuario administrador")
        return
    
    print(f"👤 Usuario para asientos: {admin_user.username}")
    print()
    
    for company in companies:
        print(f"🏢 PROCESANDO: {company.trade_name}")
        
        # Calcular desbalance actual
        company_ids = [company.id]
        
        # Activos
        activos_lines = JournalEntryLine.objects.filter(
            journal_entry__company__in=company_ids,
            journal_entry__state='posted',
            account__code__startswith='1'
        )
        
        activos_debit = activos_lines.aggregate(total=Sum('debit'))['total'] or Decimal('0.00')
        activos_credit = activos_lines.aggregate(total=Sum('credit'))['total'] or Decimal('0.00')
        activos_saldo = activos_debit - activos_credit
        
        # Pasivos
        pasivos_lines = JournalEntryLine.objects.filter(
            journal_entry__company__in=company_ids,
            journal_entry__state='posted',
            account__code__startswith='2'
        )
        
        pasivos_debit = pasivos_lines.aggregate(total=Sum('debit'))['total'] or Decimal('0.00')
        pasivos_credit = pasivos_lines.aggregate(total=Sum('credit'))['total'] or Decimal('0.00')
        pasivos_saldo = pasivos_credit - pasivos_debit
        
        # Patrimonio actual
        patrimonio_lines = JournalEntryLine.objects.filter(
            journal_entry__company__in=company_ids,
            journal_entry__state='posted',
            account__code__startswith='3'
        )
        
        patrimonio_debit = patrimonio_lines.aggregate(total=Sum('debit'))['total'] or Decimal('0.00')
        patrimonio_credit = patrimonio_lines.aggregate(total=Sum('credit'))['total'] or Decimal('0.00')
        patrimonio_saldo = patrimonio_credit - patrimonio_debit
        
        # Calcular desbalance
        diferencia = activos_saldo - (pasivos_saldo + patrimonio_saldo)
        
        print(f"   Activos: ${activos_saldo}")
        print(f"   Pasivos: ${pasivos_saldo}")
        print(f"   Patrimonio: ${patrimonio_saldo}")
        print(f"   Diferencia: ${diferencia}")
        
        if abs(diferencia) < Decimal('0.01'):
            print("   ✅ Ya está balanceado")
            continue
        
        print(f"   ⚡ Creando asiento de capital inicial por ${diferencia}")
        
        try:
            with transaction.atomic():
                # Buscar o crear cuenta de capital social
                capital_account, created = ChartOfAccounts.objects.get_or_create(
                    company=company,
                    code='3.1.01.01',
                    defaults={
                        'name': 'CAPITAL SOCIAL',
                        'account_type_id': 1,  # Asumiendo que existe un tipo de cuenta
                        'is_detail': True,
                        'is_active': True
                    }
                )
                
                if created:
                    print(f"   📋 Creada cuenta: {capital_account.code} - {capital_account.name}")
                
                # Crear asiento de capital inicial
                # Obtener el próximo número de asiento
                last_entry = JournalEntry.objects.filter(company=company).order_by('-number').first()
                next_number = 1
                if last_entry and last_entry.number:
                    try:
                        current_num = int(last_entry.number)
                        next_number = current_num + 1
                    except ValueError:
                        next_number = 1
                
                new_number = f"{next_number:06d}"
                
                # Crear el asiento
                journal_entry = JournalEntry.objects.create(
                    company=company,
                    number=new_number,
                    date=timezone.now().date(),
                    description=f"Asiento de capital inicial - Balance automático",
                    created_by=admin_user,
                    state='posted',  # Crearlo directamente como contabilizado
                    posted_by=admin_user,
                    posted_at=timezone.now()
                )
                
                # Línea de crédito - Capital Social
                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=capital_account,
                    description=f"Capital inicial - {company.trade_name}",
                    debit=Decimal('0.00'),
                    credit=diferencia
                )
                
                print(f"   ✅ Asiento {new_number} creado exitosamente")
                print(f"      Crédito: {capital_account.code} - ${diferencia}")
                
                # Calcular totales del asiento
                journal_entry.total_debit = diferencia
                journal_entry.total_credit = diferencia
                journal_entry.save()
                
        except Exception as e:
            print(f"   ❌ Error creando asiento: {e}")
            continue
    
    print("\n🎉 PROCESO COMPLETADO")
    print("\n📊 VERIFICANDO BALANCE FINAL...")
    
    # Verificar balance final
    for company in companies:
        company_ids = [company.id]
        
        # Recalcular después de los asientos
        activos_lines = JournalEntryLine.objects.filter(
            journal_entry__company__in=company_ids,
            journal_entry__state='posted',
            account__code__startswith='1'
        )
        
        activos_debit = activos_lines.aggregate(total=Sum('debit'))['total'] or Decimal('0.00')
        activos_credit = activos_lines.aggregate(total=Sum('credit'))['total'] or Decimal('0.00')
        activos_saldo = activos_debit - activos_credit
        
        pasivos_lines = JournalEntryLine.objects.filter(
            journal_entry__company__in=company_ids,
            journal_entry__state='posted',
            account__code__startswith='2'
        )
        
        pasivos_debit = pasivos_lines.aggregate(total=Sum('debit'))['total'] or Decimal('0.00')
        pasivos_credit = pasivos_lines.aggregate(total=Sum('credit'))['total'] or Decimal('0.00')
        pasivos_saldo = pasivos_credit - pasivos_debit
        
        patrimonio_lines = JournalEntryLine.objects.filter(
            journal_entry__company__in=company_ids,
            journal_entry__state='posted',
            account__code__startswith='3'
        )
        
        patrimonio_debit = patrimonio_lines.aggregate(total=Sum('debit'))['total'] or Decimal('0.00')
        patrimonio_credit = patrimonio_lines.aggregate(total=Sum('credit'))['total'] or Decimal('0.00')
        patrimonio_saldo = patrimonio_credit - patrimonio_debit
        
        diferencia_final = activos_saldo - (pasivos_saldo + patrimonio_saldo)
        
        print(f"\n🏢 {company.trade_name}:")
        print(f"   Activos: ${activos_saldo}")
        print(f"   Pasivos: ${pasivos_saldo}")
        print(f"   Patrimonio: ${patrimonio_saldo}")
        print(f"   Balance: {'✅ OK' if abs(diferencia_final) < Decimal('0.01') else '❌ Desbalanceado'}")
        
    print("\n🌐 Dashboard actualizado: http://localhost:8000/dashboard/")

if __name__ == "__main__":
    try:
        create_balance_entries()
    except Exception as e:
        print(f"❌ Error ejecutando script: {e}")
        import traceback
        traceback.print_exc()