/**
 * Handler para integración Banking-Invoicing
 * Muestra cuentas bancarias disponibles cuando se selecciona "Transferencia"
 * Version: 1.0 - Implementación cuidadosa sin afectar funcionalidad existente
 */

class BankingInvoiceIntegration {
    constructor() {
        this.paymentFormField = null;
        this.accountField = null;
        this.bankAccountField = null;
        this.isBankAccountFieldCreated = false;
        this.transferDetailHandler = null;
        this.currentUserCompanyId = null;
        this.init();
    }

    init() {
        console.log('🏦 BankingInvoiceIntegration: Iniciando...');
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    isInvoiceForm() {
        const currentPath = window.location.pathname;
        return currentPath.includes('/admin/invoicing/invoice/');
    }

    setup() {
        if (!this.isInvoiceForm()) {
            console.log('ℹ️ No es formulario de factura, cancelando inicialización banking integration.');
            return;
        }

        // Buscar campos necesarios
        this.paymentFormField = document.getElementById('id_payment_form');
        this.accountField = document.getElementById('id_account');
        
        if (!this.paymentFormField || !this.accountField) {
            console.log('⚠️ Campos payment_form o account no encontrados, reintentando...');
            setTimeout(() => this.setup(), 500);
            return;
        }

        console.log('✅ Campos encontrados, configurando eventos...');
        
        // Obtener empresa del usuario para filtrar cuentas bancarias
        this.getCurrentUserCompany();
        
        // Configurar eventos
        this.bindEvents();
        
        // Verificar estado inicial
        this.checkInitialState();
    }

    getCurrentUserCompany() {
        // Intentar obtener company_id desde el formulario
        const companyField = document.getElementById('id_company');
        if (companyField && companyField.value) {
            this.currentUserCompanyId = companyField.value;
            console.log('🏢 Company ID obtenido del formulario:', this.currentUserCompanyId);
        } else {
            // Fallback: Obtener via AJAX si no está en el formulario
            this.fetchUserCompany();
        }
    }

    async fetchUserCompany() {
        try {
            // Usar la vista AJAX existente para obtener configuración de empresa
            const response = await fetch('/admin/invoicing/invoice/company_config/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.company_id) {
                    this.currentUserCompanyId = data.company_id;
                    console.log('🏢 Company ID obtenido via AJAX:', this.currentUserCompanyId);
                }
            }
        } catch (error) {
            console.warn('⚠️ Error obteniendo company ID:', error);
            // Continuar sin company_id (mostrará todas las cuentas bancarias)
        }
    }

    bindEvents() {
        this.paymentFormField.addEventListener('change', (e) => {
            const selectedText = e.target.options[e.target.selectedIndex]?.text || '';
            console.log('💳 Payment form cambiado a:', selectedText);
            this.handlePaymentChange(selectedText, e.target.value);
        });
    }

    checkInitialState() {
        const selectedText = this.paymentFormField.options[this.paymentFormField.selectedIndex]?.text || '';
        const selectedValue = this.paymentFormField.value;
        
        if (selectedText.toLowerCase().includes('transferencia')) {
            console.log('🔄 Transferencia ya seleccionada, mostrando selector bancario...');
            this.showBankAccountSelector(selectedValue);
        }
    }

    handlePaymentChange(selectedText, selectedValue) {
        if (selectedText.toLowerCase().includes('transferencia')) {
            this.showBankAccountSelector(selectedValue);
        } else {
            this.hideBankAccountSelector();
        }
    }

    async showBankAccountSelector(paymentMethodId) {
        if (this.isBankAccountFieldCreated) {
            console.log('📱 Selector bancario ya existe, haciéndolo visible...');
            this.bankAccountField.style.display = 'inline-block';
            return;
        }

        console.log('🏗️ Creando selector de cuenta bancaria...');
        
        // Cargar cuentas bancarias disponibles
        const bankAccounts = await this.fetchBankAccounts();
        
        if (!bankAccounts || bankAccounts.length === 0) {
            console.log('⚠️ No se encontraron cuentas bancarias disponibles');
            this.showNoBankAccountsMessage();
            return;
        }

        this.createBankAccountSelector(bankAccounts);
    }

    async fetchBankAccounts() {
        try {
            const url = '/admin/invoicing/invoice/bank-accounts/' + 
                       (this.currentUserCompanyId ? `?company_id=${this.currentUserCompanyId}` : '');
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('🏦 Cuentas bancarias obtenidas:', data);
            return data.bank_accounts || [];
            
        } catch (error) {
            console.error('❌ Error obteniendo cuentas bancarias:', error);
            return [];
        }
    }

    createBankAccountSelector(bankAccounts) {
        // Buscar la fila que contiene los campos de pago
        const accountRow = this.accountField.closest('.form-row');
        if (!accountRow) {
            console.error('❌ No se encontró la fila del formulario para account');
            return;
        }

        // Crear contenedor para el selector
        const bankAccountDiv = document.createElement('div');
        bankAccountDiv.className = 'field-box field-bank_account';
        bankAccountDiv.style.cssText = `
            display: inline-block;
            margin-left: 15px;
            vertical-align: top;
        `;

        // Label
        const label = document.createElement('label');
        label.textContent = 'Cuenta Bancaria:';
        label.className = 'required';
        label.htmlFor = 'id_bank_account';
        label.style.cssText = `
            font-weight: bold;
            color: #666666;
            font-size: 11px;
            text-transform: uppercase;
            font-family: "Roboto", "Lucida Grande", Verdana, Arial, sans-serif;
            display: block;
            margin-bottom: 5px;
        `;

        // Select dropdown
        const select = document.createElement('select');
        select.name = 'bank_account';
        select.id = 'id_bank_account';
        select.className = 'admin-autocomplete';
        select.style.cssText = `
            width: 300px;
            height: 30px;
            padding: 5px 8px;
            border: 1px solid #cccccc;
            border-radius: 4px;
            font-size: 13px;
            color: #333333;
            font-family: "Roboto", "Lucida Grande", Verdana, Arial, sans-serif;
            background-color: #ffffff;
        `;

        // Opción vacía
        const emptyOption = document.createElement('option');
        emptyOption.value = '';
        emptyOption.textContent = '--- Seleccionar cuenta bancaria ---';
        select.appendChild(emptyOption);

        // Agregar opciones de cuentas bancarias
        bankAccounts.forEach(account => {
            const option = document.createElement('option');
            option.value = account.id;
            option.dataset.chartAccountId = account.chart_account_id;
            option.dataset.chartAccountCode = account.chart_account_code;
            option.dataset.chartAccountName = account.chart_account_name;
            option.textContent = `${account.bank_name} - ${account.account_type_display} - ****${account.account_number.slice(-4)}`;
            select.appendChild(option);
        });

        // Evento de cambio para auto-asignar cuenta contable
        select.addEventListener('change', (e) => {
            const selectedOption = e.target.options[e.target.selectedIndex];
            if (selectedOption && selectedOption.dataset.chartAccountId) {
                this.autoAssignChartAccount(selectedOption);
            } else {
                // Limpiar campo account si no hay selección
                this.accountField.value = '';
            }
        });

        // Ensamblar campo
        bankAccountDiv.appendChild(label);
        bankAccountDiv.appendChild(select);

        // Insertar después del campo account
        const accountFieldBox = this.accountField.closest('.field-box');
        if (accountFieldBox && accountFieldBox.parentNode) {
            accountFieldBox.parentNode.insertBefore(bankAccountDiv, accountFieldBox.nextSibling);
        } else {
            accountRow.appendChild(bankAccountDiv);
        }

        this.bankAccountField = bankAccountDiv;
        this.isBankAccountFieldCreated = true;

        console.log('✅ Selector de cuenta bancaria creado exitosamente');
    }

    autoAssignChartAccount(selectedOption) {
        const chartAccountId = selectedOption.dataset.chartAccountId;
        const chartAccountCode = selectedOption.dataset.chartAccountCode;
        const chartAccountName = selectedOption.dataset.chartAccountName;
        
        if (chartAccountId && this.accountField) {
            // Auto-asignar en el campo account
            this.accountField.value = chartAccountId;
            
            console.log('✅ Cuenta contable auto-asignada:', {
                id: chartAccountId,
                code: chartAccountCode,
                name: chartAccountName
            });
            
            // Mostrar mensaje de confirmación
            this.showAutoAssignMessage(chartAccountCode, chartAccountName);
            
            // Disparar evento change para notificar otros handlers
            const changeEvent = new Event('change', { bubbles: true });
            this.accountField.dispatchEvent(changeEvent);
        }
    }

    showAutoAssignMessage(code, name) {
        const messageDiv = document.createElement('div');
        messageDiv.style.cssText = `
            position: fixed;
            top: 60px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            font-size: 12px;
            font-family: "Roboto", sans-serif;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 10000;
            max-width: 400px;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        messageDiv.innerHTML = `
            <strong>✅ Cuenta asignada automáticamente:</strong><br>
            ${code} - ${name}
        `;
        
        document.body.appendChild(messageDiv);
        
        setTimeout(() => messageDiv.style.opacity = '1', 100);
        
        setTimeout(() => {
            messageDiv.style.opacity = '0';
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.parentNode.removeChild(messageDiv);
                }
            }, 300);
        }, 4000);
    }

    showNoBankAccountsMessage() {
        const messageDiv = document.createElement('div');
        messageDiv.style.cssText = `
            position: fixed;
            top: 60px;
            right: 20px;
            background: #ffc107;
            color: #333;
            padding: 10px 15px;
            border-radius: 5px;
            font-size: 12px;
            font-family: "Roboto", sans-serif;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 10000;
            max-width: 400px;
        `;
        messageDiv.innerHTML = `
            <strong>⚠️ No hay cuentas bancarias configuradas</strong><br>
            Vaya a <em>Banking → Bank accounts</em> para crear cuentas bancarias.
        `;
        
        document.body.appendChild(messageDiv);
        
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 6000);
    }

    hideBankAccountSelector() {
        if (this.isBankAccountFieldCreated && this.bankAccountField) {
            console.log('🙈 Ocultando selector de cuenta bancaria...');
            this.bankAccountField.style.display = 'none';
            
            // Limpiar selección
            const select = this.bankAccountField.querySelector('select');
            if (select) {
                select.value = '';
            }
            
            // NO limpiar el campo account para mantener compatibilidad
            // El usuario puede haber seleccionado una cuenta manualmente
        }
    }

    getCSRFToken() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfInput ? csrfInput.value : '';
    }
}

// Inicializar solo si no existe ya
if (!window.bankingInvoiceIntegration) {
    function initBankingInvoiceIntegration() {
        const isInvoicePage = document.querySelector('#invoice_form') || 
                             window.location.pathname.includes('/invoicing/invoice/');
        
        if (isInvoicePage) {
            console.log('🎯 Inicializando BankingInvoiceIntegration...');
            window.bankingInvoiceIntegration = new BankingInvoiceIntegration();
            console.log('✅ BankingInvoiceIntegration inicializado');
        }
    }

    // Ejecutar cuando DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initBankingInvoiceIntegration);
    } else {
        initBankingInvoiceIntegration();
    }
}

// Exportar para acceso global
window.BankingInvoiceIntegration = BankingInvoiceIntegration;