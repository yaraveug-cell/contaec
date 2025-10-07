"""
Vista de conciliación bancaria
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

from ..models import (
    BankAccount, ExtractoBancario, BankTransaction, 
    ExtractoBancarioDetalle
)
from ..forms import ReconciliationFilterForm, ReconciliationForm
from apps.core.mixins import CompanyContextMixin


class ReconciliationView(LoginRequiredMixin, CompanyContextMixin, TemplateView):
    """
    Vista principal para la conciliación bancaria manual
    """
    template_name = 'banking/conciliacion_bancaria.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Formulario de filtros
        filter_form = ReconciliationFilterForm(
            data=self.request.GET or None,
            company=self.get_current_company()
        )
        
        context['filter_form'] = filter_form
        context['bank_account'] = None
        context['extracto'] = None
        context['transactions'] = []
        context['extracto_items'] = []
        context['saldo_inicial_sistema'] = Decimal('0.00')
        context['saldo_final_sistema'] = Decimal('0.00')
        context['saldo_inicial_extracto'] = Decimal('0.00')
        context['saldo_final_extracto'] = Decimal('0.00')
        context['diferencia'] = Decimal('0.00')
        
        # Si hay filtros aplicados, cargar datos
        if filter_form.is_valid():
            bank_account = filter_form.cleaned_data.get('bank_account')
            extracto = filter_form.cleaned_data.get('extracto')
            fecha_desde = filter_form.cleaned_data.get('fecha_desde')
            fecha_hasta = filter_form.cleaned_data.get('fecha_hasta')
            
            if bank_account:
                context['bank_account'] = bank_account
                
                # Actualizar opciones de extracto
                filter_form.filter_extractos(bank_account)
                
                # Obtener transacciones del sistema
                transactions_qs = BankTransaction.objects.filter(
                    bank_account=bank_account
                ).select_related('bank_account__bank')
                
                # Aplicar filtros de fecha
                if fecha_desde:
                    transactions_qs = transactions_qs.filter(
                        transaction_date__gte=fecha_desde
                    )
                if fecha_hasta:
                    transactions_qs = transactions_qs.filter(
                        transaction_date__lte=fecha_hasta
                    )
                
                # Solo mostrar no conciliadas por defecto
                if not self.request.GET.get('show_all'):
                    transactions_qs = transactions_qs.filter(is_reconciled=False)
                
                context['transactions'] = transactions_qs.order_by('transaction_date')
                
                # Calcular saldos del sistema
                if context['transactions']:
                    context['saldo_inicial_sistema'] = bank_account.initial_balance
                    saldo_acumulado = bank_account.initial_balance
                    for trans in context['transactions']:
                        saldo_acumulado += trans.signed_amount
                    context['saldo_final_sistema'] = saldo_acumulado
                
                # Si hay extracto seleccionado
                if extracto:
                    context['extracto'] = extracto
                    
                    # Obtener items del extracto
                    extracto_items_qs = ExtractoBancarioDetalle.objects.filter(
                        extracto=extracto
                    )
                    
                    # Solo mostrar no conciliadas por defecto
                    if not self.request.GET.get('show_all'):
                        extracto_items_qs = extracto_items_qs.filter(is_reconciled=False)
                    
                    context['extracto_items'] = extracto_items_qs.order_by('fecha')
                    context['saldo_inicial_extracto'] = extracto.initial_balance
                    context['saldo_final_extracto'] = extracto.final_balance
                    
                    # Calcular diferencia
                    context['diferencia'] = (
                        context['saldo_final_extracto'] - 
                        context['saldo_final_sistema']
                    )
        
        # Formulario de conciliación
        context['reconciliation_form'] = ReconciliationForm(
            transactions=context['transactions'],
            extracto_items=context['extracto_items']
        )
        
        return context
    
    def post(self, request, *args, **kwargs):
        """
        Procesar la conciliación de transacciones seleccionadas
        """
        action = request.POST.get('action')
        
        if action == 'reconcile':
            return self._handle_reconciliation(request)
        elif action == 'unreconicle':
            return self._handle_unreconciliation(request)
        
        messages.error(request, 'Acción no válida')
        return redirect(request.path)
    
    def _handle_reconciliation(self, request):
        """
        Marca como conciliadas las transacciones seleccionadas
        """
        transaction_ids = request.POST.getlist('reconcile_transactions')
        extracto_item_ids = request.POST.getlist('reconcile_extracto_items')
        
        reconciled_count = 0
        
        try:
            with transaction.atomic():
                # Conciliar transacciones del sistema
                if transaction_ids:
                    transactions = BankTransaction.objects.filter(
                        id__in=transaction_ids,
                        bank_account__company=self.get_current_company()
                    )
                    
                    for trans in transactions:
                        trans.is_reconciled = True
                        trans.reconciliation_date = timezone.now()
                        trans.reconciled_by = request.user
                        trans.save()
                        reconciled_count += 1
                
                # Conciliar items del extracto
                if extracto_item_ids:
                    extracto_items = ExtractoBancarioDetalle.objects.filter(
                        id__in=extracto_item_ids,
                        extracto__bank_account__company=self.get_current_company()
                    )
                    
                    for item in extracto_items:
                        item.is_reconciled = True
                        item.save()
                        reconciled_count += 1
                
                if reconciled_count > 0:
                    messages.success(
                        request, 
                        f'Se conciliaron {reconciled_count} elementos exitosamente'
                    )
                else:
                    messages.warning(request, 'No se seleccionaron elementos para conciliar')
                    
        except Exception as e:
            messages.error(request, f'Error al conciliar: {str(e)}')
        
        return redirect(request.path + '?' + request.GET.urlencode())
    
    def _handle_unreconciliation(self, request):
        """
        Desmarca como conciliadas las transacciones seleccionadas
        """
        transaction_ids = request.POST.getlist('reconcile_transactions')
        extracto_item_ids = request.POST.getlist('reconcile_extracto_items')
        
        unreconciled_count = 0
        
        try:
            with transaction.atomic():
                # Desconciliar transacciones del sistema
                if transaction_ids:
                    transactions = BankTransaction.objects.filter(
                        id__in=transaction_ids,
                        bank_account__company=self.get_current_company()
                    )
                    
                    for trans in transactions:
                        trans.is_reconciled = False
                        trans.reconciliation_date = None
                        trans.reconciled_by = None
                        trans.save()
                        unreconciled_count += 1
                
                # Desconciliar items del extracto
                if extracto_item_ids:
                    extracto_items = ExtractoBancarioDetalle.objects.filter(
                        id__in=extracto_item_ids,
                        extracto__bank_account__company=self.get_current_company()
                    )
                    
                    for item in extracto_items:
                        item.is_reconciled = False
                        item.matched_transaction = None
                        item.save()
                        unreconciled_count += 1
                
                if unreconciled_count > 0:
                    messages.success(
                        request, 
                        f'Se desconciliaron {unreconciled_count} elementos exitosamente'
                    )
                else:
                    messages.warning(request, 'No se seleccionaron elementos para desconciliar')
                    
        except Exception as e:
            messages.error(request, f'Error al desconciliar: {str(e)}')
        
        return redirect(request.path + '?' + request.GET.urlencode())


class ReconciliationAjaxView(LoginRequiredMixin, CompanyContextMixin, TemplateView):
    """
    Vista AJAX para operaciones de conciliación
    """
    
    def get(self, request, *args, **kwargs):
        """
        Obtener datos para AJAX
        """
        action = request.GET.get('action')
        
        if action == 'get_extractos':
            bank_account_id = request.GET.get('bank_account_id')
            if bank_account_id:
                extractos = ExtractoBancario.objects.filter(
                    bank_account_id=bank_account_id,
                    bank_account__company=self.get_current_company()
                ).order_by('-period_end')
                
                data = [
                    {
                        'id': extracto.id,
                        'text': f"{extracto.period_start} - {extracto.period_end}"
                    }
                    for extracto in extractos
                ]
                
                return JsonResponse({'extractos': data})
        
        return JsonResponse({'error': 'Acción no válida'}, status=400)