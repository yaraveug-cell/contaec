/**
 * Manejo inteligente del campo bank_observations
 * Muestra/oculta el campo según la forma de pago seleccionada
 * Mantiene la estética congruente del admin Django
 */

(function($) {
    'use strict';
    
    // Configuración
    const CONFIG = {
        TRANSFER_KEYWORDS: ['TRANSFERENCIA', 'TRANSFER', 'BANCARIA'],
        ANIMATION_DURATION: 300,
        REQUIRED_CLASS: 'required',
        SHOW_CLASS: 'show-for-transfer',
        ANIMATE_CLASS: 'animate-in'
    };
    
    class BankObservationsHandler {
        constructor() {
            this.paymentField = null;
            this.bankObservationsField = null;
            this.bankTextarea = null;
            this.initialized = false;
            
            this.init();
        }
        
        init() {
            $(document).ready(() => {
                this.setupFields();
                this.bindEvents();
                this.setInitialState();
                this.initialized = true;
                
                console.log('🏦 BankObservationsHandler inicializado correctamente');
            });
        }
        
        setupFields() {
            // Buscar campos en el DOM
            this.paymentField = $('#id_payment_form');
            this.bankObservationsField = $('.field-bank_observations');
            this.bankTextarea = $('#id_bank_observations');
            
            if (!this.paymentField.length) {
                console.warn('⚠️ Campo payment_form no encontrado');
                return;
            }
            
            if (!this.bankObservationsField.length) {
                console.warn('⚠️ Campo bank_observations no encontrado');
                return;
            }
            
            // Configurar placeholder contextual
            this.setupPlaceholder();
            
            // Configurar help text dinámico
            this.setupHelpText();
        }
        
        bindEvents() {
            if (!this.paymentField.length) return;
            
            // Evento change en forma de pago
            this.paymentField.on('change', (e) => {
                this.handlePaymentFormChange();
            });
            
            // Validación en tiempo real del textarea
            this.bankTextarea.on('input', (e) => {
                this.validateBankObservations();
            });
            
            // Evento focus para mejor UX
            this.bankTextarea.on('focus', () => {
                this.onFieldFocus();
            });
        }
        
        setupPlaceholder() {
            if (!this.bankTextarea.length) return;
            
            const placeholder = 'Ref: 123456789 - Banco Pichincha - 06/10/2025';
            this.bankTextarea.attr('placeholder', placeholder);
        }
        
        setupHelpText() {
            if (!this.bankObservationsField.length) return;
            
            // Agregar help text si no existe
            let helpText = this.bankObservationsField.find('.help');
            if (!helpText.length) {
                helpText = $('<div class="help"></div>');
                this.bankObservationsField.append(helpText);
            }
            
            helpText.text('Referencia, banco origen y detalles de la transferencia');
        }
        
        setInitialState() {
            // Determinar estado inicial basado en la forma de pago actual
            const currentPayment = this.getCurrentPaymentMethod();
            
            if (this.isTransferPayment(currentPayment)) {
                this.showBankObservationsField();
            } else {
                this.hideBankObservationsField();
            }
        }
        
        handlePaymentFormChange() {
            const selectedPayment = this.getCurrentPaymentMethod();
            
            console.log(`💳 Forma de pago cambiada: ${selectedPayment}`);
            
            if (this.isTransferPayment(selectedPayment)) {
                this.showBankObservationsField();
                console.log('🏦 Campo observaciones bancarias mostrado');
            } else {
                this.hideBankObservationsField();
                console.log('🏦 Campo observaciones bancarias ocultado');
            }
        }
        
        getCurrentPaymentMethod() {
            if (!this.paymentField.length) return '';
            
            const selectedOption = this.paymentField.find('option:selected');
            return selectedOption.text().trim().toUpperCase();
        }
        
        isTransferPayment(paymentMethod) {
            if (!paymentMethod) return false;
            
            return CONFIG.TRANSFER_KEYWORDS.some(keyword => 
                paymentMethod.includes(keyword)
            );
        }
        
        showBankObservationsField() {
            if (!this.bankObservationsField.length) return;
            
            // Mostrar campo con animación
            this.bankObservationsField
                .addClass(CONFIG.SHOW_CLASS)
                .addClass(CONFIG.ANIMATE_CLASS);
            
            // Hacer campo requerido
            this.makeFieldRequired(true);
            
            // Focus después de la animación
            setTimeout(() => {
                this.bankTextarea.focus();
            }, CONFIG.ANIMATION_DURATION);
        }
        
        hideBankObservationsField() {
            if (!this.bankObservationsField.length) return;
            
            // Ocultar campo
            this.bankObservationsField
                .removeClass(CONFIG.SHOW_CLASS)
                .removeClass(CONFIG.ANIMATE_CLASS);
            
            // Quitar requerimiento
            this.makeFieldRequired(false);
            
            // Limpiar valor si no es transferencia
            this.clearFieldValue();
        }
        
        makeFieldRequired(required) {
            const label = this.bankObservationsField.find('label');
            
            if (required) {
                this.bankObservationsField.addClass(CONFIG.REQUIRED_CLASS);
                this.bankTextarea.attr('required', true);
            } else {
                this.bankObservationsField.removeClass(CONFIG.REQUIRED_CLASS);
                this.bankTextarea.removeAttr('required');
            }
        }
        
        clearFieldValue() {
            // Solo limpiar si está vacío o tiene contenido genérico
            const currentValue = this.bankTextarea.val().trim();
            
            if (!currentValue || currentValue.length < 10) {
                this.bankTextarea.val('');
            }
        }
        
        validateBankObservations() {
            if (!this.bankTextarea.length) return;
            
            const value = this.bankTextarea.val().trim();
            const isTransfer = this.isTransferPayment(this.getCurrentPaymentMethod());
            
            // Validar solo si es transferencia
            if (isTransfer) {
                if (value.length === 0) {
                    this.showValidationError('Las observaciones bancarias son requeridas para transferencias');
                } else if (value.length < 10) {
                    this.showValidationWarning('Proporcione más detalles sobre la transferencia');
                } else {
                    this.clearValidationMessages();
                }
            }
        }
        
        showValidationError(message) {
            this.clearValidationMessages();
            
            const errorDiv = $(`<div class="bank-validation-error" style="color: #e74c3c; font-size: 11px; margin-top: 3px;">${message}</div>`);
            this.bankObservationsField.append(errorDiv);
            
            this.bankTextarea.css('border-color', '#e74c3c');
        }
        
        showValidationWarning(message) {
            this.clearValidationMessages();
            
            const warningDiv = $(`<div class="bank-validation-warning" style="color: #f39c12; font-size: 11px; margin-top: 3px;">${message}</div>`);
            this.bankObservationsField.append(warningDiv);
            
            this.bankTextarea.css('border-color', '#f39c12');
        }
        
        clearValidationMessages() {
            this.bankObservationsField.find('.bank-validation-error, .bank-validation-warning').remove();
            this.bankTextarea.css('border-color', '');
        }
        
        onFieldFocus() {
            // Mejorar UX al hacer focus
            this.clearValidationMessages();
            
            // Expandir ligeramente el textarea (reducido para Nivel 2)
            this.bankTextarea.animate({
                'min-height': '45px'
            }, 150);
        }
        
        // Método público para validación desde otros scripts
        isValid() {
            const currentPayment = this.getCurrentPaymentMethod();
            const isTransfer = this.isTransferPayment(currentPayment);
            
            if (!isTransfer) return true;
            
            const value = this.bankTextarea.val().trim();
            return value.length >= 10;
        }
        
        // Método público para obtener datos bancarios estructurados
        getBankingData() {
            if (!this.isTransferPayment(this.getCurrentPaymentMethod())) {
                return null;
            }
            
            const observations = this.bankTextarea.val().trim();
            
            return {
                is_transfer: true,
                observations: observations,
                payment_method: this.getCurrentPaymentMethod(),
                has_sufficient_details: observations.length >= 10
            };
        }
    }
    
    // Inicializar cuando el DOM esté listo
    let bankHandler = null;
    
    $(document).ready(function() {
        bankHandler = new BankObservationsHandler();
        
        // Hacer disponible globalmente para otros scripts
        window.BankObservationsHandler = bankHandler;
    });
    
    // Integración con el sistema de validación de facturas existente
    $(document).on('form-submit-validation', function(event, form) {
        if (bankHandler && bankHandler.initialized) {
            const isValid = bankHandler.isValid();
            
            if (!isValid) {
                event.preventDefault();
                bankHandler.showValidationError('Complete las observaciones bancarias antes de guardar');
                return false;
            }
        }
    });
    
})(django.jQuery);