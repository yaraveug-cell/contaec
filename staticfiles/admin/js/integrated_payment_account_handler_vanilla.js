/**
 * Sistema dinámico integrado para filtrado de Forma de Pago y Cuenta
 * Maneja filtrado en cascada: Empresa → Forma de Pago → Cuenta Padre → Cuentas Hijas
 * Version: 5.0 - 01/10/2025 - JavaScript Vanilla (sin jQuery)
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
        console.log('🚀 IntegratedPaymentAccountHandler: Iniciando sistema integrado v5.0...');
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
        // Guardar opciones de cuentas usando JavaScript vanilla
        this.originalAccountOptions = [];
        const options = this.accountField.getElementsByTagName('option');
        
        for (let i = 0; i < options.length; i++) {
            const option = options[i];
            this.originalAccountOptions.push({
                value: option.value,
                text: option.textContent,
                selected: option.selected
            });
        }
        
        console.log('💾 Opciones originales guardadas:', this.originalAccountOptions.length, 'cuentas');
    }

    bindEvents() {
        console.log('🔗 Configurando eventos (vanilla JS)...');
        
        // Event listener para cambio de empresa
        this.companyField.addEventListener('change', (e) => {
            console.log('🏢 Empresa cambiada:', e.target.value);
            this.handleCompanyChange(e.target.value);
        });
        
        // Event listener para cambio de forma de pago
        this.paymentFormField.addEventListener('change', (e) => {
            console.log('💳 Forma de pago cambiada:', e.target.value);
            this.handlePaymentFormChange(e.target.value);
        });
        
        console.log('✅ Eventos configurados exitosamente');
    }

    loadConfigurations() {
        console.log('📡 Cargando configuraciones desde servidor...');
        
        Promise.all([
            this.loadCompanyPaymentMethods(),
            this.loadPaymentMethodAccounts()
        ]).then(() => {
            console.log('✅ Todas las configuraciones cargadas');
            console.log('📊 Resumen configuraciones:', {
                companies: Object.keys(this.companyPaymentMethods).length,
                methods: Object.keys(this.paymentMethodAccounts).length
            });
        }).catch(error => {
            console.error('❌ Error cargando configuraciones:', error);
        });
    }

    async loadCompanyPaymentMethods() {
        try {
            const response = await fetch('/admin/invoicing/invoice/company-payment-methods/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            this.companyPaymentMethods = await response.json();
            console.log('🏢 Configuraciones empresa-método cargadas:', this.companyPaymentMethods);
            
        } catch (error) {
            console.error('❌ Error cargando empresa-métodos:', error);
            this.companyPaymentMethods = {};
        }
    }

    async loadPaymentMethodAccounts() {
        try {
            const response = await fetch('/admin/invoicing/invoice/payment-method-accounts/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            this.paymentMethodAccounts = await response.json();
            console.log('💳 Configuraciones método-cuenta cargadas:', this.paymentMethodAccounts);
            
        } catch (error) {
            console.error('❌ Error cargando método-cuentas:', error);
            this.paymentMethodAccounts = {};
        }
    }

    handleCompanyChange(companyId) {
        console.log('🏢 Procesando cambio de empresa ID:', companyId);
        
        if (!companyId || companyId === '') {
            console.log('⚪ Empresa vacía, restaurando opciones originales');
            this.resetPaymentForm();
            this.resetAccountField();
            return;
        }
        
        const companyConfig = this.companyPaymentMethods[companyId];
        if (companyConfig) {
            console.log('✅ Configuración encontrada para empresa:', companyConfig);
            
            // Establecer forma de pago por defecto de la empresa
            this.paymentFormField.value = companyConfig.id;
            
            // Disparar evento de cambio de forma de pago
            const event = new Event('change', { bubbles: true });
            this.paymentFormField.dispatchEvent(event);
            
        } else {
            console.log('⚠️ No hay configuración para empresa:', companyId);
            this.resetPaymentForm();
            this.resetAccountField();
        }
    }

    handlePaymentFormChange(paymentMethodId) {
        console.log('💳 Procesando cambio de método de pago ID:', paymentMethodId);
        
        if (!paymentMethodId || paymentMethodId === '') {
            console.log('⚪ Método de pago vacío, restaurando cuentas');
            this.resetAccountField();
            return;
        }
        
        const methodConfig = this.paymentMethodAccounts[paymentMethodId];
        if (methodConfig && methodConfig.parent_account) {
            console.log('✅ Cuenta padre encontrada:', methodConfig.parent_account);
            this.filterChildAccounts(methodConfig.parent_account);
        } else {
            console.log('⚠️ No hay cuenta padre para método:', paymentMethodId);
            this.resetAccountField();
        }
    }

    filterChildAccounts(parentAccount) {
        console.log('🔍 Filtrando cuentas hijas de:', parentAccount);
        
        // Limpiar campo de cuenta
        this.accountField.innerHTML = '<option value="">---------</option>';
        
        // Buscar y agregar cuentas hijas
        const childAccounts = this.originalAccountOptions.filter(account => {
            if (!account.value) return false;
            return this.isChildAccount(account.text, parentAccount);
        });
        
        console.log(`📋 Cuentas hijas encontradas: ${childAccounts.length}`);
        
        childAccounts.forEach((account, index) => {
            const option = document.createElement('option');
            option.value = account.value;
            option.textContent = account.text;
            if (index === 0) option.selected = true; // Seleccionar primera por defecto
            this.accountField.appendChild(option);
            
            console.log(`   ${index + 1}. ${account.text}`);
        });
        
        if (childAccounts.length === 0) {
            console.warn('⚠️ No se encontraron cuentas hijas');
        } else {
            console.log('✅ Filtrado completado exitosamente');
        }
    }

    isChildAccount(accountText, parentAccount) {
        // Extraer código de cuenta del texto (formato: "CODIGO - NOMBRE")
        const codeMatch = accountText.match(/^(\d+(?:\.\d+)*)/);
        if (!codeMatch) return false;
        
        const accountCode = codeMatch[1];
        const parentCode = parentAccount.code;
        
        // Verificar si es cuenta hija (código comienza con código padre + punto)
        const isChild = accountCode.startsWith(parentCode + '.') && 
                        accountCode !== parentCode;
        
        console.log(`🔍 Verificando: ${accountCode} es hija de ${parentCode}? ${isChild ? '✅' : '❌'}`);
        return isChild;
    }

    resetPaymentForm() {
        this.paymentFormField.value = '';
        console.log('🔄 Forma de pago restablecida');
    }

    resetAccountField() {
        // Restaurar todas las opciones originales
        this.accountField.innerHTML = '';
        
        this.originalAccountOptions.forEach(account => {
            const option = document.createElement('option');
            option.value = account.value;
            option.textContent = account.text;
            option.selected = account.selected;
            this.accountField.appendChild(option);
        });
        
        console.log('🔄 Campo de cuenta restablecido con', this.originalAccountOptions.length, 'opciones');
    }

    applyInitialFilters() {
        console.log('🎯 Aplicando filtros iniciales...');
        
        setTimeout(() => {
            const companyValue = this.companyField.value;
            if (companyValue) {
                console.log('🔄 Aplicando filtro inicial para empresa:', companyValue);
                this.handleCompanyChange(companyValue);
            }
        }, 100);
    }

    // Función de test para debugging
    testFiltering(companyName = 'GUEBER', paymentName = 'Efectivo') {
        console.log(`\n🧪 EJECUTANDO TEST: ${companyName} + ${paymentName}`);
        
        // Buscar empresa
        const companyOptions = this.companyField.getElementsByTagName('option');
        let companyOption = null;
        
        for (let option of companyOptions) {
            if (option.textContent.toUpperCase().includes(companyName.toUpperCase())) {
                companyOption = option;
                break;
            }
        }
        
        if (companyOption) {
            console.log('🏢 Seleccionando empresa:', companyOption.textContent);
            this.companyField.value = companyOption.value;
            this.handleCompanyChange(companyOption.value);
            
            setTimeout(() => {
                // Buscar forma de pago
                const paymentOptions = this.paymentFormField.getElementsByTagName('option');
                let paymentOption = null;
                
                for (let option of paymentOptions) {
                    if (option.textContent.toUpperCase().includes(paymentName.toUpperCase())) {
                        paymentOption = option;
                        break;
                    }
                }
                
                if (paymentOption) {
                    console.log('💳 Seleccionando forma de pago:', paymentOption.textContent);
                    this.paymentFormField.value = paymentOption.value;
                    this.handlePaymentFormChange(paymentOption.value);
                    
                    setTimeout(() => {
                        console.log('\n📊 RESULTADO FINAL - Cuentas disponibles:');
                        const accounts = Array.from(this.accountField.getElementsByTagName('option'))
                            .filter(opt => opt.value !== '');
                        accounts.forEach((opt, idx) => {
                            console.log(`   ${idx + 1}. ${opt.textContent}`);
                            if (opt.textContent.toUpperCase().includes('CAJA GENERAL')) {
                                console.log('      ✅ ¡CAJA GENERAL ENCONTRADA!');
                            }
                        });
                        
                        if (accounts.some(opt => opt.textContent.toUpperCase().includes('CAJA GENERAL'))) {
                            console.log('\n🎉 ¡ÉXITO! El filtrado funciona correctamente');
                        } else {
                            console.log('\n❌ PROBLEMA: CAJA GENERAL no aparece');
                        }
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
        
        console.log('✅ Sistema inicializado correctamente');
        console.log('🧪 Para probar: window.testFiltering("GUEBER", "Efectivo")');
        
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
    return new IntegratedPaymentAccountHandler();
};