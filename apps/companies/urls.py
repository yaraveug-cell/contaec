from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'companies', views.CompanyViewSet, basename='company')
router.register(r'company-types', views.CompanyTypeViewSet, basename='companytype')
router.register(r'economic-activities', views.EconomicActivityViewSet, basename='economicactivity')

urlpatterns = [
    path('', include(router.urls)),
    path('switch/<int:company_id>/', views.SwitchCompanyView.as_view(), name='switch-company'),
    path('current/', views.CurrentCompanyView.as_view(), name='current-company'),
]