/**
 * Filtro en Cascada: Forma de Pago → Cuenta Contable
 * Implementación cuidadosa y robusta
 */

document.addEventListener('DOMContentLoaded', function() {
    const paymentFormField = document.getElementById('id_payment_form');
    const accountField = document.getElementById('id_account');
    const companyField = document.getElementById('id_company');
    
    if (!paymentFormField || !accountField) {
        return;
    }
    
    // Guardar opciones originales de account
    let originalAccountOptions = [];
    Array.from(accountField.options).forEach(option => {
        originalAccountOptions.push({
            value: option.value,
            text: option.textContent,
            selected: option.selected
        });
    });
    
    // Función para filtrar cuentas por forma de pago
    async function filterAccountsByPayment(paymentMethodId, preserveSelection = true) {
        if (!paymentMethodId) {
            // Restaurar todas las opciones originales
            restoreAllAccountOptions();
            return;
        }
        
        try {
            const companyId = companyField ? companyField.value : null;
            const url = new URL('/admin/invoicing/invoice/filter-accounts-by-payment/', window.location.origin);
            url.searchParams.append('payment_method_id', paymentMethodId);
            if (companyId) {
                url.searchParams.append('company_id', companyId);
            }
            
            // Filtrar cuentas por forma de pago
            
            const response = await fetch(url.toString(), {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                console.error('❌ Error del servidor:', data.error);
                restoreAllAccountOptions();
                return;
            }
            
            console.log(`✅ Recibidas ${data.count} cuentas filtradas para ${data.payment_method}`);
            console.log(`📋 Cuenta padre: ${data.parent_account}`);
            
            // Actualizar opciones del select con preservación de selección
            updateAccountOptions(data.accounts, preserveSelection);
            
        } catch (error) {
            console.error('❌ Error al filtrar cuentas:', error);
            restoreAllAccountOptions();
        }
    }
    
    // Función para actualizar las opciones del campo account
    function updateAccountOptions(filteredAccounts, preserveSelection = true) {
        // Capturar selección actual antes de limpiar (solo si se debe preservar)
        const currentSelection = preserveSelection ? accountField.value : '';
        console.log(`🔍 Selección actual capturada: "${currentSelection}"`);
        
        // Limpiar opciones existentes
        accountField.innerHTML = '';
        
        // Agregar opción por defecto
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = '--- Seleccione una cuenta ---';
        accountField.appendChild(defaultOption);
        
        // Variables para tracking de selección
        let selectionRestored = false;
        let autoSelectedFirst = false;
        
        // Agregar cuentas filtradas
        filteredAccounts.forEach((account, index) => {
            const option = document.createElement('option');
            option.value = account.id;
            option.textContent = account.display;
            
            // Lógica de selección
            if (preserveSelection && currentSelection && account.id == currentSelection) {
                // CASO 1: Preservar selección existente (modo edición)
                option.selected = true;
                selectionRestored = true;
                console.log(`✅ Selección preservada: ${account.display}`);
            } else if (!preserveSelection && !autoSelectedFirst && index === 0 && filteredAccounts.length > 0) {
                // CASO 2: Auto-seleccionar primera opción (modo creación)
                option.selected = true;
                autoSelectedFirst = true;
                console.log(`🎯 Primera cuenta auto-seleccionada: ${account.display}`);
            }
            
            accountField.appendChild(option);
        });
        
        // Logging para debugging
        if (preserveSelection && currentSelection && !selectionRestored) {
            console.log(`⚠️ No se pudo restaurar selección "${currentSelection}" - puede no estar en el filtro`);
        } else if (!preserveSelection && !autoSelectedFirst && filteredAccounts.length > 0) {
            console.log(`⚠️ No se auto-seleccionó primera cuenta - verificar lógica`);
        }
        
        console.log(`📝 Campo account actualizado: ${filteredAccounts.length} opciones, preservar=${preserveSelection}`);
    }
    
    // Función para restaurar todas las opciones originales
    function restoreAllAccountOptions() {
        accountField.innerHTML = '';
        
        originalAccountOptions.forEach(optionData => {
            const option = document.createElement('option');
            option.value = optionData.value;
            option.textContent = optionData.text;
            option.selected = optionData.selected;
            accountField.appendChild(option);
        });
        
        console.log('🔄 Opciones originales de account restauradas');
    }
    
    // Event listener para cambio de forma de pago
    paymentFormField.addEventListener('change', function() {
        const selectedValue = this.value;
        const selectedOption = this.options[this.selectedIndex];
        const selectedText = selectedOption ? selectedOption.textContent : '';
        
        console.log('💳 Forma de pago cambiada manualmente:', { value: selectedValue, text: selectedText });
        
        // Para cambios manuales, no preservar selección (comportamiento normal del filtro)
        filterAccountsByPayment(selectedValue, false);
        
        // Coordinación con BankObservationsHandler
        setTimeout(() => {
            if (window.BankObservationsHandler) {
                console.log('🔄 Notificando cambio a BankObservationsHandler');
                window.BankObservationsHandler.handlePaymentFormChange();
            }
        }, 150);
    });
    
    // Aplicar filtro inicial si ya hay una forma de pago seleccionada
    if (paymentFormField.value) {
        // Detectar si es nueva factura o edición existente
        const invoiceIdField = document.querySelector('input[name="id"]');
        const isNewInvoice = !invoiceIdField || !invoiceIdField.value;
        
        console.log('🔄 Aplicando filtro inicial para forma de pago preseleccionada');
        console.log(`📋 Contexto detectado: ${isNewInvoice ? 'NUEVA factura' : 'EDITAR factura'}`);
        
        if (isNewInvoice) {
            // Para facturas nuevas: auto-seleccionar primera cuenta filtrada
            filterAccountsByPayment(paymentFormField.value, false);
        } else {
            // Para facturas existentes: preservar selección original
            filterAccountsByPayment(paymentFormField.value, true);
        }
    }
    
    console.log('🎉 Filtro en cascada configurado exitosamente');
});