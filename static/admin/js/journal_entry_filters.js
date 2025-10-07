(function($) {
    'use strict';
    
    $(document).ready(function() {
        // Filtrar cuentas cuando cambie la empresa seleccionada
        var companyField = $('#id_company');
        
        if (companyField.length) {
            companyField.change(function() {
                var companyId = $(this).val();
                filterAccountFields(companyId);
            });
            
            // Filtrar al cargar la página si ya hay una empresa seleccionada
            var initialCompanyId = companyField.val();
            if (initialCompanyId) {
                filterAccountFields(initialCompanyId);
            }
        }
        
        function filterAccountFields(companyId) {
            // Filtrar todos los selectores de cuenta en los inlines
            $('.field-account select').each(function() {
                var accountSelect = $(this);
                var currentValue = accountSelect.val();
                
                if (companyId) {
                    // Hacer petición AJAX para obtener cuentas de la empresa
                    $.ajax({
                        url: '/admin/accounting/get_company_accounts/',
                        data: {
                            'company_id': companyId
                        },
                        success: function(data) {
                            // Limpiar y repoblar el select
                            accountSelect.empty();
                            accountSelect.append('<option value="">---------</option>');
                            
                            $.each(data.accounts, function(index, account) {
                                var selected = (account.id == currentValue) ? ' selected' : '';
                                accountSelect.append(
                                    '<option value="' + account.id + '"' + selected + '>' + 
                                    account.code + ' - ' + account.name + 
                                    '</option>'
                                );
                            });
                        }
                    });
                } else {
                    // Si no hay empresa, limpiar el select
                    accountSelect.empty();
                    accountSelect.append('<option value="">---------</option>');
                }
            });
        }
        
        // También aplicar el filtro cuando se añadan nuevas filas inline
        $(document).on('click', '.add-row a', function() {
            setTimeout(function() {
                var companyId = companyField.val();
                if (companyId) {
                    filterAccountFields(companyId);
                }
            }, 500);
        });
    });
})(django.jQuery);