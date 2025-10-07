from django.urls import path
from . import views
from .views import print_purchase_invoice_pdf, print_multiple_purchase_invoices_pdf

app_name = 'suppliers'

urlpatterns = [
    # Comprobantes de retención - PDF
    path('retention-voucher/<int:invoice_id>/', 
         views.print_retention_voucher, 
         name='print_retention_voucher'),
    
    path('retention-vouchers/multiple/', 
         views.print_multiple_retention_vouchers, 
         name='print_multiple_retention_vouchers'),
    
    # Facturas de compra - PDF
    path('purchase-invoice/<int:invoice_id>/pdf/', 
         print_purchase_invoice_pdf, 
         name='print_purchase_invoice_pdf'),
    
    path('purchase-invoices/multiple/pdf/', 
         print_multiple_purchase_invoices_pdf, 
         name='print_multiple_purchase_invoices_pdf'),
    
    # Futuras URLs de API pueden agregarse aquí
]