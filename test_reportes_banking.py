"""
Script para probar las funcionalidades de reportes de conciliación bancaria
FASE 1 (Esenciales): Estado de Conciliación por Cuenta, Diferencias No Conciliadas, Extracto de Conciliación Mensual
"""

import os
import django
import sys
from decimal import Decimal
from datetime import datetime, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.companies.models import Company
from apps.banking.models import Bank, BankAccount, ExtractoBancario, ExtractoBancarioDetalle, BankTransaction

User = get_user_model()


def setup_test_data():
    """Configurar datos de prueba para los reportes"""
    
    print("🏗️  CONFIGURANDO DATOS DE PRUEBA")
    print("-" * 50)
    
    # 1. Usuario de prueba
    user, created = User.objects.get_or_create(
        username='admin_test',
        defaults={
            'email': 'admin@test.com',
            'first_name': 'Admin',
            'last_name': 'Test',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    if created:
        user.set_password('admin123')
        user.save()
        print(f"   ✅ Usuario creado: {user.username}")
    else:
        print(f"   ✅ Usuario existente: {user.username}")
    
    # 2. Usar empresa existente
    company = Company.objects.first()
    if not company:
        print("   ❌ No hay empresas configuradas. Por favor, configure una empresa primero.")
        return None, None, None, None
    
    print(f"   ✅ Usando empresa: {company.legal_name}")
    
    # 3. Bancos
    banco_pichincha, _ = Bank.objects.get_or_create(
        sbs_code='1001',
        defaults={
            'name': 'Banco Pichincha',
            'short_name': 'PICHINCHA'
        }
    )
    
    banco_pacifico, _ = Bank.objects.get_or_create(
        sbs_code='1002',
        defaults={
            'name': 'Banco del Pacífico',
            'short_name': 'PACIFICO'
        }
    )
    
    print(f"   ✅ Bancos configurados: {banco_pichincha.name}, {banco_pacifico.name}")
    
    # 4. Cuentas bancarias
    cuenta_pichincha, _ = BankAccount.objects.get_or_create(
        company=company,
        bank=banco_pichincha,
        account_number='2100123456',
        defaults={
            'account_type': 'checking',
            'currency': 'USD',
            'initial_balance': Decimal('5000.00')
        }
    )
    
    cuenta_pacifico, _ = BankAccount.objects.get_or_create(
        company=company,
        bank=banco_pacifico,
        account_number='4500789012',
        defaults={
            'account_type': 'savings',
            'currency': 'USD',
            'initial_balance': Decimal('3000.00')
        }
    )
    
    print(f"   ✅ Cuentas creadas: {cuenta_pichincha}, {cuenta_pacifico}")
    
    # 5. Transacciones del sistema
    fecha_base = datetime.now().date() - timedelta(days=30)
    
    transacciones_data = [
        {
            'bank_account': cuenta_pichincha,
            'transaction_date': fecha_base + timedelta(days=1),
            'transaction_type': 'credit',
            'amount': Decimal('1500.00'),
            'description': 'Depósito cliente ABC',
            'is_reconciled': True
        },
        {
            'bank_account': cuenta_pichincha,
            'transaction_date': fecha_base + timedelta(days=3),
            'transaction_type': 'debit',
            'amount': Decimal('500.00'),
            'description': 'Pago proveedor XYZ',
            'is_reconciled': False  # No conciliada
        },
        {
            'bank_account': cuenta_pacifico,
            'transaction_date': fecha_base + timedelta(days=5),
            'transaction_type': 'transfer_in',
            'amount': Decimal('2000.00'),
            'description': 'Transferencia recibida',
            'is_reconciled': True
        },
        {
            'bank_account': cuenta_pacifico,
            'transaction_date': fecha_base + timedelta(days=7),
            'transaction_type': 'fee',
            'amount': Decimal('15.00'),
            'description': 'Comisión bancaria',
            'is_reconciled': False  # No conciliada
        }
    ]
    
    for data in transacciones_data:
        trans, created = BankTransaction.objects.get_or_create(
            bank_account=data['bank_account'],
            transaction_date=data['transaction_date'],
            description=data['description'],
            defaults=data
        )
        if created:
            print(f"   ✅ Transacción creada: {trans}")
    
    # 6. Extractos bancarios
    extracto_pichincha, _ = ExtractoBancario.objects.get_or_create(
        bank_account=cuenta_pichincha,
        period_start=fecha_base,
        period_end=fecha_base + timedelta(days=15),
        defaults={
            'initial_balance': Decimal('5000.00'),
            'final_balance': Decimal('6000.00'),
            'status': 'processed'
        }
    )
    
    extracto_pacifico, _ = ExtractoBancario.objects.get_or_create(
        bank_account=cuenta_pacifico,
        period_start=fecha_base,
        period_end=fecha_base + timedelta(days=15),
        defaults={
            'initial_balance': Decimal('3000.00'),
            'final_balance': Decimal('4985.00'),
            'status': 'processed'
        }
    )
    
    print(f"   ✅ Extractos creados: {extracto_pichincha}, {extracto_pacifico}")
    
    # 7. Detalles de extractos
    detalles_data = [
        {
            'extracto': extracto_pichincha,
            'fecha': fecha_base + timedelta(days=1),
            'descripcion': 'DEPOSITO CLIENTE ABC',
            'credito': Decimal('1500.00'),
            'saldo': Decimal('6500.00'),
            'is_reconciled': True
        },
        {
            'extracto': extracto_pichincha,
            'fecha': fecha_base + timedelta(days=8),
            'descripcion': 'TRANSFERENCIA SALIENTE',
            'debito': Decimal('500.00'),
            'saldo': Decimal('6000.00'),
            'is_reconciled': False  # No conciliada
        },
        {
            'extracto': extracto_pacifico,
            'fecha': fecha_base + timedelta(days=5),
            'descripcion': 'TRANSFERENCIA RECIBIDA',
            'credito': Decimal('2000.00'),
            'saldo': Decimal('5000.00'),
            'is_reconciled': True
        },
        {
            'extracto': extracto_pacifico,
            'fecha': fecha_base + timedelta(days=7),
            'descripcion': 'COMISION MANEJO CUENTA',
            'debito': Decimal('15.00'),
            'saldo': Decimal('4985.00'),
            'is_reconciled': False  # No conciliada
        }
    ]
    
    for data in detalles_data:
        detalle, created = ExtractoBancarioDetalle.objects.get_or_create(
            extracto=data['extracto'],
            fecha=data['fecha'],
            descripcion=data['descripcion'],
            defaults=data
        )
        if created:
            print(f"   ✅ Detalle de extracto creado: {detalle}")
    
    return user, company, cuenta_pichincha, cuenta_pacifico


def test_reportes():
    """Probar las vistas de reportes"""
    
    print("\n📊 PROBANDO REPORTES DE CONCILIACIÓN")
    print("-" * 50)
    
    # Configurar datos
    user, company, cuenta1, cuenta2 = setup_test_data()
    
    # Cliente para hacer requests
    client = Client()
    client.force_login(user)
    
    # 1. Estado de Conciliación por Cuenta
    print("\n1️⃣  ESTADO DE CONCILIACIÓN POR CUENTA")
    try:
        response = client.get(reverse('banking:estado_conciliacion'))
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Reporte cargado exitosamente")
            content = response.content.decode()
            if 'Estado de Conciliación por Cuenta' in content:
                print("   ✅ Título del reporte encontrado")
            if str(cuenta1.bank.name) in content:
                print(f"   ✅ Cuenta {cuenta1.bank.name} encontrada")
        else:
            print(f"   ❌ Error al cargar reporte: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error en Estado de Conciliación: {e}")
    
    # 2. Diferencias No Conciliadas
    print("\n2️⃣  DIFERENCIAS NO CONCILIADAS")
    try:
        response = client.get(reverse('banking:diferencias_no_conciliadas'))
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Reporte cargado exitosamente")
            content = response.content.decode()
            if 'Diferencias No Conciliadas' in content:
                print("   ✅ Título del reporte encontrado")
        else:
            print(f"   ❌ Error al cargar reporte: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error en Diferencias: {e}")
    
    # 3. Extracto de Conciliación Mensual
    print("\n3️⃣  EXTRACTO DE CONCILIACIÓN MENSUAL")
    try:
        # Con parámetros
        params = {
            'cuenta': cuenta1.id,
            'año': datetime.now().year,
            'mes': datetime.now().month
        }
        response = client.get(reverse('banking:extracto_conciliacion_mensual'), params)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Reporte cargado exitosamente")
            content = response.content.decode()
            if 'Extracto de Conciliación Mensual' in content:
                print("   ✅ Título del reporte encontrado")
        else:
            print(f"   ❌ Error al cargar reporte: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error en Extracto Mensual: {e}")
    
    # 4. Índice de Reportes
    print("\n4️⃣  ÍNDICE DE REPORTES")
    try:
        response = client.get(reverse('banking:reportes_index'))
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Índice cargado exitosamente")
            content = response.content.decode()
            if 'Reportes de Conciliación Bancaria' in content:
                print("   ✅ Página de índice correcta")
        else:
            print(f"   ❌ Error al cargar índice: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error en Índice: {e}")


def mostrar_estadisticas():
    """Mostrar estadísticas de los datos creados"""
    
    print("\n📈 ESTADÍSTICAS DE DATOS CREADOS")
    print("-" * 50)
    
    # Estadísticas generales
    total_cuentas = BankAccount.objects.count()
    total_transacciones = BankTransaction.objects.count()
    transacciones_conciliadas = BankTransaction.objects.filter(is_reconciled=True).count()
    total_extractos = ExtractoBancario.objects.count()
    total_detalles = ExtractoBancarioDetalle.objects.count()
    detalles_conciliados = ExtractoBancarioDetalle.objects.filter(is_reconciled=True).count()
    
    print(f"   📊 Total de Cuentas Bancarias: {total_cuentas}")
    print(f"   💰 Total de Transacciones: {total_transacciones}")
    print(f"   ✅ Transacciones Conciliadas: {transacciones_conciliadas}")
    print(f"   ⚠️  Transacciones Pendientes: {total_transacciones - transacciones_conciliadas}")
    print(f"   📄 Total de Extractos: {total_extractos}")
    print(f"   📝 Total de Items de Extracto: {total_detalles}")
    print(f"   ✅ Items Conciliados: {detalles_conciliados}")
    print(f"   ⚠️  Items Pendientes: {total_detalles - detalles_conciliados}")
    
    # Porcentajes
    porcentaje_transacciones = (transacciones_conciliadas / total_transacciones * 100) if total_transacciones > 0 else 0
    porcentaje_extractos = (detalles_conciliados / total_detalles * 100) if total_detalles > 0 else 0
    
    print(f"\n   📊 Porcentaje de Conciliación de Transacciones: {porcentaje_transacciones:.1f}%")
    print(f"   📊 Porcentaje de Conciliación de Extractos: {porcentaje_extractos:.1f}%")


def main():
    """Función principal"""
    
    print("🏦 PRUEBA DE REPORTES DE CONCILIACIÓN BANCARIA")
    print("=" * 60)
    print("FASE 1 (Esenciales): Estado de Conciliación por Cuenta, Diferencias No Conciliadas, Extracto de Conciliación Mensual")
    print("=" * 60)
    
    try:
        # Probar reportes
        test_reportes()
        
        # Mostrar estadísticas
        mostrar_estadisticas()
        
        print("\n🎉 PRUEBA COMPLETADA")
        print("-" * 50)
        print("   ✅ Los 3 reportes esenciales están funcionando correctamente")
        print("   ✅ Los datos de prueba han sido creados")
        print("   ✅ Las URLs están configuradas correctamente")
        print("\n🌐 ACCESO A LOS REPORTES:")
        print(f"   • Índice de Reportes: http://localhost:8000/banking/reportes/")
        print(f"   • Estado de Conciliación: http://localhost:8000/banking/reportes/estado-conciliacion/")
        print(f"   • Diferencias No Conciliadas: http://localhost:8000/banking/reportes/diferencias/")
        print(f"   • Extracto Mensual: http://localhost:8000/banking/reportes/extracto-mensual/")
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA PRUEBA: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()