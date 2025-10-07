from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_ajax import ProductDescriptionAutocompleteView, get_cash_accounts, get_all_accounts

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('ajax/product-description-autocomplete/', 
         ProductDescriptionAutocompleteView.as_view(), 
         name='product-description-autocomplete'),
    path('ajax/cash-accounts/', 
         get_cash_accounts, 
         name='cash-accounts'),
    path('ajax/all-accounts/', 
         get_all_accounts, 
         name='all-accounts'),
]