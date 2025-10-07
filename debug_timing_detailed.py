#!/usr/bin/env python3
"""
Diagnóstico detallado de timing y estado de campos en factura ID 99
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from apps.invoicing.models import Invoice
from apps.accounting.models import ChartOfAccounts

def main():
    print("🔍 DIAGNÓSTICO DETALLADO - TIMING Y ESTADO")
    print("=" * 60)
    
    try:
        # Obtener factura
        invoice = Invoice.objects.get(id=99)
        print(f"📄 Factura ID: {invoice.id}")
        print(f"Número: {invoice.number}")
        print(f"Forma de pago: {invoice.payment_form}")
        print()
        
        # Estado de campos críticos
        print("🎯 CAMPOS CRÍTICOS:")
        print(f"Account (Django): {invoice.account}")
        if invoice.account:
            print(f"   ID: {invoice.account.id}")
            print(f"   Código: {invoice.account.code}")
            print(f"   Nombre: {invoice.account.name}")
        
        print(f"Bank observations: {bool(invoice.bank_observations)}")
        if invoice.bank_observations:
            print(f"   Contenido: {invoice.bank_observations[:100]}...")
            
        print(f"Transfer detail: {bool(invoice.transfer_detail)}")
        print()
        
        # Verificar si la forma de pago es transferencia
        print("💳 ANÁLISIS FORMA DE PAGO:")
        if invoice.payment_form:
            print(f"Método seleccionado: {invoice.payment_form}")
            is_transfer = 'transfer' in invoice.payment_form.name.lower()
            print(f"¿Es transferencia?: {is_transfer}")
        else:
            print("⚠️ No hay forma de pago seleccionada")
        print()
        
        # Buscar cuentas bancarias relacionadas
        print("🏦 CUENTAS BANCARIAS DISPONIBLES:")
        from apps.banking.models import BankAccount
        bank_accounts = BankAccount.objects.filter(company=invoice.company)
        
        for bank_acc in bank_accounts:
            is_selected = (invoice.account and 
                          bank_acc.chart_account and 
                          bank_acc.chart_account.id == invoice.account.id)
            
            print(f"   {'✅' if is_selected else '⭕'} {bank_acc.bank} - {bank_acc.account_number}")
            print(f"      Chart Account ID: {bank_acc.chart_account.id if bank_acc.chart_account else 'None'}")
            print(f"      Account Code: {bank_acc.chart_account.code if bank_acc.chart_account else 'None'}")
            
        print()
        
        # Estado esperado del JavaScript
        print("🔧 ESTADO ESPERADO EN JAVASCRIPT:")
        print(f"originalAccountValue: {invoice.account.id if invoice.account else 'null'}")
        print(f"Selector bancario debe mostrar: {invoice.account.code if invoice.account else 'Seleccionar cuenta bancaria'}")
        print(f"Textarea observaciones debe tener: {len(invoice.bank_observations) if invoice.bank_observations else 0} caracteres")
        
        # Generar URL de prueba
        print()
        print("🌐 URL DE PRUEBA:")
        print(f"http://localhost:8000/admin/invoicing/invoice/{invoice.id}/change/")
        
        # Datos para verificar en consola JavaScript
        print()
        print("🧪 VERIFICACIONES JAVASCRIPT (copiar a consola):")
        print("// Verificar campo account oculto:")
        print("document.getElementById('id_account').value")
        print()
        print("// Verificar campo bank_observations oculto:")
        print("document.querySelector('input[name=\"bank_observations\"]')?.value")
        print()
        print("// Verificar selector bancario:")
        print("document.getElementById('unified_bank_select')?.value")
        print()
        print("// Verificar textarea observaciones:")
        print("document.getElementById('bank_observations')?.value")
        
    except Invoice.DoesNotExist:
        print("❌ Factura ID 99 no encontrada")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()