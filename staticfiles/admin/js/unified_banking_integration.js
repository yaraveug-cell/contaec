/**
 * Handler UNIFICADO para integración Banking-Invoicing
 * Reemplaza transfer_detail_handler.js y banking_invoice_integration.js
 * Muestra selector de cuentas bancarias estructurado + campo observaciones opcional
 * Version: 2.0 - Unificación cuidadosa sin afectar funcionalidad existente
 */

class UnifiedBankingIntegration {
    constructor() {
        this.paymentFormField = null;
        this.accountField = null;
        this.bankAccountField = null;
        this.observationsField = null;
        this.isBankingFieldsCreated = false;
        this.currentUserCompanyId = null;
        this.init();
    }

    init() {
        console.log('🏦 UnifiedBankingIntegration: Iniciando...');
        
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
            console.log('ℹ️ No es formulario de factura, cancelando inicialización unified banking.');
            return;
        }

        // Buscar campos necesarios
        this.paymentFormField = document.getElementById('id_payment_form');
        this.accountField = document.getElementById('id_account');
        
        // DEBUG: Verificar si hay múltiples campos con el mismo ID
        const allAccountFields = document.querySelectorAll('#id_account, [name="account"]');
        console.log('🔍 DEBUG: Campos con ID/name "account":', allAccountFields.length);
        allAccountFields.forEach((field, index) => {
            console.log(`   Campo ${index + 1}: value="${field.value}", id="${field.id}", name="${field.name}"`);
        });
        
        if (!this.paymentFormField || !this.accountField) {
            console.log('⚠️ Campos payment_form o account no encontrados, reintentando...');
            setTimeout(() => this.setup(), 500);
            return;
        }

        console.log('✅ Campos encontrados, configurando eventos unificados...');
        
        // Obtener empresa del usuario para filtrar cuentas bancarias
        this.getCurrentUserCompany();
        
        // Configurar eventos
        this.bindEvents();
        
        // Verificar estado inicial
        this.checkInitialState();
    }

    getCurrentUserCompany() {
        const companyField = document.getElementById('id_company');
        if (companyField && companyField.value) {
            this.currentUserCompanyId = companyField.value;
            console.log('🏢 Company ID obtenido del formulario:', this.currentUserCompanyId);
        }
    }

    bindEvents() {
        // Evento principal: cambio en forma de pago
        this.paymentFormField.addEventListener('change', (e) => {
            this.handlePaymentFormChange(e.target.value);
        });

        // Evento secundario: cambio en empresa (si existe)
        const companyField = document.getElementById('id_company');
        if (companyField) {
            companyField.addEventListener('change', (e) => {
                this.currentUserCompanyId = e.target.value;
                // Si ya está mostrando campos bancarios, actualizar opciones
                if (this.isBankingFieldsCreated) {
                    const paymentFormValue = this.paymentFormField.value;
                    if (paymentFormValue) {
                        this.handlePaymentFormChange(paymentFormValue);
                    }
                }
            });
        }
    }

    checkInitialState() {
        // SOLUCIÓN: Capturar valor original ANTES de interferencias
        this.originalAccountValue = this.accountField ? this.accountField.value : null;
        console.log('💾 Valor original capturado de account:', this.originalAccountValue);
        
        // Verificar si ya hay "Transferencia" seleccionada al cargar
        const selectedOption = this.paymentFormField.options[this.paymentFormField.selectedIndex];
        const selectedText = selectedOption ? selectedOption.textContent : '';
        
        if (selectedText.toLowerCase().includes('transferencia')) {
            console.log('🔄 Transferencia ya seleccionada al cargar, aplicando configuración...');
            this.handlePaymentFormChange(this.paymentFormField.value);
        } else {
            console.log('🔄 Efectivo/Crédito seleccionado al cargar, mostrando campo account tradicional...');
            this.showTraditionalAccountField();
        }
    }

    async handlePaymentFormChange(paymentMethodId) {
        // Obtener texto de la opción seleccionada
        const selectedOption = this.paymentFormField.options[this.paymentFormField.selectedIndex];
        const selectedText = selectedOption ? selectedOption.textContent : '';
        
        console.log('💳 Cambio en forma de pago:', { id: paymentMethodId, text: selectedText });

        if (selectedText.toLowerCase().includes('transferencia')) {
            console.log('🏦 Transferencia seleccionada, ocultando campo account y mostrando campos bancarios...');
            this.hideTraditionalAccountField();
            await this.showBankingFields(paymentMethodId);
        } else {
            console.log('💰 Efectivo/Crédito seleccionado, mostrando campo account y ocultando campos bancarios...');
            this.showTraditionalAccountField();
            this.hideBankingFields();
        }
    }

    async showBankingFields(paymentMethodId) {
        console.log('🔧 Configurando campos bancarios unificados...');
        
        // Obtener cuentas bancarias disponibles
        const bankAccounts = await this.fetchBankAccounts();
        
        if (bankAccounts.length === 0) {
            console.log('⚠️ No hay cuentas bancarias disponibles');
            this.showNoBankAccountsMessage();
            return;
        }
        
        // Crear o mostrar campos bancarios
        if (!this.isBankingFieldsCreated) {
            this.createBankingFields(bankAccounts);
        } else {
            this.updateBankAccountOptions(bankAccounts);
            this.showExistingBankingFields();
        }
    }

    async fetchBankAccounts() {
        try {
            const url = `/admin/invoicing/invoice/bank-accounts/?company_id=${this.currentUserCompanyId || ''}`;
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
            console.log('📋 Cuentas bancarias obtenidas:', data.count);
            return data.bank_accounts || [];
        } catch (error) {
            console.error('❌ Error obteniendo cuentas bancarias:', error);
            return [];
        }
    }

    createBankingFields(bankAccounts) {
        // Buscar la fila que contiene los campos de pago
        const accountRow = this.accountField.closest('.form-row');
        if (!accountRow) {
            console.error('❌ No se encontró la fila del formulario para account');
            return;
        }

        // Crear contenedor principal para campos bancarios
        const bankingContainer = document.createElement('div');
        bankingContainer.className = 'banking-fields-container';
        bankingContainer.style.cssText = `
            display: flex;
            gap: 15px;
            margin-top: 10px;
            align-items: flex-start;
        `;

        // === CAMPO 1: SELECTOR DE CUENTA BANCARIA ===
        const bankAccountDiv = document.createElement('div');
        bankAccountDiv.className = 'field-box field-bank_account';
        bankAccountDiv.style.cssText = `
            flex: 1;
            min-width: 300px;
        `;

        // Label cuenta bancaria
        const bankLabel = document.createElement('label');
        bankLabel.textContent = 'Cuenta Bancaria:';
        bankLabel.className = 'required';
        bankLabel.htmlFor = 'id_bank_account';
        bankLabel.style.cssText = `
            font-weight: bold;
            color: #666666;
            font-size: 11px;
            text-transform: uppercase;
            font-family: "Roboto", "Lucida Grande", Verdana, Arial, sans-serif;
            display: block;
            margin-bottom: 5px;
        `;

        // Select dropdown cuenta bancaria
        const bankSelect = document.createElement('select');
        bankSelect.name = 'bank_account';
        bankSelect.id = 'id_bank_account';
        bankSelect.className = 'admin-autocomplete';
        bankSelect.style.cssText = `
            width: 100%;
            height: 30px;
            padding: 5px 8px;
            border: 1px solid #cccccc;
            border-radius: 4px;
            font-size: 13px;
            color: #333333;
            font-family: "Roboto", "Lucida Grande", Verdana, Arial, sans-serif;
            background-color: #ffffff;
        `;

        this.populateBankAccountSelect(bankSelect, bankAccounts);

        // Evento de cambio para auto-asignar cuenta contable
        bankSelect.addEventListener('change', (e) => {
            this.handleBankAccountChange(e);
        });

        bankAccountDiv.appendChild(bankLabel);
        bankAccountDiv.appendChild(bankSelect);

        // === CAMPO 2: OBSERVACIONES OPCIONALES ===
        const observationsDiv = document.createElement('div');
        observationsDiv.className = 'field-box field-bank_observations';
        observationsDiv.style.cssText = `
            flex: 1;
            min-width: 250px;
        `;

        // Label observaciones
        const obsLabel = document.createElement('label');
        obsLabel.textContent = 'Observaciones:';
        obsLabel.htmlFor = 'id_bank_observations';
        obsLabel.style.cssText = `
            font-weight: normal;
            color: #666666;
            font-size: 11px;
            text-transform: uppercase;
            font-family: "Roboto", "Lucida Grande", Verdana, Arial, sans-serif;
            display: block;
            margin-bottom: 5px;
        `;

        // Textarea observaciones
        const obsTextarea = document.createElement('textarea');
        obsTextarea.name = 'bank_observations';
        obsTextarea.id = 'id_bank_observations';
        obsTextarea.rows = 2;
        obsTextarea.style.cssText = `
            width: 100%;
            padding: 5px 8px;
            border: 1px solid #cccccc;
            border-radius: 4px;
            font-size: 13px;
            color: #333333;
            font-family: "Roboto", "Lucida Grande", Verdana, Arial, sans-serif;
            background-color: #ffffff;
            resize: vertical;
        `;
        obsTextarea.placeholder = 'Información adicional sobre la transferencia (opcional)';

        // Sincronizar con campo Django oculto
        obsTextarea.addEventListener('input', (e) => {
            this.syncWithDjangoField('bank_observations', e.target.value);
        });

        observationsDiv.appendChild(obsLabel);
        observationsDiv.appendChild(obsTextarea);

        // === ENSAMBLAJE FINAL ===
        bankingContainer.appendChild(bankAccountDiv);
        bankingContainer.appendChild(observationsDiv);

        // Insertar después del campo account
        const accountFieldBox = this.accountField.closest('.field-box');
        
        if (accountFieldBox && accountFieldBox.parentNode) {
            accountFieldBox.parentNode.insertBefore(bankingContainer, accountFieldBox.nextSibling);
        } else {
            accountRow.appendChild(bankingContainer);
        }

        // Guardar referencias
        this.bankAccountField = bankAccountDiv;
        this.observationsField = observationsDiv;
        this.isBankingFieldsCreated = true;

        // CARGAR ESTADO INICIAL desde campos Django en modo edición (DESPUÉS de insertar en DOM)
        this.waitForOptionsAndLoadState(bankSelect, obsTextarea);

        console.log('✅ Campos bancarios unificados creados exitosamente');
        
        // El campo account ya está oculto, no necesita ser readonly
    }

    populateBankAccountSelect(select, bankAccounts) {
        // Limpiar opciones existentes
        select.innerHTML = '';

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
            option.textContent = `${account.bank_short_name} - ${account.account_type_display} - ****${account.account_number.slice(-4)}`;
            select.appendChild(option);
        });
    }

    handleBankAccountChange(event) {
        const selectedOption = event.target.options[event.target.selectedIndex];
        
        if (selectedOption && selectedOption.dataset.chartAccountId) {
            // Auto-asignar cuenta contable
            this.autoAssignChartAccount(selectedOption);
        } else {
            // Limpiar campo account si no hay selección
            this.accountField.value = '';
            this.accountField.style.backgroundColor = '#ffffff';
        }
    }

    autoAssignChartAccount(selectedOption) {
        const chartAccountId = selectedOption.dataset.chartAccountId;
        const chartAccountCode = selectedOption.dataset.chartAccountCode;
        const chartAccountName = selectedOption.dataset.chartAccountName;
        
        if (chartAccountId && this.accountField) {
            // Auto-asignar en el campo account (aunque esté oculto)
            this.accountField.value = chartAccountId;
            
            console.log('✅ Cuenta contable auto-asignada (oculta):', {
                id: chartAccountId,
                code: chartAccountCode,
                name: chartAccountName
            });
            
            // No aplicar estilos visuales ya que el campo está oculto
            // Mostrar mensaje de confirmación
            this.showAutoAssignMessage(chartAccountCode, chartAccountName);
            
            // Disparar evento change para notificar otros handlers
            const changeEvent = new Event('change', { bubbles: true });
            this.accountField.dispatchEvent(changeEvent);
        }
    }

    hideTraditionalAccountField() {
        if (this.accountField) {
            // Buscar el contenedor más específico del campo account (no la fila completa)
            let accountContainer = this.accountField.parentElement;
            
            // Si está en un div.field-account, usar ese contenedor
            if (accountContainer && accountContainer.classList.contains('field-account')) {
                accountContainer.style.display = 'none';
                console.log('🙈 Campo account tradicional ocultado (contenedor específico)');
                accountContainer.classList.add('hidden-for-transfer');
                return;
            }
            
            // Buscar contenedor con clase field- específica
            while (accountContainer && !accountContainer.classList.contains('field-account')) {
                if (accountContainer.tagName === 'DIV' && 
                    (accountContainer.className.includes('field-account') || 
                     accountContainer.querySelector('#id_account') === this.accountField)) {
                    break;
                }
                accountContainer = accountContainer.parentElement;
                // Evitar subir demasiado en el DOM
                if (!accountContainer || accountContainer.tagName === 'FORM') {
                    break;
                }
            }
            
            // Si no encontramos contenedor específico, ocultar solo el campo y su label
            if (!accountContainer || accountContainer === this.accountField.parentElement) {
                // Ocultar el campo directamente
                this.accountField.style.display = 'none';
                
                // Buscar y ocultar el label asociado
                const accountLabel = document.querySelector('label[for="id_account"]');
                if (accountLabel) {
                    accountLabel.style.display = 'none';
                    accountLabel.classList.add('hidden-for-transfer');
                }
                
                console.log('🙈 Campo account tradicional ocultado (campo individual)');
                this.accountField.classList.add('hidden-for-transfer');
            } else {
                accountContainer.style.display = 'none';
                console.log('🙈 Campo account tradicional ocultado (contenedor encontrado)');
                accountContainer.classList.add('hidden-for-transfer');
            }
        }
    }

    showTraditionalAccountField() {
        if (this.accountField) {
            // Restaurar el campo account y su label
            this.accountField.style.display = 'block';
            this.accountField.classList.remove('hidden-for-transfer');
            
            // Restaurar el label si fue ocultado
            const accountLabel = document.querySelector('label[for="id_account"]');
            if (accountLabel && accountLabel.classList.contains('hidden-for-transfer')) {
                accountLabel.style.display = 'block';
                accountLabel.classList.remove('hidden-for-transfer');
            }
            
            // Buscar y restaurar contenedor si fue ocultado
            const hiddenContainers = document.querySelectorAll('.hidden-for-transfer');
            hiddenContainers.forEach(container => {
                if (container.querySelector('#id_account') === this.accountField) {
                    container.style.display = 'block';
                    container.classList.remove('hidden-for-transfer');
                }
            });
            
            console.log('👁️ Campo account tradicional mostrado');
            
            // Restaurar campo a editable
            this.restoreAccountFieldEditable();
        }
    }

    makeAccountFieldReadonly() {
        if (this.accountField) {
            this.accountField.setAttribute('readonly', 'readonly');
            this.accountField.style.backgroundColor = '#f8f9fa';
            this.accountField.style.cursor = 'not-allowed';
            
            // Agregar tooltip
            this.accountField.title = 'Cuenta asignada automáticamente por la selección bancaria';
        }
    }

    restoreAccountFieldEditable() {
        if (this.accountField) {
            this.accountField.removeAttribute('readonly');
            this.accountField.style.backgroundColor = '#ffffff';
            this.accountField.style.cursor = 'text';
            this.accountField.title = '';
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
        }, 3000);
    }

    updateBankAccountOptions(bankAccounts) {
        const bankSelect = document.getElementById('id_bank_account');
        if (bankSelect) {
            this.populateBankAccountSelect(bankSelect, bankAccounts);
        }
    }

    showExistingBankingFields() {
        const container = document.querySelector('.banking-fields-container');
        if (container) {
            container.style.display = 'flex';
            // El campo account ya está oculto, no necesita ser readonly
        }
    }

    hideBankingFields() {
        console.log('🙈 Ocultando campos bancarios unificados...');
        
        const container = document.querySelector('.banking-fields-container');
        if (container) {
            container.style.display = 'none';
            
            // Limpiar campos bancarios
            const bankSelect = document.getElementById('id_bank_account');
            const obsTextarea = document.getElementById('id_bank_observations');
            
            if (bankSelect) bankSelect.value = '';
            if (obsTextarea) obsTextarea.value = '';
            
            // IMPORTANTE: NO limpiar el campo account aquí ya que para efectivo/crédito 
            // el usuario debe seleccionar manualmente la cuenta
            
            // Sincronizar con Django
            this.syncWithDjangoField('bank_observations', '');
        }
    }

    showNoBankAccountsMessage() {
        const messageDiv = document.createElement('div');
        messageDiv.style.cssText = `
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            padding: 10px;
            margin-top: 10px;
            font-size: 13px;
        `;
        messageDiv.innerHTML = `
            <strong>⚠️ No hay cuentas bancarias configuradas</strong><br>
            Configure cuentas bancarias en el módulo Banking para usar esta función.
        `;
        
        const accountRow = this.accountField.closest('.form-row');
        if (accountRow) {
            accountRow.appendChild(messageDiv);
            
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.parentNode.removeChild(messageDiv);
                }
            }, 5000);
        }
    }

    waitForOptionsAndLoadState(bankSelect, obsTextarea) {
        console.log('⏳ Esperando que las opciones del selector estén disponibles...');
        
        const checkOptions = () => {
            // Verificar si ya hay opciones con datos (más que solo la opción vacía)
            const optionsWithData = Array.from(bankSelect.options).filter(opt => 
                opt.value && opt.dataset.chartAccountId
            );
            
            console.log(`🔍 Opciones disponibles: ${optionsWithData.length}`);
            
            if (optionsWithData.length > 0) {
                console.log('✅ Opciones cargadas, procediendo con loadInitialState');
                this.loadInitialState(bankSelect, obsTextarea);
            } else {
                console.log('⏳ Esperando más opciones...');
                setTimeout(checkOptions, 200);
            }
        };
        
        // Empezar a verificar después de un pequeño delay
        setTimeout(checkOptions, 100);
    }

    loadInitialState(bankSelect, obsTextarea) {
        console.log('🔄 Cargando estado inicial desde campos Django...');
        console.log('🔍 BankSelect element:', bankSelect);
        console.log('🔍 ObsTextarea element:', obsTextarea);
        
        // 1. Cargar observaciones en el textarea visible desde el campo Django oculto
        console.log('🔍 Textarea de observaciones creado:', obsTextarea);
        console.log('🔍 Valor inicial del textarea:', obsTextarea.value);
        
        // Buscar el campo Django oculto para obtener las observaciones guardadas
        // Nota: Django renderiza bank_observations como input[type="hidden"] por HiddenInput()
        const hiddenBankObsField = document.getElementById('id_bank_observations');
        console.log('🔍 Campo Django oculto encontrado:', hiddenBankObsField);
        console.log('🔍 Tipo de campo:', hiddenBankObsField ? hiddenBankObsField.type : 'null');
        
        if (hiddenBankObsField && hiddenBankObsField.value && hiddenBankObsField.value.trim()) {
            console.log('📝 Valor en campo Django oculto:', hiddenBankObsField.value.substring(0, 100) + '...');
            obsTextarea.value = hiddenBankObsField.value;
            console.log('✅ Observaciones copiadas al textarea visible');
        } else {
            console.log('⚠️ No hay observaciones guardadas en el campo Django');
            console.log('🔍 Valor del campo:', hiddenBankObsField ? `"${hiddenBankObsField.value}"` : 'null');
        }
        
        // 2. Seleccionar cuenta bancaria correspondiente si hay una seleccionada
        console.log('🔍 Campo account encontrado:', this.accountField);
        
        // SOLUCIÓN: Usar valor original capturado ANTES de interferencias
        const selectedChartAccountId = this.originalAccountValue || (this.accountField ? this.accountField.value : null);
        
        console.log('💾 Valor original capturado:', this.originalAccountValue);
        console.log('� Valor actual del campo:', this.accountField ? this.accountField.value : 'null');
        console.log('🎯 Valor que usaremos:', selectedChartAccountId);
        
        if (selectedChartAccountId) {
            console.log('🏦 Cuenta contable a buscar:', selectedChartAccountId);
            console.log('🔍 Total opciones en bankSelect:', bankSelect.options.length);
            
            // Listar todas las opciones disponibles para debug
            console.log('📋 Todas las opciones disponibles:');
            Array.from(bankSelect.options).forEach((opt, index) => {
                console.log(`   ${index}: value="${opt.value}" chartAccountId="${opt.dataset.chartAccountId}" text="${opt.textContent}"`);
            });
            
            // Buscar en opciones del selector por chart_account_id en dataset
            const matchingOption = Array.from(bankSelect.options).find(option => 
                option.dataset.chartAccountId == selectedChartAccountId
            );
            
            console.log('🔍 Opción encontrada:', matchingOption);
            
            if (matchingOption) {
                bankSelect.value = matchingOption.value;
                console.log('✅ Cuenta bancaria pre-seleccionada:', matchingOption.textContent);
                console.log('✅ Chart Account ID coincidente:', matchingOption.dataset.chartAccountId);
                console.log('✅ BankSelect.value asignado a:', matchingOption.value);
                
                // Disparar evento change para sincronizar
                const changeEvent = new Event('change', { bubbles: true });
                bankSelect.dispatchEvent(changeEvent);
            } else {
                console.log('⚠️ No se encontró cuenta bancaria correspondiente para chart account:', selectedChartAccountId);
                console.log('📋 Cuentas disponibles en selector:');
                Array.from(bankSelect.options).forEach((opt, i) => {
                    if (opt.dataset.chartAccountId && opt.dataset.chartAccountId !== 'undefined') {
                        console.log(`   ${i}: chartAccountId=${opt.dataset.chartAccountId} → ${opt.textContent}`);
                    }
                });
            }
        } else {
            console.log('⚠️ No hay cuenta seleccionada (ni original ni actual)');
        }
        
        console.log('🔄 Estado inicial cargado completamente');
    }

    syncWithDjangoField(fieldName, value) {
        // Sincronizar con campos Django ocultos
        const djangoField = document.getElementById(`id_${fieldName}`);
        if (djangoField) {
            djangoField.value = value;
            console.log(`🔄 ${fieldName} sincronizado con Django:`, value);
        }

        // Compatibilidad con transfer_detail (DEPRECATED)
        if (fieldName === 'bank_observations') {
            const transferDetailField = document.getElementById('id_transfer_detail');
            if (transferDetailField) {
                transferDetailField.value = value;
                console.log('🔄 Compatibilidad: transfer_detail sincronizado:', value);
            }
        }
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new UnifiedBankingIntegration();
});

// También inicializar si el DOM ya está cargado
if (document.readyState !== 'loading') {
    new UnifiedBankingIntegration();
}