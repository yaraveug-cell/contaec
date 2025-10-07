/**
 * Handler para mostrar campo "Detalle Transferencia" dinámicamente
 * Se activa cuando Forma de Pago = "Transferencia"
 * Usa estilos nativos del Admin Django
 * Version: 1.0 - 01/10/2025
 */

class TransferDetailHandler {
    constructor() {
        this.paymentFormField = null;
        this.transferDetailField = null;
        this.isFieldCreated = false;
        this.init();
    }

    init() {
        console.log('🚀 TransferDetailHandler: Iniciando...');
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    isInvoiceForm() {
        // Verificar si estamos en el formulario de factura
        const currentPath = window.location.pathname;
        console.log('🔍 Transfer: Verificando si es formulario de factura. URL:', currentPath);
        
        const isInvoiceUrl = currentPath.includes('/admin/invoicing/invoice/');
        console.log('✅ Transfer: Es formulario de factura:', isInvoiceUrl);
        
        return isInvoiceUrl;
    }

    isEditMode() {
        // Verificar si estamos editando una factura existente
        const currentPath = window.location.pathname;
        const isEdit = currentPath.includes('/change/');
        console.log('📝 Transfer: ¿Modo edición?:', isEdit);
        return isEdit;
    }

    setup() {
        console.log('🔧 Configurando campo Detalle Transferencia...');
        
        // Verificar si estamos en la página correcta
        if (!this.isInvoiceForm()) {
            console.log('ℹ️ No se detectó formulario de factura. Cancelando inicialización.');
            return;
        }
        
        // Buscar campo Forma de Pago
        this.paymentFormField = document.getElementById('id_payment_form');
        
        if (!this.paymentFormField) {
            this.retryCount = (this.retryCount || 0) + 1;
            if (this.retryCount > 10) { // Máximo 10 intentos (5 segundos)
                console.log('❌ Campo payment_form no encontrado después de 10 intentos. Cancelando.');
                return;
            }
            console.warn(`⚠️ Campo payment_form no encontrado, reintentando (${this.retryCount}/10)...`);
            setTimeout(() => this.setup(), 500);
            return;
        }

        console.log('✅ Campo payment_form encontrado');
        
        // Configurar evento
        this.bindEvents();
        
        // Verificar estado inicial
        this.checkInitialState();
    }

    bindEvents() {
        this.paymentFormField.addEventListener('change', (e) => {
            const selectedText = e.target.options[e.target.selectedIndex]?.text || '';
            console.log('💳 Forma de pago cambiada a:', selectedText);
            this.handlePaymentChange(selectedText);
        });
    }

    checkInitialState() {
        // Verificar si ya hay "Transferencia" seleccionada al cargar
        const selectedText = this.paymentFormField.options[this.paymentFormField.selectedIndex]?.text || '';
        if (selectedText.toLowerCase().includes('transferencia')) {
            console.log('🔄 Transferencia ya seleccionada, mostrando campo...');
            this.showTransferDetail();
            
            // Cargar valor existente si estamos editando
            this.loadExistingValue();
        }
    }
    
    loadExistingValue() {
        console.log('🔍 Transfer: Buscando valor existente...');
        
        if (!this.isEditMode()) {
            console.log('🆕 Transfer: Modo creación, no hay valor previo');
            return;
        }
        
        // Buscar valor en múltiples fuentes
        let existingValue = '';
        
        // 1. Buscar en campo oculto Django (id_transfer_detail)
        const djangoField = document.getElementById('id_transfer_detail');
        if (djangoField && djangoField.value) {
            existingValue = djangoField.value;
            console.log('✅ Transfer: Valor encontrado en campo Django:', existingValue);
        }
        
        // 2. Buscar en window.invoiceData (fallback)
        if (!existingValue && window.invoiceData?.transfer_detail) {
            existingValue = window.invoiceData.transfer_detail;
            console.log('✅ Transfer: Valor encontrado en invoiceData:', existingValue);
        }
        
        // 3. Buscar en data attributes del formulario
        if (!existingValue) {
            const form = document.querySelector('.invoice-form, form');
            if (form && form.dataset.transferDetail) {
                existingValue = form.dataset.transferDetail;
                console.log('✅ Transfer: Valor encontrado en form dataset:', existingValue);
            }
        }
        
        // Aplicar valor si existe
        if (existingValue && this.transferDetailField) {
            // 🔧 FIX: Buscar el input dentro del contenedor
            const input = this.transferDetailField.querySelector('input');
            if (input) {
                input.value = existingValue;
                console.log('📋 Transfer: Valor aplicado al input:', existingValue);
            } else {
                console.log('❌ Transfer: Input no encontrado dentro del campo');
            }
        } else if (this.isEditMode()) {
            console.log('⚠️ Transfer: No se encontró valor existente en modo edición');
        }
    }

    handlePaymentChange(selectedText) {
        if (selectedText.toLowerCase().includes('transferencia')) {
            this.showTransferDetail();
        } else {
            this.hideTransferDetail();
        }
    }

    showTransferDetail() {
        if (this.isFieldCreated) {
            console.log('📱 Campo ya existe, haciéndolo visible...');
            this.transferDetailField.style.display = 'inline-block';
            // Recargar valor por si acaso
            this.loadExistingValue();
            return;
        }

        console.log('🏗️ Creando campo Detalle Transferencia...');
        
        // Buscar la fila que contiene Forma de Pago y Cuenta
        const paymentRow = this.paymentFormField.closest('.form-row');
        if (!paymentRow) {
            console.error('❌ No se encontró la fila del formulario');
            return;
        }

        // Crear el campo de texto con estilos Django Admin
        const transferDetailDiv = document.createElement('div');
        transferDetailDiv.className = 'field-box field-transfer_detail';
        transferDetailDiv.style.cssText = `
            display: inline-block;
            margin-left: 15px;
            vertical-align: top;
        `;

        // Contenedor para label y botón
        const labelContainer = document.createElement('div');
        labelContainer.style.cssText = `
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 5px;
        `;

        const label = document.createElement('label');
        label.textContent = 'Detalle Transferencia:';
        label.className = 'required';
        label.htmlFor = 'id_transfer_detail';
        label.style.cssText = `
            font-weight: bold;
            color: #666666;
            font-size: 11px;
            text-transform: uppercase;
            font-family: "Roboto", "Lucida Grande", Verdana, Arial, sans-serif;
            white-space: nowrap;
        `;

        // Botón para ocultar/mostrar campo
        const toggleButton = document.createElement('button');
        toggleButton.type = 'button';
        toggleButton.innerHTML = '✕';
        toggleButton.title = 'Ocultar campo detalle transferencia';
        toggleButton.style.cssText = `
            background: #dc3545;
            color: white;
            border: none;
            border-radius: 50%;
            width: 18px;
            height: 18px;
            font-size: 10px;
            line-height: 1;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-left: 10px;
            transition: background-color 0.2s ease;
        `;

        // Eventos del botón
        toggleButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleFieldVisibility();
        });

        toggleButton.addEventListener('mouseenter', () => {
            toggleButton.style.backgroundColor = '#c82333';
            toggleButton.title = 'Ocultar campo (se puede mostrar de nuevo cambiando forma de pago)';
        });

        toggleButton.addEventListener('mouseleave', () => {
            toggleButton.style.backgroundColor = '#dc3545';
            toggleButton.title = 'Ocultar campo detalle transferencia';
        });

        // Ensamblar contenedor de label
        labelContainer.appendChild(label);
        labelContainer.appendChild(toggleButton);

        const input = document.createElement('input');
        input.type = 'text';
        input.name = 'transfer_detail';
        input.id = 'id_transfer_detail';
        input.className = 'vTextField';
        input.style.cssText = `
            width: 440px;
            height: 26px;
            padding: 5px 8px;
            border: 1px solid #cccccc;
            border-radius: 4px;
            font-size: 13px;
            color: #333333;
            font-family: "Roboto", "Lucida Grande", Verdana, Arial, sans-serif;
            background-color: #ffffff;
        `;
        input.placeholder = 'Ej: Banco Pichincha - Cuenta Corriente 1234567890 - Referencia detallada de la transferencia';

        // Eventos para el input
        input.addEventListener('focus', () => {
            input.style.borderColor = '#79aec8';
            input.style.boxShadow = '0 0 0 2px rgba(121, 174, 200, 0.2)';
            input.style.outline = 'none';
        });

        input.addEventListener('blur', () => {
            input.style.borderColor = '#cccccc';
            input.style.boxShadow = 'none';
        });

        input.addEventListener('hover', () => {
            if (document.activeElement !== input) {
                input.style.borderColor = '#999999';
            }
        });

        input.addEventListener('mouseleave', () => {
            if (document.activeElement !== input) {
                input.style.borderColor = '#cccccc';
            }
        });

        // 🔧 FIX: Sincronizar con campo Django oculto para guardar
        input.addEventListener('input', (e) => {
            const djangoField = document.getElementById('id_transfer_detail');
            if (djangoField) {
                djangoField.value = e.target.value;
                console.log('🔄 Transfer: Sincronizado con campo Django:', e.target.value);
            }
        });

        // Ensamblar campo
        transferDetailDiv.appendChild(labelContainer);
        transferDetailDiv.appendChild(input);

        // Insertar en la misma fila
        paymentRow.appendChild(transferDetailDiv);

        this.transferDetailField = transferDetailDiv;
        this.isFieldCreated = true;

        console.log('✅ Campo Detalle Transferencia creado y mostrado');
        
        // 🔧 FIX: Cargar valor existente inmediatamente después de crear el campo
        setTimeout(() => {
            this.loadExistingValue();
        }, 100);
    }

    hideTransferDetail() {
        if (this.isFieldCreated && this.transferDetailField) {
            console.log('🙈 Ocultando campo Detalle Transferencia...');
            this.transferDetailField.style.display = 'none';
            
            // Limpiar valor cuando se oculta
            const input = this.transferDetailField.querySelector('input');
            if (input) {
                input.value = '';
            }
        }
    }

    toggleFieldVisibility() {
        if (this.isFieldCreated && this.transferDetailField) {
            const isVisible = this.transferDetailField.style.display !== 'none';
            
            if (isVisible) {
                console.log('👁️ Usuario ocultó manualmente el campo Detalle Transferencia');
                this.transferDetailField.style.display = 'none';
                
                // Limpiar valor al ocultar manualmente
                const input = this.transferDetailField.querySelector('input');
                if (input) {
                    input.value = '';
                }
                
                // Mostrar mensaje informativo
                this.showToggleMessage('Campo ocultado. Cambia la forma de pago para mostrarlo de nuevo.');
            } else {
                console.log('👁️ Usuario mostró manualmente el campo Detalle Transferencia');
                this.transferDetailField.style.display = 'inline-block';
            }
        }
    }

    showToggleMessage(message) {
        // Crear mensaje temporal
        const messageDiv = document.createElement('div');
        messageDiv.style.cssText = `
            position: fixed;
            top: 50px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            font-size: 12px;
            font-family: "Roboto", "Lucida Grande", Verdana, Arial, sans-serif;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 10000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        messageDiv.textContent = message;
        
        document.body.appendChild(messageDiv);
        
        // Mostrar mensaje
        setTimeout(() => {
            messageDiv.style.opacity = '1';
        }, 100);
        
        // Ocultar y eliminar mensaje después de 3 segundos
        setTimeout(() => {
            messageDiv.style.opacity = '0';
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.parentNode.removeChild(messageDiv);
                }
            }, 300);
        }, 3000);
    }

    // Obtener valor del campo para envío de formulario
    getTransferDetail() {
        if (this.isFieldCreated && this.transferDetailField) {
            const input = this.transferDetailField.querySelector('input');
            return input ? input.value : '';
        }
        return '';
    }

    // Establecer valor del campo
    setTransferDetail(value) {
        if (this.isFieldCreated && this.transferDetailField) {
            const input = this.transferDetailField.querySelector('input');
            if (input) {
                input.value = value || '';
            }
        }
    }
}

// Inicializar handler
let transferDetailHandler = null;

function initTransferDetailHandler() {
    // Solo inicializar en páginas de factura
    const isInvoicePage = document.querySelector('#invoice_form') || 
                         window.location.pathname.includes('/invoicing/invoice/');
    
    if (isInvoicePage) {
        console.log('🎯 Inicializando TransferDetailHandler...');
        transferDetailHandler = new TransferDetailHandler();
        
        // Funciones globales para interacción
        window.getTransferDetail = () => {
            return transferDetailHandler ? transferDetailHandler.getTransferDetail() : '';
        };
        
        window.setTransferDetail = (value) => {
            if (transferDetailHandler) {
                transferDetailHandler.setTransferDetail(value);
            }
        };
        
        console.log('✅ TransferDetailHandler inicializado');
    }
}

// Ejecutar cuando DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTransferDetailHandler);
} else {
    initTransferDetailHandler();
}

// Exportar para acceso global
window.TransferDetailHandler = TransferDetailHandler;