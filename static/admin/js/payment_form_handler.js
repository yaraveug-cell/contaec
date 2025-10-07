/**
 * Manejo de filtrado dinámico del campo Cuenta basado en Forma de Pago
 * Versión simplificada sin AJAX
 */

(function($) {
    'use strict';

    class PaymentFormHandler {
        constructor() {
            this.paymentFormField = null;
            this.accountField = null;
            this.originalOptions = [];
            this.init();
        }

        init() {
            console.log('PaymentFormHandler: Inicializando versión simplificada...');
            // Esperar a que el DOM esté listo
            $(document).ready(() => {
                console.log('PaymentFormHandler: DOM listo');
                this.setupFields();
                this.bindEvents();
                // Aplicar filtro inicial si ya hay un valor seleccionado
                this.handlePaymentFormChange();
            });
        }

        setupFields() {
            this.paymentFormField = $('#id_payment_form');
            this.accountField = $('#id_account');

            if (!this.paymentFormField.length || !this.accountField.length) {
                console.log('PaymentFormHandler: Campos no encontrados, esperando...');
                // Reintentar después de un breve delay
                setTimeout(() => this.setupFields(), 500);
                return;
            }

            console.log('PaymentFormHandler: Campos configurados correctamente');
            
            // Guardar todas las opciones originales
            this.saveOriginalOptions();
        }

        saveOriginalOptions() {
            this.originalOptions = [];
            this.accountField.find('option').each((index, option) => {
                const $option = $(option);
                this.originalOptions.push({
                    value: $option.val(),
                    text: $option.text(),
                    element: $option.clone()
                });
            });
            console.log('PaymentFormHandler: Opciones originales guardadas:', this.originalOptions.length);
        }

        bindEvents() {
            if (!this.paymentFormField || !this.paymentFormField.length) {
                return;
            }

            // Escuchar cambios en forma de pago
            this.paymentFormField.on('change', () => {
                this.handlePaymentFormChange();
            });
        }

        handlePaymentFormChange() {
            if (!this.paymentFormField || !this.accountField) {
                return;
            }

            const paymentForm = this.paymentFormField.val();
            console.log('PaymentFormHandler: Forma de pago cambiada a:', paymentForm);

            if (paymentForm === 'EFECTIVO') {
                this.filterCashAccounts();
            } else if (paymentForm === 'CREDITO') {
                this.filterClientAccounts();
            } else if (paymentForm === 'TRANSFERENCIA') {
                this.filterBankAccounts();
            } else {
                this.showAllAccounts();
            }
        }

        filterCashAccounts() {
            console.log('PaymentFormHandler: Filtrando cuentas de caja...');
            
            // Limpiar opciones actuales
            this.accountField.empty();
            
            // Agregar opción vacía
            this.accountField.append('<option value="">---------</option>');
            
            // Filtrar por cuentas que contengan "CAJA" en el texto
            const cashAccounts = this.originalOptions.filter(option => {
                const text = option.text.toUpperCase();
                return option.value && (
                    text.includes('CAJA') || 
                    text.includes('EFECTIVO') ||
                    option.value === '' // Mantener opción vacía
                );
            });
            
            console.log('PaymentFormHandler: Cuentas de caja encontradas:', cashAccounts.length - 1); // -1 por la opción vacía
            
            // Agregar cuentas de caja
            let firstAccount = null;
            cashAccounts.forEach(account => {
                if (account.value) { // No agregar la opción vacía otra vez
                    this.accountField.append(account.element);
                    if (!firstAccount) {
                        firstAccount = account;
                    }
                }
            });

            // Establecer por defecto la primera cuenta de caja
            if (firstAccount) {
                this.accountField.val(firstAccount.value);
                console.log('PaymentFormHandler: Cuenta de caja por defecto establecida:', firstAccount.text);
            }
        }

        filterClientAccounts() {
            console.log('PaymentFormHandler: Filtrando cuentas de CLIENTES RELACIONADOS...');
            
            // Limpiar opciones actuales
            this.accountField.empty();
            
            // Agregar opción vacía
            this.accountField.append('<option value="">---------</option>');
            
            // Filtrar específicamente por cuentas que tengan "CLIENTES RELACIONADOS" como cuenta padre
            const clientAccounts = this.originalOptions.filter(option => {
                const text = option.text.toUpperCase();
                return option.value && (
                    text.includes('CLIENTES RELACIONADOS') ||
                    text.includes('CLIENTE CREDITO AUTORIZADO') ||
                    text.includes('DOC CUENTAS COBRAR CLIENTES') ||
                    (text.includes('CLIENTE') && text.includes('CREDITO')) ||
                    option.value === '' // Mantener opción vacía
                );
            });
            
            console.log('PaymentFormHandler: Cuentas de CLIENTES RELACIONADOS encontradas:', clientAccounts.length - 1);
            
            // Agregar cuentas de clientes relacionados
            let firstAccount = null;
            clientAccounts.forEach(account => {
                if (account.value) { // No agregar la opción vacía otra vez
                    this.accountField.append(account.element);
                    if (!firstAccount) {
                        firstAccount = account;
                    }
                }
            });

            // Establecer por defecto la primera cuenta de clientes relacionados
            if (firstAccount) {
                this.accountField.val(firstAccount.value);
                console.log('PaymentFormHandler: Cuenta de CLIENTES RELACIONADOS por defecto establecida:', firstAccount.text);
            }
        }

        filterBankAccounts() {
            console.log('PaymentFormHandler: Filtrando cuentas de bancos...');
            
            // Limpiar opciones actuales
            this.accountField.empty();
            
            // Agregar opción vacía
            this.accountField.append('<option value="">---------</option>');
            
            // Filtrar por cuentas que contengan términos relacionados con bancos
            const bankAccounts = this.originalOptions.filter(option => {
                const text = option.text.toUpperCase();
                return option.value && (
                    text.includes('BANCO') || 
                    text.includes('BANCOS') ||
                    text.includes('BANCARIO') ||
                    text.includes('INTERNACIONAL') ||
                    text.includes('PICHINCHA') ||
                    text.includes('GUAYAQUIL') ||
                    text.includes('PACIFICO') ||
                    text.includes('TRANSFERENCIA') ||
                    option.value === '' // Mantener opción vacía
                );
            });
            
            console.log('PaymentFormHandler: Cuentas de bancos encontradas:', bankAccounts.length - 1);
            
            // Agregar cuentas de bancos
            let firstAccount = null;
            bankAccounts.forEach(account => {
                if (account.value) { // No agregar la opción vacía otra vez
                    this.accountField.append(account.element);
                    if (!firstAccount) {
                        firstAccount = account;
                    }
                }
            });

            // Establecer por defecto la primera cuenta bancaria
            if (firstAccount) {
                this.accountField.val(firstAccount.value);
                console.log('PaymentFormHandler: Cuenta bancaria por defecto establecida:', firstAccount.text);
            }
        }

        showAllAccounts() {
            console.log('PaymentFormHandler: Mostrando todas las cuentas...');
            
            // Limpiar opciones actuales
            this.accountField.empty();
            
            // Restaurar todas las opciones originales
            this.originalOptions.forEach(option => {
                this.accountField.append(option.element);
            });
            
            console.log('PaymentFormHandler: Todas las cuentas restauradas');
        }
    }

    // Inicializar cuando el documento esté listo
    new PaymentFormHandler();

})(django.jQuery);