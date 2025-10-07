/**
 * Manejo dinámico de formas de pago vinculadas a empresas en facturas
 */

class DynamicPaymentFormHandler {
    constructor() {
        this.companyField = null;
        this.paymentFormField = null;
        this.originalPaymentMethods = [];
        this.companyPaymentMethods = {};
        this.init();
    }

    init() {
        // Esperar a que el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        console.log('DynamicPaymentFormHandler: Iniciando configuración...');

        // Buscar campos en el formulario
        this.companyField = $('#id_company');
        this.paymentFormField = $('#id_payment_form');

        if (!this.companyField.length || !this.paymentFormField.length) {
            console.log('DynamicPaymentFormHandler: Campos no encontrados, reintentando...');
            setTimeout(() => this.setup(), 500);
            return;
        }

        console.log('DynamicPaymentFormHandler: Campos encontrados');
        
        // Guardar opciones originales
        this.saveOriginalOptions();
        
        // Cargar configuración de empresa-forma de pago
        this.loadCompanyPaymentMethods();
        
        // Configurar eventos
        this.bindEvents();
        
        // Aplicar filtro inicial
        this.handleCompanyChange();
    }

    saveOriginalOptions() {
        this.originalPaymentMethods = [];
        this.paymentFormField.find('option').each((index, option) => {
            const $option = $(option);
            this.originalPaymentMethods.push({
                value: $option.val(),
                text: $option.text(),
                element: $option.clone()
            });
        });
        console.log('DynamicPaymentFormHandler: Opciones originales guardadas:', this.originalPaymentMethods.length);
    }

    async loadCompanyPaymentMethods() {
        try {
            console.log('DynamicPaymentFormHandler: Cargando configuración empresa-forma de pago...');
            
            // Hacer petición AJAX para obtener configuración
            const response = await fetch('/admin/invoicing/company-payment-methods/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                this.companyPaymentMethods = await response.json();
                console.log('DynamicPaymentFormHandler: Configuración cargada:', this.companyPaymentMethods);
            } else {
                console.warn('DynamicPaymentFormHandler: Error cargando configuración, usando fallback');
                this.companyPaymentMethods = {};
            }
        } catch (error) {
            console.warn('DynamicPaymentFormHandler: Error en petición AJAX:', error);
            this.companyPaymentMethods = {};
        }
    }

    bindEvents() {
        // Escuchar cambios en el campo empresa
        this.companyField.on('change', () => {
            this.handleCompanyChange();
        });
    }

    handleCompanyChange() {
        const selectedCompanyId = this.companyField.val();
        console.log('DynamicPaymentFormHandler: Empresa seleccionada:', selectedCompanyId);
        
        if (!selectedCompanyId) {
            // Si no hay empresa seleccionada, mostrar todas las opciones
            this.showAllPaymentMethods();
            return;
        }
        
        // Filtrar formas de pago según la empresa
        this.filterPaymentMethodsByCompany(selectedCompanyId);
    }

    filterPaymentMethodsByCompany(companyId) {
        console.log('DynamicPaymentFormHandler: Filtrando formas de pago para empresa:', companyId);
        
        // Limpiar opciones actuales
        this.paymentFormField.empty();
        
        // Agregar opción vacía
        this.paymentFormField.append('<option value="">---------</option>');
        
        // Obtener forma de pago configurada para la empresa
        const companyDefaultMethod = this.companyPaymentMethods[companyId];
        let defaultMethodSet = false;
        
        // Agregar todas las formas de pago disponibles
        this.originalPaymentMethods.forEach(method => {
            if (method.value) { // No agregar la opción vacía duplicada
                this.paymentFormField.append(method.element.clone());
                
                // Establecer como predeterminado si es el configurado en la empresa
                if (companyDefaultMethod && method.value == companyDefaultMethod.id) {
                    this.paymentFormField.val(method.value);
                    defaultMethodSet = true;
                    console.log('DynamicPaymentFormHandler: Forma de pago predeterminada establecida:', method.text);
                }
            }
        });
        
        // Si la empresa tiene configurada una forma de pago pero no se encontró, mostrar mensaje
        if (companyDefaultMethod && !defaultMethodSet) {
            console.warn('DynamicPaymentFormHandler: Forma de pago de empresa no encontrada en opciones disponibles');
        }
        
        // Disparar evento para que otros componentes reaccionen
        this.paymentFormField.trigger('change');
        
        console.log('DynamicPaymentFormHandler: Filtrado completado');
    }

    showAllPaymentMethods() {
        console.log('DynamicPaymentFormHandler: Mostrando todas las formas de pago');
        
        // Limpiar y restaurar todas las opciones
        this.paymentFormField.empty();
        
        this.originalPaymentMethods.forEach(method => {
            this.paymentFormField.append(method.element.clone());
        });
        
        this.paymentFormField.trigger('change');
    }

    getCSRFToken() {
        // Obtener token CSRF de las cookies o del formulario
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                         this.getCookie('csrftoken');
        return csrfToken;
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
}

// Inicializar cuando el documento esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Solo inicializar en la página de facturas
    if (document.querySelector('#invoice_form') || 
        window.location.pathname.includes('/invoicing/invoice/')) {
        new DynamicPaymentFormHandler();
    }
});

// También inicializar si se carga dinámicamente
if (typeof window.initDynamicPaymentFormHandler === 'undefined') {
    window.initDynamicPaymentFormHandler = function() {
        new DynamicPaymentFormHandler();
    };
}