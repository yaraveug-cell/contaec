#!/usr/bin/env python3
"""
Análisis del comportamiento actual de valores por defecto en formulario de factura
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def main():
    print("🔍 ANÁLISIS DE VALORES POR DEFECTO - CREAR FACTURA")
    print("=" * 60)
    
    from apps.companies.models import PaymentMethod, Company
    from apps.accounting.models import ChartOfAccounts
    
    # 1. Analizar configuración actual de "Efectivo"
    print("💰 1. CONFIGURACIÓN DE 'EFECTIVO':")
    print("-" * 40)
    
    try:
        efectivo_method = PaymentMethod.objects.filter(
            is_active=True,
            name__icontains='efectivo'
        ).first()
        
        if efectivo_method:
            print(f"✅ Método 'Efectivo' encontrado:")
            print(f"   ID: {efectivo_method.id}")
            print(f"   Nombre: {efectivo_method.name}")
            print(f"   Cuenta padre: {efectivo_method.parent_account}")
            if efectivo_method.parent_account:
                print(f"   Código cuenta padre: {efectivo_method.parent_account.code}")
        else:
            print("❌ Método 'Efectivo' NO encontrado")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # 2. Analizar cuentas hijas de Efectivo
    print("🏦 2. CUENTAS FILTRADAS PARA 'EFECTIVO':")
    print("-" * 40)
    
    if efectivo_method and efectivo_method.parent_account:
        gueber = Company.objects.get(trade_name="GUEBER")
        parent_code = efectivo_method.parent_account.code
        
        # Simular filtro del endpoint AJAX
        child_accounts = ChartOfAccounts.objects.filter(
            company=gueber,
            code__startswith=parent_code,
            accepts_movement=True
        ).exclude(
            code=parent_code
        ).order_by('code')
        
        print(f"📋 Cuenta padre: {parent_code} - {efectivo_method.parent_account.name}")
        print(f"🎯 Cuentas hijas disponibles ({child_accounts.count()}):")
        
        for i, account in enumerate(child_accounts):
            is_first = i == 0
            marker = "👈 PRIMERA (debe ser por defecto)" if is_first else ""
            print(f"   {'✅' if is_first else '📄'} {account.code} - {account.name} {marker}")
            if is_first:
                first_account_id = account.id
                first_account_display = f"{account.code} - {account.name}"
    
    print()
    
    # 3. Estado actual del JavaScript
    print("🔧 3. COMPORTAMIENTO ACTUAL DEL JAVASCRIPT:")
    print("-" * 40)
    print("""
    ESTADO ACTUAL:
    ✅ Forma de pago se establece como "Efectivo" por defecto (Django)
    ✅ Al cargar página, JavaScript detecta valor preseleccionado  
    ✅ Aplica filtro automáticamente: filterAccountsByPayment(efectivo_id)
    ❌ Campo cuenta muestra "--- Seleccione una cuenta ---" (no preselecciona primera)
    
    PROBLEMA IDENTIFICADO:
    - updateAccountOptions() siempre crea opción vacía por defecto
    - No preselecciona automáticamente la primera cuenta filtrada
    """)
    
    # 4. Cambios necesarios
    print("🎯 4. CAMBIOS NECESARIOS:")
    print("-" * 40)
    print("""
    MODIFICACIONES REQUERIDAS:
    
    A. DJANGO (apps/invoicing/admin.py):
       ✅ YA IMPLEMENTADO: payment_form.initial = efectivo_method.id
    
    B. JAVASCRIPT (static/admin/js/simple_payment_handler.js):
       
       🆕 MODIFICAR updateAccountOptions():
       
       function updateAccountOptions(filteredAccounts, autoSelectFirst = false) {
           // Limpiar opciones existentes
           accountField.innerHTML = '';
           
           // Agregar opción por defecto
           const defaultOption = document.createElement('option');
           defaultOption.value = '';
           defaultOption.textContent = '--- Seleccione una cuenta ---';
           accountField.appendChild(defaultOption);
           
           // Agregar cuentas filtradas
           filteredAccounts.forEach((account, index) => {
               const option = document.createElement('option');
               option.value = account.id;
               option.textContent = account.display;
               
               // 🆕 NUEVO: Preseleccionar primera cuenta si autoSelectFirst=true
               if (autoSelectFirst && index === 0) {
                   option.selected = true;
               }
               
               accountField.appendChild(option);
           });
       }
       
       🆕 MODIFICAR llamada inicial:
       
       // Aplicar filtro inicial con preselección automática para nuevas facturas
       if (paymentFormField.value) {
           const isNewInvoice = !document.querySelector('input[name="id"]')?.value;
           filterAccountsByPayment(paymentFormField.value, isNewInvoice);
       }
    """)
    
    # 5. Resultado esperado
    print("🎉 5. RESULTADO ESPERADO DESPUÉS DE CAMBIOS:")
    print("-" * 40)
    
    if efectivo_method and efectivo_method.parent_account:
        print(f"""
    COMPORTAMIENTO AL CREAR NUEVA FACTURA:
    
    1. 💳 Forma de pago: "{efectivo_method.name}" (preseleccionado por Django)
    2. 🏦 Campo cuenta: Se filtra automáticamente por JavaScript
    3. ✅ Cuenta preseleccionada: "{first_account_display}" (primera del filtro)
    4. 🎯 Usuario solo necesita completar cliente y productos
    
    FLUJO MEJORADO:
    - Menos clics para el usuario
    - Configuración más intuitiva  
    - Consistente con lógica de negocio (mayoría de ventas son en efectivo)
        """)
    
    # 6. URLs de prueba
    print("🌐 6. URLS PARA PROBAR:")
    print("-" * 40)
    print("""
    ANTES DE CAMBIOS: http://localhost:8000/admin/invoicing/invoice/add/
    - Forma de pago: "Efectivo" ✅
    - Cuenta: "--- Seleccione una cuenta ---" ❌
    
    DESPUÉS DE CAMBIOS: http://localhost:8000/admin/invoicing/invoice/add/  
    - Forma de pago: "Efectivo" ✅
    - Cuenta: "1.1.01.01 - CAJA GENERAL" ✅ (primera filtrada)
    """)

if __name__ == '__main__':
    main()