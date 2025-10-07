"""
Formularios para la conciliación bancaria
"""

from django import forms
from django.forms import modelformset_factory
from ..models import BankAccount, ExtractoBancario, BankTransaction, ExtractoBancarioDetalle


class ReconciliationFilterForm(forms.Form):
    """
    Formulario para filtrar la conciliación bancaria
    """
    bank_account = forms.ModelChoiceField(
        queryset=BankAccount.objects.none(),
        empty_label="Selecciona una cuenta bancaria",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_bank_account'
        }),
        label='Cuenta Bancaria'
    )
    
    extracto = forms.ModelChoiceField(
        queryset=ExtractoBancario.objects.none(),
        empty_label="Selecciona un extracto bancario",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_extracto'
        }),
        label='Extracto Bancario',
        required=False
    )
    
    fecha_desde = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='Fecha Desde',
        required=False
    )
    
    fecha_hasta = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='Fecha Hasta',
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        if company:
            self.fields['bank_account'].queryset = BankAccount.objects.filter(
                company=company
            ).select_related('bank')
            
        # Si hay datos y se seleccionó una cuenta bancaria, filtrar extractos ANTES de validar
        if self.data and self.data.get('bank_account'):
            try:
                bank_account_id = self.data.get('bank_account')
                if company:
                    # Verificar que la cuenta bancaria pertenezca a la empresa
                    bank_account = BankAccount.objects.filter(
                        id=bank_account_id,
                        company=company
                    ).first()
                    
                    if bank_account:
                        self.fields['extracto'].queryset = ExtractoBancario.objects.filter(
                            bank_account=bank_account
                        ).order_by('-period_end')
            except (ValueError, BankAccount.DoesNotExist):
                # Si hay error, mantener queryset vacío
                pass
            
    def filter_extractos(self, bank_account):
        """Filtra los extractos según la cuenta bancaria seleccionada"""
        if bank_account:
            self.fields['extracto'].queryset = ExtractoBancario.objects.filter(
                bank_account=bank_account
            ).order_by('-period_end')


class ReconciliationForm(forms.Form):
    """
    Formulario para procesar la conciliación
    """
    reconcile_transactions = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    reconcile_extracto_items = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    def __init__(self, transactions=None, extracto_items=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if transactions:
            self.fields['reconcile_transactions'].choices = [
                (t.id, f"{t.transaction_date} - {t.description} - {t.signed_amount}")
                for t in transactions
            ]
        
        if extracto_items:
            self.fields['reconcile_extracto_items'].choices = [
                (item.id, f"{item.fecha} - {item.descripcion} - {item.monto}")
                for item in extracto_items
            ]


class ExtractoBancarioUploadForm(forms.ModelForm):
    """
    Formulario para subir extractos bancarios
    """
    
    class Meta:
        model = ExtractoBancario
        fields = ['bank_account', 'file', 'period_start', 'period_end', 
                 'initial_balance', 'final_balance', 'notes']
        widgets = {
            'bank_account': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.csv,.xlsx,.xls'
            }),
            'period_start': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'period_end': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'initial_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'final_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            })
        }
    
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        if company:
            self.fields['bank_account'].queryset = BankAccount.objects.filter(
                company=company
            ).select_related('bank')