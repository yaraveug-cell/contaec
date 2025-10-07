/**
 * Sistema dinámico integrado para filtrado de Forma de Pago y Cuenta
 * Maneja filtrado en cascada: Empresa → Forma de Pago → Cuenta Padre → Cuentas Hijas
 * Version: 4.0 - 01/10/2025 - Con logs detallados de debugging
 */

class IntegratedPaymentAccountHandler {
    constructor() {
        this.companyField = null;
        this.paymentFormField = null;
        this.accountField = null;
        this.originalAccountOptions = [];
        this.companyPaymentMethods = {};
        this.paymentMethodAccounts = {};
        this.init();
    }

    init() {
        console.log('🚀 IntegratedPaymentAccountHandler: Iniciando sistema integrado...');
        console.log('📄 Document ready state:', document.readyState);
        console.log('🌍 URL actual:', window.location.pathname);
        console.log('⚡ Modo: JavaScript Vanilla (sin jQuery)');
        
        // Verificar DOM directamente
        this.checkDOM();
    }

    checkDOM() {
        console.log('🔍 Verificando DOM y campos...');
        
        // Esperar a que el DOM esté listo
        if (document.readyState === 'loading') {
            console.log('⏳ DOM cargando, esperando...');
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            console.log('✅ DOM listo, iniciando setup...');
            this.setup();
        }
    }

    setup() {
        console.log('🔧 IntegratedPaymentAccountHandler: Configurando campos...');
        
        // Buscar campos usando JavaScript vanilla
        this.companyField = document.getElementById('id_company');
        this.paymentFormField = document.getElementById('id_payment_form');
        this.accountField = document.getElementById('id_account');
        
        console.log('🔍 Búsqueda de campos (vanilla JS):', {
            company: this.companyField ? 'Encontrado' : 'No encontrado',
            payment: this.paymentFormField ? 'Encontrado' : 'No encontrado',
            account: this.accountField ? 'Encontrado' : 'No encontrado'
        });
        
        if (!this.companyField || !this.paymentFormField || !this.accountField) {
            console.warn('⚠️ Campos no encontrados, reintentando en 500ms...');
            setTimeout(() => this.setup(), 500);
            return;
        }
        
        console.log('✅ Todos los campos encontrados exitosamente');
        
        // Guardar opciones originales
        this.saveOriginalOptions();
        
        // Cargar configuraciones
        this.loadConfigurations();
        
        // Configurar eventos
        this.bindEvents();
        
        // Aplicar filtros iniciales
        this.applyInitialFilters();
    }

    saveOriginalOptions() {
        // Guardar opciones de cuentas
        this.originalAccountOptions = [];
        this.accountField.find('option').each((index, option) => {
            const $option = $(option);
            this.originalAccountOptions.push({
                value: $option.val(),
                text: $option.text(),
                element: $option.clone()
            });
        });
        
        console.log('IntegratedPaymentAccountHandler: Opciones originales guardadas:', {
            accounts: this.originalAccountOptions.length
        });
    }

    async loadConfigurations() {
        try {
            console.log('📡 Cargando configuraciones desde el servidor...');
            
            // Cargar configuración empresa → forma de pago
            console.log('🏢 Cargando configuración de empresas...');
            const companyResponse = await this.fetchWithFallback('/admin/invoicing/invoice/company-payment-methods/', {});
            this.companyPaymentMethods = companyResponse;
            console.log('📊 Empresas cargadas:', this.companyPaymentMethods);
            
            // Cargar configuración forma de pago → cuentas padre
            console.log('💳 Cargando configuración de métodos de pago...');
            const accountResponse = await this.fetchWithFallback('/admin/invoicing/invoice/payment-method-accounts/', {});
            this.paymentMethodAccounts = accountResponse;
            console.log('📋 Métodos de pago cargados:', this.paymentMethodAccounts);
            
            console.log('✅ Configuraciones cargadas exitosamente:', {
                companies: Object.keys(this.companyPaymentMethods).length,
                paymentMethods: Object.keys(this.paymentMethodAccounts).length
            });
            
        } catch (error) {
            console.error('❌ Error cargando configuraciones:', error);
            // Continuar con datos vacíos - el sistema funcionará pero sin filtrado inteligente
            this.companyPaymentMethods = {};
            this.paymentMethodAccounts = {};
        }
    }

    async fetchWithFallback(url, fallback) {
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                return await response.json();
            } else {
                console.warn('IntegratedPaymentAccountHandler: Respuesta no exitosa, usando fallback');
                return fallback;
            }
        } catch (error) {
            console.warn('IntegratedPaymentAccountHandler: Error en fetch, usando fallback');
            return fallback;
        }
    }

    bindEvents() {
        // Escuchar cambios en empresa
        this.companyField.on('change', () => {
            console.log('IntegratedPaymentAccountHandler: Empresa cambiada');
            this.handleCompanyChange();
        });
        
        // Escuchar cambios en forma de pago (múltiples eventos)
        this.paymentFormField.on('change change.integrated', () => {
            console.log('IntegratedPaymentAccountHandler: Forma de pago cambiada');
            this.handlePaymentFormChange();
        });
        
        // También escuchar eventos manuales
        this.paymentFormField.on('input blur', () => {
            console.log('IntegratedPaymentAccountHandler: Forma de pago cambiada manualmente');
            setTimeout(() => this.handlePaymentFormChange(), 100);
        });
    }

    applyInitialFilters() {
        console.log('IntegratedPaymentAccountHandler: Aplicando filtros iniciales...');
        
        // Aplicar filtro inicial basado en empresa seleccionada
        this.handleCompanyChange();
    }

    handleCompanyChange() {
        const selectedCompanyId = this.companyField.val();
        const selectedCompanyText = this.companyField.find('option:selected').text();
        console.log('🏢 CAMBIO DE EMPRESA detectado');
        console.log('   ID seleccionado:', selectedCompanyId);
        console.log('   Nombre:', selectedCompanyText);
        
        if (!selectedCompanyId) {
            console.log('⚠️ Sin empresa seleccionada, limpiando filtros...');
            this.clearPaymentFormFilter();
            this.clearAccountFilter();
            return;
        }
        
        console.log('📋 Configuración disponible para empresa:', this.companyPaymentMethods[selectedCompanyId]);
        
        // Establecer forma de pago predeterminada según empresa
        this.setDefaultPaymentMethod(selectedCompanyId);
        
        // Filtrar cuentas según la nueva forma de pago
        setTimeout(() => {
            console.log('🔄 Procesando filtrado de cuentas después del cambio...');
            this.handlePaymentFormChange();
        }, 100);
    }

    setDefaultPaymentMethod(companyId) {
        const companyConfig = this.companyPaymentMethods[companyId];
        
        if (companyConfig && companyConfig.id) {
            // Establecer forma de pago predeterminada
            const currentValue = this.paymentFormField.val();
            this.paymentFormField.val(companyConfig.id);
            console.log('IntegratedPaymentAccountHandler: Forma de pago predeterminada establecida:', companyConfig.name);
            
            // Solo disparar evento si cambió el valor
            if (currentValue !== companyConfig.id.toString()) {
                this.paymentFormField.trigger('change');
            }
        } else {
            // Sin configuración específica, usar primera opción si está disponible
            const firstOption = this.paymentFormField.find('option[value!=""]:first');
            if (firstOption.length) {
                const currentValue = this.paymentFormField.val();
                this.paymentFormField.val(firstOption.val());
                console.log('IntegratedPaymentAccountHandler: Usando primera forma de pago disponible');
                
                // Solo disparar evento si cambió el valor
                if (currentValue !== firstOption.val()) {
                    this.paymentFormField.trigger('change');
                }
            }
        }
    }

    handlePaymentFormChange() {
        const selectedPaymentMethodId = this.paymentFormField.val();
        const selectedPaymentMethodText = this.paymentFormField.find('option:selected').text();
        console.log('💳 CAMBIO DE FORMA DE PAGO detectado');
        console.log('   ID seleccionado:', selectedPaymentMethodId);
        console.log('   Nombre:', selectedPaymentMethodText);
        
        if (!selectedPaymentMethodId) {
            console.log('⚠️ Sin forma de pago seleccionada, limpiando cuentas...');
            this.clearAccountFilter();
            return;
        }
        
        console.log('📋 Configuración disponible para método:', this.paymentMethodAccounts[selectedPaymentMethodId]);
        
        // Filtrar cuentas basándose en la cuenta padre del método de pago
        this.filterAccountsByPaymentMethod(selectedPaymentMethodId);
    }

    filterAccountsByPaymentMethod(paymentMethodId) {
        console.log('IntegratedPaymentAccountHandler: Filtrando cuentas para método:', paymentMethodId);
        
        // Obtener configuración del método de pago
        const methodConfig = this.paymentMethodAccounts[paymentMethodId];
        
        if (!methodConfig || !methodConfig.parent_account) {
            console.warn('IntegratedPaymentAccountHandler: Sin cuenta padre configurada para método:', paymentMethodId);
            this.showAllAccounts();
            return;
        }
        
        const parentAccountInfo = methodConfig.parent_account;
        console.log('IntegratedPaymentAccountHandler: Cuenta padre encontrada:', parentAccountInfo);
        
        // Filtrar cuentas hijas
        this.filterChildAccounts(parentAccountInfo);
    }

    filterChildAccounts(parentAccountInfo) {
        console.log('IntegratedPaymentAccountHandler: Filtrando cuentas hijas de:', parentAccountInfo.name);
        console.log('Código padre:', parentAccountInfo.code);
        console.log('Total opciones originales:', this.originalAccountOptions.length);
        
        // Limpiar campo de cuentas
        this.accountField.empty();
        
        // Agregar opción vacía
        this.accountField.append('<option value="">---------</option>');
        
        let childAccountsCount = 0;
        let defaultAccount = null;
        
        // Filtrar opciones originales
        this.originalAccountOptions.forEach(option => {
            if (!option.value) return; // Skip empty option
            
            const optionText = option.text.toUpperCase();
            console.log('Evaluando opción:', option.text);
            
            // Verificar si es cuenta hija del padre especificado
            if (this.isChildAccount(optionText, parentAccountInfo)) {
                this.accountField.append(option.element.clone());
                childAccountsCount++;
                
                // Establecer primera cuenta como predeterminada
                if (!defaultAccount) {
                    defaultAccount = option;
                }
                
                console.log('✅ IntegratedPaymentAccountHandler: Cuenta hija incluida:', option.text);
            } else {
                console.log('❌ IntegratedPaymentAccountHandler: Cuenta excluida:', option.text);
            }
        });
        
        // Si no se encontraron cuentas hijas, mostrar todas como fallback
        if (childAccountsCount === 0) {
            console.warn('IntegratedPaymentAccountHandler: No se encontraron cuentas hijas, mostrando todas');
            this.showAllAccounts();
            return;
        }
        
        // Establecer cuenta predeterminada
        if (defaultAccount) {
            this.accountField.val(defaultAccount.value);
            console.log('IntegratedPaymentAccountHandler: Cuenta predeterminada establecida:', defaultAccount.text);
        }
        
        console.log('IntegratedPaymentAccountHandler: Total cuentas hijas encontradas:', childAccountsCount);
        
        // Disparar evento para notificar cambio
        this.accountField.trigger('change');
    }

    isChildAccount(accountText, parentAccountInfo) {
        console.log('Verificando si es cuenta hija:', accountText, 'de padre:', parentAccountInfo);
        
        // Extraer código de la cuenta de la opción (formato: "CODIGO - NOMBRE")
        const accountCode = accountText.split(' - ')[0] || '';
        const parentCode = parentAccountInfo.code || '';
        
        console.log('Códigos:', { account: accountCode, parent: parentCode });
        
        // Estrategias para identificar cuentas hijas:
        
        // 1. Por código jerárquico exacto (más preciso)
        if (parentCode && accountCode) {
            // Remover punto final del código padre si existe
            const cleanParentCode = parentCode.replace(/\.$/, '');
            
            // La cuenta hija debe empezar con el código del padre
            if (accountCode.startsWith(cleanParentCode)) {
                // Y debe tener más niveles (más puntos)
                const parentLevels = cleanParentCode.split('.').length;
                const accountLevels = accountCode.split('.').length;
                
                if (accountLevels > parentLevels) {
                    console.log('✅ Cuenta hija por código jerárquico:', accountText);
                    return true;
                }
            }
        }
        
        // 2. Por jerarquía de nombres (fallback)
        const parentName = parentAccountInfo.name.toUpperCase();
        
        // Casos específicos conocidos
        if (parentName.includes('CAJA') && this.isCashAccount(accountText)) {
            console.log('✅ Cuenta hija por tipo CAJA:', accountText);
            return true;
        }
        
        if (parentName.includes('CLIENTES RELACIONADOS') && this.isClientAccount(accountText)) {
            console.log('✅ Cuenta hija por tipo CLIENTES:', accountText);
            return true;
        }
        
        if (parentName.includes('BANCO') && this.isBankAccount(accountText)) {
            console.log('✅ Cuenta hija por tipo BANCO:', accountText);
            return true;
        }
        
        console.log('❌ No es cuenta hija:', accountText);
        return false;
    }

    isCashAccount(accountText) {
        return accountText.includes('CAJA') && !accountText.includes('BANCO');
    }

    isClientAccount(accountText) {
        return (accountText.includes('CLIENTE') && accountText.includes('CREDITO')) ||
               accountText.includes('CLIENTES RELACIONADOS');
    }

    isBankAccount(accountText) {
        return accountText.includes('BANCO') || 
               accountText.includes('BANCARIO') ||
               accountText.includes('CUENTA CORRIENTE') ||
               accountText.includes('AHORRO');
    }

    clearPaymentFormFilter() {
        console.log('IntegratedPaymentAccountHandler: Limpiando filtro de forma de pago');
        // Restaurar todas las opciones de forma de pago si es necesario
    }

    clearAccountFilter() {
        console.log('IntegratedPaymentAccountHandler: Limpiando filtro de cuentas');
        this.accountField.empty();
        this.accountField.append('<option value="">---------</option>');
    }

    showAllAccounts() {
        console.log('IntegratedPaymentAccountHandler: Mostrando todas las cuentas');
        
        // Restaurar todas las opciones
        this.accountField.empty();
        this.originalAccountOptions.forEach(option => {
            this.accountField.append(option.element.clone());
        });
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               this.getCookie('csrftoken');
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Función de test manual accesible desde consola
    testFiltering(companyName, paymentName) {
        companyName = companyName || 'GUEBER';
        paymentName = paymentName || 'Efectivo';
        
        console.log('🧪 INICIANDO TEST MANUAL');
        console.log('   Empresa objetivo:', companyName);
        console.log('   Forma de pago objetivo:', paymentName);
        
        // Seleccionar empresa
        const companyOption = Array.from(this.companyField[0].options)
            .find(opt => opt.text.includes(companyName));
        
        if (companyOption) {
            console.log('✅ Empresa encontrada:', companyOption.text);
            this.companyField.val(companyOption.value).trigger('change');
            
            setTimeout(() => {
                // Seleccionar forma de pago
                const paymentOption = Array.from(this.paymentFormField[0].options)
                    .find(opt => opt.text.includes(paymentName));
                
                if (paymentOption) {
                    console.log('✅ Forma de pago encontrada:', paymentOption.text);
                    this.paymentFormField.val(paymentOption.value).trigger('change');
                    
                    setTimeout(() => {
                        const accounts = Array.from(this.accountField[0].options)
                            .filter(opt => opt.value !== '');
                        console.log('📊 RESULTADO FINAL - Cuentas disponibles:', 
                            accounts.map(opt => opt.text));
                    }, 1000);
                } else {
                    console.error('❌ Forma de pago no encontrada:', paymentName);
                }
            }, 1000);
        } else {
            console.error('❌ Empresa no encontrada:', companyName);
        }
    }
}

// Variable global para acceso desde consola
let globalFilteringHandler = null;

// Inicializar sistema integrado
function initSystemWhenReady() {
    console.log('🔍 Verificando condiciones para inicialización...');
    
    // Verificar jQuery
    if (typeof $ === 'undefined') {
        console.log('⏳ jQuery no disponible, esperando...');
        setTimeout(initSystemWhenReady, 100);
        return;
    }
    
    // Verificar que estemos en la página correcta
    if (document.querySelector('#invoice_form') || 
        window.location.pathname.includes('/invoicing/invoice/')) {
        
        console.log('🚀 Iniciando sistema integrado de filtrado...');
        const handler = new IntegratedPaymentAccountHandler();
        globalFilteringHandler = handler;
        
        // Función global de test
        window.testFiltering = (company = 'GUEBER', payment = 'Efectivo') => {
            if (globalFilteringHandler) {
                globalFilteringHandler.testFiltering(company, payment);
            } else {
                console.error('❌ Handler no disponible');
            }
        };
    } else {
        console.log('ℹ️ No estamos en la página de invoicing, sistema no inicializado');
    }
}

// Ejecutar cuando DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSystemWhenReady);
} else {
    initSystemWhenReady();
}

// Función global para inicialización manual si es necesaria
window.initIntegratedPaymentAccountHandler = function() {
    new IntegratedPaymentAccountHandler();
};