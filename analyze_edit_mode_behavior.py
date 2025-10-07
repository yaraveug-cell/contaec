#!/usr/bin/env python3
"""
Análisis del comportamiento al editar facturas existentes
Verificar si se mantienen los valores seleccionados originalmente
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contaec.settings')
django.setup()

def main():
    print("🔍 ANÁLISIS - EDITAR FACTURA EXISTENTE")
    print("=" * 60)
    
    from apps.invoicing.models import Invoice
    from apps.companies.models import PaymentMethod
    
    # Buscar facturas de prueba con diferentes formas de pago
    print("📄 1. FACTURAS DE PRUEBA EXISTENTES:")
    print("-" * 40)
    
    test_invoices = Invoice.objects.filter(id__in=[99, 101]).select_related(
        'payment_form', 'account', 'company'
    ).order_by('id')
    
    for invoice in test_invoices:
        print(f"📋 Factura ID {invoice.id}:")
        print(f"   Número: {invoice.number}")
        print(f"   Estado: {invoice.status}")
        print(f"   Forma de pago: {invoice.payment_form} (ID: {invoice.payment_form.id if invoice.payment_form else 'None'})")
        print(f"   Cuenta: {invoice.account} (ID: {invoice.account.id if invoice.account else 'None'})")
        print(f"   Empresa: {invoice.company}")
        print(f"   URL editar: http://localhost:8000/admin/invoicing/invoice/{invoice.id}/change/")
        print()
    
    print("🔧 2. COMPORTAMIENTO ACTUAL DEL JAVASCRIPT:")
    print("-" * 40)
    print("""
    ESTADO ACTUAL en edit mode:
    
    A. AL CARGAR PÁGINA:
       ✅ Django renderiza valores guardados en payment_form y account
       ✅ JavaScript detecta: paymentFormField.value (tiene valor seleccionado)
       ✅ Ejecuta: filterAccountsByPayment(paymentFormField.value)
       ❓ PROBLEMA POTENCIAL: ¿Se mantiene la cuenta seleccionada después del filtro?
    
    B. FLUJO ACTUAL:
       1. Página carga con payment_form="Transferencia" y account="BANCO PICHINCHA"
       2. JavaScript detecta payment_form preseleccionado
       3. Hace AJAX para filtrar cuentas por "Transferencia"  
       4. Recibe: [BANCO INTERNACIONAL, BANCO PICHINCHA]
       5. Ejecuta: updateAccountOptions(filteredAccounts)
       6. ❌ PROBLEMA: updateAccountOptions() recrea todo el select
       7. ❌ RESULTADO: Se pierde la selección original de "BANCO PICHINCHA"
    """)
    
    print("🚨 3. PROBLEMA IDENTIFICADO:")
    print("-" * 40)
    print("""
    FUNCIÓN PROBLEMÁTICA: updateAccountOptions()
    
    Código actual:
    function updateAccountOptions(filteredAccounts) {
        // ❌ PROBLEMA: Borra todo el contenido
        accountField.innerHTML = '';
        
        // ❌ PROBLEMA: Siempre crea opción vacía por defecto
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = '--- Seleccione una cuenta ---';
        accountField.appendChild(defaultOption);
        
        // ❌ PROBLEMA: Agrega cuentas sin preservar selección original
        filteredAccounts.forEach(account => {
            const option = document.createElement('option');
            option.value = account.id;
            option.textContent = account.display;
            // ❌ FALTA: option.selected = ?
            accountField.appendChild(option);
        });
    }
    
    CONSECUENCIA:
    - Al editar factura, se pierde la cuenta seleccionada originalmente
    - Usuario ve "--- Seleccione una cuenta ---" en lugar del valor guardado
    """)
    
    print("🎯 4. SOLUCIÓN NECESARIA:")
    print("-" * 40)
    print("""
    MODIFICACIONES REQUERIDAS:
    
    A. PRESERVAR VALOR ORIGINAL AL FILTRAR:
    
    function updateAccountOptions(filteredAccounts, preserveSelection = true) {
        // 🆕 NUEVO: Capturar selección actual antes de limpiar
        const currentSelection = preserveSelection ? accountField.value : '';
        
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
            
            // 🆕 NUEVO: Preservar selección original si existe
            if (preserveSelection && currentSelection && account.id == currentSelection) {
                option.selected = true;
            }
            // 🆕 NUEVO: Auto-seleccionar primera para facturas nuevas
            else if (!preserveSelection && index === 0) {
                option.selected = true;  
            }
            
            accountField.appendChild(option);
        });
        
        // 🆕 NUEVO: Log para debugging
        if (currentSelection) {
            console.log(`🔄 Selección preservada: ${currentSelection}`);
        }
    }
    
    B. DETECTAR CONTEXTO (NUEVA vs EDITAR):
    
    // Detectar si es nueva factura o edición
    const isNewInvoice = !document.querySelector('input[name="id"]')?.value;
    
    // Aplicar filtro con comportamiento contextual
    if (paymentFormField.value) {
        if (isNewInvoice) {
            // Para nuevas: auto-seleccionar primera cuenta filtrada
            filterAccountsByPayment(paymentFormField.value, false); // preserveSelection = false
        } else {
            // Para edición: preservar selección original
            filterAccountsByPayment(paymentFormField.value, true); // preserveSelection = true
        }
    }
    """)
    
    print("🧪 5. CASOS DE PRUEBA:")
    print("-" * 40)
    
    for invoice in test_invoices:
        if invoice.payment_form and invoice.account:
            print(f"📋 Factura {invoice.id}:")
            print(f"   ANTES: payment_form='{invoice.payment_form}' + account='{invoice.account}'")
            print(f"   DEBE: Mostrar ambos valores preservados después del filtro JavaScript")
            print(f"   URL: http://localhost:8000/admin/invoicing/invoice/{invoice.id}/change/")
            print()
    
    print("🎪 6. COMPORTAMIENTO ESPERADO DESPUÉS DE CAMBIOS:")
    print("-" * 40)
    print("""
    ESCENARIOS:
    
    A. CREAR NUEVA FACTURA:
       1. payment_form = "Efectivo" (Django por defecto)
       2. JavaScript filtra y auto-selecciona primera cuenta de caja
       3. Resultado: Ambos campos preseleccionados automáticamente
    
    B. EDITAR FACTURA EXISTENTE (ej. ID 101):
       1. payment_form = "Transferencia" (valor guardado)
       2. account = "BANCO PICHINCHA" (valor guardado)  
       3. JavaScript filtra por transferencia pero preserva "BANCO PICHINCHA"
       4. Resultado: Ambos campos muestran valores originales
    
    C. CAMBIAR FORMA DE PAGO EN EDICIÓN:
       1. Usuario cambia de "Transferencia" a "Efectivo"
       2. JavaScript filtra cuentas de caja
       3. Campo cuenta se resetea a primera opción (comportamiento normal)
    """)
    
    print("⚠️  7. VALIDACIÓN CRÍTICA:")
    print("-" * 40)
    print("""
    ASEGURARSE QUE:
    
    ✓ Facturas nuevas: Auto-selección inteligente
    ✓ Facturas existentes: Preservación de valores originales  
    ✓ Cambios manuales: Funcionamiento normal del filtro
    ✓ Compatibilidad: No romper funcionalidad existente
    
    PRUEBAS NECESARIAS:
    1. Crear nueva factura → Verificar auto-selección
    2. Editar factura existente → Verificar preservación  
    3. Cambiar forma de pago → Verificar filtro normal
    """)

if __name__ == '__main__':
    main()