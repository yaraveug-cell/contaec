"""
Vistas para reportes de conciliación bancaria
FASE 1 (Esenciales): Estado de Conciliación por Cuenta, Diferencias No Conciliadas, Extracto de Conciliación Mensual
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q, Case, When, Value, DecimalField, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from ..models import (
    BankAccount, ExtractoBancario, BankTransaction, 
    ExtractoBancarioDetalle
)
from apps.core.mixins import CompanyContextMixin


class ReportesIndexView(LoginRequiredMixin, TemplateView):
    """
    Vista del índice principal de reportes
    """
    template_name = 'banking/reportes/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fecha_generacion'] = timezone.now()
        return context


class EstadoConciliacionPorCuentaView(LoginRequiredMixin, CompanyContextMixin, TemplateView):
    """
    Reporte: Estado de Conciliación por Cuenta
    Muestra el estado actual de conciliación de todas las cuentas bancarias
    """
    template_name = 'banking/reportes/estado_conciliacion_cuenta.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener todas las cuentas de la empresa
        cuentas = BankAccount.objects.filter(
            company=self.get_current_company(),
            is_active=True
        ).select_related('bank')
        
        # Preparar datos del reporte
        datos_reporte = []
        
        for cuenta in cuentas:
            # Obtener estadísticas de transacciones del sistema
            transacciones_stats = BankTransaction.objects.filter(
                bank_account=cuenta
            ).aggregate(
                total_transacciones=Count('id'),
                conciliadas=Count('id', filter=Q(is_reconciled=True)),
                no_conciliadas=Count('id', filter=Q(is_reconciled=False)),
                monto_conciliado=Sum(
                    Case(
                        When(is_reconciled=True, then='amount'),
                        default=Value(0),
                        output_field=DecimalField()
                    )
                ),
                monto_no_conciliado=Sum(
                    Case(
                        When(is_reconciled=False, then='amount'),
                        default=Value(0),
                        output_field=DecimalField()
                    )
                )
            )
            
            # Obtener estadísticas de extractos
            extractos_stats = ExtractoBancario.objects.filter(
                bank_account=cuenta
            ).aggregate(
                total_extractos=Count('id'),
                extractos_procesados=Count('id', filter=Q(status='processed')),
                extractos_conciliados=Count('id', filter=Q(status='reconciled'))
            )
            
            # Obtener estadísticas de detalles de extractos
            detalles_stats = ExtractoBancarioDetalle.objects.filter(
                extracto__bank_account=cuenta
            ).aggregate(
                total_items=Count('id'),
                items_conciliados=Count('id', filter=Q(is_reconciled=True)),
                items_no_conciliados=Count('id', filter=Q(is_reconciled=False))
            )
            
            # Calcular porcentajes
            porcentaje_transacciones = 0
            if transacciones_stats['total_transacciones']:
                porcentaje_transacciones = (
                    transacciones_stats['conciliadas'] / 
                    transacciones_stats['total_transacciones'] * 100
                )
            
            porcentaje_extractos = 0
            if detalles_stats['total_items']:
                porcentaje_extractos = (
                    detalles_stats['items_conciliados'] / 
                    detalles_stats['total_items'] * 100
                )
            
            # Último extracto procesado
            ultimo_extracto = ExtractoBancario.objects.filter(
                bank_account=cuenta,
                status__in=['processed', 'reconciled']
            ).order_by('-period_end').first()
            
            datos_reporte.append({
                'cuenta': cuenta,
                'transacciones': transacciones_stats,
                'extractos': extractos_stats,
                'detalles': detalles_stats,
                'porcentaje_transacciones': round(porcentaje_transacciones, 2),
                'porcentaje_extractos': round(porcentaje_extractos, 2),
                'ultimo_extracto': ultimo_extracto,
                'saldo_inicial': cuenta.initial_balance,
                'monto_conciliado': transacciones_stats['monto_conciliado'] or Decimal('0.00'),
                'monto_no_conciliado': transacciones_stats['monto_no_conciliado'] or Decimal('0.00')
            })
        
        context['datos_reporte'] = datos_reporte
        context['fecha_reporte'] = timezone.now()
        context['total_cuentas'] = len(datos_reporte)
        
        return context


class DiferenciasNoConciliadasView(LoginRequiredMixin, CompanyContextMixin, TemplateView):
    """
    Reporte: Diferencias No Conciliadas
    Muestra todas las transacciones y items de extracto que no han sido conciliados
    """
    template_name = 'banking/reportes/diferencias_no_conciliadas.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtros de la request
        cuenta_id = self.request.GET.get('cuenta')
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        
        # Preparar queryset base para cuentas de la empresa
        cuentas_qs = BankAccount.objects.filter(
            company=self.get_current_company(),
            is_active=True
        ).select_related('bank')
        
        # Aplicar filtro de cuenta si se especifica
        if cuenta_id:
            try:
                cuenta_seleccionada = get_object_or_404(BankAccount, id=cuenta_id, company=self.get_current_company())
                cuentas_qs = cuentas_qs.filter(id=cuenta_id)
                context['cuenta_seleccionada'] = cuenta_seleccionada
            except (ValueError, BankAccount.DoesNotExist):
                pass
        
        # Obtener transacciones no conciliadas
        transacciones_qs = BankTransaction.objects.filter(
            bank_account__in=cuentas_qs,
            is_reconciled=False
        ).select_related('bank_account__bank')
        
        # Aplicar filtros de fecha
        if fecha_desde:
            try:
                fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                transacciones_qs = transacciones_qs.filter(transaction_date__gte=fecha_desde_obj)
                context['fecha_desde'] = fecha_desde
            except ValueError:
                pass
        
        if fecha_hasta:
            try:
                fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                transacciones_qs = transacciones_qs.filter(transaction_date__lte=fecha_hasta_obj)
                context['fecha_hasta'] = fecha_hasta
            except ValueError:
                pass
        
        # Obtener items de extracto no conciliados
        extracto_items_qs = ExtractoBancarioDetalle.objects.filter(
            extracto__bank_account__in=cuentas_qs,
            is_reconciled=False
        ).select_related('extracto__bank_account__bank')
        
        # Aplicar mismos filtros de fecha
        if fecha_desde:
            try:
                fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                extracto_items_qs = extracto_items_qs.filter(fecha__gte=fecha_desde_obj)
            except ValueError:
                pass
        
        if fecha_hasta:
            try:
                fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                extracto_items_qs = extracto_items_qs.filter(fecha__lte=fecha_hasta_obj)
            except ValueError:
                pass
        
        # Agrupar por cuenta
        diferencias_por_cuenta = {}
        
        for cuenta in cuentas_qs:
            transacciones_cuenta = transacciones_qs.filter(bank_account=cuenta).order_by('-transaction_date')
            extracto_items_cuenta = extracto_items_qs.filter(extracto__bank_account=cuenta).order_by('-fecha')
            
            # Calcular totales
            total_transacciones = transacciones_cuenta.aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')
            
            total_extracto_debitos = extracto_items_cuenta.filter(
                debito__isnull=False
            ).aggregate(total=Sum('debito'))['total'] or Decimal('0.00')
            
            total_extracto_creditos = extracto_items_cuenta.filter(
                credito__isnull=False
            ).aggregate(total=Sum('credito'))['total'] or Decimal('0.00')
            
            diferencias_por_cuenta[cuenta.id] = {
                'cuenta': cuenta,
                'transacciones': transacciones_cuenta,
                'extracto_items': extracto_items_cuenta,
                'total_transacciones': total_transacciones,
                'total_extracto_debitos': total_extracto_debitos,
                'total_extracto_creditos': total_extracto_creditos,
                'diferencia_neta': total_extracto_creditos - total_extracto_debitos - total_transacciones
            }
        
        # Lista de todas las cuentas para el filtro
        context['todas_las_cuentas'] = BankAccount.objects.filter(
            company=self.get_current_company(),
            is_active=True
        ).select_related('bank')
        
        context['diferencias_por_cuenta'] = diferencias_por_cuenta
        context['fecha_reporte'] = timezone.now()
        context['total_cuentas_con_diferencias'] = len([
            d for d in diferencias_por_cuenta.values() 
            if d['transacciones'] or d['extracto_items']
        ])
        
        return context


class ExtractoConciliacionMensualView(LoginRequiredMixin, CompanyContextMixin, TemplateView):
    """
    Reporte: Extracto de Conciliación Mensual
    Genera un reporte detallado de conciliación para una cuenta específica en un mes
    """
    template_name = 'banking/reportes/extracto_conciliacion_mensual.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Parámetros requeridos
        cuenta_id = self.request.GET.get('cuenta')
        año = self.request.GET.get('año')
        mes = self.request.GET.get('mes')
        
        # Validaciones
        cuenta = None
        fecha_inicio = None
        fecha_fin = None
        
        if cuenta_id:
            try:
                cuenta = get_object_or_404(BankAccount, id=cuenta_id, company=self.get_current_company())
            except (ValueError, BankAccount.DoesNotExist):
                pass
        
        if año and mes:
            try:
                año_int = int(año)
                mes_int = int(mes)
                fecha_inicio = datetime(año_int, mes_int, 1).date()
                
                # Último día del mes
                if mes_int == 12:
                    fecha_fin = datetime(año_int + 1, 1, 1).date() - timedelta(days=1)
                else:
                    fecha_fin = datetime(año_int, mes_int + 1, 1).date() - timedelta(days=1)
            except (ValueError, TypeError):
                pass
        
        # Si no hay parámetros, usar cuenta y mes actual por defecto
        if not cuenta:
            cuenta = BankAccount.objects.filter(
                company=self.get_current_company(),
                is_active=True
            ).first()
        
        if not fecha_inicio:
            hoy = timezone.now().date()
            fecha_inicio = datetime(hoy.year, hoy.month, 1).date()
            fecha_fin = (fecha_inicio.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
        reporte_data = None
        
        if cuenta and fecha_inicio and fecha_fin:
            # Obtener saldo inicial (al final del mes anterior)
            saldo_inicial = cuenta.initial_balance
            
            # Transacciones anteriores al período
            transacciones_anteriores = BankTransaction.objects.filter(
                bank_account=cuenta,
                transaction_date__lt=fecha_inicio
            ).aggregate(
                total=Sum(Case(
                    When(transaction_type__in=['debit', 'transfer_out', 'fee'], then=Value(-1) * F('amount')),
                    default=F('amount'),
                    output_field=DecimalField()
                ))
            )['total'] or Decimal('0.00')
            
            saldo_inicial += transacciones_anteriores
            
            # Transacciones del período
            transacciones_periodo = BankTransaction.objects.filter(
                bank_account=cuenta,
                transaction_date__range=(fecha_inicio, fecha_fin)
            ).order_by('transaction_date', 'created_at')
            
            # Extractos del período
            extractos_periodo = ExtractoBancario.objects.filter(
                bank_account=cuenta,
                period_start__lte=fecha_fin,
                period_end__gte=fecha_inicio
            ).order_by('period_start')
            
            # Items de extracto del período
            extracto_items_periodo = ExtractoBancarioDetalle.objects.filter(
                extracto__in=extractos_periodo,
                fecha__range=(fecha_inicio, fecha_fin)
            ).order_by('fecha')
            
            # Calcular estadísticas
            stats_transacciones = transacciones_periodo.aggregate(
                total_count=Count('id'),
                conciliadas_count=Count('id', filter=Q(is_reconciled=True)),
                total_debitos=Sum('amount', filter=Q(transaction_type__in=['debit', 'transfer_out', 'fee'])),
                total_creditos=Sum('amount', filter=Q(transaction_type__in=['credit', 'transfer_in', 'interest'])),
                conciliadas_debitos=Sum('amount', filter=Q(
                    is_reconciled=True,
                    transaction_type__in=['debit', 'transfer_out', 'fee']
                )),
                conciliadas_creditos=Sum('amount', filter=Q(
                    is_reconciled=True,
                    transaction_type__in=['credit', 'transfer_in', 'interest']
                ))
            )
            
            stats_extractos = extracto_items_periodo.aggregate(
                total_count=Count('id'),
                conciliados_count=Count('id', filter=Q(is_reconciled=True)),
                total_debitos=Sum('debito'),
                total_creditos=Sum('credito')
            )
            
            # Calcular saldo final del sistema
            movimiento_neto = (stats_transacciones['total_creditos'] or Decimal('0.00')) - (stats_transacciones['total_debitos'] or Decimal('0.00'))
            saldo_final_sistema = saldo_inicial + movimiento_neto
            
            # Saldo final según extracto
            ultimo_extracto = extractos_periodo.order_by('-period_end').first()
            saldo_final_extracto = ultimo_extracto.final_balance if ultimo_extracto else None
            
            # Diferencia
            diferencia = None
            if saldo_final_extracto is not None:
                diferencia = saldo_final_extracto - saldo_final_sistema
            
            reporte_data = {
                'cuenta': cuenta,
                'periodo': {
                    'inicio': fecha_inicio,
                    'fin': fecha_fin,
                    'año': fecha_inicio.year,
                    'mes': fecha_inicio.month,
                    'mes_nombre': fecha_inicio.strftime('%B')
                },
                'saldos': {
                    'inicial': saldo_inicial,
                    'final_sistema': saldo_final_sistema,
                    'final_extracto': saldo_final_extracto,
                    'diferencia': diferencia
                },
                'transacciones': {
                    'queryset': transacciones_periodo,
                    'stats': stats_transacciones
                },
                'extractos': {
                    'queryset': extractos_periodo,
                    'items': extracto_items_periodo,
                    'stats': stats_extractos
                },
                'porcentaje_conciliacion_transacciones': (
                    (stats_transacciones['conciliadas_count'] / stats_transacciones['total_count']) * 100
                    if stats_transacciones['total_count'] > 0 else 0
                ),
                'porcentaje_conciliacion_extractos': (
                    (stats_extractos['conciliados_count'] / stats_extractos['total_count']) * 100
                    if stats_extractos['total_count'] > 0 else 0
                )
            }
        
        # Lista de cuentas para selector
        context['todas_las_cuentas'] = BankAccount.objects.filter(
            company=self.get_current_company(),
            is_active=True
        ).select_related('bank')
        
        # Generar opciones de años (últimos 3 años)
        año_actual = timezone.now().year
        context['años_disponibles'] = range(año_actual - 2, año_actual + 1)
        
        # Meses
        context['meses_disponibles'] = [
            (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
            (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
            (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
        ]
        
        context['reporte_data'] = reporte_data
        context['cuenta_seleccionada'] = cuenta
        context['año_seleccionado'] = int(año) if año else timezone.now().year
        context['mes_seleccionado'] = int(mes) if mes else timezone.now().month
        context['fecha_reporte'] = timezone.now()
        
        return context


# Vista AJAX para exportar reportes
class ExportarReporteView(LoginRequiredMixin, CompanyContextMixin, TemplateView):
    """
    Vista para exportar reportes en diferentes formatos (JSON, CSV)
    """
    
    def get(self, request, *args, **kwargs):
        formato = request.GET.get('formato', 'json')
        tipo_reporte = request.GET.get('tipo')
        
        if tipo_reporte == 'estado_conciliacion':
            return self._exportar_estado_conciliacion(formato)
        elif tipo_reporte == 'diferencias':
            return self._exportar_diferencias(formato)
        elif tipo_reporte == 'extracto_mensual':
            return self._exportar_extracto_mensual(formato)
        
        return JsonResponse({'error': 'Tipo de reporte no válido'}, status=400)
    
    def _exportar_estado_conciliacion(self, formato):
        """Exportar reporte de estado de conciliación"""
        # Reutilizar lógica de EstadoConciliacionPorCuentaView
        view = EstadoConciliacionPorCuentaView()
        view.request = self.request
        context = view.get_context_data()
        
        if formato == 'json':
            data = []
            for item in context['datos_reporte']:
                data.append({
                    'cuenta': str(item['cuenta']),
                    'banco': item['cuenta'].bank.name,
                    'total_transacciones': item['transacciones']['total_transacciones'],
                    'transacciones_conciliadas': item['transacciones']['conciliadas'],
                    'porcentaje_conciliacion': item['porcentaje_transacciones'],
                    'monto_conciliado': float(item['monto_conciliado']),
                    'monto_no_conciliado': float(item['monto_no_conciliado'])
                })
            
            response = JsonResponse({
                'reporte': 'estado_conciliacion',
                'fecha': context['fecha_reporte'].isoformat(),
                'datos': data
            })
            response['Content-Disposition'] = f'attachment; filename="estado_conciliacion_{timezone.now().strftime("%Y%m%d")}.json"'
            return response
        
        return JsonResponse({'error': 'Formato no soportado'}, status=400)
    
    def _exportar_diferencias(self, formato):
        """Exportar reporte de diferencias no conciliadas"""
        # Implementar exportación de diferencias
        return JsonResponse({'mensaje': 'Funcionalidad en desarrollo'})
    
    def _exportar_extracto_mensual(self, formato):
        """Exportar extracto de conciliación mensual"""
        # Implementar exportación de extracto mensual
        return JsonResponse({'mensaje': 'Funcionalidad en desarrollo'})